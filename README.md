# my-claude-best

My personal collection of engineering best practices: how I set up projects, write and review code, and work with AI coding agents. Almost everything here is Markdown. The exception is `claude-config/`: my Claude Code configuration, as files you copy to your own machine. There is nothing to build.

**Navigation**

- [Layout](#layout)
- [Conventions](#conventions)
- [License](#license)

## Layout

- `docs/engineering/` — engineering practices, one folder per topic, each with a `README.md` map, a rules file and examples; `docs/engineering/CLAUDE.md` is the contract for writing one. Start with [git/](docs/engineering/git/): branches, commits, pull requests, merging, and what never happens to shared history. Then [python/](docs/engineering/python/): where a constraint belongs, and what in Python actually enforces one. Then [refactoring/](docs/engineering/refactoring/): how old code reaches a practice — new, touched and untouched code, a sweep or step by step, and a migration that has an end. Then [file-structure/](docs/engineering/file-structure/): where code lives in an application — adapters, modules and `core/` with one import direction, one shape for every module, file names that say what the file holds, and the moves by which the tree grows. Then [logging/](docs/engineering/logging/): how a Python application logs through the standard logger — one config per process, a constant message with fields, five levels with narrow meanings, each exception logged once, request, dialogue and trace ids on every line, and no prompts or secrets in the log, with FastAPI and LangChain cases. Then [readability/](docs/engineering/readability/): how one function or class reads — one job and a name that says it, the main path flat under guard clauses, comments that give reasons, blank lines between stages, every input and every object it calls in the signature, and names from the business.
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

## License

© 2026 a6m1n. This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See [LICENSE](LICENSE). You can use, change, and share it, including commercially, as long as you credit the author.

Please credit as: "a6m1n, my-claude-best, https://github.com/a6m1n/my-claude-best".
