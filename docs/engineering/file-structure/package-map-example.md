# Example: the package map in `docs/ARCHITECTURE.md`

A worked example for [file-structure.md](file-structure.md) section 10: the "Package map" section
of `docs/ARCHITECTURE.md` for the service in [layout-example.md](layout-example.md). Everything
between the two rules below is what the repository's own file holds. `<app>`, `<domain>` and the
rest are placeholders in this example; a real map writes its own package and domain names and
keeps `<module>`, `<name>` and `<system>` as they are, because those stand for many instances.

---

## Package map: kinds and rules, not a file list

`ls` lists the instances: `ls src/<app>/<domain>` shows the modules, `ls` inside a module shows its
files. This map holds what `ls` cannot tell you: what each kind of file is for, and what must hold
for every one of them. Adding a module or a file changes nothing here; a new kind of file or a new
rule does.

```
src/<app>/
├── core/              # cross-cutting: config · consts (limits every module obeys) · errors (the base
│                      # error every adapter maps) · logging · schemas (types two or more modules use) ·
│                      # database · one <system>_client.py per external system, the only path to it.
│                      # Imports no module and no adapter.
├── <domain>/          # one folder per module; imports no web or CLI framework. Every module:
│   └── <module>/
│       ├── usecase.py     # the one entry point the adapters call; composition only
│       ├── schemas.py     # the module's data: its input, its result
│       ├── consts.py      # model names, trace names — never a value one service tunes
│       ├── errors.py      # only when the module raises an error of its own
│       ├── validation.py  # only when raw input is checked before it is decoded
│       ├── models.py      # only when the module stores data: its tables
│       ├── repository.py  # only when the module stores data: one function per query
│       ├── prompts.py     # only when it calls a model: its prompt texts — or prompts/, one
│       │                  # prompt_<name>.py per prompt, once the name no longer tells which
│       ├── <role>.py      # any other role, named for what it holds — never utils.py
│       └── services/      # the doers — one service_<name>.py per external call or computation;
│                          # a value a service tunes lives in its file, next to the logic
├── api/               # HTTP adapter: main · app (wires every router) · one routes_<module>.py per
│                      # module · schemas (request bodies, the error envelope) · errors (the status map)
└── cli/               # command-line adapter: main · one commands_<module>.py per module it offers ·
                       # errors (the exit-code map)
```

## Rules

1. Imports point one way: `api/` and `cli/` → `<domain>/` → `core/`. `lint-imports` checks it in
   CI; the contracts are in `pyproject.toml`.
2. Modules do not import each other. The allowed exceptions are listed under `ignore_imports` in
   the independence contract, each going through the other module's `usecase.py`.
3. `api/` and `cli/` never import each other.
4. Nothing under `<domain>/` or `core/` imports `fastapi` or `typer`.
5. Every call to an external system goes through its file in `core/`.

## I want to…

- **Add a module** → a new `<domain>/<module>/` in the shape above; `api/routes_<module>.py`, wired
  into `api/app.py`; `cli/commands_<module>.py` only if the CLI offers it; `tests/unit/<module>/`
  for its tests.
- **Split a file whose name no longer tells which part a reader wants** → turn it into a folder of
  the same name, one `<role>_<name>.py` per part, empty `__init__.py`, imports changed in the same
  commit
  ([file-structure.md](file-structure.md) section 6, move 2).
- **Share code between two modules** → no knowledge of either module, or a table both use: move
  it to `core/`; one module's knowledge: copy a small pure function, or call that module's
  `usecase.py` and add the import to `ignore_imports`.
- **Add a way in** → a new adapter folder next to `api/`, with one file per module it offers and its
  own error map; add it to the adapters layer in the layers contract.
- **Change how errors map to status codes** → `api/errors.py`; exit codes → `cli/errors.py`.
- **Change a timeout, a retry or a spend limit for an external system** → its file in `core/`.

---

What to notice:

- **No module is named.** The map would read the same with three modules or thirty.
  `ls src/<app>/<domain>` is the list of modules; nothing else keeps one.
- **Every comment is a rule or a purpose, never a description of today's code.** "Composition only"
  and "never utils.py" can be checked against any module; "calls the model twice" could not.
- **The "I want to…" lines name files by role**, so they stay true when modules come and go.
