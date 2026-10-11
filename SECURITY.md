# Security policy

The code in this repository that runs on your machine is two scripts:

- [claude-config/statusline/statusline.py](claude-config/statusline/statusline.py), with the install commands and the one-paste prompt in [install.md](claude-config/statusline/install.md) that put it there. It runs with your user's rights every time Claude Code refreshes the status line.
- [claude-config/settings-local/hooks/block-env-read.py](claude-config/settings-local/hooks/block-env-read.py), once you copy it into a project as [its README](claude-config/settings-local/README.md#use-it-in-a-project) says. It runs with your user's rights before every Read, Grep, Bash and PowerShell call Claude makes in that project.

The skills in [skills/](skills/README.md) are text, but once you copy them into `.claude/skills/`, they make Claude Code run git and file commands in your repository, some with no permission prompt, on text cloned from a source repository. A way to make a skill write, run or approve something it should not is a security problem too.

## Report a vulnerability

Report it privately: open the repository's Security tab (GitHub may label it "Security and quality") and choose "Report a vulnerability". Never put the details in a public issue, because a public issue shows the problem to everyone before a fix exists. If the button is not there, open an issue that says only that you have a security report, and I will open a private channel.

## Supported versions

Only the latest version on `main`. A fix lands there. [install.md](claude-config/statusline/install.md) says how to copy the status line script to your machine again, [the settings README](claude-config/settings-local/README.md#use-it-in-a-project) how to copy the hook, and [skills/README.md](skills/README.md) how to copy a skill.
