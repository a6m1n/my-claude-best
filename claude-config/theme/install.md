# Install Eos and Nyx

What each file is and what the colours change is in [README.md](README.md).

**Navigation**

- [What the script does on your machine](#what-the-script-does-on-your-machine)
- [Set it up by hand](#set-it-up-by-hand)
- [Install with one paste](#install-with-one-paste)
- [If the theme does not switch](#if-the-theme-does-not-switch)
- [Undo](#undo)
- [Sources](#sources)

## What the script does on your machine

It runs `defaults read -g AppleInterfaceStyle` to learn whether macOS is in dark mode. Then it reads `nyx.json` (dark) or `eos.json` (light) from the themes folder of Claude Code's config folder, `~/.claude/themes/` (or `$CLAUDE_CONFIG_DIR/themes/` when that variable is set), and writes `eos-nyx.json` in the same folder. It builds the new file in your temp folder and moves it into place, and when nothing changed it writes nothing. It prints nothing, makes no network calls, and runs with your user's rights at every session start, so read it before you install it: it is one short file.

## Set it up by hand

You need:

- macOS. On other systems the script always picks the light theme.
- A Claude Code version with custom themes: `/theme` shows **New custom theme…** at the end of its list.
- A clone of [this repository](../../README.md) (the green Code button on the repository page copies its address: `git clone <address>`), and one terminal in the clone's root for all the commands.

If you set `CLAUDE_CONFIG_DIR`, use that folder in place of `~/.claude` in every command and in the settings below.

1. **Keep a dated copy of what you have.** Your themes folder, hooks folder or settings may already hold files with these names. The copies end in `.bak-<stamp>`, and Claude Code loads only files that end in `.json`, so they do not show up as themes.

   ```sh
   stamp=$(date +%Y%m%d-%H%M%S)
   for f in ~/.claude/themes/eos.json ~/.claude/themes/nyx.json ~/.claude/themes/eos-nyx.json ~/.claude/hooks/theme-follow-appearance.sh ~/.claude/settings.json; do
     if [ -e "$f" ]; then cp "$f" "$f.bak-${stamp:?run the stamp line first}"; fi
   done
   ```

2. **Copy the three themes and the script.** `~/.claude/` holds your own Claude Code settings for every project, so the theme follows you everywhere. The script must be executable, because the hook runs it as a command.

   ```sh
   SRC=claude-config/theme
   mkdir -p ~/.claude/themes ~/.claude/hooks
   cp "$SRC/eos.json" "$SRC/nyx.json" "$SRC/eos-nyx.json" ~/.claude/themes/
   cp "$SRC/theme-follow-appearance.sh" ~/.claude/hooks/
   chmod 755 ~/.claude/hooks/theme-follow-appearance.sh
   ```

   If `~/.claude/themes/` did not exist before this step, restart the Claude Code sessions you have open: Claude Code starts watching the folder only when it exists at start.

3. **Run the script once.** This checks it before Claude Code runs it, and puts the theme for the current macOS mode into `eos-nyx.json`.

   ```sh
   ~/.claude/hooks/theme-follow-appearance.sh; echo "exit $?"
   grep '"name"' ~/.claude/themes/eos-nyx.json
   ```

   It prints `exit 0` and `"name": "Nyx (auto)"` in dark mode, or `"name": "Eos (auto)"` in light mode. Anything else, see [below](#if-the-theme-does-not-switch).

4. **Add the theme and the hook to `~/.claude/settings.json`.** The file may already hold your permissions, hooks and model choice, so merge these keys into it; never replace the whole file. Step 1 kept a copy of it.

   ```json
   {
     "theme": "custom:eos-nyx",
     "hooks": {
       "SessionStart": [
         {
           "hooks": [
             {
               "type": "command",
               "command": "~/.claude/hooks/theme-follow-appearance.sh",
               "timeout": 10
             }
           ]
         }
       ]
     }
   }
   ```

   | Part | What it means |
   |---|---|
   | `"theme": "custom:eos-nyx"` | The theme Claude Code shows: the file `eos-nyx.json`, named without `.json`. |
   | `SessionStart` | Run the hook when a session starts. The entry has no `matcher`, so it runs on every start: a new session, resume, `/clear`, compact and fork. |
   | `"command"` | The script to run. Claude Code runs it through `sh -c`, so `~` works. |
   | `"timeout": 10` | Stop the script after 10 seconds. It needs well under one. |

   If `"theme"` is already there, replace its value; never add a second `"theme"`, `"hooks"` or `"SessionStart"` key, because the last one wins and hides the first. If `"hooks"` is there without `"SessionStart"`, add the `"SessionStart": [ … ]` part inside it. If `hooks.SessionStart` is there, add only the inner `{ "hooks": [ … ] }` object to its list and keep your other entries. If the file does not exist, create it with just this block. Then check that it is still valid JSON, because a broken file turns off every setting in it:

   ```sh
   python3 -m json.tool ~/.claude/settings.json > /dev/null && echo ok
   ```

   Anything but `ok` means the merge broke the file: fix it, or copy the dated copy from step 1 back.

   ```sh
   for f in ~/.claude/settings.json.bak-${stamp:?run the stamp line in step 1 first} ~/.claude/settings.json; do
     if [ -e "$f" ]; then python3 -c 'import json, sys; s = json.load(open(sys.argv[1])); print(s.get("theme"), {k: len(v) for k, v in s.get("hooks", {}).items()})' "$f"; fi
   done
   ```

   The last line must start with `custom:eos-nyx` and show the same hook counts as the line above it, with `SessionStart` one higher. Anything else means a key is there twice: fix it, or copy the dated copy back. If you had no `settings.json` before step 1, only one line prints, and it must read `custom:eos-nyx {'SessionStart': 1}`.

5. **Start a new session.** Run `/theme`: `Nyx (auto)` or `Eos (auto)` is the current theme. To see the switch, change the appearance in System Settings → Appearance, then start a new session in another window: the first window changes its colours too.

## Install with one paste

Clone [this repository](../../README.md) (the green Code button on the repository page copies its address: `git clone <address>`), open a terminal in the clone, start `claude`, and paste the prompt below (the copy button sits in the corner of the block).

Claude Code checks everything first, then backs up your files, copies the themes and the script, merges the settings and shows you each change. It asks before it replaces anything you already have. In Manual mode Claude Code asks before most commands and every file edit; in auto mode a classifier reviews them instead. Press Shift+Tab to switch to Manual first if you want to approve each change yourself.

```text
Install the Eos and Nyx themes from claude-config/theme/ in a clone of the my-claude-best repository into my global Claude Code config. Change nothing in the config folder except the four files named below, settings.json and the backups named below: not CLAUDE.md, skills, agents, other hooks or any other setting. If the current folder is a clone of that repository, its CLAUDE.local.md is an example for other projects; ignore it. Otherwise follow your instruction files as usual. Follow the steps in order, and stop to ask me when a step says so. If a step fails after you have changed a file, copy that file's backup back before you stop.

1. Run `uname`. If it does not print Darwin, stop and tell me: the script reads the macOS appearance only.
2. Find claude-config/theme/ under the current directory. If it is not there, stop and ask me for the path. Read theme-follow-appearance.sh and tell me in two lines what it reads and writes on my machine.
3. If the CLAUDE_CONFIG_DIR environment variable is set, use that folder as CONFIG below; otherwise CONFIG is ~/.claude.
4. Check the settings before you change anything: if CONFIG/settings.json exists and does not parse as JSON, stop and show me the parse error. If "theme" is set to something other than "custom:eos-nyx", show me the current value and ask whether to replace it.
5. Make a timestamp once, in the form YYYYMMDD-HHMMSS, and use it for every backup. Never overwrite an existing file with a backup; if a backup name is taken, add -2, -3 and so on.
6. For each of CONFIG/themes/eos.json, CONFIG/themes/nyx.json, CONFIG/themes/eos-nyx.json and CONFIG/hooks/theme-follow-appearance.sh: if it does not exist or is identical to the file in claude-config/theme/, go on. If it differs, show me the difference and ask before you replace it; if I agree, first copy the old one to <its name>.bak-<timestamp> as a regular file (plain cp). If I say no, stop and change nothing more.
7. Create CONFIG/themes and CONFIG/hooks if they are missing, copy the three JSON files to CONFIG/themes/ and the script to CONFIG/hooks/, and run chmod 755 on the copied script. If CONFIG/themes did not exist before this step, remember to tell me at the end to restart the Claude Code sessions I have open.
8. Run the copied script once and show me its exit code and the "name" line of CONFIG/themes/eos-nyx.json. It must exit 0 and the name must be "Nyx (auto)" or "Eos (auto)". If not, stop and show me its error.
9. If CONFIG/settings.json exists, copy it to CONFIG/settings.json.bak-<timestamp> as a regular file. Then set "theme" to "custom:eos-nyx" (unless I said no in step 4), and add this object to the hooks.SessionStart list, creating "hooks" and "SessionStart" if they are missing, and keep every other key and hook exactly as it is:
   {"hooks": [{"type": "command", "command": "~/.claude/hooks/theme-follow-appearance.sh", "timeout": 10}]}
   When CONFIG is not ~/.claude, write the full path of the copied script in "command". If an entry with that command is already in SessionStart, do not add a second one.
10. Parse the settings file again to prove it is valid JSON, and show me the diff against the backup.
11. Finish with what changed, the exact paths of the backups you made, and how to undo it: remove the SessionStart entry you added, put back the old "theme" value from the settings backup (or pick another theme in /theme), delete the files you copied if I had none before, and copy the .bak-<timestamp> files back where you replaced mine. Then tell me to start a new session and run /theme to see Eos (auto) or Nyx (auto) as the current theme.
```

## If the theme does not switch

- A "SessionStart:startup hook error" notice appears (the word after the colon can also be resume, clear, compact or fork): the line under its title ends with the script's message. `cannot read …` means a theme file is missing; `cannot create a temp file …` means your temp folder is missing; `failed to write …` means the themes folder is not writable.
- Claude Code shows its default dark colours, or `/theme` does not list `Eos (auto)` or `Nyx (auto)`: a theme file is not valid JSON, or the themes folder did not exist when Claude Code started. Check each file with `python3 -m json.tool ~/.claude/themes/eos.json`, then `nyx.json` and `eos-nyx.json`. Fix the light or dark file and run the script again (step 3). If all three are valid, restart Claude Code once.
- No notice and no switch: check that `"theme"` is `"custom:eos-nyx"`, then run the script by hand (step 3). The `disableAllHooks` setting turns all hooks off, and so does `allowManagedHooksOnly` when your organization sets it.
- The colours follow macOS but not your terminal: the script reads the macOS setting. Set your terminal profile to follow the system appearance.

## Undo

- Delete the `SessionStart` entry you added, and pick another theme in `/theme`, or put back the old `"theme"` value from your settings copy.
- Delete `~/.claude/hooks/theme-follow-appearance.sh` and `~/.claude/themes/eos-nyx.json`, and the light and dark files too if you do not want them. Where you had your own files before, copy the `.bak-<stamp>` copies back.

Copying the whole settings copy back is exact only right after the install; later it also undoes your `/model` and `/config` changes.

## Sources

- Anthropic, "Configure your terminal for Claude Code": https://code.claude.com/docs/en/terminal-config (custom themes in `~/.claude/themes/`, the `custom:<slug>` setting, `/theme` and **New custom theme…**, live reload, one restart when the folder did not exist at start)
- Anthropic, "Hooks reference": https://code.claude.com/docs/en/hooks (`SessionStart` and its sources, no matcher means every source, `sh -c` for a command without `args`, `timeout` in seconds, the non-blocking error notice)
- Anthropic, "Choose a permission mode": https://code.claude.com/docs/en/permission-modes (Manual mode asks before most commands and every file edit; in auto mode a classifier reviews them; Shift+Tab switches the mode)
- Claude Code 2.1.301, read from the installed program: a theme file must end in `.json` to load; `disableAllHooks` and `allowManagedHooksOnly` as the settings schema describes them.
