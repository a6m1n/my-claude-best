# File structure rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. The shape: three kinds of folder, one direction](#2-the-shape-three-kinds-of-folder-one-direction)
- [3. A module folder: one file per role](#3-a-module-folder-one-file-per-role)
- [4. `core/`: code every module may use](#4-core-code-every-module-may-use)
- [5. Adapters: one folder per way in](#5-adapters-one-folder-per-way-in)
- [6. How the tree grows: six moves](#6-how-the-tree-grows-six-moves)
- [7. Names: the file name says what it holds](#7-names-the-file-name-says-what-it-holds)
- [8. Tests](#8-tests)
- [9. The repository root](#9-the-repository-root)
- [10. The map: kinds and rules, not a file list](#10-the-map-kinds-and-rules-not-a-file-list)
- [11. Check the direction with a tool](#11-check-the-direction-with-a-tool)
- [12. Where it stops holding](#12-where-it-stops-holding)
- [13. Sources](#13-sources)

## 1. Purpose and the one rule

This file is for everyone who adds a file or a folder to an application: people and AI agents
alike. Read it before you create a file, a folder or a module, or move code from one folder to
another.

It is about where code lives and what its files are called, not about how the code inside a file
works. It decides three things: the folders, the one import direction those folders encode (a
folder's place in that direction tells you what may go in it), and the names of the files. The
examples and the tools are Python. The three kinds of folder, the import direction, absolute
imports, one role per file and the six moves hold in any language; the file-name forms of section
7, the empty `__init__.py` of move 2, the `src/` layout and the tools, ruff's `TID252` check
included, are the Python case.

The one rule: **a reader finds code by its path, without opening a file.** The path says which
feature the code serves and what kind of code it is: `<domain>/<module>/schemas.py` holds the data
of one module and nothing else. Three things follow. Every module has the same shape. Every file
holds one kind of thing, and its name says which. And the tree grows by a few fixed moves
(section 6), never by improvising a new place.

Why it matters:

- A reader, human or agent, loads only the files a task needs. When a file mixes constants, data
  models and logic, the reader loads all three to change one. When the name says `utils.py`, the
  reader opens it to find out.
- People copy what they see. "Engineers tend to use existing code as examples when writing new
  code" (*Software Engineering at Google*, ch. 22), and agents do the same. A tree with one shape
  teaches that shape; a tree with three shapes teaches all three.
- A fixed shape makes the next file an easy call. Where the rules already say where a prompt, a
  query or an error type goes, nobody invents a fourth place for it.

In this file a **module** is one feature folder, `<domain>/<module>/`: one thing a caller asks
the application to do. Its name is unique in the application. A Python `.py` file is called a
file.

**Cut modules by what the caller asks for, not by the nouns in the database.** "Approve an
invoice" (`<domain>/approve_invoice/`) and "export the ledger" (`<domain>/export_ledger/`) are
modules; `invoices/` and `users/` as folders for everything that touches a table are not. Derek
Comartin names the failure: "When you focus on entities, you risk creating unnecessary coupling"
(*Screaming Architecture: Not Driven by Entities*, 2025). A module built around a table ends up
holding every workflow that reads it, and those workflows change for different reasons.

## 2. The shape: three kinds of folder, one direction

The application package holds three kinds of folder:

```
src/<app>/
├── core/          # code every module may use; knows no module and no adapter
├── <domain>/      # the modules of one business area, named for the area
│   └── <module>/
└── api/           # one folder per way in: HTTP, a command line, a queue consumer
```

| Folder | Holds | Imports |
|---|---|---|
| `core/` | settings, logging, shared errors and types, one client class per external system | only libraries |
| `<domain>/<module>/` | one feature: its entry point, its data, its doers | `core/` and libraries; never another module, never an adapter |
| an adapter (`api/`, `cli/`) | turns a request into a call to one `usecase.py` and the result back into a response | modules, `core/`, its own framework; never another adapter |

Imports point one way: adapters → modules → core. Nothing points back.

- **The domain folder is named for what the application does**, never `modules/`, `features/`
  or `app/`. Robert C. Martin's test for the top of a tree: "Architectures should tell readers
  about the system, not about the frameworks you used in your system" (*Screaming Architecture*,
  2011). An application that does two unrelated kinds of work has two domain folders; one that does
  one kind has one.
- **The framework stays in its adapter.** No module and nothing in `core/` imports the web
  framework, the CLI framework or any other adapter's framework. Alistair Cockburn's reason is the whole point:
  the application should be driven "equally ... by users, programs, automated test or batch
  scripts, and ... developed and tested in isolation from its eventual run-time devices and
  databases" (*Hexagonal Architecture*, 2005). A module that needs a request object has taken
  transport work that belongs in the adapter.
- **Modules do not import each other.** Jimmy Bogard's rule for feature slices is "Minimize
  coupling between slices, and maximize coupling in a slice" (*Vertical Slice Architecture*,
  2018). A second module that needs the same code gets it from `core/` or its own copy (section
  6, move 3). A module that must call another does it through the other's `usecase.py`, and the
  import is listed as a named exception in the contract (section 11), so a reviewer sees each one.

Check: `lint-imports` passes in CI (section 11).

## 3. A module folder: one file per role

Every module has the same set of role files. Create a file only when the module has something of
that kind; never an empty placeholder kept for symmetry.

| File | Holds | Never holds |
|---|---|---|
| `usecase.py` | the one entry point the adapters call: it holds the business `if` and the calls to the services, the repository and the clients it is handed, and returns the module's result ([python.md](../python/python.md) section 2) | a business rule, a query, prompt text, a framework type |
| `schemas.py` | only when the module has data of its own: its input, its result, the shapes its services pass | logic |
| `consts.py` | only when the module has named values: model names, trace names, a limit only this module has | logic; a value one service tunes or one rule reads (that sits next to its logic) |
| `services/` | the doers, one per file: one call to an external system with the code that prepares it or reads its answer, or one computation; whether a call is worth a doer of its own is [python.md](../python/python.md) section 2, condition 5 | a second doer |
| `errors.py` | only when the module raises an error of its own | anything else |
| `validation.py` | only when raw input is checked before it is decoded | anything past that check |
| `models.py` | only when the module stores data: its tables | queries |
| `repository.py` | only when the module reads or writes stored data: one function per query | a business rule |
| `prompts.py` | only when the module calls a language model: its prompt texts | code that sends it |
| `<role>.py` | any other role, named for what it holds: `<name>_format.py`, `<name>_rules.py`; a business rule sits in such a file with the threshold it reads | a second role |

- **A file holds one kind of thing, even in a small module.** Constants, data models and logic never
  share a file, also when the module has one caller today; the one exception is a value one service
  tunes or one rule reads, which sits next to that logic (next bullet). The split costs one import.
  A mixed file costs every reader the parts they did not come for.
- **A constant lives next to the one thing that changes it.** A value one service tunes or one rule
  reads sits in that file, next to its logic. A value the use case reads, and any other named value
  of the whole module, sits in the module's `consts.py`. A limit every module obeys sits in
  `core/consts.py`. A model name changes when the provider retires the model; a
  threshold changes when the business changes its rule. Different reasons to change, different
  files.
- **A subfolder inside a module is for a different reason to change**, such as the wiring of a
  pipeline, never for grouping files by topic. Files that are all doers belong in `services/`.
- **Role folders live inside a module, never at the top.** A top-level `services/` or `schemas/` for
  the whole application is package-by-layer, which Angular's current style guide also warns against
  ("avoid creating directories like `components`, `directives`, and `services`"). A `services/`
  folder inside one module holds that module's doers and nothing else.

Check: for every file, "this file holds only ___" has one answer, and the file name gives it.

## 4. `core/`: code every module may use

`core/` holds code that no module owns and every module may use:

- settings, read from the environment once (`config.py`);
- logging setup;
- the base error that every adapter maps, and errors every module raises;
- types two or more modules use (`schemas.py`), and limits every module obeys (`consts.py`);
- **data two or more modules share**: a table both modules read or write (`models.py`), named for
  what it holds and split by move 2 when it grows. The queries stay in each module's own
  `repository.py`.
- **one client per external system** (`<system>_client.py`, `database.py`), from the first module
  on: the class every call to that system goes through, so timeouts, retries, tracing and spend
  limits are written once. A second path to the same system is a bug waiting for the day the first
  one gains a limit. One instance is built at startup by the adapter (section 5) and handed in as a
  parameter ([python.md](../python/python.md) section 2).

Rules:

- `core/` imports no module and no adapter.
- **Code moves into `core/` when a second module needs it and no single module owns it**: it
  carries the knowledge of neither, or, like a shared table, of both alike. Not before: a type used
  by one module lives in that module, even when it looks general. The clients above are the
  exception: each sits in `core/` from the first module on.
- `core/` grows by the same moves as a module: a file that holds several clients becomes
  `core/clients/`, one file per client (section 6, move 2).

## 5. Adapters: one folder per way in

Each way into the application is a folder: `api/` for HTTP, `cli/` for a command line, one for a
queue consumer or a scheduled job. An adapter decodes the input, calls one `usecase.py`, encodes the
result and maps errors to its own protocol. It holds no business rule. Cosmic Python puts it in one
line: the endpoints' "only responsibility is doing 'web stuff,' such as parsing JSON and producing
the right HTTP codes" (Percival and Gregory, *Architecture Patterns with Python*, ch. 4).

An adapter folder holds:

- `main.py`, the process entry point, and the file that builds the app and one instance of each
  client, once, and wires its parts (`app.py`, `server.py`, or `main.py` itself in a command-line
  adapter);
- **one file per module it offers**, named for the role and the module: `routes_<module>.py`,
  `commands_<module>.py`, `handlers_<module>.py`;
- its own `schemas.py` (request bodies, the error envelope) and `errors.py` (module error → status
  code, exit code or protocol error).

Rules:

- Adapters never import each other. Each can be deleted without touching the others.
- **One process that runs two adapters is started by one file above them**, `src/<app>/main.py`.
  An HTTP server that also runs a queue consumer in the same process has to import both; that
  file is the only one that does, and it holds wiring only. It sits outside every layer of the
  contract (section 11), so the rule that adapters never import each other still holds for every
  file inside them.
- When two adapters must return the same public shape, the shape lives in one file both import,
  named for the role (`contract.py`), never copied into each.
- A new way in is a new folder. No module changes for it.
- **Name a top-level package so it does not hide a library.** Python puts the directory of the
  running script first on the import path, so "scripts in that directory will be loaded instead of
  modules of the same name in the library directory" (Python tutorial, § The Module Search Path).
  A folder `email/` at the repository root hides the standard library's `email` package;
  `src/<app>/email/`, imported as `<app>.email`, does not.

## 6. How the tree grows: six moves

The tree is never drawn in one go. It starts with `core/`, one domain folder, one module and one
adapter. Every change that needs more makes one of these moves. Moves 2 and 3 change where
existing code lives, so they land as a refactoring before the change that needed them
([refactoring.md](../refactoring/refactoring.md) section 3); the other moves add new code and land
with the change that needs them.

1. **A new feature → a new module.** A new folder in the shape of section 3, one file in each
   adapter that offers it, and `tests/unit/<module>/` for its tests (section 8). Nothing in the other
   modules changes, and neither does the map (section 10).
2. **A file stops telling what is inside → it becomes a folder of the same name.** The moment is
   a file that has grown hard to follow: too much code, and a name that no longer says what is
   inside. The test is the name, not a line count: a file that holds several things a reader looks
   for one at a time, such as three prompts in `prompts.py`, no longer tells which one is where.
   Django's docs give the same trigger for models: "If you have many models, organizing them in
   separate files may be useful." Then:
   - the file becomes a folder with the same name in the same place: `prompts.py` → `prompts/`;
   - each part gets its own file, named for the role in the singular and then for what this part
     holds: `prompts/prompt_<name>.py`, `schemas/schema_<name>.py`;
   - `__init__.py` stays empty and the imports change in the same commit, so each part has one
     import path. The exception is a framework that needs the re-export, as Django's model registry
     does. Even then the re-export is an absolute import
     (`from <app>.<domain>.<module>.models.model_<name> import <Name>`); only the non-empty
     `__init__.py` is the exception, never a relative import.

   Split only into parts a reader looks for one at a time. Two functions that are always read
   together stay in one file: a folder of one-function files makes the reader "flip back and forth
   between the implementations" (John Ousterhout, in his 2024–2025 debate with Robert C. Martin), and
   the Zen of Python's "Flat is better than nested" still holds. The test is the name: if each new
   file gets a name that says what it holds, the split was right; if the names come out as
   `part_1.py` and `part_2.py`, it was not.
3. **A second module needs the same code → it moves down, or it is copied.** Code with no knowledge
   of either module moves to `core/`. Code that is one module's knowledge stays there; a small
   pure function may be copied into the second module instead. Data both modules use, such as a
   table, moves to `core/` as well, and each module keeps its own queries in its `repository.py`.
   Two copies of a five-line function cost less than a coupling between two modules. Milan
   Jovanović, writing about shared code in feature slices, names the risk on the other side: a shared folder "inevitably becomes a junk
   drawer" when everything two slices touch is moved into it (2025).
4. **A new kind of file → a file named for its role.** Something that fits no row of section 3 gets a
   file named for what it holds, never `utils.py`. When the role will recur in other modules, the map
   gains a row in the same commit.
5. **A new way in → a new adapter folder**, with one file per module it offers. No module changes.
6. **A second business area → a second domain folder** next to the first, with its own modules. Not
   before the application really does a second kind of work: one area, one folder. The same commit
   updates the contracts (section 11): both domain folders go in the middle layer as siblings
   joined by `:`, and the independence contract lists the modules of both, so a call from a module
   in one area to a module in the other is one more named exception there. Module names stay
   unique across the application: the second area names its modules so they do not clash with the
   first, and adapter files (`routes_<module>.py`) and test folders (`tests/unit/<module>/`) stay
   flat.

Check: a structural move (2 or 3) lands in its own commit, with no change in behavior
([refactoring.md](../refactoring/refactoring.md) section 3). The diff of a new module adds files
and touches no other module.

## 7. Names: the file name says what it holds

- **Never `utils`, `helpers`, `common`, `misc`, `base`, `shared` or `manager`**, as a file or a
  folder. The Go team's reason holds for any language: "Packages named util, common, or misc provide
  clients with no sense of what the package contains" (Sameer Ajmani, *Package names*, 2015). Such a
  file becomes the place for every function nobody knew where to put. Jonathan Hall's answer is the
  practical one: "Give each package/class its own meaningful name. Even if it only contains a 2-line
  helper function" (*Junk drawer*, 2022). Good projects do ship `utils` files: the widely copied
  FastAPI best-practices guide, which otherwise organises by module much as this practice does, puts
  a `utils.py` in every module. This practice departs from it there, so the rule is a choice, not a
  law of nature. Django shows the way out even there: `django.utils` is a folder of
  files named for their role (`text`, `timezone`, `http`), never one `utils.py`. A generic helper
  with no module to own it goes to `core/` under a name that says what it does.
- **The role comes first, then which one.** A file in a role folder, or a file that serves one module
  in an adapter, starts with its role: `prompt_<name>.py`, `service_<name>.py`,
  `routes_<module>.py`, `test_<unit>.py`. The role is singular when the file holds one thing
  (`prompt_`) and plural when it holds several (`routes_`). Python already reads names this way:
  pytest collects `test_*.py`, and Django's docs split a grown `tests.py` into a `tests/` folder of
  `test_models.py` and `test_views.py`, the role in the folder and again in each file. The reason is
  the moments when a file is seen without its folder: an editor tab, a fuzzy file search, a grep
  hit, a log line (`logging`'s `%(filename)s` prints the file name alone). Angular's old style guide
  gave the same reason for its type suffixes: "Type names provide a consistent way to quickly
  identify what is in the file."

  The role goes in the file name once. Names inside the file do not repeat it:
  `service_totals_check.py` holds `check_totals()`, not `TotalsCheckService`, and
  `prompt_<name>.py` holds `SYSTEM` and `USER`, not `<NAME>_PROMPT_SYSTEM`. Go's style guide calls the
  repetition noise, because "the package name, ... import path, and even filename can all provide
  context that automatically qualifies all names". The import line still carries the role twice
  (`<module>.prompts.prompt_<name>`). That is the price of a file name that stands on its own, and it
  is a known one: Angular dropped its type suffixes in 2025 because they made the framework "feel
  cumbersome and boilerplate-y". This practice pays it, because here the name is what a reader sees
  first.
- **The same role has the same name in every module.** `schemas.py` is always the schemas. A reader
  who knows one module can find their way in all of them.
- File and folder names are `lower_with_under` (Google Python Style Guide) and state one job: a name
  you could not finish with "this file holds only ___" is not done.
- **Imports are always absolute, never relative**: `from <app>.<domain>.<module>.schemas import
  <Name>`, never `from .schemas import <Name>` or `from ..core import config`. An absolute import
  names the file's place in the tree, so the import line alone tells a reader, a search and a
  reviewer which module and which role the name comes from. It also keeps section 6 honest: when a
  file becomes a folder, every import of it shows up in the diff. PEP 8 recommends absolute imports
  but still allows relative ones; this practice takes the stricter line of the Google Python Style
  Guide: "Do not use relative names in imports. Even if the module is in the same package, use the
  full package name. This helps prevent unintentionally importing a package twice." It takes only
  that part: the same guide also asks you to import modules rather than names, which this practice
  leaves to the project.

  Check: ruff's `TID252` rule with `ban-relative-imports = "all"` fails the build on any relative
  import. The rule is not on by default, so `pyproject.toml` selects it
  ([layout-example.md](layout-example.md) section 3).

## 8. Tests

```
tests/
├── conftest.py        # applies the suite marker by folder; fixtures every suite uses
├── unit/              # offline and fast: the default run and CI
│   └── <module>/      # one folder per module
├── integration/       # real database, real provider: run on demand
│   └── <subject>/     # a subject that needs its own harness gets a folder in its suite
└── support/           # test tooling shared by the suites; no test files
```

- **Tests live outside the application package**, in `tests/` at the repository root. The pytest
  docs call keeping them apart "often a good idea", and with the src layout (section 9) the tests
  import the installed package, not the working copy.
- **One folder per suite, by what it needs to run**: `unit/` needs nothing outside the process and
  runs on every push; `integration/` needs a real database or a real provider and runs on demand.
  Add `e2e/` when a suite drives the running application from the outside. The folder names are the
  common ones, but the line between them is what the test touches, not a definition of "unit":
  Martin Fowler calls those terms "rather murky" (*On the Diverse And Fantastical Shapes of
  Testing*, 2021). A new test file goes into a suite folder, never directly under `tests/`.
- **Tests are grouped by suite, not placed inside the modules**, so CI picks a suite by its folder
  and a module folder holds only the code that ships. Keeping tests next to the code they test is a
  respected alternative (the HackSoft Django Styleguide puts `tests/` in each app; Kent C. Dodds
  argues for colocation); a framework that expects it, as Django's `startapp` does, keeps it.
- **The suite folder applies the marker.** A hook in `tests/conftest.py` marks every test by the
  folder it sits in, so nobody writes a suite marker by hand and none is forgotten.
- **`support/` holds fakes and builders that more than one suite uses**, laid out by the same role
  rules as a module. It has no `test_` files, so nothing in it is collected. Tests reach it through
  fixtures in `tests/conftest.py`, which pytest finds by itself: under `--import-mode=importlib` a
  test cannot import another module from `tests/` directly, and the pytest docs say fixtures
  "should be placed in `conftest.py` files".
- **Name a test file for the unit or the flow it pins**: `test_<unit>.py`. Run pytest with
  `--import-mode=importlib`, which the pytest docs recommend for new projects: two test files with
  the same name in different folders then do not collide.
- **Unit tests have one folder per module**: `tests/unit/<module>/test_<unit>.py`. A new module gets
  its test folder in the same commit (section 6, move 1). A reader who knows the module finds its
  tests by path, and two modules can each have a `test_usecase.py`, which a flat folder cannot hold.
  Home Assistant's developer docs make this the rule for thousands of test files: "Tests for each
  integration are stored inside a directory named after the integration domain"; PyPI's Warehouse
  mirrors its packages the same way in a `tests/unit/` of about two hundred files. Stop at the
  module: a deeper mirror doubles every rename inside the package.

## 9. The repository root

```
<repo>/
├── src/<app>/          # the application package
├── tests/
├── docs/
│   ├── ARCHITECTURE.md # the map (section 10)
│   └── guides/         # for people who call or run the application
├── migrations/         # only with a database: one file per schema change
├── scripts/            # run by hand; the application never imports them
├── .github/workflows/
├── .env.example        # every setting, no real value
├── Dockerfile
├── pyproject.toml
├── <lockfile>
├── CLAUDE.md
└── README.md
```

- **Put the package under `src/`.** The Python Packaging User Guide: "The src layout helps prevent
  accidental usage of the in-development copy of the code". With the package at the root, Python
  imports the working copy from the current directory, and tests can pass against code that the
  installed package does not contain. Hynek Schlawack's summary: without `src/`, "your tests do not
  run against the package as it will be installed by its users" (*Testing & Packaging*, 2021).
  The cost is real and small: "The src layout requires installation of the project to be able to run
  its code" (the same guide), so the project is installed into its environment before anything runs.
  `uv sync` does that, and since uv 0.12 (July 2026) `uv init` lays out an application this way by
  default.
- **The root holds only the files a tool or a person looks for there**: the build and lock files,
  the container files, the CI config, the agent instruction file, `README.md`, `.env.example`, and the
  top folders above. Never a `.env` with real values, never a loose script.
- **`scripts/` is for commands a person runs by hand**: seed data, a one-off upload. The application
  never imports from it; code both need lives in the package.

## 10. The map: kinds and rules, not a file list

Every application has one map of its structure, in `docs/ARCHITECTURE.md` under "Package map". It
shows the tree down to the role files of one module and puts one comment on each kind: what it is
for, and what must hold for every one of that kind. Names in it are placeholders: `<module>`,
`<name>`, never a real module.

- **The map never lists the instances.** `ls src/<app>/<domain>` lists the modules and `ls` inside a
  module lists its files. The map holds what `ls` cannot tell: what each kind of file is for and what
  it may not do.
- **It changes when a kind changes, not when a file is added.** Adding a module or a service changes
  nothing in the map. A new kind of file, a new adapter kind or a new rule adds a line.
- **It ends with "I want to…" lines** that route the common changes: add a module, add a way in,
  change how errors map to status codes. Each names the files to touch.

[package-map-example.md](package-map-example.md) is the map for the tree in
[layout-example.md](layout-example.md).

Check: `git show --stat <commit>` of a commit that adds a module or a file does not list
`docs/ARCHITECTURE.md`; of a commit that adds a kind, it does.

## 11. Check the direction with a tool

A rule about imports that nothing checks is a wish. Python has no package-private names, so a
folder boundary means nothing to the interpreter: any file can import any other. Simon Brown makes
the same point about Java: "the packages become an irrelevant detail if all of the types are marked
as public". Write the direction of section 2 as import-linter contracts in `pyproject.toml`, and run
`lint-imports` as [static-checks.md](../static-checks/static-checks.md) section 5 says, so the
build fails on a broken contract:

- a **layers** contract: adapters, then the domain folder, then `core/`;
- an **independence** contract over the modules, with each allowed cross-module import listed under
  `ignore_imports`;
- a **forbidden** contract that keeps the frameworks out of the modules and `core/`.

[layout-example.md](layout-example.md) section 3 has the contracts. import-linter reads the
`import` statements in the source, including those inside functions. It cannot see an import built
from a string at run time (`importlib.import_module`, a plugin entry point); the rule still holds
there, and review is what checks it.

## 12. Where it stops holding

- **A script or a one-module tool.** Below two modules, the three kinds of folder are ceremony. Start
  with one package and its role files; move to this shape at the second module.
- **An application with one workflow and deep technical layers.** Well-known Python examples put
  layers at the top: Cosmic Python's `adapters/`, `domain/`, `service_layer/`, and the official
  FastAPI full-stack template's `api/`, `core/`, `crud.py`, `models.py`. That works while the
  application does one thing. When a second workflow arrives, its files spread across every layer
  folder; that is the moment to move to modules.
- **A library.** Its folders are its public API, and users import them by path. This practice is for
  applications and services, which nobody imports.
- **A framework with its own layout.** Django apps, for example, already are modules; keep the
  framework's names for what it owns and apply these rules to the rest.
- **Another language.** The shape carries over, absolute imports included; the mechanics do not. In Go every folder is a
  package and test files must end in `_test.go`; NestJS names TypeScript files
  `<name>.controller.ts`. Keep the three kinds of folder, the direction, absolute imports, one role
  per file and the moves, and take the language's own file names and its own check for imports.

## 13. Sources

- Robert C. Martin, "Screaming Architecture", 2011:
  https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html
- Alistair Cockburn, "Hexagonal architecture", 2005: https://alistair.cockburn.us/hexagonal-architecture/
- Jimmy Bogard, "Vertical Slice Architecture", 2018:
  https://www.jimmybogard.com/vertical-slice-architecture/
- Simon Brown, "Package by component": https://simonbrown.je/modular-monolith/
- Harry Percival and Bob Gregory, *Architecture Patterns with Python*, ch. 4 and appendix B:
  https://www.cosmicpython.com/book/chapter_04_service_layer.html
- Sameer Ajmani, "Package names", Go blog, 2015: https://go.dev/blog/package-names
- Jonathan Hall, "Junk drawer", 2022: https://jhall.io/archive/2022/10/04/junk-drawer/
- Django docs, "Organizing models in a package":
  https://docs.djangoproject.com/en/stable/topics/db/models/#organizing-models-in-a-package
- Python Packaging User Guide, "src layout vs flat layout":
  https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- Hynek Schlawack, "Testing & Packaging", 2021: https://hynek.me/articles/testing-packaging/
- pytest docs, "Good Integration Practices": https://docs.pytest.org/en/stable/explanation/goodpractices.html
- Python tutorial, "The Module Search Path":
  https://docs.python.org/3/tutorial/modules.html#the-module-search-path
- import-linter docs: https://import-linter.readthedocs.io/en/stable/
- Titus Winters, Tom Manshreck and Hyrum Wright, *Software Engineering at Google*, ch. 22.
- Derek Comartin, "Screaming Architecture: Not Driven by Entities", 2025:
  https://codeopinion.com/screaming-architecture-not-driven-by-entities/
- John Ousterhout and Robert C. Martin, "A Philosophy of Software Design vs Clean Code", 2024–2025:
  https://github.com/johnousterhout/aposd-vs-clean-code
- Tim Peters, PEP 20, "The Zen of Python": https://peps.python.org/pep-0020/
- PEP 8, § Imports: https://peps.python.org/pep-0008/#imports
- Google Python Style Guide, § 2.2 Imports and § 3.16 Naming:
  https://google.github.io/styleguide/pyguide.html
- Google Go Style Guide, § Repetition: https://google.github.io/styleguide/go/decisions#repetition
- Angular style guide, v17 (type names in file names, rule 02-02):
  https://raw.githubusercontent.com/angular/angular/17.3.x/aio/content/guide/styleguide.md ;
  the current guide: https://angular.dev/style-guide
- Milan Jovanović, "Vertical Slice Architecture: Where Does the Shared Logic Live?", 2025:
  https://milanjovanovic.tech/blog/vertical-slice-architecture-where-does-the-shared-logic-live
- HackSoft Django Styleguide: https://github.com/HackSoftware/Django-Styleguide
- Kent C. Dodds, "Colocation", 2019: https://kentcdodds.com/blog/colocation
- Home Assistant developer docs, "Integration tests file structure":
  https://developers.home-assistant.io/docs/creating_integration_tests_file_structure/
- PyPI Warehouse, `tests/unit/`: https://github.com/pypi/warehouse/tree/main/tests/unit
- pytest docs, "pytest import mechanisms and sys.path/PYTHONPATH":
  https://docs.pytest.org/en/stable/explanation/pythonpath.html
- Angular RFC on dropping type suffixes, 2024: https://github.com/angular/angular/discussions/58412
- zhanymkanov, "FastAPI Best Practices": https://github.com/zhanymkanov/fastapi-best-practices
- FastAPI full-stack template: https://github.com/fastapi/full-stack-fastapi-template
- Django docs, "Writing and running tests" (splitting `tests.py` into a package) and
  `django.utils`: https://docs.djangoproject.com/en/stable/topics/testing/overview/ ,
  https://docs.djangoproject.com/en/stable/ref/utils/
- Python docs, `logging` LogRecord attributes: https://docs.python.org/3/library/logging.html
- Martin Fowler, "On the Diverse And Fantastical Shapes of Testing", 2021:
  https://martinfowler.com/articles/2021-test-shapes.html
- uv docs, "Creating projects": https://docs.astral.sh/uv/concepts/projects/init/
- ruff rule `TID252` and the `ban-relative-imports` setting:
  https://docs.astral.sh/ruff/rules/relative-imports/
- Go docs, "How to Write Go Code": https://go.dev/doc/code
- NestJS docs, "First steps": https://docs.nestjs.com/first-steps
