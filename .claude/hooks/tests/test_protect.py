"""Tests for the .env protection in protect.py.

The hook is a plain text search over the whole command (fail-closed): any mention of
a .env file blocks, also inside commit messages or heredocs. Commit and PR texts go
through files instead (git commit -F, gh pr create --body-file).

Run from the repository root:  uv run --no-project --with pytest pytest .claude/hooks/tests
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from protect import ENV_BLOCKED, check


def bash(command: str) -> str | None:
    return check({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": ""})


@pytest.mark.parametrize(
    "command",
    [
        "cat .env",
        "cat .env.local",
        "cat backend/.env",
        "cat '/home/user/project/.env'",
        "ls .env*",
        "grep TOKEN .env",
        "source .env",
        ". .env",
        "cp .env.example .env",
        "echo x > .env",
        "echo $(cat .env)",
        "cat `echo .env`",
        "docker compose --env-file .env up",
        "docker compose --env-file=.env up",
        "git show HEAD:.env",
        "cat '.env",
        # Paths inside code for any interpreter.
        "python3 -c \"print(open('.env').read())\"",
        "bash -c 'cat .env'",
        "awk '{print}' .env",
        'lua -e \'print(io.open(".env"):read("a"))\'',
        "git -c alias.x='!cat .env' x",
        # Brace and parameter expansion.
        "cat {.env,}",
        "cp backend/{.env,x} /tmp/",
        "cat ${HOME:+.env}",
        # Heredocs: content is not trusted, quoted delimiter or not.
        "cat > .env <<'EOF'\nA=1\nEOF",
        "python3 - <<'EOF'\nprint(open('.env').read())\nEOF",
        "cat <<EOF\n$(cat .env)\nEOF",
        "cat > docker-compose.yml <<'EOF'\nenv_file: .env\nEOF",
        # Inline commit and PR texts are not exempt: use -F / --body-file instead.
        "git commit -m 'Keep .env out of the Docker image'",
        'git commit -m "$(cat .env)"',
        "git commit -m x -- .env",
        "gh pr create --title 'Protect .env' --body 'Never commit .env files'",
        "gh pr create --title x --body-file .env",
    ],
)
def test_blocks_env_file_access(command: str) -> None:
    assert bash(command) == ENV_BLOCKED


@pytest.mark.parametrize(
    "command",
    [
        "grep env_prefix config.py",
        "cat .env.example",
        "ls -la",
        "uv run pytest",
        # The documented way for commit and PR texts.
        "git commit -F .git/COMMIT_MSG_DRAFT",
        'gh pr create --title "chore: editor config" --body-file .git/PR_BODY_DRAFT',
    ],
)
def test_allows_commands_without_env_file(command: str) -> None:
    assert bash(command) is None


@pytest.mark.parametrize("path", ["/repo/.env", "/repo/backend/.env.local"])
def test_file_tools_still_block_env_paths(path: str) -> None:
    event = {"tool_name": "Read", "tool_input": {"file_path": path}}
    assert check(event) == ENV_BLOCKED


def test_file_tools_allow_env_example() -> None:
    assert check({"tool_name": "Read", "tool_input": {"file_path": "/repo/.env.example"}}) is None


def test_write_tool_allows_draft_files() -> None:
    for name in ("COMMIT_MSG_DRAFT", "PR_BODY_DRAFT"):
        event = {"tool_name": "Write", "tool_input": {"file_path": f"/repo/.git/{name}"}}
        assert check(event) is None
