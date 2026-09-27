# Example: the tree of a service, and how it grows

A worked example for [file-structure.md](file-structure.md). It shows the whole tree of a Python
service with an HTTP API and a command-line tool, one database and one external model provider.
Names in angle brackets are placeholders: `<app>` is the package, `<domain>` a business area,
`<module>` one feature folder, `<name>` whatever the file holds. No real module name appears,
because the shape is the point: it is the same for every module, and `ls` shows which modules a
repository has.

**Navigation**

- [1. The tree](#1-the-tree)
- [2. How a tree grows](#2-how-a-tree-grows)
- [3. The import rules, as CI runs them](#3-the-import-rules-as-ci-runs-them)

## 1. The tree

Every folder under `src/` has an `__init__.py`; the tree leaves them out. A file marked
"only when" exists in a module that needs it and nowhere else.

```
<repo>/
├── src/
│   └── <app>/
│       ├── core/                           # cross-cutting; imports no module and no adapter
│       │   ├── config.py                   # settings, read from the environment once
│       │   ├── consts.py                   # limits every module obeys: upload size, timeouts
│       │   ├── errors.py                   # the base error every adapter maps
│       │   ├── logging.py
│       │   ├── schemas.py                  # types two or more modules use
│       │   ├── database.py                 # only with a database: the one way to reach it
│       │   └── <system>_client.py          # one per external system: every call to it goes here
│       ├── <domain>/                       # the modules of one business area, named for the area
│       │   └── <module>/                   # one feature: the thing a caller asks the app to do
│       │       ├── usecase.py              # the one entry point the adapters call; composition only
│       │       ├── schemas.py              # the module's data: its input, its result
│       │       ├── consts.py               # the module's named values: model names, trace names
│       │       ├── errors.py               # only when the module raises an error of its own
│       │       ├── validation.py           # only when raw input is checked before it is decoded
│       │       ├── models.py               # only when the module stores data: its tables
│       │       ├── repository.py           # only when the module stores data: one function per query
│       │       ├── prompts.py              # only when it calls a model: its prompt texts
│       │       ├── <role>.py               # any other role, named for what it holds — never utils.py
│       │       └── services/               # the doers
│       │           └── service_<name>.py   # one external call or one computation per file
│       ├── api/                            # one folder per way in; this one is HTTP
│       │   ├── main.py                     # the process entry point
│       │   ├── app.py                      # builds the app and wires every router
│       │   ├── routes_<module>.py          # one file per module the adapter offers
│       │   ├── schemas.py                  # request bodies, the error envelope
│       │   └── errors.py                   # module error → HTTP status
│       └── cli/                            # the command-line adapter, same shape
│           ├── main.py
│           ├── commands_<module>.py
│           └── errors.py                   # module error → exit code
├── tests/
│   ├── conftest.py                         # marks every test by the suite folder it sits in
│   ├── unit/                               # offline; the default run and CI
│   │   └── <module>/                       # one folder per module, added with the module
│   │       └── test_<unit>.py
│   ├── integration/                        # real database, real provider; run on demand
│   │   ├── test_<flow>.py
│   │   └── <subject>/                      # a subject with its own harness gets a folder
│   └── support/                            # fakes and builders; tests reach them through fixtures
│       └── fake_<system>.py
├── migrations/                             # only with a database: one file per schema change
├── scripts/                                # run by hand; the app never imports them
├── docs/
│   ├── ARCHITECTURE.md                     # the package map: kinds and rules, not a file list
│   └── guides/                             # for people who call the app
├── .github/workflows/
├── .env.example                            # every setting, no real values
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── CLAUDE.md
└── README.md
```

What to notice:

- **Every name says what the file holds before it says which one.** `routes_<module>.py`,
  `commands_<module>.py`, `service_<name>.py`, `test_<unit>.py`: a file seen alone, in an editor
  tab or a search result, still tells its kind.
- **Modules share one shape, not one file list.** Every module has `usecase.py` and `schemas.py`.
  A module that stores nothing has no `models.py`; a module that calls no model has no prompts. No
  folder holds an empty file kept for symmetry.
- **`core/` has one file per external system.** Timeouts, retries, tracing and spend limits for that
  system live there once, and every service that calls it gets them.
- **The adapters hold no business rule.** Each decodes a request, calls one `usecase.py`, encodes
  the result and maps errors to its own protocol. The CLI may offer fewer modules than the API.

## 2. How a tree grows

Nobody draws the tree above on day one. A service starts with `core/`, one domain folder, one
module and one adapter, and each change that needs more makes one of the moves in
[file-structure.md](file-structure.md) section 6. Here they are in the order a young service
usually meets them.

**A second module.** A new folder next to the first, in the same shape, one `routes_<module>.py` in
`api/`, and `tests/unit/<module>/` for its tests. The second module's `test_usecase.py` sits in its
own folder, next to nothing of the first module's. Nothing in the first module changes. `docs/ARCHITECTURE.md` does
not change either: it describes `<module>`, and a new module is one more of a kind it already
describes.

**A file becomes a folder.** A module's `prompts.py` held one prompt. A second prompt arrives, and
then a third; now the file holds three things a reader looks for one at a time, and its name no
longer tells which. The change that adds the third prompt first moves the file into a folder of
the same name, in its own commit:

```
<module>/prompts.py            →   <module>/prompts/
                                   ├── __init__.py                      # empty
                                   ├── prompt_<first name>.py
                                   ├── prompt_<second name>.py
                                   └── prompt_<third name>.py
```

Each new file starts with the role, in the singular, and ends with what this one holds. The
imports change in the same commit; `__init__.py` stays empty, so each prompt has one import path.
The same move turns a `schemas.py` that grew five unrelated models into `schemas/schema_<name>.py`.

**A second module needs the same code.** A type or a helper that one module owns is needed by a
second. If it carries no knowledge of either module — a `Money` type, a retry wrapper — it moves
to `core/`, in its own commit. If it is one module's knowledge, it stays there: the second
module keeps its own copy of a small pure function, or calls the owner's `usecase.py`, never its
`services/`. A table both modules use moves to `core/`, and each module keeps its own queries.

**A new kind of file.** A module needs something that is not any role in the table — a file
format it writes, say. It gets a file named for that role, such as `<name>_format.py`, never a
`utils.py`. If the role will recur in other modules, it gets a row in the role table of
`docs/ARCHITECTURE.md` in the same commit.

**A second way in.** A new folder next to `api/`, in the same shape: one file per module it offers,
its own error map. `<domain>/` does not change: the new adapter calls the same `usecase.py` files.

**A second business area.** When the app starts doing a second kind of thing, with its own words
and its own rules, the new modules get their own folder next to the first `<domain>/`, and its
module names do not repeat those of the first area, so adapter files and `tests/unit/<module>/`
stay as they are. Until then there is one area and one folder.

## 3. The import rules, as CI runs them

The direction in [file-structure.md](file-structure.md) section 2 is written as import-linter
contracts in `pyproject.toml`. CI runs `lint-imports` and fails on a broken contract.

```toml
[tool.importlinter]
root_package = "<app>"
include_external_packages = true   # the third contract names fastapi and typer

[[tool.importlinter.contracts]]
name = "Adapters, then modules, then core"
type = "layers"
layers = [
    "<app>.api | <app>.cli",
    "<app>.<domain>",
    "<app>.core",
]

[[tool.importlinter.contracts]]
name = "Modules do not import each other"
type = "independence"
modules = ["<app>.<domain>.*"]
ignore_imports = [
    # each allowed cross-module call, one line, through the other module's usecase.py
    "<app>.<domain>.<module a>.usecase -> <app>.<domain>.<module b>.usecase",
]

[[tool.importlinter.contracts]]
name = "Modules and core stay free of web and CLI frameworks"
type = "forbidden"
source_modules = ["<app>.<domain>", "<app>.core"]
forbidden_modules = ["fastapi", "typer"]
```

The first contract puts `api` and `cli` in one layer with `|`, which also stops them from importing
each other. The second makes every module independent of the others; each exception is one line a
reviewer reads, and a new one shows up in the diff. The third keeps the frameworks at the edge: a
module that needs a request object has put transport logic in the wrong folder. It names outside
packages, so `include_external_packages = true` must be set at the top; without it import-linter
stops with an error. Name the top-level package only (`fastapi`, never `fastapi.routing`): the tool
rejects a subpackage of an outside package.

A `src/<app>/main.py` that starts both adapters in one process sits in no layer, so the layers
contract does not check it. With a second domain folder, the middle layer becomes
`"<app>.<domain> : <app>.<second domain>"` (a colon: the layers contract lets the two areas import
each other, and the independence contract over the modules of both is what checks each cross-area
call) and the independence contract lists `"<app>.<second domain>.*"` as well.

Relative imports are banned by ruff in the same file:

```toml
[tool.ruff.lint]
extend-select = ["TID252"]

[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "all"
```
