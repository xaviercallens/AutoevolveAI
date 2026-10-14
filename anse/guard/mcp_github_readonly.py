#!/usr/bin/env python3
"""
Read-Only GitHub Model Context Protocol (MCP) Server for Antigravity & ANSE.
Provides strictly read-only access to public and private GitHub repositories, files,
commits, issues, pull requests, and search queries with zero write/mutation tools.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any

import httpx
from fastmcp import FastMCP

GITHUB_API_BASE = "https://api.github.com"
mcp = FastMCP("github-readonly")


def _extract_token_from_file(p: Path) -> str:
    """Extract first matching GitHub token from a .env file."""
    if not p.is_file():
        return ""
    try:
        target_keys = {
            "GITHUB_READONLY_TOKEN",
            "GITHUB_PERSONAL_ACCESS_TOKEN",
            "GITHUB_TOKEN",
            "GH_TOKEN",
        }
        for raw_line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() in target_keys:
                val = v.strip().strip("'\"")
                if val:
                    return val
    except Exception:
        pass
    return ""


def _resolve_token() -> str:
    """
    Resolve GitHub token from environment variables or .env files.
    Prefers read-only specific variables before generic tokens.
    """
    token = (
        os.getenv("GITHUB_READONLY_TOKEN")
        or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        or os.getenv("GITHUB_TOKEN")
        or os.getenv("GH_TOKEN")
    )
    if token:
        return token.strip()

    env_paths = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
        Path.home() / ".env",
    ]
    for p in env_paths:
        val = _extract_token_from_file(p)
        if val:
            return val
    return ""


def _get_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ANSE-SocrateAI-GitHub-ReadOnly-MCP/1.0",
    }
    token = _resolve_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _github_get(endpoint: str, params: dict[str, Any] | None = None) -> Any:
    """Execute authenticated GET request against GitHub REST API."""
    url = f"{GITHUB_API_BASE}/{endpoint.lstrip('/')}"
    headers = _get_headers()

    with httpx.Client(timeout=20.0) as client:
        resp = client.get(url, headers=headers, params=params)
        if resp.status_code == 401:
            raise RuntimeError(
                "GitHub Authentication Failed: Token is missing or invalid. "
                "Ensure GITHUB_READONLY_TOKEN or GITHUB_PERSONAL_ACCESS_TOKEN is configured in .env"
            )
        if resp.status_code == 404:
            raise FileNotFoundError(f"Resource not found on GitHub: {endpoint}")
        if resp.status_code == 403 and "rate limit exceeded" in resp.text.lower():
            raise RuntimeError("GitHub API rate limit exceeded.")
        resp.raise_for_status()
        return resp.json()


# --- Read-Only Repository Tools ---


@mcp.tool()
def list_my_repositories(
    visibility: str = "all", sort: str = "updated", limit: int = 30
) -> list[dict[str, Any]]:
    """
    List public and private repositories accessible to the authenticated user.
    Args:
        visibility: Can be 'all', 'public', or 'private'.
        sort: Sort field: 'created', 'updated', 'pushed', 'full_name'.
        limit: Max repositories to return (default: 30, max: 100).
    """
    data = _github_get(
        "/user/repos",
        params={
            "visibility": visibility,
            "sort": sort,
            "per_page": min(limit, 100),
            "affiliation": "owner,collaborator,organization_member",
        },
    )
    results: list[dict[str, Any]] = []
    for item in data:
        results.append(
            {
                "name": item.get("name"),
                "full_name": item.get("full_name"),
                "private": item.get("private"),
                "description": item.get("description"),
                "default_branch": item.get("default_branch"),
                "stars": item.get("stargazers_count"),
                "forks": item.get("forks_count"),
                "language": item.get("language"),
                "updated_at": item.get("updated_at"),
                "html_url": item.get("html_url"),
            }
        )
    return results


@mcp.tool()
def get_repository(owner: str, repo: str) -> dict[str, Any]:
    """
    Get detailed metadata for a specific repository (public or private).
    Args:
        owner: GitHub user or organization name.
        repo: Repository name.
    """
    item = _github_get(f"/repos/{owner}/{repo}")
    return {
        "name": item.get("name"),
        "full_name": item.get("full_name"),
        "private": item.get("private"),
        "description": item.get("description"),
        "default_branch": item.get("default_branch"),
        "language": item.get("language"),
        "open_issues_count": item.get("open_issues_count"),
        "license": (item.get("license") or {}).get("spdx_id"),
        "topics": item.get("topics", []),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "html_url": item.get("html_url"),
    }


@mcp.tool()
def search_repositories(query: str, limit: int = 30) -> list[dict[str, Any]]:
    """
    Search GitHub repositories using search syntax (e.g. 'org:xaviercallens topic:physics').
    Args:
        query: GitHub search query string.
        limit: Max results (default: 30, max: 100).
    """
    data = _github_get("/search/repositories", params={"q": query, "per_page": min(limit, 100)})
    items = data.get("items", [])
    results: list[dict[str, Any]] = []
    for item in items:
        results.append(
            {
                "full_name": item.get("full_name"),
                "private": item.get("private"),
                "description": item.get("description"),
                "stars": item.get("stargazers_count"),
                "html_url": item.get("html_url"),
            }
        )
    return results


# --- Read-Only File & Directory Contents Tools ---


@mcp.tool()
def get_file_contents(owner: str, repo: str, path: str, ref: str = "") -> dict[str, Any]:
    """
    Fetch contents of a file from a repository (public or private).
    Args:
        owner: GitHub repository owner.
        repo: Repository name.
        path: Path to file within repository (e.g. 'src/main.rs').
        ref: Optional branch, commit SHA, or tag (defaults to default branch).
    """
    params: dict[str, Any] = {}
    if ref:
        params["ref"] = ref

    data = _github_get(f"/repos/{owner}/{repo}/contents/{path.lstrip('/')}", params=params)
    if isinstance(data, list):
        raise ValueError(f"Path '{path}' is a directory, not a file. Use list_directory_contents.")

    encoding = data.get("encoding", "")
    raw_content = data.get("content", "")

    if encoding == "base64" and raw_content:
        try:
            decoded_text = base64.b64decode(raw_content).decode("utf-8")
        except UnicodeDecodeError:
            decoded_text = f"<Binary data, base64 length: {len(raw_content)}>"
    else:
        decoded_text = raw_content

    return {
        "name": data.get("name"),
        "path": data.get("path"),
        "sha": data.get("sha"),
        "size": data.get("size"),
        "content": decoded_text,
        "download_url": data.get("download_url"),
    }


@mcp.tool()
def list_directory_contents(
    owner: str, repo: str, path: str = "", ref: str = ""
) -> list[dict[str, Any]]:
    """
    List files and directories at a given path in a repository.
    Args:
        owner: GitHub repository owner.
        repo: Repository name.
        path: Directory path (leave empty for root).
        ref: Optional branch, commit SHA, or tag.
    """
    params: dict[str, Any] = {}
    if ref:
        params["ref"] = ref

    data = _github_get(f"/repos/{owner}/{repo}/contents/{path.lstrip('/')}", params=params)
    if not isinstance(data, list):
        data = [data]

    results: list[dict[str, Any]] = []
    for item in data:
        results.append(
            {
                "name": item.get("name"),
                "path": item.get("path"),
                "type": item.get("type"),  # 'file' or 'dir'
                "size": item.get("size"),
                "sha": item.get("sha"),
            }
        )
    return results


# --- Read-Only Code & Commit Tools ---


@mcp.tool()
def search_code(query: str, limit: int = 30) -> list[dict[str, Any]]:
    """
    Search code in GitHub repositories (e.g. 'filename:Cargo.toml repo:xaviercallens/AutoevolveAI').
    Args:
        query: GitHub code search query string.
        limit: Max results (default: 30, max: 100).
    """
    data = _github_get("/search/code", params={"q": query, "per_page": min(limit, 100)})
    items = data.get("items", [])
    results: list[dict[str, Any]] = []
    for item in items:
        results.append(
            {
                "name": item.get("name"),
                "path": item.get("path"),
                "repository": (item.get("repository") or {}).get("full_name"),
                "html_url": item.get("html_url"),
            }
        )
    return results


@mcp.tool()
def list_commits(
    owner: str, repo: str, sha: str = "", limit: int = 30
) -> list[dict[str, Any]]:
    """
    List recent commit history in a repository.
    Args:
        owner: GitHub repository owner.
        repo: Repository name.
        sha: Optional branch or SHA to start listing from.
        limit: Max commits to return (default: 30, max: 100).
    """
    params: dict[str, Any] = {"per_page": min(limit, 100)}
    if sha:
        params["sha"] = sha

    data = _github_get(f"/repos/{owner}/{repo}/commits", params=params)
    results: list[dict[str, Any]] = []
    for item in data:
        commit_info = item.get("commit", {})
        results.append(
            {
                "sha": item.get("sha"),
                "message": commit_info.get("message", "").splitlines()[0]
                if commit_info.get("message")
                else "",
                "author": (commit_info.get("author") or {}).get("name"),
                "date": (commit_info.get("author") or {}).get("date"),
                "html_url": item.get("html_url"),
            }
        )
    return results


@mcp.tool()
def get_commit(owner: str, repo: str, commit_sha: str) -> dict[str, Any]:
    """
    Get detailed commit information including message, author, and changed files.
    Args:
        owner: GitHub repository owner.
        repo: Repository name.
        commit_sha: The commit SHA hash.
    """
    data = _github_get(f"/repos/{owner}/{repo}/commits/{commit_sha}")
    files: list[dict[str, Any]] = []
    for f in data.get("files", []):
        files.append(
            {
                "filename": f.get("filename"),
                "status": f.get("status"),
                "additions": f.get("additions"),
                "deletions": f.get("deletions"),
                "patch": f.get("patch", "")[:1000] if f.get("patch") else "",
            }
        )
    commit_info = data.get("commit", {})
    return {
        "sha": data.get("sha"),
        "message": commit_info.get("message"),
        "author": (commit_info.get("author") or {}).get("name"),
        "date": (commit_info.get("author") or {}).get("date"),
        "stats": data.get("stats"),
        "files": files,
    }


# --- Read-Only Issues & Pull Requests Tools ---


@mcp.tool()
def list_issues(
    owner: str, repo: str, state: str = "open", limit: int = 30
) -> list[dict[str, Any]]:
    """
    List issues in a repository (excluding pull requests).
    Args:
        owner: GitHub repository owner.
        repo: Repository name.
        state: 'open', 'closed', or 'all'.
        limit: Max issues to return (default: 30, max: 100).
    """
    data = _github_get(
        f"/repos/{owner}/{repo}/issues",
        params={"state": state, "per_page": min(limit, 100)},
    )
    results: list[dict[str, Any]] = []
    for item in data:
        # GitHub issue endpoint returns PRs too; filter them out
        if "pull_request" in item:
            continue
        results.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "author": (item.get("user") or {}).get("login"),
                "comments": item.get("comments"),
                "created_at": item.get("created_at"),
                "html_url": item.get("html_url"),
            }
        )
    return results


@mcp.tool()
def get_issue(owner: str, repo: str, issue_number: int) -> dict[str, Any]:
    """
    Get full issue details and body text.
    Args:
        owner: GitHub repository owner.
        repo: Repository name.
        issue_number: Issue index number.
    """
    item = _github_get(f"/repos/{owner}/{repo}/issues/{issue_number}")
    return {
        "number": item.get("number"),
        "title": item.get("title"),
        "body": item.get("body"),
        "state": item.get("state"),
        "author": (item.get("user") or {}).get("login"),
        "comments": item.get("comments"),
        "labels": [lbl.get("name") for lbl in item.get("labels", [])],
        "created_at": item.get("created_at"),
        "html_url": item.get("html_url"),
    }


@mcp.tool()
def list_pull_requests(
    owner: str, repo: str, state: str = "open", limit: int = 30
) -> list[dict[str, Any]]:
    """
    List pull requests in a repository.
    Args:
        owner: GitHub repository owner.
        repo: Repository name.
        state: 'open', 'closed', or 'all'.
        limit: Max PRs to return (default: 30, max: 100).
    """
    data = _github_get(
        f"/repos/{owner}/{repo}/pulls",
        params={"state": state, "per_page": min(limit, 100)},
    )
    results: list[dict[str, Any]] = []
    for item in data:
        results.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "author": (item.get("user") or {}).get("login"),
                "head": (item.get("head") or {}).get("ref"),
                "base": (item.get("base") or {}).get("ref"),
                "created_at": item.get("created_at"),
                "html_url": item.get("html_url"),
            }
        )
    return results


@mcp.tool()
def get_pull_request(owner: str, repo: str, pull_number: int) -> dict[str, Any]:
    """
    Get full details for a pull request.
    Args:
        owner: GitHub repository owner.
        repo: Repository name.
        pull_number: Pull request index number.
    """
    item = _github_get(f"/repos/{owner}/{repo}/pulls/{pull_number}")
    return {
        "number": item.get("number"),
        "title": item.get("title"),
        "body": item.get("body"),
        "state": item.get("state"),
        "author": (item.get("user") or {}).get("login"),
        "head": (item.get("head") or {}).get("ref"),
        "base": (item.get("base") or {}).get("ref"),
        "mergeable": item.get("mergeable"),
        "merged": item.get("merged"),
        "additions": item.get("additions"),
        "deletions": item.get("deletions"),
        "changed_files": item.get("changed_files"),
        "html_url": item.get("html_url"),
    }


@mcp.tool()
def get_pull_request_files(
    owner: str, repo: str, pull_number: int
) -> list[dict[str, Any]]:
    """
    List files changed in a pull request.
    Args:
        owner: GitHub repository owner.
        repo: Repository name.
        pull_number: Pull request index number.
    """
    data = _github_get(f"/repos/{owner}/{repo}/pulls/{pull_number}/files")
    results: list[dict[str, Any]] = []
    for f in data:
        results.append(
            {
                "filename": f.get("filename"),
                "status": f.get("status"),
                "additions": f.get("additions"),
                "deletions": f.get("deletions"),
                "patch": f.get("patch", "")[:1000] if f.get("patch") else "",
            }
        )
    return results


if __name__ == "__main__":
    mcp.run()
