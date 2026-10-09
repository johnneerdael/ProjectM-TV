#!/usr/bin/env python3
"""Trusted Claude review routing and current-head native review publication."""
import argparse
import json
import os
from pathlib import Path
import re
from review_gate import GitHub, writer
REVIEWERS = {"claude[bot]", "github-actions[bot]"}


def ready(pr):
    return pr["state"] == "open" and not pr["draft"] and pr["base"]["ref"] == "main"


def prepare(api, repo, name, event, ref, actor, input_number):
    if ref != "refs/heads/main":
        return None
    if name == "issue_comment":
        comment = event["comment"]
        if ("pull_request" not in event["issue"] or comment["user"].get("type") != "User"
                or not re.fullmatch(r"@claude\s+review", (comment.get("body") or "").strip(), re.I)):
            return None
        if not writer(api, comment["user"]["login"]):
            return None
        number = event["issue"]["number"]
    elif name == "workflow_dispatch":
        if not re.fullmatch(r"[1-9][0-9]*", input_number):
            raise ValueError("A positive numeric PR number is required")
        if not writer(api, actor):
            return None
        number = int(input_number)
    elif name == "pull_request_target":
        number = event["pull_request"]["number"]
    else:
        return None
    if type(number) is not int or number <= 0:
        raise ValueError("A positive numeric PR number is required")
    pr = api.get(f"pulls/{number}")
    if not ready(pr):
        return None
    if name == "pull_request_target":
        # Never spend credentials automatically on untrusted authors/forks.
        if (pr["head"].get("repo") or {}).get("full_name") != repo or not writer(api, pr["user"]["login"]):
            return None
        reviews = api.pages(f"pulls/{number}/reviews?per_page=100")
        if any(review["user"]["login"] in REVIEWERS and review["user"].get("type") == "Bot"
               and (review.get("body") or "").startswith("## Claude Review\n") for review in reviews):
            return None
    head = pr["head"]["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise ValueError("GitHub did not supply a full head SHA")
    return number, head


def current(api, number, head):
    if type(number) is not int or number <= 0 or not re.fullmatch(r"[0-9a-f]{40}", head):
        raise ValueError("A positive PR number and full expected SHA are required")
    pr = api.get(f"pulls/{number}")
    return ready(pr) and pr["head"]["sha"] == head


def record(api, repo, number, head, run, result, summary):
    if not re.fullmatch(r"[1-9][0-9]*", run):
        raise ValueError("A numeric workflow run ID is required")
    if not current(api, number, head):
        print("PR closed, became draft or changed revision; no review published.")
        return None
    body = (f"## Claude Review\n\n**Reviewed commit:** `{head}`\n**Result:** {result}\n"
            f"**Workflow run:** {run}\n\n{summary}\n\n"
            f"[Review run](https://github.com/{repo}/actions/runs/{run})")
    api.post(f"pulls/{number}/reviews", dict(commit_id=head, event="APPROVE" if result == "APPROVED" else "COMMENT", body=body))
    return result


def start(api, repo, number, head, run):
    return record(api, repo, number, head, run, "RUNNING", "Claude is reviewing this revision. This is not approval.")


def publish(api, repo, number, head, output, conclusion, run):
    result, summary = "INCOMPLETE", "Claude did not return a complete, valid review for this revision. No approval was granted."
    try:
        review = json.loads(output)
    except (json.JSONDecodeError, TypeError):
        review = None
    if (conclusion == "success" and isinstance(review, dict)
            and set(review) == {"reviewed_commit", "approved", "summary"}
            and review["reviewed_commit"] == head and type(review["approved"]) is bool
            and isinstance(review["summary"], str) and review["summary"].strip()):
        result = "APPROVED" if review["approved"] else "FINDINGS"
        summary = review["summary"].strip()
    return record(api, repo, number, head, run, result, summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "start", "publish", "read"])
    parser.add_argument("--path")
    args = parser.parse_args()
    repo = os.environ["GITHUB_REPOSITORY"]
    api = GitHub(repo)
    if args.mode == "read":
        # Keep inspection read-only even though feedback uses a write-capable App token.
        if not args.path or not re.match(r"^(contents/|git/trees/|git/blobs/|commits/)", args.path):
            raise ValueError("Only repository source/commit read endpoints are supported")
        print(json.dumps(api.get(args.path)))
        return
    if args.mode == "prepare":
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
        request = prepare(api, repo, os.environ["GITHUB_EVENT_NAME"], event, os.environ["GITHUB_REF"],
                          os.environ["GITHUB_ACTOR"], os.environ.get("INPUT_PR_NUMBER", ""))
        with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as target:
            target.write(f"eligible={'true' if request else 'false'}\n")
            if request:
                target.write(f"pr_number={request[0]}\nhead_sha={request[1]}\n")
        return
    number, head, run = int(os.environ["PR_NUMBER"]), os.environ["EXPECTED_HEAD"], os.environ["GITHUB_RUN_ID"]
    if args.mode == "start":
        start(api, repo, number, head, run)
    else:
        result = publish(api, repo, number, head, os.environ.get("REVIEW_OUTPUT", ""),
                         os.environ.get("REVIEW_CONCLUSION", ""), run)
        if result == "INCOMPLETE":
            raise SystemExit("Claude review was incomplete; no signoff published")


if __name__ == "__main__":
    main()
