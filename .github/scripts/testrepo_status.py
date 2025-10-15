#!/usr/bin/env python3

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

API_ROOT = "https://api.github.com"
TEST_REPO = "JacobDomagala/TestRepo"
WORKFLOW_FILE = "test.yml"
COMMENT_MARKER = "<!-- testrepo-integration-status -->"
COMMENT_TITLES = (
    "SA CMake output",
    "SA non-CMake output",
    "Static analysis result",
)
POLL_SECONDS = 15


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect = subparsers.add_parser("collect")
    collect.add_argument("--token", required=True)
    collect.add_argument("--phase", choices=("started", "completed"), required=True)
    collect.add_argument("--triggered-at", required=True)
    collect.add_argument("--main-sha", required=True)
    collect.add_argument("--test-static-sha", required=True)
    collect.add_argument("--fork-sha", required=True)
    collect.add_argument("--timeout-seconds", type=int, default=300)
    collect.add_argument("--output", required=True)

    comment = subparsers.add_parser("upsert-comment")
    comment.add_argument("--token", required=True)
    comment.add_argument("--repo", required=True)
    comment.add_argument("--pr-number", required=True)
    comment.add_argument("--run-url", required=True)
    comment.add_argument("--run-label", required=True)
    comment.add_argument("--status-file", required=True)

    assert_success = subparsers.add_parser("assert-success")
    assert_success.add_argument("--status-file", required=True)

    return parser.parse_args()


def parse_github_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def format_now() -> str:
    return now_utc().strftime("%Y-%m-%d %H:%M:%S UTC")


def github_request(token: str, method: str, path: str, payload: Any = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "StaticAnalysis-TestRepo-Status",
    }
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(f"{API_ROOT}{path}", data=body, headers=headers, method=method)

    try:
        with urlopen(request) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API request failed ({method} {path}): {error.code} {details}"
        ) from error


def list_workflow_runs(token: str, event_name: str) -> list[dict[str, Any]]:
    page = 1
    runs: list[dict[str, Any]] = []
    while True:
        query = urlencode({"event": event_name, "per_page": 100, "page": page})
        payload = github_request(
            token,
            "GET",
            f"/repos/{TEST_REPO}/actions/workflows/{quote(WORKFLOW_FILE, safe='')}/runs?{query}",
        )
        workflow_runs = payload.get("workflow_runs", [])
        runs.extend(workflow_runs)
        if len(workflow_runs) < 100:
            break
        page += 1
    return runs


def list_issue_comments(token: str, repo: str, pr_number: int) -> list[dict[str, Any]]:
    page = 1
    comments: list[dict[str, Any]] = []
    while True:
        query = urlencode({"per_page": 100, "page": page})
        page_comments = github_request(
            token, "GET", f"/repos/{repo}/issues/{pr_number}/comments?{query}"
        )
        comments.extend(page_comments)
        if len(page_comments) < 100:
            break
        page += 1
    return comments


def find_pr_for_head(token: str, head_owner: str, head_branch: str) -> dict[str, Any] | None:
    query = urlencode(
        {
            "state": "open",
            "head": f"{head_owner}:{head_branch}",
            "per_page": 1,
        }
    )
    payload = github_request(token, "GET", f"/repos/{TEST_REPO}/pulls?{query}")
    return payload[0] if payload else None


