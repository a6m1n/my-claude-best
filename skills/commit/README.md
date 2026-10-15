# commit

A Claude Code skill that drafts a commit message for your changes, shows it to you, and commits
only after your yes.

**Navigation**

- [What it does](#what-it-does)
- [Where it departs from git.md](#where-it-departs-from-gitmd)
- [Install](#install)
- [What to fill in](#what-to-fill-in)
- [Files](#files)

## What it does

The skill works in two phases, and never runs both in the same turn.

1. **Draft.** It reads `git status`, the diff, the last five commits and the branch name, and
   checks the commit identity. Then it writes the message. When the branch name or a recent
   commit carries a ticket key, the title is `type [PROJ-123]: title`. When neither does, the
   title is `type(scope): title`. Bullets follow, each saying what changed and why, and a
   `Co-Authored-By` trailer ends the message. It shows the message and the exact files it will
   commit, and stops.
2. **Commit.** After your explicit yes, it stages those files one by one, by path, and commits
   them. It never uses `git add -A`, `git add .` or `git commit -a`, because another session may
   have its own changes in the same working tree. Then it shows `git log -1 --stat`.

It never pushes and never opens a pull request: that is a separate step, for a `pr` skill or
for you.

To change a draft, give your feedback as arguments, such as `/commit type should be fix, not
feat`. The skill changes only what you name and keeps the rest of the message as it was.

The message format lives in `SKILL.md`, Steps 2, 4 and 5. To change it, edit those steps in
your copy. A project binding (see [What to fill in](#what-to-fill-in)) is not the place to change
the format. It holds facts about one repository, such as its ticket key pattern, and example
messages, and these win over the skill where the two conflict. Without a binding, the skill takes
those facts from your `git log` and your project's instruction files.

## Where it departs from git.md

This format is the skill's own. It differs from the git practice of the library this skill comes
from (`docs/engineering/any-language/git/git.md`, sections 2 and 3):

- the title has no length limit, and the skill's examples start the title with a capital letter;
- with no ticket, the title may be a bare `type: title` when no scope fits, while git.md always
  uses `type(scope):`;
- when a ticket exists, the title always carries `[KEY-123]`, while git.md leaves it out in a
  repository that lints commits with a Conventional Commits tool, because such a linter rejects
  that form;
- the body always has bullets, with no limit on their number and no wrap rule, and a bullet may
  name a file that is not obvious from the diff;
- there is no `chore` type, and a commit may have no type at all;
- a commit that mixes kinds of change takes the type of the main one, while git.md makes two
  unrelated changes two commits;
- every commit ends with a `Co-Authored-By` trailer, which git.md does not have.

If your agent follows both git.md and this skill, it gets two different forms, so choose one. To
use git.md's format, edit Steps 2, 4 and 5 in your copy.

## Install

1. Copy this folder into your personal skills folder. If `~/.claude/skills/commit/` already
   exists, move it out of your skills folder first, for example with
   `mv ~/.claude/skills/commit ~/commit-skill.old`: a folder left inside `~/.claude/skills/`
   still loads as a skill. `cp -R` writes over the files the two folders share without asking,
   and leaves the old folder's other files in place.

   From the root of a clone of this repository, run:

   ```bash
   mkdir -p ~/.claude/skills
   cp -R skills/commit ~/.claude/skills/
   ```

   If you have only the `commit` folder, run these two commands from the folder that holds it:

   ```bash
   mkdir -p ~/.claude/skills
   cp -R commit ~/.claude/skills/
   ```

   Use the personal folder: when a personal skill and a project skill have the same name, Claude
   Code runs the personal one ([Claude Code docs, skills](https://code.claude.com/docs/en/skills)).
   That keeps the project path `.claude/skills/commit/SKILL.md` free for a binding. You can copy
   the folder into one project's `.claude/skills/` instead. It works, but then the skill sits at
   the binding path itself, so there is no separate binding. In that copy, open `SKILL.md` and
   add the project's facts as a short list at the end of its "Project binding" section. The four
   kinds of facts are listed under **The binding** below.

2. Set the commit identity in each repository where you use the skill. Use your own name and
   email in place of the example values:

   ```bash
   git config --local user.name "Jane Doe"
   git config --local user.email "jane.doe@example.com"
   ```

   The skill commits only under a name and email set in the repository's own `.git/config`. If
   they come from `--global`, the system config or environment variables, it shows you the value
   and where it comes from, and stops until you set the pair in the repository. It also asks you
   to remove that value. It stops, too, while something overrides the repository's pair: a
   `GIT_AUTHOR_*` or `GIT_COMMITTER_*` environment variable, or an `author.*` or `committer.*`
   entry in a git config. If nothing is set at all, git often invents a name from your OS user
   name and host name and still commits, so the skill stops before that. For that reason, set
   the pair in your other repositories before you remove a global value. It never sets the
   identity unless you give it the values and ask it to.

3. Change a file in that repository, then type `/commit` in Claude Code. If `/commit` does not
   show up, run `/reload-skills`: Claude Code does not watch a skills folder created after the
   session started. A new session also works. You get the message in a code block and one line
   with the files it will commit. Nothing is staged until you answer yes.
   [output_example.md](output_example.md) shows one such draft.

## What to fill in

Only the identity in [Install](#install) step 2 is required. Everything below is optional.

| What | Where | When you need it |
| --- | --- | --- |
| Your project's facts: the ticket key pattern, the paths to leave out, the scope words, example messages your team likes | A binding file, `.claude/skills/commit/SKILL.md` in the project | Your project's conventions differ from what `git log` shows, or you want them written down |
| The message format: the types, the title and body rules, the good and bad examples | `SKILL.md`, Steps 2, 4 and 5, in your copy | You want a different format, for example because your repository lints commit messages with a Conventional Commits tool. The change applies in every repository where you use your copy; a binding is not meant to change it. |
| The `Co-Authored-By` trailer | `SKILL.md`, Step 5, in your copy, and `attribution.commit` in your settings | You do not want it |
| Trigger phrases in your language | `description` in the `SKILL.md` front matter | You write to Claude in another language |
| The commands that run with no permission prompt | `allowed-tools` in the `SKILL.md` front matter, and `ask` rules in your settings | You want Claude Code to ask before one of them |

**The binding.** A binding is a plain Markdown file that holds facts about one repository, not
rules. The skill reads it at the start of each run and follows it where the two conflict. It can
hold four things:

- the ticket key pattern, such as "`PROJ-` and digits, taken from the branch name";
- the paths that are working documents, which the skill never stages or describes, such as
  `scratch/`;
- the scope words for branches with no ticket, such as `api`, `web`, `docs`;
- one or two example messages your team considers good.

Keep the binding to facts, and write its example messages in the skill's format: the skill
follows the binding where the two conflict, so examples in another format pull the drafts away
from Steps 2, 4 and 5. To change the format, edit those steps in your copy.

The binding file is also a project skill named `commit`. When both exist, `/commit` runs your
personal skill, and that skill reads the file as its binding. Start the binding with this front
matter:

```markdown
---
name: commit
description: Project facts for the commit skill. Not a skill of its own.
user-invocable: false
disable-model-invocation: true
---
```

With `user-invocable: false` and `disable-model-invocation: true`, a teammate who has not
installed the skill gets no `/commit` made of the binding's fact lines.

**The trailer.** Step 5 adds `Co-Authored-By: <model> <noreply@anthropic.com>` to every commit,
naming the model that wrote the change. Claude Code has its own setting for this line,
`attribution.commit`, which changes or hides the trailer Claude Code adds to commits
([settings reference](https://code.claude.com/docs/en/settings-reference)). To drop the trailer,
do both: delete the trailer line from the Step 5 template and the sentence under it, and set
`attribution.commit` to an empty string in your settings. Deleting only the line may not be
enough, because by default Claude Code adds the trailer itself. Setting only the empty string
may not be enough either. The settings reference says your own instructions about attribution,
such as a `CLAUDE.md` or memory rule, win over that setting, unless your organization sets the
line in managed settings. It does not say whether a skill counts as such an instruction.

**Trigger phrases.** The phrases are in English, inside `description`. Add your own after them.
Claude Code cuts a skill's listing text at 1,536 characters (`description` and `when_to_use`
together), and `description` here is about 800, so keep the addition short.

**Permissions.** `allowed-tools` lists the git commands that run with no permission prompt. The
list works only in the turn that starts the skill
([Claude Code docs, skills](https://code.claude.com/docs/en/skills)). The commit happens in a
later turn, after your yes. In that turn your own permission settings decide whether Claude Code
asks before `git add` and `git commit`. Removing an entry does not bring back a prompt for plain
git reads such as `git status`, `git diff` and `git log`: Claude Code runs those without asking
in any case. To be asked before one, add an `ask` rule for it in your settings
([permissions](https://code.claude.com/docs/en/permissions)).

## Files

- [SKILL.md](SKILL.md): the procedure, from your feedback (Step 0) to the commit (Step 7), and
  the identity gate. Read it before you change a rule.
- [output_example.md](output_example.md): one draft on invented values. Read it to see what the
  skill shows you.
