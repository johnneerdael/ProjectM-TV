"""Regression coverage for review-gated PR builds."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "review_gate.py"


def load_gate():
    if not SCRIPT.exists():
        raise AssertionError("The review gate is not implemented")
    spec = importlib.util.spec_from_file_location("review_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HEAD = "a" * 40
BASE = "b" * 40
MERGE = "c" * 40
BOT = "chatgpt-codex-connector[bot]"


def snapshot():
    return dict(number=42, state="open", draft=False, base=dict(ref="main", sha=BASE),
                head=dict(sha=HEAD), mergeable=True, merge_commit_sha=MERGE,
                user=dict(login="author"), requested_reviewers=[], requested_teams=[])


def human(state="APPROVED", sha=HEAD, login="reviewer"):
    return dict(state=state, commit_id=sha, submitted_at="2026-10-05T10:00:00Z",
                user=dict(login=login, type="User"), author_association="COLLABORATOR")


def summary(state="Completed", sha=HEAD[:7], login=BOT):
    return dict(user=dict(login=login), body=(
        "<!-- codex-pull-request-review-summary -->\n"
        "| Review | Status | Commit | Review trigger |\n"
        f"| 📝 **Code Review** | ✅ **{state}** | `{sha}` | Manual request |"))


class EligibilityTests(unittest.TestCase):
    def setUp(self):
        self.gate = load_gate()

    def eligible(self, reviews=None, comments=None, threads=None, pr=None):
        return self.gate.eligibility(pr or snapshot(), reviews or [], comments or [], threads or [])[0]

    def test_no_review_or_stale_review_does_not_unlock_builds(self):
        self.assertFalse(self.eligible())
        self.assertFalse(self.eligible([human(sha=BASE)]))

    def test_current_human_review_or_codex_completion_unlocks(self):
        self.assertTrue(self.eligible([human()]))
        self.assertTrue(self.eligible([human(state="COMMENTED")]))
        self.assertTrue(self.eligible(comments=[summary()]))

    def test_author_and_untrusted_bot_or_comment_cannot_unlock(self):
        self.assertFalse(self.eligible([human(login="author")]))
        self.assertFalse(self.eligible(comments=[summary(login="author")]))
        review = human()
        review["author_association"] = "NONE"
        self.assertFalse(self.eligible([review]))

    def test_stale_or_running_codex_summary_is_not_completion(self):
        self.assertFalse(self.eligible(comments=[summary(sha=BASE[:7])]))
        self.assertFalse(self.eligible(comments=[summary(state="In progress")]))
        self.assertFalse(self.eligible([human()], [summary(state="In progress")]))

    def test_submitted_codex_review_with_findings_counts_after_resolution(self):
        review = human(state="COMMENTED", login=BOT)
        review["user"]["type"] = "Bot"
        self.assertTrue(self.eligible([review], threads=[dict(isResolved=True)]))
        self.assertFalse(self.eligible([review], threads=[dict(isResolved=False)]))

    def test_unresolved_outdated_thread_still_blocks(self):
        self.assertFalse(self.eligible([human()], threads=[dict(isResolved=False, isOutdated=True)]))

    def test_outstanding_changes_requested_block_even_after_new_comment(self):
        rejected = human(state="CHANGES_REQUESTED", sha=BASE)
        self.assertFalse(self.eligible([rejected, human(state="COMMENTED")]))
        self.assertTrue(self.eligible([rejected, human()]))

    def test_pending_or_requested_review_blocks(self):
        self.assertFalse(self.eligible([human(), human(state="PENDING", login="second")]))
        pr = snapshot()
        pr["requested_reviewers"] = [dict(login="second")]
        self.assertFalse(self.eligible([human()], pr=pr))

    def test_non_main_draft_closed_or_conflicting_pr_blocks(self):
        for field, value in [("draft", True), ("state", "closed"), ("mergeable", False), ("mergeable", None)]:
            pr = snapshot()
            pr[field] = value
            self.assertFalse(self.eligible([human()], pr=pr))
        pr = snapshot()
        pr["base"]["ref"] = "release"
        self.assertFalse(self.eligible([human()], pr=pr))

    def test_dismissed_review_does_not_count(self):
        self.assertFalse(self.eligible([human(state="DISMISSED")]))


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.gate = load_gate()

    def test_every_build_must_succeed(self):
        for outcome in ["skipped", "failure", "cancelled", ""]:
            self.assertFalse(self.gate.builds_passed(dict(android="success", presets="success", docs=outcome)))
        self.assertFalse(self.gate.builds_passed({}))
        self.assertTrue(self.gate.builds_passed(dict(android="success", presets="success", docs="success")))

    def test_build_snapshot_must_match_current_head_and_base(self):
        self.assertTrue(self.gate.matches(snapshot(), HEAD, BASE, MERGE))
        self.assertFalse(self.gate.matches(snapshot(), BASE, BASE, MERGE))
        self.assertFalse(self.gate.matches(snapshot(), HEAD, HEAD, MERGE))
        self.assertFalse(self.gate.matches(snapshot(), HEAD, BASE, BASE))


class FakeGitHub:
    def __init__(self, gate, ready=True):
        self.gate = gate
        self.ready = ready
        self.pr = snapshot()
        self.runs = []
        self.statuses = []
        self.writes = []

    def snapshot(self, number):
        return self.pr, (self.ready, "Waiting for review")

    def pages(self, path, key=None):
        return self.runs if path.startswith("actions/") else self.statuses

    def status(self, head, state, description, url=None):
        self.writes.append((state, description))
        self.statuses.insert(0, dict(context=self.gate.CONTEXT, state=state,
                                    description=description, created_at="2099-01-01T00:00:00Z"))

    def post(self, path, data):
        self.writes.append((path, data))

    def run(self, status="in_progress", conclusion=None):
        return dict(id=1, display_title=self.gate.title(self.pr), head_branch="main",
                    status=status, conclusion=conclusion, html_url="https://example.test/run/1")


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.gate = load_gate()
        self.api = FakeGitHub(self.gate)

    def test_waiting_review_does_not_dispatch(self):
        self.api.ready = False
        self.gate.reconcile(self.api, 42)
        self.assertEqual(self.api.writes, [("pending", "Waiting for review")])

    def test_ready_dispatches_once_on_main_with_exact_shas(self):
        self.gate.reconcile(self.api, 42)
        self.gate.reconcile(self.api, 42)
        dispatches = [data for path, data in self.api.writes if path.endswith("/dispatches")]
        self.assertEqual(dispatches, [dict(ref="main", inputs=dict(pr_number="42", head_sha=HEAD,
                                                                 base_sha=BASE, merge_sha=MERGE))])

    def test_running_build_is_not_duplicated(self):
        self.api.runs = [self.api.run()]
        self.gate.reconcile(self.api, 42)
        self.assertEqual(len(self.api.writes), 1)
        self.assertEqual(self.api.writes[0][0], "pending")

    def test_new_finding_revokes_success_and_cancels_running_builds(self):
        self.api.ready = False
        self.api.runs = [self.api.run()]
        self.gate.reconcile(self.api, 42)
        self.assertEqual(self.api.writes[0][0], "pending")
        self.assertEqual(self.api.writes[1], ("actions/runs/1/cancel", {}))

    def test_failed_or_skipped_build_is_not_reported_as_success(self):
        self.api.runs = [self.api.run("completed", "failure")]
        self.gate.reconcile(self.api, 42)
        self.assertEqual(self.api.writes[0][0], "failure")
        self.assertEqual(len(self.api.writes), 1)

    def test_push_cancels_validation_of_the_old_head_before_new_review(self):
        old = self.api.run()
        old["display_title"] = old["display_title"].replace(HEAD, MERGE)
        self.api.runs = [old]
        self.api.ready = False
        self.gate.reconcile(self.api, 42)
        self.assertIn(("actions/runs/1/cancel", {}), self.api.writes)

    def test_explicit_retry_can_restart_failed_validation(self):
        self.api.runs = [self.api.run("completed", "failure")]
        self.gate.reconcile(self.api, 42, retry=True)
        self.assertTrue(self.api.writes[-1][0].endswith("/dispatches"))

    def test_success_is_reused_only_for_current_base(self):
        self.api.statuses = [dict(context=self.gate.CONTEXT, state="success",
                                 description=f"Passed all builds against main {BASE}")]
        self.gate.reconcile(self.api, 42)
        self.assertEqual(self.api.writes, [])
        self.api.pr["base"]["sha"] = HEAD
        self.gate.reconcile(self.api, 42)
        self.assertTrue(self.api.writes[-1][0].endswith("/dispatches"))


if __name__ == "__main__":
    unittest.main()
