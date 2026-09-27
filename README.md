# my-claude-best

My personal collection of engineering best practices: how I set up projects, write and review code, and work with AI coding agents. Everything here is Markdown. There is nothing to build or run.

- [Layout](#layout)
- [Conventions](#conventions)
- [License](#license)

## Layout

- `docs/engineering/` — engineering practices, one folder per topic, each with a `README.md` map, a rules file and examples; `docs/engineering/CLAUDE.md` is the contract for writing one. Start with [git/](docs/engineering/git/): branches, commits, pull requests, merging, and what never happens to shared history. Then [python/](docs/engineering/python/): where a constraint belongs, and what in Python actually enforces one. Then [refactoring/](docs/engineering/refactoring/): how old code reaches a practice — new, touched and untouched code, a sweep or step by step, and a migration that has an end. Then [file-structure/](docs/engineering/file-structure/): where code lives in an application — adapters, modules and `core/` with one import direction, one shape for every module, file names that say what the file holds, and the moves by which the tree grows.
- `docs/claude-code/` — how I set up and instruct Claude Code. So far: [claude-md.md](docs/claude-code/claude-md.md), which says what belongs in a `CLAUDE.md` and what does not.
- `docs/artifacts/` — working files a session writes (plans, reports, research runs). Git-ignored: not part of the library.
- `skills/` — Claude Code skills, kept here to read and copy. Nothing in this folder is loaded automatically.
- `CLAUDE.local.md` — an example of the practices section of a project `CLAUDE.md`, for a repository that copies `docs/engineering/` in. The rule file this repo itself runs on is local and not committed.

## Conventions

- All content is in English.
- One topic per file, named by the topic (for example `code-review.md`). A topic with examples becomes a folder named by the topic, with a `README.md` map. Under `docs/engineering/` a practice is always a folder.
- Every `README.md` with two or more sections opens with a list of links to them, so a reader clicks a line and lands on that section. [git.md](docs/engineering/git/git.md) section 9 has the rule.
- Every name in the examples is fictional: companies, people, tickets, domains.

## License

© 2026 a6m1n. This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See [LICENSE](LICENSE). You can use, change, and share it, including commercially, as long as you credit the author.

Please credit as: "a6m1n, my-claude-best, https://github.com/a6m1n/my-claude-best".
