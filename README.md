# my-claude-best

My personal collection of engineering best practices: how I set up projects, write and review code, and work with AI coding agents. Almost everything here is Markdown. The exception is `claude-config/`: my Claude Code configuration, as files you copy to your own machine. There is nothing to build.

**Navigation**

- [Layout](#layout)
- [Conventions](#conventions)
- [Where to get help](#where-to-get-help)
- [Maintainers and contributing](#maintainers-and-contributing)
- [License](#license)

## Layout

- `docs/engineering/` — engineering practices, one folder per topic, each with a `README.md` map, a rules file and examples; `docs/engineering/CLAUDE.md` is the contract for writing one. Start with [git/](docs/engineering/git/): branches, commits, pull requests, merging, and what never happens to shared history. Then [python/](docs/engineering/python/): where a constraint belongs, what in Python actually enforces one, and strict types a checker can read, with no closed set of values left a bare string. Then [refactoring/](docs/engineering/refactoring/): how old code reaches a practice — new, touched and untouched code, a sweep or step by step, and a migration that has an end. Then [file-structure/](docs/engineering/file-structure/): where code lives in an application — adapters, modules and `core/` with one import direction, one shape for every module, file names that say what the file holds, and the moves by which the tree grows. Then [logging/](docs/engineering/logging/): how a Python application logs through the standard logger — one config per process, a constant message with fields, five levels with narrow meanings, each exception logged once, request, dialogue and trace ids on every line, and no prompts or secrets in the log, with FastAPI and LangChain cases. Then [readability/](docs/engineering/readability/): how one function or class reads — one job and a name that says it, the main path flat under guard clauses, comments that give reasons, blank lines between stages, every input and every object it calls in the signature, and names from the business. Then [static-checks/](docs/engineering/static-checks/): how a Python repository runs its formatter, linter, strict type checker and import contracts — one locked version per tool, light pre-commit hooks, and CI as the gate.
- `docs/claude-code/` — how I set up and instruct Claude Code. So far: [claude-md.md](docs/claude-code/claude-md.md), which says what belongs in a `CLAUDE.md` and what does not.
- `docs/artifacts/` — working files a session writes (plans, reports, research runs). Git-ignored: not part of the library.
- `skills/` — Claude Code skills, kept here to read and copy. Nothing in this folder is loaded automatically.
- `claude-config/` — my global Claude Code configuration (`~/.claude/`), one folder per module; each module's `README.md` shows what it does and links to its install guide. So far: [statusline/](claude-config/statusline/), a status line for context, usage limits, the prompt cache and the agent panel.
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
