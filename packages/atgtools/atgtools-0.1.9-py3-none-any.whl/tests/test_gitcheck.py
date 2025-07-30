from typing import List, Union
import pytest
from pathlib import Path

from atg.tools.git import gitcheck


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repository for testing.
    
    Args:
        tmp_path: pytest fixture for creating temporary directories
        
    Returns:
        Path: Path to the temporary git repository
    """
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    git_dir = repo_path / ".git"
    git_dir.mkdir()
    return repo_path


def test_gitcheck_no_changes(git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test gitcheck when there are no changes.
    
    Args:
        git_repo: Path to temporary git repository
        monkeypatch: pytest fixture for patching
    """
    def mock_search_repositories(*args: tuple, **kwargs: dict) -> List[str]:
        return [str(git_repo)]

    def mock_git_exec(*args: tuple, **kwargs: dict) -> str:
        if "branch" in args[1]:
            return "* main"
        elif "status" in args[1]:
            return ""
        elif "remote" in args[1]:
            return "origin"
        return ""

    monkeypatch.setattr("atg.tools.git.search_repositories", mock_search_repositories)
    monkeypatch.setattr("atg.tools.git.git_exec", mock_git_exec)

    action_needed = gitcheck(
        verbose=False,
        checkremote=False,
        checkuntracked=True,
        search_dir=str(git_repo.parent),
        quiet=False,
        checkall="",
        show_stash=False,
    )
    assert not action_needed


def test_gitcheck_with_changes(git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test gitcheck when there are local changes.
    
    Args:
        git_repo: Path to temporary git repository
        monkeypatch: pytest fixture for patching
    """
    def mock_search_repositories(*args: tuple, **kwargs: dict) -> List[str]:
        return [str(git_repo)]

    def mock_git_exec(*args: tuple, **kwargs: dict) -> str:
        if "branch" in args[1]:
            return "* main"
        elif "status" in args[1]:
            return " M modified.txt\n?? new.txt"
        elif "remote" in args[1]:
            return "origin"
        return ""

    monkeypatch.setattr("atg.tools.git.search_repositories", mock_search_repositories)
    monkeypatch.setattr("atg.tools.git.git_exec", mock_git_exec)

    action_needed = gitcheck(
        verbose=False,
        checkremote=False,
        checkuntracked=True,
        search_dir=str(git_repo.parent),
        quiet=False,
        checkall="",
        show_stash=False,
    )
    assert action_needed


def test_gitcheck_with_remote_updates(git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test gitcheck when remote updates are available.
    
    Args:
        git_repo: Path to temporary git repository
        monkeypatch: pytest fixture for patching
    """
    def mock_search_repositories(*args: tuple, **kwargs: dict) -> List[str]:
        return [str(git_repo)]

    def mock_git_exec(*args: tuple, **kwargs: dict) -> str:
        if "branch" in args[1]:
            if "-r" in args[1]:
                return "origin/main"
            return "* main"
        elif "status" in args[1]:
            return ""
        elif "remote" in args[1]:
            return "origin"
        elif "log" in args[1]:
            if "..origin/main" in args[1]:
                return "abc123 remote commit"
            elif "origin/main.." in args[1]:
                return ""
        elif "remote update" in args[1]:
            return ""
        return ""

    monkeypatch.setattr("atg.tools.git.search_repositories", mock_search_repositories)
    monkeypatch.setattr("atg.tools.git.git_exec", mock_git_exec)

    action_needed = gitcheck(
        verbose=False,
        checkremote=True,
        checkuntracked=True,
        search_dir=str(git_repo.parent),
        quiet=False,
        checkall="",
        show_stash=False,
    )
    assert action_needed
