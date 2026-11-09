#!/usr/bin/env python3
"""PreToolUse hook: keep Claude away from .env files and from committing/pushing to main.

Claude Code passes the tool call as JSON on stdin. Exit code 2 blocks the call and
shows stderr to Claude; exit code 0 lets it through. On unexpected errors the hook
blocks (fail-closed), because it is a safety check.
"""

import json
import re
import subprocess
import sys

# ".env", ".env.local", ".env_backup", ... as a path component (not ".envrc", not "os.environ").
ENV_FILE = re.compile(r"(?<![\w.-])\.env(?![a-zA-Z])[\w.-]*")
# "git commit ..." / "git push ...", also with global options like "git -C dir push".
GIT_COMMAND = re.compile(r"\bgit((?:\s+-\S+(?:\s+[^-\s]\S*)?)*)\s+(commit|push)\b(.*)")
# A push refspec that targets main: "main", "HEAD:main", "+main", "x:refs/heads/main".
MAIN_REFSPEC = re.compile(r"^(?:.*[:+])?(?:refs/heads/)?main$")
SWITCH_TO_MAIN = re.compile(r"\bgit\s+(?:checkout|switch)\s+main\s*$")
SKIP_HOOKS = re.compile(r"--no-verify|core\.hooksPath")
SHORT_N = re.compile(r"^-[a-zA-Z]*n")
GITLEAKS = re.compile(r"\bgitleaks\s+(?!version\b|help\b|-h\b|--help\b)")
GITLEAKS_DIR_SCAN = re.compile(r"\bgitleaks\s+(?:dir|directory|files)\b|--no-git")

ENV_BLOCKED = "Access to .env is blocked. Secrets stay out of Claude's context."
MAIN_BLOCKED = "Committing or pushing to main is blocked. Use a feature branch and a PR."


def mentions_env_file(text: str) -> bool:
    return any(not m.group().endswith(".example") for m in ENV_FILE.finditer(text))


def current_branch(cwd: str) -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=cwd or None,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def check_gitleaks(command: str) -> str | None:
    # Scanning the working folder would read the real .env and could print its secrets.
    if not GITLEAKS.search(command):
        return None
    if GITLEAKS_DIR_SCAN.search(command):
        return "gitleaks must not scan the working folder (it contains .env). Use 'gitleaks git'."
    if "--redact" not in command:
        return "Always run gitleaks with --redact, so no secret ends up in the output."
    return None


def check_git(command: str, cwd: str) -> str | None:
    on_main = current_branch(cwd) == "main"
    # Treat quotes, backticks and parentheses as separators, so "git push origin 'main'",
    # "$(git push ...)" and 'bash -c "git push ..."' are checked like plain commands.
    command = re.sub(r"[\"'`()]", " ", command)
    # Check each part of a chained command ("git rebase main && git push") on its own.
    for part in re.split(r"&&|\|\||[;|\n]", command):
        if SWITCH_TO_MAIN.search(part):
            on_main = True  # e.g. "git checkout main && git commit ..."
        match = GIT_COMMAND.search(part)
        if not match:
            continue
        global_options, action, rest = match.groups()
        args = rest.split()
        # "-n" means --no-verify for commit, also inside bundles like "-nm".
        no_verify = action == "commit" and any(SHORT_N.match(a) for a in args)
        if SKIP_HOOKS.search(global_options + rest) or no_verify:
            return "Skipping git hooks is blocked. Fix the reported problem instead."
        if action == "commit" and on_main:
            return MAIN_BLOCKED
        if action == "push":
            if "--all" in args or "--mirror" in args:  # would push main too
                return MAIN_BLOCKED
            positional = [a for a in args if not a.startswith("-")]
            # positional[0] is the remote; everything after it are refspecs.
            if any(MAIN_REFSPEC.match(ref) for ref in positional[1:]):
                return MAIN_BLOCKED
            if len(positional) <= 1 and on_main:
                return MAIN_BLOCKED
    return None


def check(event: dict) -> str | None:
    """Return a reason to block the tool call, or None to allow it."""
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}

    if tool == "Bash":
        command = tool_input.get("command") or ""
        if mentions_env_file(command):
            return ENV_BLOCKED
        return check_gitleaks(command) or check_git(command, event.get("cwd") or "")

    # File tools (Read, Edit, Write, ...) and search tools. Grep's "pattern" searches
    # file contents, so only path-like fields are checked.
    keys = ["file_path", "notebook_path", "path", "glob"]
    if tool == "Glob":
        keys.append("pattern")
    for key in keys:
        value = tool_input.get(key)
        if isinstance(value, str) and mentions_env_file(value):
            return ENV_BLOCKED
    return None


def main() -> int:
    try:
        reason = check(json.load(sys.stdin))
    except Exception as error:  # fail-closed: block if the input cannot be checked
        reason = f"protect hook could not check this tool call ({error!r})."
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
