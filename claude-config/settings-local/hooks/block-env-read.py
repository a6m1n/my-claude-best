#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The my-claude-best authors
"""Claude Code PreToolUse hook: deny tool calls that name a .env file.

It checks Read, Grep, Bash and PowerShell calls. Standard library only and Python 3.8
or later, so the hook runs with the python3 a system already has and nothing to
install. That trades away a validation library at the edge: read_tool_call() is the
one place raw input is parsed.
"""

# This import lets dict[...] annotations run on Python 3.8, and X | None on 3.8 and
# 3.9: without it they fail when the function is defined.
from __future__ import annotations

import json
import os
import re
import sys
from typing import Final, Mapping

# Example files carry key names, not secrets, so Claude may read them to learn a
# project's setup.
ALLOWED_ENV_NAMES: Final = frozenset({".env.example", ".env.local.example"})

# After ".env": a dot starts a variant such as .env.local; *, ? and [ start a shell or
# Grep pattern that expands to .env files, such as .env* or .env.*.
PROTECTED_PREFIXES: Final = (".env.", ".env*", ".env?", ".env[")

# A file name inside a command ends at whitespace, quotes, shell operators,
# redirections, the "," of a brace list ({a,.env}), and the "=" or ":" before a value
# (--file=.env, $HOME:.env). A wider split only finds more names.
COMMAND_SEPARATORS: Final = re.compile(r"[\s'\"`=<>|;&(){}:,]+")

# A name inside a Grep glob ends at whitespace, where Claude Code splits the field into
# separate globs, and at {, }, "," and "/" inside one, such as in {.env,.env.local} or
# **/.env*.
GLOB_SEPARATORS: Final = re.compile(r"[\s{},/]+")

SHELL_TOOLS: Final = frozenset({"Bash", "PowerShell"})


def is_protected_env_file(path: str) -> bool:
    """Return True when the path ends in a .env name, or a pattern that matches one."""
    # Lower case: macOS and Windows open .env for .ENV. On Linux, where they are
    # different files, it also blocks .ENV (one retry) and lets .ENV.EXAMPLE through
    # as an example file.
    name = os.path.basename(path.replace("\\", "/").rstrip("/")).lower()

    if name in ALLOWED_ENV_NAMES:
        return False

    return name == ".env" or name.startswith(PROTECTED_PREFIXES)


def command_names_protected_env(command: str) -> bool:
    """Return True when any word of a shell command is a protected .env name.

    The hook reads the text; it never runs or parses the command. So it also blocks a
    command that only mentions .env, such as an echo: a false block costs Claude one
    retry, a missed read leaks the secrets.
    """
    words = COMMAND_SEPARATORS.split(command)

    return any(is_protected_env_file(word) for word in words)


def glob_names_protected_env(glob: str) -> bool:
    """Return True when any part of a Grep glob is a protected .env name."""
    return any(is_protected_env_file(part) for part in GLOB_SEPARATORS.split(glob))


def denial_reason(tool_name: str, tool_input: Mapping[str, str]) -> str | None:
    """Return why the call is denied, or None to leave it to the permission rules."""
    file_path = tool_input.get("file_path", "")
    path = tool_input.get("path", "")
    glob = tool_input.get("glob", "")
    command = tool_input.get("command", "")

    if tool_name == "Read" and is_protected_env_file(file_path):
        return f"Reading protected .env files is forbidden: {file_path}"

    if tool_name == "Grep" and is_protected_env_file(path):
        return f"Grep on protected .env files is forbidden: {path}"

    if tool_name == "Grep" and glob_names_protected_env(glob):
        return f"Grep targeting protected .env files is forbidden: glob={glob}"

    if tool_name in SHELL_TOOLS and command_names_protected_env(command):
        return f"{tool_name} command references protected .env files: {command}"

    return None


def read_tool_call() -> tuple[str, dict[str, str]] | None:
    """Return the tool name and its text fields from stdin, or None for other input."""
    try:
        # Decode as UTF-8 explicitly: on Windows, sys.stdin reads a pipe in the ANSI
        # code page, and one character outside it would fail the decode and switch the
        # check off for that call.
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except ValueError:
        # Fail open: Claude Code always sends a JSON object, and a guard that blocked
        # every call on input it cannot read would stop the whole session.
        # ValueError covers bad JSON and bad UTF-8.
        return None

    if not isinstance(payload, dict):
        return None

    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    fields = tool_input if isinstance(tool_input, dict) else {}
    # Keep only text fields: every field the checks read is a string, so no later read
    # coerces.
    text_fields = {
        key: value for key, value in fields.items() if isinstance(value, str)
    }

    return (tool_name if isinstance(tool_name, str) else ""), text_fields


def main() -> None:
    tool_call = read_tool_call()

    if tool_call is None:
        return

    reason = denial_reason(*tool_call)

    if reason is None:
        # No output and exit 0 is no decision: Claude Code applies the permission
        # rules as usual.
        return

    decision = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(decision))  # noqa: T201  # The hook answers Claude Code on stdout


if __name__ == "__main__":
    main()
