"""Regression coverage for review-gated PR builds."""
import importlib.util
import copy
import io
import json
import os
import re
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

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


def codex_review(sha=HEAD):
    review = human(state="COMMENTED", sha=sha, login=BOT)
    review["user"]["type"] = "Bot"
    review["body"] = f"### 💡 Codex Review\n\n**Reviewed commit:** `{sha[:10]}`"
    return review


def summary(state="Completed", sha=HEAD, login=BOT):
    return dict(user=dict(login=login, type="Bot" if login == BOT else "User"), updated_at="2026-10-05T10:00:00Z", body=(
        "<!-- codex-pull-request-review-summary -->\n"
        "| Review | Status | Commit | Review trigger |\n"
        f'| 📝 **Code Review** | ✅ **{state}** <relative-time datetime="2026-10-05T10:00:00Z">10:00</relative-time> | `{sha}` | Manual request |'))


def set_summary_time(comment, timestamp):
    comment["updated_at"] = timestamp
    comment["body"] = re.sub(r'datetime="[^"]+"', f'datetime="{timestamp}"', comment["body"])


def legacy_completion(sha=HEAD, login=BOT):
    return dict(user=dict(login=login, type="Bot" if login == BOT else "User"), created_at="2026-10-05T10:00:00Z",
                body=f"Codex Review: No findings.\n\n**Reviewed commit:** `{sha}`")


def claude_review(result="APPROVED", sha=HEAD, login="claude[bot]", timestamp="2026-10-05T12:00:00Z"):
    return dict(state="APPROVED" if result == "APPROVED" else "COMMENTED", commit_id=sha,
                submitted_at=timestamp, user=dict(login=login, type="Bot"), _workflow_verified=True,
                body=f"## Claude Review\n\n**Reviewed commit:** `{sha}`\n**Result:** {result}\n**Workflow run:** 123")