def build_scenarios(args: argparse.Namespace) -> list[dict[str, Any]]:
    return [
        {
            "key": "push-main",
            "label": "Push",
            "event": "push",
            "head_repo": TEST_REPO,
            "head_owner": "JacobDomagala",
            "head_branch": "main",
            "head_sha": args.main_sha,
            "comment_titles": [],
            "query_url": (
                "https://github.com/JacobDomagala/TestRepo/actions/workflows/test.yml"
                "?query=event%3Apush+branch%3Amain"
            ),
        },
        {
            "key": "test-static-analysis",
            "label": "Pull Request",
            "event": "pull_request_target",
            "head_repo": TEST_REPO,
            "head_owner": "JacobDomagala",
            "head_branch": "test-static-analysis",
            "head_sha": args.test_static_sha,
            "comment_titles": list(COMMENT_TITLES),
            "query_url": (
                "https://github.com/JacobDomagala/TestRepo/actions/workflows/test.yml"
                "?query=event%3Apull_request_target"
            ),
        },
        {
            "key": "test-branch-fork",
            "label": "Fork Pull Request",
            "event": "pull_request_target",
            "head_repo": "JacobDTest/TestRepo",
            "head_owner": "JacobDTest",
            "head_branch": "test-branch-fork",
            "head_sha": args.fork_sha,
            "comment_titles": list(COMMENT_TITLES),
            "query_url": (
                "https://github.com/JacobDomagala/TestRepo/actions/workflows/test.yml"
                "?query=event%3Apull_request_target"
            ),
        },
    ]


def candidate_head_branches(run: dict[str, Any]) -> set[str]:
    branches = {run.get("head_branch")}
    for pull_request in run.get("pull_requests") or []:
        head = pull_request.get("head") or {}
        branches.add(head.get("ref"))
    return {branch for branch in branches if branch}


def candidate_head_repos(run: dict[str, Any]) -> set[str]:
    repos = {((run.get("head_repository") or {}).get("full_name"))}
    for pull_request in run.get("pull_requests") or []:
        head = pull_request.get("head") or {}
        repo = head.get("repo") or {}
        repos.add(repo.get("full_name"))
    return {repo for repo in repos if repo}


def candidate_head_shas(run: dict[str, Any]) -> set[str]:
    shas = {run.get("head_sha"), ((run.get("head_commit") or {}).get("id"))}
    for pull_request in run.get("pull_requests") or []:
        head = pull_request.get("head") or {}
        shas.add(head.get("sha"))
    return {sha for sha in shas if sha}


def matching_run(run: dict[str, Any], scenario: dict[str, Any], triggered_at: datetime) -> bool:
    if run.get("event") != scenario["event"]:
        return False

    branches = candidate_head_branches(run)
    if branches and scenario["head_branch"] not in branches:
        return False

    shas = candidate_head_shas(run)
    if scenario["event"] == "push" and shas and scenario["head_sha"] not in shas:
        return False

    repos = candidate_head_repos(run)
    if scenario["head_repo"] and repos and scenario["head_repo"] not in repos:
        return False

    created_at = parse_github_datetime(run["created_at"])
    return created_at >= triggered_at


def find_matching_run(
    runs: list[dict[str, Any]], scenario: dict[str, Any], triggered_at: datetime
) -> dict[str, Any] | None:
    candidates = [
        run for run in runs if matching_run(run, scenario, triggered_at)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda run: run["created_at"])


def extract_run_metadata(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": run["id"],
        "html_url": run["html_url"],
        "status": run["status"],
        "conclusion": run.get("conclusion"),
        "created_at": run["created_at"],
        "updated_at": run["updated_at"],
    }


def find_comment_links(
    token: str, pr_number: int, run_metadata: dict[str, Any], titles: list[str]
) -> list[dict[str, Any]]:
    comments = list_issue_comments(token, TEST_REPO, pr_number)
    run_started_at = parse_github_datetime(run_metadata["created_at"])

    latest_by_title: dict[str, dict[str, Any]] = {}
    for comment in comments:
        body = comment.get("body") or ""
        updated_at = parse_github_datetime(comment["updated_at"])
        if updated_at < run_started_at:
            continue

        for title in titles:
            if title not in body:
                continue

            previous = latest_by_title.get(title)
            if previous is None or updated_at > parse_github_datetime(
                previous["updated_at"]
            ):
                latest_by_title[title] = {
                    "title": title,
                    "url": comment["html_url"],
                    "updated_at": comment["updated_at"],
                }

    return [
        {"title": title, "url": latest_by_title[title]["url"]}
        for title in titles
        if title in latest_by_title
    ]


