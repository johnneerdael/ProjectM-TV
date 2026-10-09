"""Claude routing and publication must fail closed at the current PR revision."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "claude_review.py"
HEAD = "a" * 40


def load_script():
    if not SCRIPT.exists():
        raise AssertionError("Trusted Claude reviewer tooling is not implemented")
    spec = importlib.util.spec_from_file_location("claude_review", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPT.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


class Api:
    def __init__(self):
        self.pr = dict(number=70, state="open", draft=False, base=dict(ref="main"),
                       head=dict(sha=HEAD, repo=dict(full_name="owner/repo")), user=dict(login="writer"))
        self.permission = "write"
        self.reviews = []
        self.writes = []

    def get(self, path):
        if path == "pulls/70":
            return self.pr
        if path.startswith("collaborators/"):
            return dict(permission=self.permission)
        raise AssertionError(path)

    def pages(self, path):
        return self.reviews

    def post(self, path, payload):
        self.writes.append((path, payload))


class ClaudeReviewTests(unittest.TestCase):
    def setUp(self):
        self.script = load_script()
        self.api = Api()
        self.event = dict(issue=dict(number=70, pull_request={}),
                          comment=dict(body="@claude review", user=dict(login="writer", type="User")))

    def prepare(self, event=None, name="issue_comment", ref="refs/heads/main", actor="writer", number="70"):
        return self.script.prepare(self.api, "owner/repo", name, event or self.event, ref, actor, number)

    def test_only_exact_authorized_pr_commands_route_to_reviewer(self):
        self.assertEqual(self.prepare(), (70, HEAD))
        for text in ["@claude review this", "@claude fix", "@claude review; echo bad"]:
            self.event["comment"]["body"] = text
            self.assertIsNone(self.prepare())
        self.event["comment"]["body"] = "  @claude   review\n"
        self.assertEqual(self.prepare(), (70, HEAD))
        self.api.permission = "read"
        self.assertIsNone(self.prepare())
        self.api.permission = "write"
        self.event["comment"]["user"]["type"] = "Bot"
        self.assertIsNone(self.prepare())

    def test_issue_mentions_drafts_closed_and_other_bases_never_review(self):
        self.event["issue"].pop("pull_request")
        self.assertIsNone(self.prepare())
        self.event["issue"]["pull_request"] = {}
        for key, value in [("draft", True), ("state", "closed")]:
            prior = self.api.pr[key]
            self.api.pr[key] = value
            self.assertIsNone(self.prepare())
            self.api.pr[key] = prior
        self.api.pr["base"]["ref"] = "other"
        self.assertIsNone(self.prepare())

    def test_initial_review_is_once_only_and_forks_need_manual_authorization(self):
        event = dict(pull_request=dict(number=70))
        self.assertEqual(self.prepare(event, "pull_request_target"), (70, HEAD))
        self.api.reviews = [dict(user=dict(login="claude[bot]", type="Bot"), body="## Claude Review\nprevious result")]
        self.assertIsNone(self.prepare(event, "pull_request_target"))
        self.api.reviews = []
        self.api.pr["head"]["repo"]["full_name"] = "fork/repo"
        self.assertIsNone(self.prepare(event, "pull_request_target"))
        self.assertEqual(self.prepare(), (70, HEAD))

    def test_dispatch_requires_main_write_actor_and_numeric_input(self):
        self.assertEqual(self.prepare(name="workflow_dispatch"), (70, HEAD))
        self.assertIsNone(self.prepare(name="workflow_dispatch", ref="refs/heads/feature"))
        self.api.permission = "read"
        self.assertIsNone(self.prepare(name="workflow_dispatch"))
        self.api.permission = "write"
        for number in ["70;evil", "0", "-1", ""]:
            with self.subTest(number=number):
                with self.assertRaises(ValueError):
                    self.prepare(name="workflow_dispatch", number=number)

    def publish(self, result=None, conclusion="success", head=HEAD):
        import json
        output = json.dumps(result if result is not None else dict(reviewed_commit=HEAD, approved=True, summary="No findings."))
        return self.script.publish(self.api, "owner/repo", 70, head, output, conclusion, "123")

    def test_only_complete_clean_matching_result_publishes_approval(self):
        self.publish()
        path, review = self.api.writes[-1]
        self.assertEqual(path, "pulls/70/reviews")
        self.assertEqual(review["event"], "APPROVE")
        self.assertEqual(review["commit_id"], HEAD)
        self.assertIn("**Result:** APPROVED", review["body"])
        self.assertIn("**Workflow run:** 123", review["body"])

    def test_findings_failed_empty_malformed_and_wrong_sha_do_not_approve(self):
        cases = [({}, "success"), (dict(reviewed_commit=HEAD, approved="true", summary="Bad type"), "success"),
                 (dict(reviewed_commit="b" * 40, approved=True, summary="Wrong head"), "success"),
                 (dict(reviewed_commit=HEAD, approved=True, summary=""), "success"),
                 (dict(reviewed_commit=HEAD, approved=True, summary="Clean"), "failure"),
                 (dict(reviewed_commit=HEAD, approved=False, summary="Bug in x.py:4"), "success")]
        for result, conclusion in cases:
            with self.subTest(result=result, conclusion=conclusion):
                self.api.writes.clear()
                self.publish(result, conclusion)
                self.assertEqual(self.api.writes[-1][1]["event"], "COMMENT")
        self.script.publish(self.api, "owner/repo", 70, HEAD, "not JSON", "success", "123")
        self.assertEqual(self.api.writes[-1][1]["event"], "COMMENT")

    def test_concurrent_push_or_close_prevents_any_publication(self):
        self.api.pr["head"]["sha"] = "b" * 40
        self.publish()
        self.assertEqual(self.api.writes, [])
        self.api.pr["head"]["sha"] = HEAD
        self.api.pr["state"] = "closed"
        self.publish()
        self.assertEqual(self.api.writes, [])

    def test_start_records_full_head_and_never_approves(self):
        self.script.start(self.api, "owner/repo", 70, HEAD, "123")
        self.assertEqual(self.api.writes[-1][1]["event"], "COMMENT")
        self.assertIn("**Result:** RUNNING", self.api.writes[-1][1]["body"])

    def test_source_wrapper_rejects_other_endpoints_and_method_flags(self):
        with patch.dict("os.environ", GITHUB_REPOSITORY="owner/repo"), patch.object(self.script, "GitHub", return_value=self.api):
            for endpoint in ["pulls/70/reviews", "../actions/secrets", "https://example.com"]:
                with self.subTest(endpoint=endpoint), patch.object(sys, "argv", ["claude_review.py", "read", "--path", endpoint]):
                    with self.assertRaises(ValueError):
                        self.script.main()
            with patch.object(sys, "argv", ["claude_review.py", "read", "--path", "contents/x?ref=" + HEAD, "--method", "POST"]):
                with self.assertRaises(SystemExit):
                    self.script.main()
        self.assertEqual(self.api.writes, [])
