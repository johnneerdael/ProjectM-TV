#!/usr/bin/env python3
"""Trusted controller for reviewed PR validation; run only from main."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import subprocess

CONTEXT = "Reviewed PR builds"
WORKFLOW = "pr-builds.yml"
CODEX = "chatgpt-codex-connector[bot]"
TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}


def eligibility(pr, reviews, comments, threads):
    if pr["state"] != "open" or pr["draft"] or pr["base"]["ref"] != "main":
        return False, "Waiting for an open, ready PR targeting main"
    if pr.get("requested_reviewers") or pr.get("requested_teams"):
        return False, "Waiting for requested reviews"
    if any(not thread["isResolved"] for thread in threads):
        return False, "Waiting for all review threads to be resolved"
    # GitHub hides other users' private drafts. Outstanding review requests above
    # are the observable blocking signal; also reject any draft the API does expose.
    if any(review["state"] == "PENDING" for review in reviews):
        return False, "Waiting for a visible pending review"
    # A comment-only follow-up does not revoke a request for changes.
    decisions = {}
    for review in reviews:
        if review["state"] in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            decisions[review["user"]["login"]] = review["state"]
    if "CHANGES_REQUESTED" in decisions.values():
        return False, "Waiting for requested changes to be accepted"
    head = pr["head"]["sha"]
    completed = False
    requests, completions = {}, {}

    def completed_at(kind, value):
        if value:
            timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
            completions[kind] = max(timestamp, completions.get(kind, timestamp))

    for comment in comments:
        user = comment["user"]["login"]
        trusted = user == pr["user"]["login"] or comment.get("author_association") in TRUSTED
        request = re.match(r"^@codex\s+(security\s+)?review\b", (comment.get("body") or "").strip(), re.I)
        if trusted and request and comment.get("created_at"):
            kind = "security" if request[1] else "code"
            timestamp = datetime.fromisoformat(comment["created_at"].replace("Z", "+00:00"))
            requests[kind] = max(timestamp, requests.get(kind, timestamp))
    for comment in comments:
        if comment["user"]["login"] != CODEX:
            continue
        body = comment.get("body") or ""
        if "<!-- codex-pull-request-review-summary -->" in body:
            for row in body.splitlines():
                if "**Code Review**" not in row and "**Security Review**" not in row:
                    continue
                commit = re.search(r"`([0-9a-f]{7,40})`", row)
                if commit and "**Completed**" in row:
                    completed = completed or head.startswith(commit[1])
                    kind = "security" if "**Security Review**" in row else "code"
                    date = re.search(r'datetime="([^"]+)"', row)
                    completed_at(kind, date[1] if date else comment.get("updated_at"))
                elif commit and head.startswith(commit[1]):
                    return False, "Waiting for Codex review to finish"
        else:
            commit = re.search(r"\*\*Reviewed commit:\*\*\s*`([0-9a-f]{7,40})`", body)
            if commit and "Codex Review" in body:
                completed = completed or head.startswith(commit[1])
                kind = "security" if re.search(r"Codex Security Review", body, re.I) else "code"
                completed_at(kind, comment.get("created_at"))
    for review in reviews:
        user = review["user"]
        trusted = user["login"] == CODEX or (
            user.get("type") == "User" and user["login"] != pr["user"]["login"]
            and review.get("author_association") in TRUSTED)
        if user["login"] == CODEX and review.get("submitted_at") and review["state"] in {"APPROVED", "COMMENTED"}:
            kind = "security" if re.search(r"Codex Security Review", review.get("body") or "", re.I) else "code"
            completed_at(kind, review["submitted_at"])
        if (trusted and review.get("submitted_at") and review["commit_id"] == head
                and review["state"] in {"APPROVED", "COMMENTED"}):
            completed = True
    if any(kind not in completions or completions[kind] < timestamp for kind, timestamp in requests.items()):
        return False, "Waiting for requested Codex reviews to finish"
    if not completed:
        return False, "Waiting for a completed review of the latest commit"
    if pr.get("mergeable") is not True or not pr.get("merge_commit_sha"):
        return False, "Waiting for a mergeable PR and its test merge commit"
    return True, "Review complete; no outstanding findings"


def matches(pr, head, base, merge):
    return (pr["head"]["sha"], pr["base"]["sha"], pr.get("merge_commit_sha")) == (head, base, merge)


def builds_passed(results):
    return set(results) == {"android", "presets", "docs"} and all(value == "success" for value in results.values())


class GitHub:
    def __init__(self, repo):
        self.repo = repo

    def request(self, endpoint, data=None, paginate=False):
        command = ["gh", "api", endpoint]
        if data is not None:
            command += ["--method", "POST", "--input", "-"]
        if paginate:
            command += ["--paginate", "--slurp"]
        result = subprocess.run(command, input=json.dumps(data) if data is not None else None,
                                text=True, capture_output=True, check=True)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def get(self, path):
        return self.request(f"repos/{self.repo}/{path}")

    def post(self, path, data):
        return self.request(f"repos/{self.repo}/{path}", data)

    def pages(self, path, key=None):
        pages = self.request(f"repos/{self.repo}/{path}", paginate=True)
        return [item for page in pages for item in (page[key] if key else page)]

    def snapshot(self, number):
        pr = self.get(f"pulls/{number}")
        reviews = self.pages(f"pulls/{number}/reviews?per_page=100")
        comments = self.pages(f"issues/{number}/comments?per_page=100")
        owner, name = self.repo.split("/")
        threads, cursor = [], None
        while True:
            data = self.request("graphql", dict(query="""
              query($owner:String!, $name:String!, $number:Int!, $cursor:String) {
                repository(owner:$owner,name:$name) {
                  pullRequest(number:$number) {
                    reviewThreads(first:100,after:$cursor) {
                      nodes { isResolved }
                      pageInfo { hasNextPage endCursor }
                    }
                  }
                }
              }""", variables=dict(owner=owner, name=name, number=number, cursor=cursor)))
            if data.get("errors"):
                raise RuntimeError(f"Cannot read review threads: {data['errors']}")
            connection = data["data"]["repository"]["pullRequest"]["reviewThreads"]
            threads.extend(connection["nodes"])
            if not connection["pageInfo"]["hasNextPage"]:
                break
            cursor = connection["pageInfo"]["endCursor"]
        # Re-read to reject a snapshot collected across a push or base change.
        current = self.get(f"pulls/{number}")
        if not matches(current, pr["head"]["sha"], pr["base"]["sha"], pr.get("merge_commit_sha")):
            return current, (False, "PR changed while reading reviews; recheck required")
        return current, eligibility(current, reviews, comments, threads)

    def status(self, head, state, description, url=None):
        previous = next((s for s in self.pages(f"commits/{head}/statuses?per_page=100")
                         if s["context"] == CONTEXT), None)
        if previous and (previous["state"], previous["description"]) == (state, description):
            return
        payload = dict(state=state, context=CONTEXT, description=description[:140])
        if url:
            payload["target_url"] = url
        self.post(f"statuses/{head}", payload)


def title(pr):
    return f"Reviewed PR #{pr['number']} @ {pr['head']['sha']} + {pr['base']['sha']}"


def reconcile(api, number, retry=False):
    pr, (ready, reason) = api.snapshot(number)
    all_runs = [run for run in api.pages(f"actions/workflows/{WORKFLOW}/runs?event=workflow_dispatch&per_page=100", "workflow_runs")
                if run["head_branch"] == "main" and run["display_title"].startswith(f"Reviewed PR #{number} @ ")]
    for run in all_runs:
        if run["status"] != "completed" and (run["display_title"] != title(pr) or pr["state"] != "open"):
            api.post(f"actions/runs/{run['id']}/cancel", {})
    if pr["state"] != "open" or pr["base"]["ref"] != "main":
        return
    head = pr["head"]["sha"]
    runs = [run for run in all_runs if run["display_title"] == title(pr)]
    runs.sort(key=lambda run: run["id"], reverse=True)
    active = [run for run in runs if run["status"] != "completed"]
    if not ready:
        api.status(head, "pending", reason)
        for run in active:
            api.post(f"actions/runs/{run['id']}/cancel", {})
        return
    if active:
        api.status(head, "pending", "Reviewed; full validation is running", active[0]["html_url"])
        return
    previous = next((s for s in api.pages(f"commits/{head}/statuses?per_page=100") if s["context"] == CONTEXT), None)
    passed = f"Passed all builds against main {pr['base']['sha']}"
    if previous and previous["state"] == "success" and previous["description"] == passed:
        return
    # A failed build is actionable; do not spend minutes retrying it every five minutes.
    if runs and not retry:
        last = runs[0]
        if last["conclusion"] not in {"cancelled", "skipped"}:
            api.status(head, "failure", "Validation did not pass; fix the PR or rerun validation", last["html_url"])
            return
    # Dispatch reservations prevent duplicate runs while GitHub queues a new workflow.
    reservation = f"Queued builds against main {pr['base']['sha']}"
    if previous and previous["state"] == "pending" and previous["description"] == reservation:
        created = datetime.fromisoformat(previous["created_at"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) - created < timedelta(minutes=20):
            return
    api.status(head, "pending", reservation)
    api.post(f"actions/workflows/{WORKFLOW}/dispatches", dict(ref="main", inputs=dict(
        pr_number=str(number), head_sha=head, base_sha=pr["base"]["sha"], merge_sha=pr["merge_commit_sha"])))


def snapshot_safely(api, number):
    try:
        return api.snapshot(number)
    except (RuntimeError, subprocess.CalledProcessError, KeyError):
        pr = api.get(f"pulls/{number}")
        if pr["state"] == "open" and pr["base"]["ref"] == "main":
            api.status(pr["head"]["sha"], "pending", "Unable to verify review state; recheck required")
        raise


def reconcile_safely(api, numbers, retry=False):
    errors = []
    for number in numbers:
        try:
            reconcile(api, number, retry)
        except (RuntimeError, subprocess.CalledProcessError, KeyError) as error:
            # Fail closed if review reads fail after a previously successful build.
            try:
                pr = api.get(f"pulls/{number}")
                if pr["state"] == "open" and pr["base"]["ref"] == "main":
                    api.status(pr["head"]["sha"], "pending", "Unable to verify review state; recheck required")
            except (RuntimeError, subprocess.CalledProcessError, KeyError) as status_error:
                errors.append(f"PR #{number}: cannot invalidate status: {status_error}")
            errors.append(f"PR #{number}: {error}")
    if errors:
        raise RuntimeError("; ".join(errors))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["reconcile", "preflight", "finish"])
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"), required=not os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--pr", type=int, default=0)
    parser.add_argument("--retry", action="store_true")
    args = parser.parse_args()
    api = GitHub(args.repo)
    if args.mode == "reconcile":
        numbers = [args.pr] if args.pr else [pr["number"] for pr in api.pages("pulls?state=open&base=main&per_page=100")]
        reconcile_safely(api, numbers, args.retry)
        return
    head, base, merge = (os.environ[name] for name in ["PR_HEAD", "PR_BASE", "PR_MERGE"])
    if any(not re.fullmatch(r"[0-9a-f]{40}", sha) for sha in [head, base, merge]):
        raise ValueError("Full commit SHAs are required")
    pr, (ready, reason) = snapshot_safely(api, args.pr)
    ready = ready and matches(pr, head, base, merge)
    if args.mode == "preflight":
        if not ready:
            raise RuntimeError(f"PR is not eligible or its revision changed: {reason}")
        with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
            output.write(f"merge_sha={merge}\n")
        return
    results = json.loads(os.environ["BUILD_RESULTS"])
    # Never mutate the new head's status from an old validation run.
    if pr["head"]["sha"] != head:
        return
    url = f"https://github.com/{args.repo}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    if not ready:
        api.status(head, "pending", "Review or base changed; fresh validation required", url)
    elif builds_passed(results):
        api.status(head, "success", f"Passed all builds against main {base}", url)
    else:
        api.status(head, "failure", "Validation failed, was cancelled, or skipped a required build", url)
        raise RuntimeError(f"Required builds did not pass: {results}")


if __name__ == "__main__":
    main()