class ClaudeEligibilityTests(unittest.TestCase):
    def setUp(self):
        self.gate = load_gate()

    def check(self, reviews=(), comments=(), reactions=(), pr=None, threads=()):
        return self.gate.eligibility(pr or snapshot(), reviews, comments, threads, reactions)[0]

    def test_current_clean_claude_review_can_sign_off_without_codex(self):
        self.assertTrue(self.check([claude_review()]))

    def test_claude_completion_findings_stale_or_spoofed_never_sign_off(self):
        for result in ["RUNNING", "FINDINGS", "INCOMPLETE"]:
            self.assertFalse(self.check([claude_review(result)]))
        for login in ["author", "claude"]:
            self.assertFalse(self.check([claude_review(login=login)]))
        self.assertTrue(self.check([claude_review(login="github-actions[bot]")]))
        for sha in [BASE, HEAD[:10]]:
            self.assertFalse(self.check([claude_review(sha=sha)]))
        report = claude_review()
        report["body"] = report["body"].replace(HEAD, BASE)
        self.assertFalse(self.check([report]))
        report = claude_review()
        report["user"]["type"] = "User"
        self.assertFalse(self.check([report]))

    def test_latest_code_command_selects_only_one_provider(self):
        codex = dict(user=dict(login="author"), body="@codex review", created_at="2026-10-05T09:00:00Z")
        claude = dict(user=dict(login="new-writer"), author_association="NONE", _claude_authorized=True,
                      body="@claude review", created_at="2026-10-05T11:00:00Z")
        self.assertTrue(self.check([claude_review()], [codex, claude]))
        self.assertFalse(self.check([claude_review()], [claude, dict(codex, created_at="2026-10-05T13:00:00Z")]))
        completed = summary()
        set_summary_time(completed, "2026-10-05T14:00:00Z")
        thumb = dict(user=dict(login=BOT), content="+1", created_at="2026-10-05T14:01:00Z")
        self.assertTrue(self.check([claude_review()], [claude, dict(codex, created_at="2026-10-05T13:00:00Z"), completed], [thumb]))

    def test_claude_request_requires_later_current_approval_and_security_stays_separate(self):
        request = dict(user=dict(login="author"), _claude_authorized=True, body="@claude review", created_at="2026-10-05T12:00:00Z")
        self.assertFalse(self.check([claude_review()], [request]))
        request["created_at"] = "2026-10-05T11:00:00Z"
        self.assertTrue(self.check([claude_review()], [request]))
        security = dict(request, body="@codex security review", created_at="2026-10-05T09:00:00Z")
        self.assertFalse(self.check([claude_review()], [security, request]))

    def test_unknown_claude_command_does_not_block_a_valid_review(self):
        request = dict(user=dict(login="stranger"), author_association="NONE", body="@claude review", created_at="2026-10-05T13:00:00Z")
        self.assertTrue(self.check([claude_review()], [request]))

    def test_claude_running_review_blocks_codex_until_terminal_or_run_finished(self):
        running = claude_review("RUNNING", login="github-actions[bot]")
        running["_workflow_active"] = True
        thumb = dict(user=dict(login=BOT), content="+1", created_at="2026-10-05T14:00:00Z")
        self.assertFalse(self.check([running], [summary()], [thumb]))
        running["_workflow_active"] = False
        self.assertTrue(self.check([running], [summary()], [thumb]))
        running["_workflow_active"] = True
        self.assertTrue(self.check([running, claude_review()], [summary()], [thumb]))

    def test_claude_approval_does_not_bypass_unresolved_threads(self):
        self.assertFalse(self.check([claude_review()], threads=[dict(isResolved=False)]))

    def test_later_findings_revoke_earlier_claude_signoff_until_new_review(self):
        finding = claude_review("FINDINGS", timestamp="2026-10-05T13:00:00Z")
        finding["body"] = finding["body"].replace("123", "124")
        self.assertFalse(self.check([claude_review(), finding]))
        self.assertTrue(self.check([finding, claude_review(timestamp="2026-10-05T14:00:00Z")]))
        thumb = dict(user=dict(login=BOT), content="+1", created_at="2026-10-05T14:01:00Z")
        completed = summary()
        self.assertFalse(self.check([finding], [completed], [thumb]))
        set_summary_time(completed, "2026-10-05T14:00:00Z")
        self.assertTrue(self.check([finding], [completed], [thumb]))

    def test_unverified_or_still_running_workflow_cannot_supply_approval(self):
        report = claude_review()
        report["_workflow_verified"] = False
        self.assertFalse(self.check([report]))
        report["_workflow_verified"] = True
        report["_workflow_active"] = True
        self.assertFalse(self.check([report]))

    def test_later_selected_codex_can_finish_while_older_claude_run_is_active(self):
        running = claude_review("RUNNING", login="github-actions[bot]")
        running["_workflow_active"] = True
        request = dict(user=dict(login="author"), body="@codex review", created_at="2026-10-05T13:00:00Z")
        completed = summary()
        set_summary_time(completed, "2026-10-05T14:00:00Z")
        thumb = dict(user=dict(login=BOT), content="+1", created_at="2026-10-05T14:01:00Z")
        self.assertTrue(self.check([running], [request, completed], [thumb]))

    def test_trusted_dispatch_selects_claude_over_an_older_codex_command(self):
        running = claude_review("RUNNING", login="github-actions[bot]", timestamp="2026-10-05T11:00:01Z")
        running.update(_workflow_event="workflow_dispatch", _workflow_started_at="2026-10-05T11:00:00Z", _workflow_active=False)
        codex = dict(user=dict(login="author"), body="@codex review", created_at="2026-10-05T09:00:00Z")
        self.assertTrue(self.check([running, claude_review()], [codex]))
        self.assertFalse(self.check([running], [codex, summary()]))

    def test_later_claude_selection_supersedes_older_running_codex_code_review(self):
        running = summary("Running")
        request = dict(user=dict(login="author"), _claude_authorized=True, body="@claude review", created_at="2026-10-05T11:00:00Z")
        self.assertTrue(self.check([claude_review()], [running, request]))
        self.assertFalse(self.check([claude_review()], [running]))
        running["body"] = running["body"].replace("**Code Review**", "**Security Review**")
        self.assertFalse(self.check([claude_review()], [running, request]))


    def test_external_author_cannot_select_claude_without_workflow_authorization(self):
        request = dict(user=dict(login="author"), body="@claude review", created_at="2026-10-05T13:00:00Z")
        self.assertTrue(self.check([claude_review()], [request]))
        request["_claude_authorized"] = True
        self.assertFalse(self.check([claude_review()], [request]))


