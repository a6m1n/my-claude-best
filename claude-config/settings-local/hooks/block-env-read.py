#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The my-claude-best authors
"""Claude Code PreToolUse hook: deny Read, Grep, Bash and PowerShell calls that name a .env file.

Standard library only, so the hook runs with any python3 and nothing to install. That trades away
a validation library at the edge: read_tool_call() is the one place raw input is parsed.
"""

import json
import os
import re
import sys
from typing import Dict, Final, Optional, Tuple

# Example files carry key names, not secrets, so Claude may read them to learn a project's setup.
ALLOWED_ENV_NAMES: Final = frozenset({".env.example", ".env.local.example"})

# After ".env": a dot starts a variant such as .env.local; *, ? and [ start a shell or Grep pattern
# that expands to .env files, such as .env* or .env.*.
PROTECTED_PREFIXES: Final = (".env.", ".env*", ".env?", ".env[")

# What ends a file name inside a command: whitespace, quotes, shell operators, redirections, and
# the "=" or ":" before a value (--file=.env, $HOME:.env). A wider split only finds more names.
COMMAND_SEPARATORS: Final = re.compile(r"[\s'\"`=<>|;&(){}:,]+")

# What ends a name inside a Grep glob such as {.env,.env.local} or **/.env*.
GLOB_SEPARATORS: Final = re.compile(r"[{},/]+")

SHELL_TOOLS: Final = frozenset({"Bash", "PowerShell"})


def is_protected_env_file(path: str) -> bool:
    """True when the last part of the path is a .env file name, or a pattern that matches one."""
    name = os.path.basename(path.replace("\\", "/").rstrip("/"))
    if name in ALLOWED_ENV_NAMES:
        return False
    return name == ".env" or name.startswith(PROTECTED_PREFIXES)


def command_names_protected_env(command: str) -> bool:
    """True when any word of a shell command is a protected .env name.

    The hook reads the text; it never runs or parses the command. So it also blocks a command that
    only mentions .env, such as an echo: a false block costs Claude one retry, a missed read leaks
    the secrets.
    """
    return any(is_protected_env_file(word) for word in COMMAND_SEPARATORS.split(command))


def glob_targets_env(glob: str) -> bool:
    """True when any part of a Grep glob is a protected .env name."""
    return any(is_protected_env_file(part) for part in GLOB_SEPARATORS.split(glob))


def denial_reason(tool_name: str, tool_input: Dict[str, object]) -> Optional[str]:
    """Why this tool call must be denied, or None when it goes on to the permission rules."""
    if tool_name == "Read":
        file_path = str(tool_input.get("file_path") or "")
        if is_protected_env_file(file_path):
            return f"Reading protected .env files is forbidden: {file_path}"

    elif tool_name == "Grep":
        path = str(tool_input.get("path") or "")
        glob = str(tool_input.get("glob") or "")
        if is_protected_env_file(path):
            return f"Grep on protected .env files is forbidden: {path}"
        if glob_targets_env(glob):
            return f"Grep targeting protected .env files is forbidden: glob={glob}"

    elif tool_name in SHELL_TOOLS:
        command = str(tool_input.get("command") or "")
        if command_names_protected_env(command):
            return f"{tool_name} command references protected .env files: {command}"

    return None


def read_tool_call() -> Optional[Tuple[str, Dict[str, object]]]:
    """The tool name and its input from the hook's stdin, or None when stdin is not a tool call."""
    try:
        # Decode as UTF-8 explicitly: on Windows, sys.stdin reads a pipe in the ANSI code page, and
        # one character outside it would fail the decode and switch the check off for that call.
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except ValueError:
        # Fail open: Claude Code always sends a JSON object, and a guard that blocked every call on
        # input it cannot read would stop the whole session. ValueError covers bad JSON and bad UTF-8.
        return None
    if not isinstance(payload, dict):
        return None

    tool_input = payload.get("tool_input")
    return str(payload.get("tool_name") or ""), tool_input if isinstance(tool_input, dict) else {}


def main() -> None:
    tool_call = read_tool_call()
    if tool_call is None:
        return
    reason = denial_reason(*tool_call)
    if reason is None:
        # No output and exit 0 is no decision: Claude Code applies the permission rules as usual.
        return

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


if __name__ == "__main__":
    main()