def collect_status(args: argparse.Namespace) -> int:
    triggered_at = parse_github_datetime(args.triggered_at)
    scenarios = build_scenarios(args)
    deadline = time.monotonic() + args.timeout_seconds

    while True:
        runs_by_event = {
            "push": list_workflow_runs(args.token, "push"),
            "pull_request_target": list_workflow_runs(args.token, "pull_request_target"),
        }

        all_ready = True
        for scenario in scenarios:
            run = find_matching_run(
                runs_by_event[scenario["event"]], scenario, triggered_at
            )
            scenario["run"] = extract_run_metadata(run) if run else None

            if scenario["event"] == "pull_request_target":
                pr = find_pr_for_head(
                    args.token, scenario["head_owner"], scenario["head_branch"]
                )
                scenario["pr"] = (
                    {"number": pr["number"], "html_url": pr["html_url"]} if pr else None
                )
            else:
                scenario["pr"] = None

            if args.phase == "started":
                if scenario["run"] is None:
                    all_ready = False
            else:
                run_metadata = scenario["run"]
                if run_metadata is None or run_metadata["status"] != "completed":
                    all_ready = False

                if scenario["pr"] and run_metadata and run_metadata["status"] == "completed":
                    scenario["comment_links"] = find_comment_links(
                        args.token,
                        scenario["pr"]["number"],
                        run_metadata,
                        scenario["comment_titles"],
                    )
                else:
                    scenario["comment_links"] = []

        if all_ready or time.monotonic() >= deadline:
            break
        time.sleep(POLL_SECONDS)

    if args.phase == "completed":
        for scenario in scenarios:
            if "comment_links" not in scenario:
                scenario["comment_links"] = []

    result = {
        "phase": args.phase,
        "timed_out": not all_ready,
        "generated_at": format_now(),
        "scenarios": scenarios,
    }

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)
        file.write("\n")

    return 0


def human_status(scenario: dict[str, Any]) -> str:
    run = scenario.get("run")
    if run is None:
        return "waiting for workflow run"

    if run["status"] != "completed":
        return "in progress"

    conclusion = run.get("conclusion") or "completed"
    if conclusion == "success":
        return "success"
    return conclusion.replace("_", " ")


def scenario_verification_error(scenario: dict[str, Any]) -> str | None:
    run = scenario.get("run")
    if run is None:
        return "workflow run was not detected"

    if run["status"] != "completed":
        return "workflow run did not complete"

    if scenario["event"] != "pull_request_target":
        return None

    if scenario.get("pr") is None:
        return "pull request was not found"

    if not scenario.get("comment_links"):
        return "result comments were not found"

    return None


def display_status(scenario: dict[str, Any]) -> str:
    error = scenario_verification_error(scenario)
    if error is not None:
        if scenario.get("run") is None:
            return "Waiting"
        if scenario.get("run", {}).get("status") != "completed":
            return "In progress"
        return "Needs attention"

    run = scenario.get("run")
    if run is None:
        return "Waiting"

    if scenario["event"] == "pull_request_target":
        return "Comments captured"

    if run.get("conclusion") == "success":
        return "Completed"

    return "Completed with findings"


def verification_failures(status_data: dict[str, Any]) -> list[str]:
    failures = []
    for scenario in status_data["scenarios"]:
        error = scenario_verification_error(scenario)
        if error is not None:
            failures.append(f"{scenario['label']}: {error}")
    return failures


def overall_status(status_data: dict[str, Any]) -> str:
    scenarios = status_data["scenarios"]
    if any(scenario.get("run") is None for scenario in scenarios):
        return "Waiting for downstream workflow runs to appear"
    if any(
        scenario["run"]["status"] != "completed"
        for scenario in scenarios
        if scenario.get("run") is not None
    ):
        return "Waiting for downstream workflows to finish"

    failures = verification_failures(status_data)
    if failures:
        return "Completed with missing verification artifacts"

    if any(
        scenario["run"].get("conclusion") != "success"
        for scenario in scenarios
        if scenario.get("run") is not None
    ):
        return "Completed, findings were reported as expected"

    return "Completed successfully"


