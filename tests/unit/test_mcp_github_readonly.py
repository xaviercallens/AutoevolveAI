"""
Unit tests for Read-Only GitHub MCP Server (anse/guard/mcp_github_readonly.py).
Validates token resolution, mocked API responses, base64 decoding, error handling,
and strictly enforces that zero mutation/write tools exist.
"""

from __future__ import annotations

import base64
from unittest.mock import MagicMock, patch

import pytest

from anse.guard.mcp_github_readonly import (
    _get_headers,
    _resolve_token,
    get_commit,
    get_file_contents,
    get_issue,
    get_pull_request,
    get_pull_request_files,
    get_repository,
    list_commits,
    list_directory_contents,
    list_issues,
    list_my_repositories,
    list_pull_requests,
    mcp,
    search_code,
    search_repositories,
)


def test_strict_readonly_invariants():
    """Verify that only read-only tools are exposed and zero mutation tools exist."""
    import asyncio

    tools = asyncio.run(mcp.list_tools())
    tool_names = [t.name for t in tools]

    # Prohibited write keywords
    prohibited_prefixes = ("create_", "update_", "delete_", "push_", "merge_", "post_", "put_")
    for name in tool_names:
        for prefix in prohibited_prefixes:
            assert not name.startswith(prefix), f"Prohibited write tool found: {name}"

    # Required read tools
    expected_tools = {
        "list_my_repositories",
        "get_repository",
        "search_repositories",
        "get_file_contents",
        "list_directory_contents",
        "search_code",
        "list_commits",
        "get_commit",
        "list_issues",
        "get_issue",
        "list_pull_requests",
        "get_pull_request",
        "get_pull_request_files",
    }
    assert expected_tools.issubset(set(tool_names))


def test_token_resolution_and_headers(monkeypatch):
    """Test token retrieval from environment and header formatting."""
    monkeypatch.setenv("GITHUB_READONLY_TOKEN", "ghp_mock_readonly_token_12345")
    token = _resolve_token()
    assert token == "ghp_mock_readonly_token_12345"

    headers = _get_headers()
    assert headers["Authorization"] == "Bearer ghp_mock_readonly_token_12345"
    assert headers["Accept"] == "application/vnd.github+json"
    assert headers["X-GitHub-Api-Version"] == "2022-11-28"


@patch("httpx.Client.get")
def test_list_my_repositories_mock(mock_get):
    """Test listing user repositories with public and private filtering."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {
            "name": "AutoevolveAI",
            "full_name": "xaviercallens/AutoevolveAI",
            "private": False,
            "description": "ANSE Autopoietic Neuro-Symbolic Engine",
            "default_branch": "main",
            "stargazers_count": 42,
            "forks_count": 5,
            "language": "Python",
            "updated_at": "2026-09-30T10:00:00Z",
            "html_url": "https://github.com/xaviercallens/AutoevolveAI",
        },
        {
            "name": "secret-research-vault",
            "full_name": "xaviercallens/secret-research-vault",
            "private": True,
            "description": "Private experimental preprints",
            "default_branch": "main",
            "stargazers_count": 0,
            "forks_count": 0,
            "language": "Lean 4",
            "updated_at": "2026-09-29T12:00:00Z",
            "html_url": "https://github.com/xaviercallens/secret-research-vault",
        },
    ]
    mock_get.return_value = mock_resp

    repos = list_my_repositories(visibility="all", limit=10)
    assert len(repos) == 2
    assert repos[0]["name"] == "AutoevolveAI"
    assert repos[0]["private"] is False
    assert repos[1]["name"] == "secret-research-vault"
    assert repos[1]["private"] is True


@patch("httpx.Client.get")
def test_get_file_contents_base64_decode(mock_get):
    """Test fetching and decoding a text file from a repository."""
    raw_code = "print('Hello from private repository')"
    encoded = base64.b64encode(raw_code.encode("utf-8")).decode("utf-8")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "name": "main.py",
        "path": "src/main.py",
        "sha": "abc123456",
        "size": len(raw_code),
        "encoding": "base64",
        "content": encoded,
        "download_url": "https://raw.githubusercontent.com/owner/repo/main/src/main.py",
    }
    mock_get.return_value = mock_resp

    res = get_file_contents("xaviercallens", "AutoevolveAI", "src/main.py")
    assert res["name"] == "main.py"
    assert res["content"] == raw_code


@patch("httpx.Client.get")
def test_get_file_contents_directory_rejection(mock_get):
    """Assert ValueError when a directory is requested as a file."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [{"name": "file1.py"}, {"name": "file2.py"}]
    mock_get.return_value = mock_resp

    with pytest.raises(ValueError, match="is a directory"):
        get_file_contents("xaviercallens", "AutoevolveAI", "src")


@patch("httpx.Client.get")
def test_list_commits_and_get_commit(mock_get):
    """Test listing commits and retrieving detailed commit diffs."""
    mock_resp_list = MagicMock()
    mock_resp_list.status_code = 200
    mock_resp_list.json.return_value = [
        {
            "sha": "commit_sha_123",
            "commit": {
                "message": "feat: add read-only github mcp server\n\nDetailed body",
                "author": {"name": "Xavier Callens", "date": "2026-09-30T10:00:00Z"},
            },
            "html_url": "https://github.com/xaviercallens/AutoevolveAI/commit/commit_sha_123",
        }
    ]

    mock_get.return_value = mock_resp_list
    commits = list_commits("xaviercallens", "AutoevolveAI", limit=5)
    assert len(commits) == 1
    assert commits[0]["sha"] == "commit_sha_123"
    assert commits[0]["message"] == "feat: add read-only github mcp server"

    # Test detailed commit
    mock_resp_single = MagicMock()
    mock_resp_single.status_code = 200
    mock_resp_single.json.return_value = {
        "sha": "commit_sha_123",
        "commit": {
            "message": "feat: full message",
            "author": {"name": "Xavier Callens", "date": "2026-09-30T10:00:00Z"},
        },
        "stats": {"total": 10, "additions": 10, "deletions": 0},
        "files": [
            {
                "filename": "mcp_github_readonly.py",
                "status": "added",
                "additions": 10,
                "deletions": 0,
                "patch": "@@ -0,0 +1,10 @@",
            }
        ],
    }
    mock_get.return_value = mock_resp_single
    detail = get_commit("xaviercallens", "AutoevolveAI", "commit_sha_123")
    assert detail["sha"] == "commit_sha_123"
    assert len(detail["files"]) == 1


@patch("httpx.Client.get")
def test_list_issues_filters_pull_requests(mock_get):
    """Test that list_issues filters out pull requests."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {"number": 1, "title": "Regular Issue", "user": {"login": "dev1"}, "comments": 2},
        {
            "number": 2,
            "title": "A Pull Request mistakenly returned by issues API",
            "user": {"login": "dev2"},
            "pull_request": {"url": "https://..."},
        },
    ]
    mock_get.return_value = mock_resp

    issues = list_issues("xaviercallens", "AutoevolveAI")
    assert len(issues) == 1
    assert issues[0]["number"] == 1
    assert issues[0]["title"] == "Regular Issue"


@patch("httpx.Client.get")
def test_authentication_error_handling(mock_get):
    """Assert clear RuntimeError when GitHub returns HTTP 401."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Bad credentials"
    mock_get.return_value = mock_resp

    with pytest.raises(RuntimeError, match="GitHub Authentication Failed"):
        get_repository("xaviercallens", "AutoevolveAI")
