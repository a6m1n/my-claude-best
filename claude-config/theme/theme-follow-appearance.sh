#!/bin/sh
# Claude Code SessionStart hook: keeps themes/eos-nyx.json a copy of eos.json (light) or nyx.json
# (dark), picked by the macOS appearance. Claude Code reloads a changed theme file live, so every
# open session that uses custom:eos-nyx follows. Edit eos.json and nyx.json, never the copy.
#
# Why it exists: Claude Code's own "theme": "auto" switches only between the built-in light and
# dark themes, and a custom theme's "base" can name only a built-in preset, not another custom
# theme. So settings.json selects custom:eos-nyx, and this script swaps that file's content.
#
# Wired in: settings.json -> hooks.SessionStart with no matcher, so it runs on every session
# source: startup, resume, /clear, compact and fork.
# Run by hand to switch now: ~/.claude/hooks/theme-follow-appearance.sh
# Undo: delete the SessionStart entry, set "theme" back to e.g. custom:eos, delete
# themes/eos-nyx.json and this script.
#
# Prints nothing on stdout, because SessionStart adds stdout to Claude's context. On success it
# exits 0. On a failure it writes one line to stderr and exits 1: Claude Code then shows a
# non-blocking "SessionStart:<source> hook error" notice with that line, while stderr after
# exit 0 is never shown.

# macOS stores AppleInterfaceStyle=Dark only in dark mode; in light mode the key is absent and the
# read fails (error hidden), so anything but "Dark" means light. This reads the macOS setting, not
# the terminal background: it matches only while the Terminal profile follows the system
# appearance (the "Basic" profile does; a fixed white or black profile does not).

# Claude Code keeps its themes in the themes folder of its config folder: $CLAUDE_CONFIG_DIR when
# that is set, ~/.claude otherwise.
dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/themes"
if [ "$(defaults read -g AppleInterfaceStyle 2>/dev/null)" = "Dark" ]; then
  theme=nyx
  label=Nyx
else
  theme=eos
  label=Eos
fi
src="$dir/$theme.json"
dst="$dir/eos-nyx.json"

if [ ! -r "$src" ]; then
  echo "theme-follow-appearance: cannot read $src" >&2
  exit 1
fi

# Build outside the watched folder, then rename into place, so Claude Code never sees a half-written file.
tmp=$(mktemp "${TMPDIR:-/tmp}/eos-nyx.XXXXXX" 2>/dev/null) || { echo "theme-follow-appearance: cannot create a temp file in ${TMPDIR:-/tmp}" >&2; exit 1; }
if ! sed -E "s/^([[:space:]]*\"name\"[[:space:]]*:[[:space:]]*)\"[^\"]*\"/\1\"$label (auto)\"/" "$src" > "$tmp" 2>/dev/null; then
  echo "theme-follow-appearance: failed to build $dst from $src" >&2
  rm -f "$tmp"
  exit 1
fi

if cmp -s "$tmp" "$dst"; then
  rm -f "$tmp"
else
  chmod 644 "$tmp"
  if ! mv -f "$tmp" "$dst" 2>/dev/null; then
    echo "theme-follow-appearance: failed to write $dst" >&2
    rm -f "$tmp"
    exit 1
  fi
fi
exit 0
