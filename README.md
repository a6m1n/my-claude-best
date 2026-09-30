# my-claude-best

Engineering practices for teams that code with AI agents, plus a Claude Code status line.

**Navigation**

- [What it is](#what-it-is)
- [Start here](#start-here)
- [Layout](#layout)
- [Conventions](#conventions)
- [Where to get help](#where-to-get-help)
- [Maintainers and contributing](#maintainers-and-contributing)
- [License](#license)

## What it is

My personal collection of engineering best practices: how I set up projects, write and review code, and work with AI coding agents. Each practice is a folder of rules and examples that you copy into your own repository, and that your coding agent reads before it works there. Almost everything here is Markdown. The exception is `claude-config/`: my Claude Code configuration, as files you copy to your own machine. There is nothing to build. The code examples are in Python.

This is an unofficial project, not affiliated with or endorsed by Anthropic.

## Start here

- To adopt a practice, open [docs/engineering/git/](docs/engineering/git/). Its `README.md` has a "How to adopt" section: the steps that copy the folder into your repository and point your agent at it.
- To try something in five minutes, install the [status line](claude-config/statusline/): context, usage limits, the prompt cache and the agent panel, under the Claude Code prompt.
- To write instructions for Claude Code, read [claude-md.md](docs/claude-code/claude-md.md): what belongs in a `CLAUDE.md` and what does not.

## Layout

- `docs/engineering/` — engineering practices, one folder per topic, each with a `README.md` map, its rules and examples. [docs/engineering/CLAUDE.md](docs/engineering/CLAUDE.md) is the contract for writing one. In the order to read them:
  - [git/](docs/engineering/git/) — branches, commits, pull requests, merging, and no rewriting of pushed history.
  - [python/](docs/engineering/python/) — where a constraint belongs, what in Python enforces it, and strict types a checker can read.
  - [refactoring/](docs/engineering/refactoring/) — how old code reaches a practice without a rewrite of the repository.
  - [file-structure/](docs/engineering/file-structure/) — where code lives in an application, and file names that say what a file holds.
  - [logging/](docs/engineering/logging/) — how a Python application logs through the standard logger.
  - [readability/](docs/engineering/readability/) — how one function or class reads.
  - [static-checks/](docs/engineering/static-checks/) — the formatter, the linter, a strict type checker and import contracts, run the same way in hooks and in CI.
  - [prompt-engineering/](docs/engineering/prompt-engineering/) — the prompts that application code sends to a language model, and the call that carries them.
  - [testing/](docs/engineering/testing/) — which code earns a test, and how a pytest suite is laid out and written.
  - [evals/](docs/engineering/evals/) — how to check what a language model does in an application: real calls on real cases, judges checked against people's labels, pass rules over repeated runs, agents and RAG.
- `docs/claude-code/` — how I set up and instruct Claude Code. So far: [claude-md.md](docs/claude-code/claude-md.md).
- `docs/artifacts/` — working files a session writes (plans, reports, research runs). Git-ignored: not part of the library.
- `skills/` — Claude Code skills to read and copy. None yet: `pr/` and `commit/` are planned. Nothing in this folder is loaded automatically.
- `claude-config/` — my global Claude Code configuration (`~/.claude/`), one folder per module; each module's `README.md` shows what it does and links to its install guide. So far: [statusline/](claude-config/statusline/).
- `CLAUDE.local.md` — an example of the practices section of a project `CLAUDE.md`, for a repository that copies `docs/engineering/` in. The rule file this repo itself runs on is local and not committed.

## Conventions

- All content is in English.
- One topic per file, named by the topic (for example `code-review.md`). A topic with examples becomes a folder named by the topic, with a `README.md` map. Under `docs/engineering/` a practice is always a folder.
- Every `README.md` with two or more `##` sections, and every long rules file or guide a reader consults section by section, opens with a **Navigation** block of links to its sections. [git.md](docs/engineering/git/git.md) section 9 says which files get one and which do not.
- Every name in the examples is fictional: companies, people, tickets, domains.
- A good example follows every practice that governs what it shows. [docs/engineering/CLAUDE.md](docs/engineering/CLAUDE.md) holds the rules for good and bad examples.

## Where to get help

- A question, or a mistake in a practice: open an issue. Name the file and the section, and quote the line.
- A security problem in `claude-config/`: never describe it in an issue. See [SECURITY.md](SECURITY.md).

## Maintainers and contributing

I maintain this library alone, and the practices say how I work. Issues are welcome. Pull requests are open to collaborators only: when I agree with an issue, I change the text myself, in the library's style. [CONTRIBUTING.md](CONTRIBUTING.md) says what a useful issue holds.

## License

- Text, documentation and images, except the code below: © 2026 a6m1n and the collaborators whose commits are in the history, under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/), see [LICENSE](LICENSE). You can use, change, and share it, including commercially. When you share it, credit the author, link the license, and say if you changed it.
- Code: © 2026 The my-claude-best authors (the author and every collaborator whose commit is in the history), under the [MIT License](LICENSE-CODE). It covers the scripts in `claude-config/` and every fenced block in the repository's Markdown files, such as the one-paste prompt in `install.md` and the `CLAUDE.md` section in `CLAUDE.local.md`. Keep its copyright and permission notice in copies or substantial portions of the code.

Please credit as: "a6m1n, my-claude-best, https://github.com/a6m1n/my-claude-best".