class EligibilityTests(unittest.TestCase):
    def setUp(self):
        self.gate = load_gate()

    def eligible(self, reviews=None, comments=None, threads=None, pr=None, reactions=None):
        if reactions is None:
            reactions = [dict(user=dict(login=BOT, type="User"), content="+1", created_at="2026-10-05T23:00:00Z")]
        return self.gate.eligibility(pr or snapshot(), reviews or [], comments or [], threads or [], reactions)[0]

    def test_no_review_or_stale_review_does_not_unlock_builds(self):
        self.assertFalse(self.eligible())
        self.assertFalse(self.eligible([human(sha=BASE)]))

    def test_current_human_review_or_codex_thumb_with_metadata_unlocks(self):
        self.assertTrue(self.eligible([human()]))
        self.assertTrue(self.eligible([human(state="COMMENTED")]))
        self.assertTrue(self.eligible(comments=[summary()]))

    def test_full_hash_completion_metadata_and_thumb_can_qualify(self):
        for completion in [summary(), legacy_completion()]:
            with self.subTest(completion=completion):
                self.assertTrue(self.eligible(comments=[completion]))

    def test_unresolved_abbreviations_or_colliding_codex_hashes_never_qualify(self):
        other = HEAD[:7] + BASE[7:]
        for format_completion in [summary, legacy_completion]:
            for sha in [HEAD[:7], HEAD[:10], HEAD[:39], HEAD + "a", "a" * 64, other]:
                with self.subTest(format=format_completion.__name__, sha=sha):
                    self.assertFalse(self.eligible(comments=[format_completion(sha=sha)]))

    def test_abbreviated_completion_cannot_fulfill_a_pending_request(self):
        request = dict(user=dict(login="author"), body="@codex review", created_at="2026-10-05T09:00:00Z")
        for format_completion in [summary, legacy_completion]:
            with self.subTest(format=format_completion.__name__):
                self.assertFalse(self.eligible([human()], [request, format_completion(sha=HEAD[:7])]))

    def test_submitted_full_hash_review_can_qualify_with_short_summary(self):
        review = codex_review()
        self.assertTrue(self.eligible([review], [summary(sha=HEAD[:7])]))
        review["commit_id"] = HEAD[:7] + BASE[7:]
        self.assertFalse(self.eligible([review], [summary(sha=HEAD[:7])]))

    def test_bot_reply_review_record_cannot_count_as_codex_completion(self):
        reply = codex_review()
        reply["body"] = ""
        self.assertFalse(self.eligible([reply]))
        request = dict(user=dict(login="author"), body="@codex review", created_at="2026-10-05T09:00:00Z")
        self.assertFalse(self.eligible([human(), reply], [request]))

    def test_submitted_codex_completion_requires_full_commit_id(self):
        request = dict(user=dict(login="author"), body="@codex review", created_at="2026-10-05T09:00:00Z")
        self.assertFalse(self.eligible([human(), codex_review(sha=HEAD[:7])], [request]))

    def test_running_short_summary_blocks_despite_current_human_review(self):
        running = summary(state="Running", sha=HEAD[:7])
        running["_reviewed_commits"] = {HEAD[:7]: HEAD}
        self.assertFalse(self.eligible([human()], [running]))

    def test_author_and_untrusted_bot_or_comment_cannot_unlock(self):
        self.assertFalse(self.eligible([human(login="author")]))
        self.assertFalse(self.eligible(comments=[summary(login="author")]))
        review = human()
        review["author_association"] = "NONE"
        self.assertFalse(self.eligible([review]))

    def test_stale_or_running_codex_summary_is_not_completion(self):
        self.assertFalse(self.eligible(comments=[summary(sha=BASE)]))
        self.assertFalse(self.eligible(comments=[summary(state="In progress")]))
        self.assertFalse(self.eligible([human()], [summary(state="In progress")]))

    def test_authorized_codex_request_waits_for_later_completion(self):
        request = dict(user=dict(login="author"), body="@codex review", created_at="2026-10-05T11:00:00Z")
        self.assertFalse(self.eligible([human()], [request]))
        self.assertFalse(self.eligible([human()], [summary(), request]))
        completed = summary()
        set_summary_time(completed, "2026-10-05T12:00:00Z")
        self.assertTrue(self.eligible([human()], [completed, request]))

    def test_summary_without_its_own_time_cannot_clear_a_later_request(self):
        request = dict(user=dict(login="author"), body="@codex review", created_at="2026-10-05T11:00:00Z")
        completed = summary()
        completed["body"] = re.sub(r' <relative-time.*?</relative-time>', '', completed["body"])
        completed["updated_at"] = "2026-10-05T12:00:00Z"
        completed["body"] += (f'\n| **Security Review** | **Completed** '
                              f'<relative-time datetime="2026-10-05T12:00:00Z">12:00</relative-time> | `{HEAD}` | Manual request |')
        self.assertFalse(self.eligible([human()], [request, completed]))
        # A row-specific timestamp proves which review completed after the request.
        completed["body"] = completed["body"].replace('**Code Review** | ✅ **Completed**',
            '**Code Review** | ✅ **Completed** <relative-time datetime="2026-10-05T12:00:00Z">12:00</relative-time>')
        self.assertTrue(self.eligible([human()], [request, completed]))

    def test_same_second_completion_cannot_clear_a_new_or_edited_request(self):
        request = dict(user=dict(login="author"), body="@codex review",
                       created_at="2026-10-05T09:00:00Z", updated_at="2026-10-05T11:00:00Z")
        for timestamp, expected in [("2026-10-05T11:00:00Z", False),
                                    ("2026-10-05T11:00:00.999999Z", False),
                                    ("2026-10-05T11:00:01Z", True)]:
            completed = summary()
            set_summary_time(completed, timestamp)
            legacy = legacy_completion()
            legacy["created_at"] = timestamp
            reviewed = codex_review()
            reviewed["submitted_at"] = timestamp
            for reviews, comments in [([human()], [request, completed]),
                                      ([human()], [request, legacy]),
                                      ([human(), reviewed], [request])]:
                with self.subTest(timestamp=timestamp, reviews=reviews, comments=comments):
                    self.assertEqual(self.eligible(reviews, comments), expected)

    def test_edited_codex_command_requires_completion_after_latest_edit(self):
        for command, label in [("@codex review", "Code"), ("@codex security review", "Security")]:
            with self.subTest(command=command):
                request = dict(user=dict(login="author"), body=command,
                               created_at="2026-10-05T09:00:00Z", updated_at="2026-10-05T11:00:00Z")
                completed = summary()
                completed["body"] = completed["body"].replace("**Code Review**", f"**{label} Review**")
                self.assertFalse(self.eligible([human()], [completed, request]))
                set_summary_time(completed, "2026-10-05T12:00:00Z")
                self.assertTrue(self.eligible([human()], [completed, request]))
                # Editing the command again must invalidate that newer completion too.
                request["updated_at"] = "2026-10-05T13:00:00Z"
                self.assertFalse(self.eligible([human()], [completed, request]))

    def test_old_commit_completion_cannot_clear_a_request_for_current_head(self):
        request = dict(user=dict(login="author"), body="@codex review", created_at="2026-10-05T11:00:00Z")
        old_summary = summary(sha=BASE)
        set_summary_time(old_summary, "2026-10-05T12:00:00Z")
        old_legacy = legacy_completion(sha=BASE)
        old_legacy["created_at"] = "2026-10-05T12:00:00Z"
        old_review = codex_review(sha=BASE)
        old_review["submitted_at"] = "2026-10-05T12:00:00Z"
        for reviews, comments in [([human()], [request, old_summary]),
                                  ([human()], [request, old_legacy]),
                                  ([human(), old_review], [request])]:
            with self.subTest(reviews=reviews, comments=comments):
                self.assertFalse(self.eligible(reviews, comments))
        current = codex_review()
        current["submitted_at"] = "2026-10-05T12:00:00Z"
        self.assertTrue(self.eligible([human(), current], [request]))

    def test_unknown_commenter_cannot_request_review_or_fake_completion(self):
        request = dict(user=dict(login="stranger"), author_association="NONE", body="@codex review",
                       created_at="2026-10-05T11:00:00Z")
        self.assertTrue(self.eligible([human()], [request]))

    def test_security_review_request_needs_security_completion(self):
        request = dict(user=dict(login="author"), body="@codex security review", created_at="2026-10-05T09:00:00Z")
        self.assertFalse(self.eligible([human()], [summary(), request]))
        completed = summary()
        completed["body"] = completed["body"].replace("**Code Review**", "**Security Review**")
        self.assertTrue(self.eligible([human()], [completed, request]))

    def test_legacy_security_completion_requires_current_full_sha(self):
        request = dict(user=dict(login="author"), body="@codex security review", created_at="2026-10-05T09:00:00Z")
        for sha, expected in [(HEAD, True), (HEAD[:7], False), (BASE, False)]:
            with self.subTest(sha=sha):
                completion = legacy_completion(sha=sha)
                completion["body"] = completion["body"].replace("Codex Review:", "Codex Security Review:")
                self.assertEqual(self.eligible([human()], [request, completion]), expected)

    def test_submitted_codex_review_with_findings_counts_after_resolution(self):
        review = codex_review()
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


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.gate = load_gate()
        class Api(self.gate.GitHub):
            def __init__(self):
                super().__init__("owner/repo")
                self.pr = snapshot()
                self.main = [BASE, BASE]
                self.parents = [BASE, HEAD]
                self.reviews = [human()]
                self.comments = []
                self.reactions = []
                self.resolved = HEAD
                self.resolution_error = None
                self.permission = "write"

            def get(self, path):
                if path.startswith("collaborators/"):
                    return dict(permission=self.permission)
                if path == "actions/runs/123":
                    return dict(path=".github/workflows/claude-code-review.yml", head_branch="main", event="issue_comment",
                                status="completed", conclusion="success", created_at="2026-10-05T11:00:00Z", updated_at="2026-10-05T12:00:01Z")
                if path.startswith("git/matching-refs/"):
                    return []
                if path.startswith("commits/"):
                    if self.resolution_error:
                        raise self.resolution_error
                    return dict(sha=self.resolved)
                if path == "pulls/42":
                    return copy.deepcopy(self.pr)
                if path == "git/ref/heads/main":
                    return dict(object=dict(sha=self.main.pop(0)))
                if path == f"git/commits/{MERGE}":
                    return dict(parents=[dict(sha=sha) for sha in self.parents])
                raise AssertionError(path)

            def pages(self, path, key=None):
                if "/reviews?" in path:
                    return self.reviews
                if "/comments?" in path:
                    return self.comments
                if "/reactions?" in path:
                    return self.reactions
                return []

            def request(self, endpoint, data=None, paginate=False):
                return dict(data=dict(repository=dict(pullRequest=dict(reviewThreads=dict(
                    nodes=[], pageInfo=dict(hasNextPage=False))))))
        self.api = Api()

    def use_codex_approval(self):
        self.api.reviews = []
        self.api.comments = [summary(sha=HEAD[:7])]
        self.api.reactions = [dict(user=dict(login=BOT, type="User"), content="+1",
                                   created_at="2026-10-05T10:00:03Z")]

    def test_real_codex_short_summary_and_pr_reaction_are_loaded(self):
        self.use_codex_approval()
        pr, (ready, _) = self.api.snapshot(42)
        self.assertTrue(ready)
        self.assertEqual(pr["head"]["sha"], HEAD)

    def test_api_resolved_collision_cannot_approve_another_head(self):
        self.use_codex_approval()
        self.api.resolved = HEAD[:7] + BASE[7:]
        _, (ready, _) = self.api.snapshot(42)
        self.assertFalse(ready)

    def test_resolution_error_does_not_fall_back_to_prefix_matching(self):
        self.use_codex_approval()
        self.api.resolution_error = RuntimeError("Ambiguous commit")
        with self.assertRaises(RuntimeError):
            self.api.snapshot(42)

    def test_current_main_ref_is_used_instead_of_cached_pr_base(self):
        self.api.pr["base"]["sha"] = MERGE
        pr, (ready, _) = self.api.snapshot(42)
        self.assertEqual(pr["base"]["sha"], BASE)
        self.assertTrue(ready)

    def test_main_advancing_during_snapshot_requires_another_check(self):
        self.api.main = [BASE, MERGE]
        _, (ready, _) = self.api.snapshot(42)
        self.assertFalse(ready)

    def test_cached_merge_without_current_main_parent_cannot_qualify(self):
        self.api.parents = [MERGE, HEAD]
        _, (ready, _) = self.api.snapshot(42)
        self.assertFalse(ready)

    def test_claude_approval_requires_authentic_workflow_and_start_receipt(self):
        started = claude_review("RUNNING", login="github-actions[bot]", timestamp="2026-10-05T11:01:00Z")
        self.api.reviews = [started, claude_review()]
        _, (ready, _) = self.api.snapshot(42)
        self.assertTrue(ready)
        self.api.reviews = [claude_review()]
        self.api.main = [BASE, BASE]
        _, (ready, _) = self.api.snapshot(42)
        self.assertFalse(ready)

    def test_initial_target_workflow_reports_pr_branch_and_still_authenticates(self):
        started = claude_review("RUNNING", login="github-actions[bot]", timestamp="2026-10-05T11:01:00Z")
        self.api.reviews = [started, claude_review()]
        original = self.api.get
        def get(path):
            result = original(path)
            if path == "actions/runs/123":
                result.update(event="pull_request_target", head_branch="feature", head_sha=BASE,
                              pull_requests=[dict(number=42, base=dict(ref="main"), head=dict(sha=HEAD))])
            return result
        with patch.object(self.api, "get", get):
            _, (ready, _) = self.api.snapshot(42)
            self.assertTrue(ready)

    def test_snapshot_checks_the_same_writer_permission_as_the_claude_workflow(self):
        request = dict(user=dict(login="author", type="User"), body="@claude review", created_at="2026-10-05T11:00:00Z")
        self.api.comments = [request]
        self.api.permission = "read"
        _, (ready, _) = self.api.snapshot(42)
        self.assertTrue(ready)
        self.api.permission = "write"
        self.api.main = [BASE, BASE]
        _, (ready, _) = self.api.snapshot(42)
        self.assertFalse(ready)

    def test_claude_approval_from_other_workflow_or_after_run_end_cannot_qualify(self):
        started = claude_review("RUNNING", login="github-actions[bot]", timestamp="2026-10-05T11:01:00Z")
        self.api.reviews = [started, claude_review()]
        original = self.api.get
        for field, value in [("path", ".github/workflows/claude.yml"), ("head_branch", "feature"),
                             ("conclusion", "failure"), ("updated_at", "2026-10-05T11:30:00Z")]:
            def get(path):
                result = original(path)
                if path == "actions/runs/123":
                    result[field] = value
                return result
            with self.subTest(field=field), patch.object(self.api, "get", get):
                self.api.main = [BASE, BASE]
                _, (ready, _) = self.api.snapshot(42)
                self.assertFalse(ready)