def render_link_cell(label: str, url: str) -> str:
    return f"[{label}]({url})"


def render_comment_links(comment_links: list[dict[str, Any]]) -> str:
    if not comment_links:
        return "n/a"
    return "<br>".join(
        render_link_cell(link["title"], link["url"]) for link in comment_links
    )


def render_run_link(scenario: dict[str, Any]) -> str:
    run = scenario.get("run")
    if run is not None:
        return render_link_cell("Workflow run", run["html_url"])

    if scenario.get("query_url"):
        return render_link_cell("Workflow query", scenario["query_url"])

    return "n/a"


def render_pr_link(scenario: dict[str, Any]) -> str:
    pr = scenario.get("pr")
    if pr is not None:
        return render_link_cell("PR", pr["html_url"])

    if scenario["event"] == "pull_request_target":
        return "not found"

    return "n/a"


def render_comment_cell(scenario: dict[str, Any]) -> str:
    comment_links = scenario.get("comment_links", [])
    if comment_links:
        return render_comment_links(comment_links)

    pr = scenario.get("pr")
    run = scenario.get("run")
    if pr is not None and run is not None and run["status"] == "completed":
        return "not found"

    return "n/a"


def render_comment_body(
    status_data: dict[str, Any], run_url: str, run_label: str
) -> str:
    lines = [
        "## TestRepo Integration Status",
        "",
        COMMENT_MARKER,
        "",
        "| Summary | Value |",
        "| --- | --- |",
        f"| Overall status | `{overall_status(status_data)}` |",
        f"| Source workflow | [{run_label}]({run_url}) |",
        f"| Last updated | `{format_now()}` |",
        "",
    ]

    if status_data.get("timed_out"):
        lines.extend(
            [
                "> Timed out while waiting for at least one downstream workflow state change.",
                "",
            ]
        )

    lines.extend(
        [
            "### Scenarios",
            "",
            "| Scenario | Status | Workflow | PR | Result comments |",
            "| --- | --- | --- | --- | --- |",
        ]
    )

    for scenario in status_data["scenarios"]:
        lines.append(
            "| "
            f"{scenario['label']} | "
            f"`{display_status(scenario)}` | "
            f"{render_run_link(scenario)} | "
            f"{render_pr_link(scenario)} | "
            f"{render_comment_cell(scenario)} |"
        )

    return "\n".join(lines)


def upsert_comment(args: argparse.Namespace) -> int:
    with open(args.status_file, "r", encoding="utf-8") as file:
        status_data = json.load(file)

    body = render_comment_body(status_data, args.run_url, args.run_label)
    comments = list_issue_comments(args.token, args.repo, int(args.pr_number))

    existing = next(
        (comment for comment in comments if COMMENT_MARKER in (comment.get("body") or "")),
        None,
    )

    if existing is None:
        github_request(
            args.token,
            "POST",
            f"/repos/{args.repo}/issues/{args.pr_number}/comments",
            {"body": body},
        )
    else:
        github_request(
            args.token,
            "PATCH",
            f"/repos/{args.repo}/issues/comments/{existing['id']}",
            {"body": body},
        )

    return 0


def assert_success(args: argparse.Namespace) -> int:
    with open(args.status_file, "r", encoding="utf-8") as file:
        status_data = json.load(file)

    failures = verification_failures(status_data)

    if failures:
        for failure in failures:
            print(failure)
        return 1
    return 0


def main() -> int:
    args = parse_args()

    if args.command == "collect":
        return collect_status(args)
    if args.command == "upsert-comment":
        return upsert_comment(args)
    if args.command == "assert-success":
        return assert_success(args)

    raise RuntimeError(f"Unsupported command {args.command}")


if __name__ == "__main__":
    sys.exit(main())
