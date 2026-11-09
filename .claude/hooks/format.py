#!/usr/bin/env python3
"""PostToolUse hook: format a file after Claude edited it.

Uses the formatter installed in the project (backend: ruff, frontend: Prettier).
If the formatter is not installed yet, it does nothing. Never blocks.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

PRETTIER_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".css", ".json", ".html"}


def formatter_command(file: Path, project: Path) -> list[str] | None:
    backend, frontend = project / "backend", project / "frontend"
    if file.suffix == ".py" and file.is_relative_to(backend):
        ruff = backend / ".venv" / "bin" / "ruff"
        if ruff.exists():
            return [str(ruff), "format", "--quiet", str(file)]
    if file.suffix in PRETTIER_SUFFIXES and file.is_relative_to(frontend):
        prettier = frontend / "node_modules" / ".bin" / "prettier"
        if prettier.exists():
            return [str(prettier), "--write", "--log-level", "warn", str(file)]
    return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
        file_path = (event.get("tool_input") or {}).get("file_path")
        if not file_path:
            return 0
        project = Path(os.environ.get("CLAUDE_PROJECT_DIR", event.get("cwd", "."))).resolve()
        command = formatter_command(Path(file_path).resolve(), project)
        if command:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"format hook: {result.stderr.strip()}", file=sys.stderr)
    except Exception as error:  # formatting is a convenience: never fail the tool call
        print(f"format hook: {error!r}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