class ReactionApprovalTests(unittest.TestCase):
    def setUp(self):
        self.gate = load_gate()

    def check(self, comments, reactions, reviews=None):
        # Raw reactions can label the connector account as User even though comments say Bot.
        pr = snapshot()
        return self.gate.eligibility(pr, reviews or [], comments, [], reactions)[0]

    def thumb(self, timestamp="2026-10-05T10:00:03Z", login=BOT, content="+1"):
        return dict(id=7, user=dict(login=login, type="User"), content=content, created_at=timestamp)

    def resolved(self, completion, sha=HEAD):
        completion["_reviewed_commits"] = {HEAD[:7]: sha, HEAD[:10]: sha}
        return completion

    def test_actual_short_summary_and_pr_thumb_unlock_current_head(self):
        self.assertTrue(self.check([self.resolved(summary(sha=HEAD[:7]))], [self.thumb()]))

    def test_completion_comment_without_pr_thumb_never_approves(self):
        self.assertFalse(self.check([summary()], []))
        self.assertFalse(self.check([legacy_completion()], []))
        self.assertFalse(self.check([], [], [codex_review()]))

    def test_thumb_without_current_revision_metadata_never_approves(self):
        self.assertFalse(self.check([], [self.thumb()]))
        self.assertFalse(self.check([summary(sha=BASE)], [self.thumb()]))
        self.assertFalse(self.check([self.resolved(summary(sha=HEAD[:7]), BASE)], [self.thumb()]))

    def test_only_connector_plus_one_on_pr_counts(self):
        for login, content in [("author", "+1"), ("stranger", "+1"), (BOT, "eyes"), (BOT, "heart")]:
            with self.subTest(login=login, content=content):
                self.assertFalse(self.check([summary()], [self.thumb(login=login, content=content)]))

    def test_old_thumb_cannot_approve_new_review_of_same_head(self):
        self.assertFalse(self.check([summary()], [self.thumb("2026-10-05T09:59:59Z")]))

    def test_running_review_blocks_even_with_pr_thumb(self):
        self.assertFalse(self.check([self.resolved(summary("Running", HEAD[:7]))], [self.thumb()]))

    def test_conflicting_written_and_api_review_revisions_cannot_approve(self):
        report = codex_review()
        report["body"] = f"### Codex Review\n**Reviewed commit:** `{BASE[:10]}`"
        self.assertFalse(self.check([], [self.thumb()], [report]))

    def test_connector_user_typed_review_cannot_bypass_thumb_as_human(self):
        report = codex_review()
        report["user"]["type"] = "User"
        report["body"] = ""
        self.assertFalse(self.check([], [], [report]))

    def test_resolved_short_legacy_metadata_and_thumb_can_approve(self):
        self.assertTrue(self.check([self.resolved(legacy_completion(HEAD[:10]))], [self.thumb()]))

    def test_reaction_does_not_override_unresolved_findings(self):
        pr = snapshot()
        self.assertFalse(self.gate.eligibility(pr, [], [summary()], [dict(isResolved=False)], [self.thumb()])[0])


