# Install the status line

What each part of the line means is in [README.md](README.md).

**Navigation**

- [What the script does on your machine](#what-the-script-does-on-your-machine)
- [Set it up by hand](#set-it-up-by-hand)
- [Install with one paste](#install-with-one-paste)
- [If nothing appears](#if-nothing-appears)
- [Undo](#undo)
- [Sources](#sources)

## What the script does on your machine

It reads the JSON that Claude Code sends on stdin, and the last 2 MB of the session transcript to count cache hits and tokens per hour. It writes two small files per session to your temp folder, `claude_statusline_burn_<session>.json` and `claude_statusline_agents_<session>.json`, because `burn` and the pause timer need a history that Claude Code does not keep. It makes no network calls. It runs with your user's rights on every refresh, so read it before you install it: it is one file.

## Set it up by hand

You need:

- Python 3.9 or newer (`python3 --version`).
- A clone of [this repository](../../README.md#license) (its License section shows the full address to clone), or only the file: open [statusline.py](statusline.py) on GitHub, click Raw, copy the raw URL, and download it into a new empty folder, never into `~/.claude`: `cd "$(mktemp -d)" && curl -fsSL <raw URL> -o statusline.py`.
- One terminal for all the commands, in the clone's root or in that new folder.

The commands are for macOS and Linux. On Windows, use the [one-paste route](#install-with-one-paste), which finds `python3`, `python` or `py -3`; it is not tested on Windows yet.

1. **Run the script once where it is.** Claude Code shows an empty line when a status line command fails, so first check that Python runs the file. The first line sets the path to the script once; with only the file, make it `SRC=statusline.py`.

   ```sh
   SRC=claude-config/statusline/statusline.py
   echo '{"model": {"display_name": "Opus"}}' | python3 "$SRC"
   ```

   It prints `ctx: — │ Opus │ cache: —`, with colors. The dashes are fine: a real session fills them in.

2. **Copy it to `~/.claude/statusline.py`.** `~/.claude/` holds your own Claude Code settings for every project, so the status line follows you everywhere. If you already have your own `~/.claude/statusline.py`, the second line keeps a dated copy of it, and any `statusLine` that runs that file runs this script from now on.

   ```sh
   stamp=$(date +%Y%m%d-%H%M%S)
   if [ -e ~/.claude/statusline.py ]; then cp ~/.claude/statusline.py ~/.claude/statusline.py.bak-${stamp:?run the stamp line first}; fi
   cp "$SRC" ~/.claude/statusline.py
   ```

   Check it: run the command from step 1 on `~/.claude/statusline.py`. It prints the same line.

3. **Add two keys to `~/.claude/settings.json`.** The file may already hold your permissions, hooks and model choice, so keep a dated copy first, then merge the keys into it; never replace the whole file.

   ```sh
   if [ -e ~/.claude/settings.json ]; then cp ~/.claude/settings.json ~/.claude/settings.json.bak-${stamp:?run the stamp line first}; fi
   ```

   Open `~/.claude/settings.json` in an editor and paste the two keys without the block's outer braces, inside the file's outer `{ }`, with a comma after the key before them. If `statusLine` or `subagentStatusLine` is already there, replace its value, or leave that key out to keep yours. If the file does not exist, create it with just this block. To use the status line in one project only, put the keys in that project's `.claude/settings.local.json` instead (personal; if you create the file by hand, add it to `.gitignore`), and run the backup and the checks on that file.

   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "python3 ~/.claude/statusline.py",
       "refreshInterval": 300
     },
     "subagentStatusLine": {
       "type": "command",
       "command": "python3 ~/.claude/statusline.py --subagents"
     }
   }
   ```

   `refreshInterval: 300` redraws the line every 5 minutes, so the reset times and the cache countdown stay current to within 5 minutes.

   Then check that the file is still valid JSON. A broken file turns off every setting in it, not only the status line:

   ```sh
   python3 -m json.tool ~/.claude/settings.json > /dev/null && echo ok
   grep -oE '"(statusLine|subagentStatusLine)"' ~/.claude/settings.json | wc -l
   ```

   Anything but `ok` means the merge broke the file: fix it, or copy the dated backup back. The second line must print `2`; more means a key is there twice.

4. **Send any message in Claude Code.** The line appears once you save the file; the numbers fill in after the next answer. To see the agent rows, ask Claude to do a task with a subagent: each row now shows the model (a named agent's name comes first). To remove it, see [Undo](#undo). If nothing appears, see [below](#if-nothing-appears).

## Install with one paste

Two routes:

- With a clone: clone [this repository](../../README.md#license) (its License section shows the full address to clone), open a terminal in the clone, start `claude`, and paste the prompt below (the copy button sits in the corner of the block).
- Without a clone: start `claude` anywhere and paste the prompt. When it asks for the script, give it the raw URL of statusline.py: open [statusline.py](statusline.py) on GitHub, click Raw, and copy the address.

Claude Code checks everything first, then backs up your files, copies the script, merges the two keys and shows you each change. It asks before it replaces anything you already have. In Manual mode Claude Code asks before most commands and every file edit; in auto mode a classifier reviews them instead. Press Shift+Tab to switch to Manual first if you want to approve each change yourself. When it is done, send one message and look under the prompt; if nothing appears, see [below](#if-nothing-appears). This route has not been tested on Windows.

```text
Install the status line from claude-config/statusline/statusline.py in a clone of the my-claude-best repository, or from the raw URL I give you, into my global Claude Code config. Change nothing in ~/.claude/ except ~/.claude/statusline.py, ~/.claude/settings.json and the backups named below: not CLAUDE.md, skills, agents, hooks or any other setting. If the current folder is a clone of that repository, its CLAUDE.local.md is an example for other projects; ignore it. Otherwise follow your instruction files as usual. Follow the steps in order, and stop to ask me when a step says so. If a step fails after you have changed a file, copy that file's backup back before you stop.

1. Find the script: claude-config/statusline/statusline.py under the current directory. If it is not there, stop and ask me for the path to statusline.py or for its raw URL. Download a URL with `curl -fsSL <url> -o <a temp file>`, never with a web-fetch tool, which returns a summary instead of the file; then show me its line count and its first and last lines.
2. Read the whole script and tell me in two lines what it reads and writes on my machine.
3. Check Python: run `python3 --version`. If it fails or prints no version, try `python --version`, then `py -3 --version`, and use the first one that works as PYTHON below. It must be 3.9 or newer; if not, stop and tell me.
4. Test the script where it is: pipe '{"model": {"display_name": "Opus"}}' into `PYTHON <path from step 1>` and show me the output. It must print one line that starts with "ctx:". If it fails, stop and show me the error.
5. Check the settings before you change anything: if ~/.claude/settings.json exists and does not parse as JSON, stop and show me the parse error. If statusLine or subagentStatusLine is already set, show me the current value and ask whether to replace it.
6. Make a timestamp once, in the form YYYYMMDD-HHMMSS, and use it for every backup. Never overwrite an existing file with a backup; if a backup name is taken, add -2, -3 and so on.
7. Copy the script to ~/.claude/statusline.py. If that file exists and is identical, skip the copy. If it exists and differs, show me the first lines of both files and ask before you replace it; if I agree, first copy the old one to ~/.claude/statusline.py.bak-<timestamp> as a regular file (plain cp, never cp -a or -P; check the backup with `test ! -L`). If I say no, stop and change nothing. If it is a symlink, write through it to the file it points to and keep the link.
8. If ~/.claude/settings.json exists, copy it to ~/.claude/settings.json.bak-<timestamp>, as a regular file the same way. Then merge these two keys into it, or create it with just these keys, and keep every other key exactly as it is. If I said no to replacing statusLine or subagentStatusLine in step 5, leave that key as it is (merge only what I agreed to). If it is a symlink, edit the file it points to in place and keep the link.
   "statusLine": {"type": "command", "command": "python3 ~/.claude/statusline.py", "refreshInterval": 300}
   "subagentStatusLine": {"type": "command", "command": "python3 ~/.claude/statusline.py --subagents"}
   If PYTHON from step 3 is not python3, use it in both commands instead of python3. Use forward slashes in paths.
9. Parse the settings file again to prove it is valid JSON, and show me the diff against the backup.
10. Finish with what changed, the exact paths of the backups you made, and how to undo it: delete the keys you added, and ~/.claude/statusline.py if I had none before; where you replaced mine, put back the old values of those keys from the settings backup and copy the statusline.py backup back. Then tell me to send one message and look for the line under the prompt, and to run a task with a subagent to see the agent rows.
```

## If nothing appears

- Run `claude --debug`: it logs the script's errors and its exit code.
- Accept the workspace trust prompt. Claude Code runs no status line in a folder you have not trusted.
- The `disableAllHooks` setting turns the status line off, and so does `allowManagedHooksOnly` when your organization sets it.
- Claude Code may find a different `python3` than your terminal does. Run `command -v python3` and put that full path in `command` in place of `python3`.
- If the agent rows keep their default look, update Claude Code: older versions do not send the model of each agent.

## Undo

- Delete the keys you added (from `~/.claude/settings.json`, or the project's `.claude/settings.local.json`); where you replaced a value, put back the old one from your first settings backup.
- Delete `~/.claude/statusline.py` if you had none before; otherwise copy `statusline.py.bak-<stamp>` back.

Copying the whole settings backup back is exact only right after the install; later it also undoes your `/model` and `/config` changes.

## Sources

- Anthropic, "Customize your status line": https://code.claude.com/docs/en/statusline (`refreshInterval`, `subagentStatusLine` and its one-row-per-agent output, the Windows shell, the troubleshooting list)
- Anthropic, "Choose a permission mode": https://code.claude.com/docs/en/permission-modes (Manual mode asks before most commands and every file edit; in auto mode a classifier reviews them; Shift+Tab switches the mode)
