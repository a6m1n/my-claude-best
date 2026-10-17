# create-jira-ticket

A Claude Code skill that turns short notes into Jira tickets and creates them after your yes.

**Navigation**

- [What it does](#what-it-does)
- [Install](#install)
- [Connect Jira](#connect-jira)
- [What you fill in](#what-you-fill-in)
- [Where it differs from the project-management practice](#where-it-differs-from-the-project-management-practice)
- [Files](#files)

## What it does

You run `/create-jira-ticket` with a few lines of notes, in any language, or ask Claude for a
quick ticket or an epic. The skill:

1. Picks the type: a story in most cases, a bug or a task when the notes describe one. It drafts
   an epic only when you ask for one; when the notes look like an epic, the preview says so and
   you can switch with one reply.
2. When you ask for stories under an epic, drafts them as one batch: a new epic with its
   stories, or new stories under an epic that already exists. The stories take the epic's
   assignee, priority, component, labels and fix version.
3. Reads the project's fields from Jira, and, when the notes miss a fact your code holds, sends
   one read-only agent into your repository.
4. Shows one preview: the ticket in English, then a numbered list of every field with where its
   value came from, then numbered questions. In a batch the preview lists the story titles first,
   then each story. The labels around the ticket follow your language.
5. Searches Jira in the background for duplicates and related issues, and offers to link them.
6. Creates the issue, or the epic and its stories, when you reply with a clear yes, and prints
   the keys and links. Any other reply changes the draft and shows the whole preview again. A
   batch stops at the first issue Jira rejects and says what was created and what was not.

It does not write a plan or sub-tasks, create several tickets that are not one epic's stories,
or change an existing issue: stories added under an existing epic leave the epic as it is. It
never writes to Jira before your yes, and it installs or configures nothing.
[output_example.md](output_example.md) shows four whole runs: a story, an epic with its stories,
a bug and a task.

Use it when a few lines of notes should become a ticket, or an epic and its stories, in one
pass. It is the wrong tool when the work needs a plan, research or a review before it goes into
the backlog, when you need sub-tasks or several unrelated tickets, or when an existing issue
needs a change: the skill does none of these, so write or edit those issues in Jira itself.

## Install

From a clone of this repository, copy the folder for all your projects:

```bash
mkdir -p ~/.claude/skills
cp -R skills/create-jira-ticket ~/.claude/skills/
```

Or for one project:

```bash
mkdir -p ../your-project/.claude/skills
cp -R skills/create-jira-ticket ../your-project/.claude/skills/
```

Keep `SKILL.md` and `output_example.md` together: the skill reads the example before each
preview. A running session picks up the new folder; if the `skills` folder itself is new, run
`/reload-skills`.

## Connect Jira

The skill works through Atlassian's remote MCP server. It needs a Jira Cloud site and an account
that may create issues in the project. Without the server, the skill still writes the draft, and
its first question asks you to connect Jira.

1. Add the server once, for all your projects. The skill is written for this endpoint, Atlassian
   MCP v1, and does not work on v2:

   ```bash
   claude mcp add --transport http --scope user atlassian https://mcp.atlassian.com/v1/mcp/authv2
   ```

2. Start Claude Code, run `/mcp`, pick `atlassian`, and sign in to Atlassian in the browser.
3. Check, inside the project where you use the skill: `claude mcp get atlassian` shows the status
   `Connected` and the URL above. If it shows `Needs authentication`, run `/mcp`, pick
   `atlassian` and sign in again.

If step 1 says `atlassian` already exists, or step 3 shows another URL (Atlassian's own guide
adds the v2 endpoint), remove that entry with the `claude mcp remove` command that
`claude mcp get atlassian` prints, then repeat steps 1 to 3. `claude mcp list` shows every
`atlassian` entry you have.

If the skill asked you to connect in the middle of a draft, the draft stays in that conversation.
Leave the session, do steps 1 to 3, then run `claude --continue` in the same folder and answer
the skill's question. If that opens another conversation, run `/create-jira-ticket` again with
your notes.

If the sign-in is refused, or the skill still cannot read Jira after you signed in, ask your
organization admin. In Atlassian Administration, under Connectors → Atlassian MCP server, the
admin decides which AI tools may connect, and an IP allowlist can also block the calls
([Control Atlassian MCP server settings](https://support.atlassian.com/security-and-access-policies/docs/control-atlassian-rovo-mcp-server-settings/)).

On 1 March 2027 Atlassian moves every v1 connection to its v2 tools. After that date the skill
needs an update.

## What you fill in

Nothing. The skill finds the Jira site from your sign-in, and the project from the notes or from
the issue keys your repository uses (the branch name, recent commits, the instruction files).
When it cannot tell, it asks in the preview.
Two optional changes in your copy of `SKILL.md`:

- **Trigger phrases.** The skill starts on `/create-jira-ticket` and on English phrases such as
  "quick ticket" or "create an epic", listed in the `description` field. Add phrases in your own
  language there when you ask for tickets in that language; when you start the skill by its
  command, leave the field as it is. Claude Code cuts that field at 1,536 characters in its
  skill listing, and it holds about 920 now, so keep the addition short.
- **Approval words.** Step 6 gives "yes", "create", "ok" and "go" as examples of a clear
  approval. Add the words you use in your own language. Leave it as it is when you reply in
  English.

## Where it differs from the project-management practice

This repository has a
[project-management practice](../../docs/engineering/any-language/project-management/README.md)
with its own rules for Jira work items. The skill keeps its own rules, which differ in these
points. If your project follows the practice, change the Type, Assignee, Priority, Fix version
and Parent lines in the preview before you say yes: reply with the line's number and the value
you want. The other rows are rules the skill follows on every run, so change them in your copy
of `SKILL.md`.

| Point | This skill | The practice |
| --- | --- | --- |
| Size | Flags a story that is clearly bigger than one sprint or needs more than five criteria, and suggests an epic | Splits any work item longer than three working days into stories under the same epic, and never turns it into an epic |
| Who makes an epic | You, by asking for one | The product owner or the project manager, in planning, from the work breakdown structure |
| Epic description | Problem, Outcome and Done when; Scope and Out of scope when the notes give them | The work breakdown structure's dictionary entry: scope, owner and done criteria |
| Epic dates | No Start date or Due date | The plan's Start date and Due date on every epic |
| Description of a story or a task | Has a Problem section (a story in a batch has none: the epic's Problem covers it) | The story and its acceptance criteria, with no Problem section |
| Type when two fit equally | Story, with Bug asked as a numbered question | Bug, the first row that fits |
| "so that" | Left out and flagged when the notes give no reason | Always part of a story |
| Assignee | The person the notes name, else you; the stories of a batch take the epic's assignee | Unassigned until someone takes the item |
| Priority | The urgency the notes state, else the Jira default; the stories of a batch take the epic's priority | The default on a story or a task; from severity on a bug |
| Fix version | On an epic when the notes give one, and the stories of a batch take it | None on an epic; each work item carries the version that ships it |
| Bug fields | No Environment, no Affects versions | Both on every bug |
| Parent | Only the epic the notes name, or the epic of the batch | The epic of the work package |
| Links | Duplicate and Relates | Also "blocks" and "is blocked by" for a dependency |

## Files

- [SKILL.md](SKILL.md): the procedure, the ticket shapes, the output contract and the sources
  behind each rule. Read it before you change a rule.
- [output_example.md](output_example.md): four whole runs on invented values, a story, an epic
  with its stories, a bug and a task, each from the preview to the created issues. Read it to
  see what the skill prints.