class CommitResolutionTests(unittest.TestCase):
    def setUp(self):
        self.gate = load_gate()
        class Api(self.gate.GitHub):
            def __init__(self):
                super().__init__("owner/repo")
                self.paths = []
                self.refs = {"heads": [], "tags": []}
                self.resolved = HEAD
                self.error = None

            def get(self, path):
                self.paths.append(path)
                if path.startswith("git/matching-refs/"):
                    return self.refs[path.split("/")[2]]
                if self.error:
                    raise self.error
                return {"sha": self.resolved}
        self.api = Api()

    def test_short_hash_resolves_to_full_commit(self):
        self.assertEqual(self.api.resolve_review_commit(HEAD[:7]), HEAD)
        self.assertEqual(self.api.paths[-1], "commits/" + HEAD[:7])

    def test_full_hash_needs_no_network_resolution(self):
        self.assertEqual(self.api.resolve_review_commit(HEAD), HEAD)
        self.assertEqual(self.api.paths, [])

    def test_named_refs_cannot_shadow_a_commit_abbreviation(self):
        for namespace in ["heads", "tags"]:
            with self.subTest(namespace=namespace):
                self.api.paths = []
                self.api.refs[namespace] = [{"ref": f"refs/{namespace}/{HEAD[:7]}"}]
                self.assertIsNone(self.api.resolve_review_commit(HEAD[:7]))
                self.assertNotIn("commits/" + HEAD[:7], self.api.paths)
                self.api.refs[namespace] = []

    def test_similar_named_refs_do_not_block_commit_resolution(self):
        self.api.refs["heads"] = [{"ref": "refs/heads/" + HEAD[:7] + "-feature"}]
        self.assertEqual(self.api.resolve_review_commit(HEAD[:7]), HEAD)

    def test_invalid_or_wrong_prefix_response_fails_closed(self):
        for sha in [BASE, HEAD[:10], "a" * 64, None]:
            with self.subTest(sha=sha):
                self.api.resolved = sha
                with self.assertRaises(RuntimeError):
                    self.api.resolve_review_commit(HEAD[:7])

    def test_ambiguous_or_unavailable_resolution_fails_closed(self):
        self.api.error = RuntimeError("Ambiguous commit or API unavailable")
        with self.assertRaises(RuntimeError):
            self.api.resolve_review_commit(HEAD[:7])

    def test_invalid_identifiers_cannot_be_used_as_api_paths(self):
        for written in [HEAD[:6], HEAD + "a", "a" * 64, "main", "../main"]:
            self.assertIsNone(self.api.resolve_review_commit(written))
        self.assertEqual(self.api.paths, [])


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

    def get(self, path):
        return self.pr

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

    def finish(self, results, preflight="success"):
        env = dict(PR_HEAD=HEAD, PR_BASE=BASE, PR_MERGE=MERGE,
                   BUILD_RESULTS=json.dumps(results), GITHUB_RUN_ID="1", PREFLIGHT_RESULT=preflight)
        with patch.object(self.gate, "GitHub", return_value=self.api), patch.dict(os.environ, env), \
                patch("sys.argv", ["review_gate.py", "finish", "--repo", "owner/repo", "--pr", "42"]):
            self.gate.main()

    def test_successful_builds_rerun_once_after_review_eligibility_recovers(self):
        self.api.ready = False
        self.finish(dict(android="success", presets="success", docs="success"))
        self.assertEqual(self.api.statuses[0]["state"], "pending")
        self.api.runs = [self.api.run("completed", "success")]
        self.gate.reconcile(self.api, 42)
        self.assertFalse(any(path.endswith("/dispatches") for path, _ in self.api.writes))
        self.api.ready = True
        self.gate.reconcile(self.api, 42)
        self.gate.reconcile(self.api, 42)
        dispatches = [data for path, data in self.api.writes if path.endswith("/dispatches")]
        self.assertEqual(dispatches, [dict(ref="main", inputs=dict(pr_number="42", head_sha=HEAD,
                                                                 base_sha=BASE, merge_sha=MERGE))])
        self.assertNotIn("failure", [state for state, _ in self.api.writes])

    def test_recovered_preflight_with_no_builds_stays_pending_and_retries(self):
        # The preflight error is handled by the workflow, so no build jobs run.
        self.finish(dict(android="skipped", presets="skipped", docs="skipped"), preflight="failure")
        self.assertEqual(self.api.statuses[0]["state"], "pending")
        self.api.runs = [self.api.run("completed", "success")]
        self.gate.reconcile(self.api, 42)
        self.gate.reconcile(self.api, 42)
        self.assertEqual(sum(path.endswith("/dispatches") for path, _ in self.api.writes), 1)

    def test_skipped_jobs_after_successful_preflight_are_a_real_failure(self):
        with self.assertRaisesRegex(RuntimeError, "Required builds did not pass"):
            self.finish(dict(android="skipped", presets="skipped", docs="skipped"))
        self.assertEqual(self.api.statuses[0]["state"], "failure")

    def test_failed_preflight_does_not_hide_a_build_that_actually_failed(self):
        with self.assertRaisesRegex(RuntimeError, "Required builds did not pass"):
            self.finish(dict(android="failure", presets="skipped", docs="skipped"), preflight="failure")
        self.assertEqual(self.api.statuses[0]["state"], "failure")

    def test_preflight_revokes_prior_success_before_any_builds_start(self):
        self.api.statuses = [dict(context=self.gate.CONTEXT, state="success",
                                 description=f"Passed all builds against main {BASE}")]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            env = dict(PR_HEAD=HEAD, PR_BASE=BASE, PR_MERGE=MERGE, GITHUB_OUTPUT=str(output))
            with patch.object(self.gate, "GitHub", return_value=self.api), patch.dict(os.environ, env), \
                    patch("sys.argv", ["review_gate.py", "preflight", "--repo", "owner/repo", "--pr", "42"]):
                self.gate.main()
            self.assertEqual(output.read_text(), f"merge_sha={MERGE}\n")
        self.assertEqual(self.api.statuses[0]["state"], "pending")

    def test_reporter_read_error_after_successful_builds_is_retryable(self):
        with patch.object(self.api, "snapshot", side_effect=RuntimeError("GitHub unavailable")):
            self.finish(dict(android="success", presets="success", docs="success"))
        self.assertEqual(self.api.statuses[0]["state"], "pending")
        self.api.runs = [self.api.run("completed", "success")]
        self.gate.reconcile(self.api, 42)
        self.assertTrue(self.api.writes[-1][0].endswith("/dispatches"))

    def test_old_reporter_api_error_never_invalidates_new_head_status(self):
        self.api.pr["head"]["sha"] = BASE
        with patch.object(self.api, "snapshot", side_effect=RuntimeError("GitHub unavailable")), \
                patch.object(self.api, "status", wraps=self.api.status) as status:
            self.finish(dict(android="success", presets="success", docs="success"))
        self.assertTrue(status.called)
        self.assertTrue(all(call.args[0] == HEAD for call in status.call_args_list))

    def test_reporter_status_error_after_successful_builds_is_retryable(self):
        original = self.api.status
        def unavailable_once(head, state, description, url=None):
            if state == "success":
                raise RuntimeError("GitHub status unavailable")
            return original(head, state, description, url)
        with patch.object(self.api, "status", side_effect=unavailable_once):
            self.finish(dict(android="success", presets="success", docs="success"))
        self.assertEqual(self.api.statuses[0]["state"], "pending")
        self.api.runs = [self.api.run("completed", "success")]
        self.gate.reconcile(self.api, 42)
        self.assertTrue(self.api.writes[-1][0].endswith("/dispatches"))

    def test_reporter_error_does_not_mask_an_actual_failed_build(self):
        with patch.object(self.api, "snapshot", side_effect=RuntimeError("GitHub unavailable")):
            with self.assertRaisesRegex(RuntimeError, "GitHub unavailable"):
                self.finish(dict(android="failure", presets="success", docs="success"))

    def test_failed_builds_still_need_retry_after_review_eligibility_recovers(self):
        self.api.ready = False
        self.finish(dict(android="success", presets="failure", docs="success"))
        self.api.runs = [self.api.run("completed", "failure")]
        self.api.ready = True
        self.gate.reconcile(self.api, 42)
        self.assertEqual(self.api.statuses[0]["state"], "failure")
        self.assertFalse(any(path.endswith("/dispatches") for path, _ in self.api.writes))

    def test_push_cancels_validation_of_the_old_head_before_new_review(self):
        old = self.api.run()
        old["display_title"] = old["display_title"].replace(HEAD, MERGE)
        self.api.runs = [old]
        self.api.ready = False
        self.gate.reconcile(self.api, 42)
        self.assertIn(("actions/runs/1/cancel", {}), self.api.writes)

    def test_inspect_reports_revisions_without_writing_or_dispatching(self):
        output = io.StringIO()
        with patch.object(self.gate, "GitHub", return_value=self.api), \
                patch("sys.argv", ["review_gate.py", "inspect", "--repo", "owner/repo", "--pr", "42"]), \
                patch("sys.stdout", output):
            self.gate.main()
        self.assertEqual(json.loads(output.getvalue()), dict(pr=42, head=HEAD, base=BASE,
                         merge=MERGE, eligible=True, reason="Waiting for review"))
        self.assertEqual(self.api.writes, [])

    def test_inspect_requires_one_specific_pr(self):
        with patch.object(self.gate, "GitHub", return_value=self.api), \
                patch("sys.argv", ["review_gate.py", "inspect", "--repo", "owner/repo"]):
            with self.assertRaisesRegex(ValueError, "positive PR"):
                self.gate.main()
        self.assertEqual(self.api.writes, [])

    def test_review_read_failure_invalidates_a_previous_passing_status(self):
        class FailingApi(FakeGitHub):
            def snapshot(self, number):
                raise RuntimeError("GraphQL unavailable")

            def get(self, path):
                return self.pr

        api = FailingApi(self.gate)
        with self.assertRaisesRegex(RuntimeError, "GraphQL unavailable"):
            self.gate.reconcile_safely(api, [42])
        self.assertEqual(api.writes[0][0], "pending")

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
