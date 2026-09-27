# Python rules

**Navigation**

- [1. Purpose](#1-purpose)
- [2. Explicit is better than implicit: the reader sees what happens at the line they read](#2-explicit-is-better-than-implicit-the-reader-sees-what-happens-at-the-line-they-read)
- [3. Strict types: the checker reads every signature](#3-strict-types-the-checker-reads-every-signature)

## 1. Purpose

This file is for everyone who writes Python in the repository: people and AI agents alike.
Read it before you add a module, a type, or a check.

Each section below is one principle. Each says when it fires, what you do, and how anyone
tells that it happened.

The code here assumes Python 3.11 or newer (`python --version`); `typing.assert_never` and
`enum.StrEnum` are the newest features used. Section 3 takes `override` and `TypeIs` from
`typing_extensions`, which backports them to 3.11.

## 2. Explicit is better than implicit: the reader sees what happens at the line they read

That first phrase is a line from the Zen of Python, PEP 20. Tim Peters wrote the list to capture
Guido van Rossum's unstated design principles, and it states the principle without arguing for
it. Brett Cannon gives the reason: implicit knowledge is hard to communicate and easy to get
wrong.

The test is what the reader can tell at the line in front of them: which path runs, what the code
depends on, what can fail, and what comes back. Python's design FAQ gives the language's own case:
`self.x` makes it "absolutely clear that an instance variable or method is used ... even if you
don't know the class definition by heart". Aaron Turon asks the same question for Rust, "how much
information do you need to confidently understand what a particular line of code is doing, and how
hard is that information to find?", and counts detail that is easy to find as fine to leave
implicit. Michał Nazarewicz, who argues the Zen line is only a proxy, names the goal behind it:
least astonishment. The test is not the word count. Explicit code sometimes costs a few words:
Alyssa Coghlan's PEP 642, rejected in favour of a shorter syntax, argued for a longer pattern
syntax because its meaning does not change when a nearby lookup is refactored. It never means
spelling out what the language already makes clear, and PEP 8 prefers `if not items:` to a length
check.

### A business decision is an `if` in the use case

The use case is the function an adapter calls for one business operation, such as `place_order`
or `renew_subscription`: the module's `usecase.py` in
[file-structure.md](../file-structure/file-structure.md) sections 3 and 5. When the operation can
go two ways, the `if` that chooses stands in the use case, where the reader of the flow looks, and
it asks a named rule. The branches below it are calls. Three roles, each in its own place:

- **The rule** is a pure function named for the question it answers, such as `needs_manual_review`.
  It takes plain values and returns a value, and reads its threshold or rate from one named
  constant. It stays apart from the types: the types change when the shape of the data changes, the
  rule when the business changes its mind, and Robert C. Martin's single-responsibility rule is to
  separate things that change for different reasons. Where the rule, the types and the constant
  live is [file-structure.md](../file-structure/file-structure.md) section 3.
- **The use case** is the one function that has both a branch and side effects. It asks the rule,
  acts on the answer, and returns a value that says which path ran. It holds no threshold and no
  formula, only the branch, and it receives the clients it calls as parameters instead of reaching
  for module-level instances.
- **The doers**, a client's method such as `charge` or a small function of your own, each do one
  thing, for every value their signature admits. They hold no `if` on a business question.

Mark Seemann's fix for decisions tangled with side effects is this split: the pure step returns
"a value that indicates the decision", and the impure step acts on it. Alex Kladov states the
move as "push ifs up": the branches end up "centralizing control flow in a single function",
while "all the actual work is delegated to straight line subroutines". Robert C. Martin puts
"application specific business rules" in the use cases, and Percival and Gregory's service layer
has the same shape: get what the operation needs, check, call the domain, save. Brandon Rhodes'
"hoist your I/O" is the same instruction from the other side: the rule gets data, never a client.

The shapes that hide a decision, and what to write instead:

- **A doer that decides.** A function named for one act that sometimes does another, such as a
  `charge_card` that sends the order to review instead of charging. Move the condition into a
  named rule and the `if` into the use case. Separating the question from the act is the idea
  behind Fowler's Separate Query from Modifier; moving the branch to the caller is Kladov's "push
  ifs up".
- **A silent skip.** A `return` that does nothing when a condition fails, so the call reads as if
  it always acts. The caller decides whether to call.
- **An outcome passed through an argument.** A status one function writes into its argument so
  another knows whether to act. The order of the calls becomes a rule nobody wrote down, which Mark
  Seemann calls temporal coupling. Return the value instead, and when one step must follow another,
  let the second take what the first returned, so the wrong order fails at the type checker, or on
  the first run of that path, instead of passing silently.
- **A dependency the signature does not show.** A module-level client imported inside a doer
  hides the doer's second job with it, and a test has to patch the module to run it. Pass the
  client in.
- **A boolean argument that switches what a function does.** "Boolean arguments loudly declare
  that the function does more than one thing" (Martin). Write two named functions, unless the
  choice is data the caller carries, where a keyword-only `flag=` at least names it at the call
  site.
- **A failure turned into `None`, or an `except` that carries on.** Raise instead, because `None`,
  `0` and `""` all read as false and the caller's `if` will not tell them apart (Slatkin,
  Lefkowitz). `None` stays right for a documented "no result" in an `X | None` return, as
  `re.match` uses it. An outcome that is normal, such as "sent to review", is neither: return it
  as a value of a closed set.

### A rule about a value is written in the type, where the value enters

When a value obeys a rule, such as a closed set of codes, a field that always exists or a state
that must hold, the rule is a construct the reader sees on the type: an enum for the closed set,
a non-optional field for the thing that always exists, a separate type for a state (a
`PaidOrder` cannot be unpaid). The type is built once, where untrusted data first arrives, by a
function whose every exit is the type or one named error; Alexis King calls the move "parse,
don't validate". The types sit in a file of their own
([file-structure.md](../file-structure/file-structure.md) section 3). It names no sender and no
format, the parser at the edge imports it, and a file that only uses the value never imports the
parser.

### One decision, one home

- **A condition that repeats gets a name** when it is the same knowledge in two places: one
  authoritative representation, as Hunt and Thomas define DRY. The same shape for two different
  reasons stays duplicated, because the wrong abstraction costs more than the duplication it
  removed (Metz). Once named, the condition reads at the call site as a word:
  `if needs_manual_review(...)`, not the arithmetic.
- **A branch on a closed set is one `match` in one place**, with a `case _ as unreachable:
  assert_never(unreachable)` arm, so a member added later fails the type checker at that line
  and fails at runtime with `AssertionError` if no checker ran. Without that arm, an unmatched
  value runs no arm and raises nothing. When one set drives two facts, the `match` returns one
  value that carries both, or the facts live on the enum member (Lefkowitz's active enum); two
  `match` statements on the same value in two files is the failure.
- **Dispatch is a later move, not the first.** One class per variant removes the `if` at the cost
  of scattering the branch targets across files. Kerievsky found a simple conditional "a perfectly
  sufficient solution" at two or three variants. This practice's line is three or more variants
  that carry behaviour and belong to the same party as the set; at two, keep the `if`.

### What Python actually enforces

Choose the mechanism knowing what stands behind it. Half of the obvious answers are enforced
by nobody unless you run a checker.

| What you write | Enforced by | What a bad value does |
|---|---|---|
| `enum.Enum`, `enum.StrEnum` | CPython, at runtime | `CheckoutResult("done")` raises `ValueError`; `CheckoutResult["DONE"]` raises `KeyError` |
| `@dataclass(frozen=True)` | CPython, at runtime | a wrong-typed value is accepted at construction; assigning afterwards raises `FrozenInstanceError` |
| a pydantic model | pydantic, at runtime | `__init__` and `model_validate` raise `ValidationError` |
| `match` on an enum with a `case _: assert_never(x)` arm | a type checker before it runs; CPython at runtime | the checker reports the arm as reachable; at runtime the arm raises `AssertionError` |
| `match` on an enum with no `case _` arm | nobody, unless every arm returns in a function with a declared return type: then mypy's default `[return]` check and pyright's `reportReturnType` report the missing member | an unmatched value runs no arm and the statement completes |
| `typing.Literal["USD", "EUR"]` | a type checker only | nothing at runtime; any value is accepted |
| `typing.NewType("OrderId", str)` | a type checker only | nothing at runtime; it returns its argument unchanged |
| `NAME: Final = value` | a type checker only | nothing at runtime; a second assignment works, and a mutable value can still be changed |
| a beartype or typeguard decorator | the library, at runtime, when the function is called | a bad item after the first in a container usually passes: typeguard checks the first item by default, beartype one sampled item |
| `isinstance(x, P)` on a `@runtime_checkable` Protocol | CPython, at runtime, by method names only | an object with the right method names and wrong signatures passes |
| a docstring, a comment, a naming convention | nobody | nothing |

The checker rows hold only where a checker runs; name the tool and the command in CI. For a `match`
whose arms do not all return, mypy reports a non-exhaustive `match` only through the `assert_never`
arm unless `--enable-error-code exhaustive-match` is on (mypy 1.17, opt-in); pyright reports it on
its own only in strict mode (`reportMatchNotExhaustive` is off in basic and standard). Outside
those settings the arm, not the checker's configuration, is the enforcement.

- **Give an enum its own members, and do not rely on aliasing.** Two members sharing a value
  makes the second a silent alias for the first rather than an error. `@enum.unique` turns that
  into a `ValueError` at class creation; use it. `IntFlag` is the exception to the value half of
  the table's first row: `Perm(8)` accepts a value outside its members instead of raising, while
  name lookup still raises `KeyError`. It aliases like any other enum, so `@enum.unique` still
  applies.
- **Declare a closed set once, and annotate every field and parameter that carries it.** Pick
  the form by how the members are used. Use `StrEnum` when code writes the members by name in more
  than one place, such as a result the use case returns and the adapter matches; CPython makes a
  member's `str()` and `format()` return the plain value, to support replacing existing string
  constants. Its cost is that `CheckoutResult.CONFIRMED == "confirmed"` is true, so a bare string
  passes where a member is expected and only a type checker notices. Use a `Literal` alias when the
  values only pass through typed carriers, or when someone else owns the vocabulary, such as the
  mode of `open()`.

### Where it stops holding

Five conditions. Outside them, state the rule and the decision as above; inside them, this
section costs more than it returns.

1. **The type has to carry something a caller could not otherwise work out.** A wrapper whose
   only content is the parameter name already next to it adds a type with nothing to check.
   To tell: name the value the wrapper rejects. If there is none, it is a rename with extra
   steps.
2. **A function does not re-test its own precondition; a check on outside data never moves.**
   A precondition is the caller's to satisfy — Meyer's rule, in Eiffel's words: a routine body
   should never test for the precondition, since it is the client's responsibility to ensure
   it. The split this section makes, and Meyer does not: a check on a value from outside the
   system stays where the data enters, always. To tell: read the call sites of the function
   holding the check. If every one already passes the type, the check belongs at the edge; if
   the value comes from a wire, a file or a user, the check is the edge.
3. **A state a function must refuse is a guard at its top, not a decision for the caller.**
   Fowler's guard clause stays inside the function: it checks an unusual case at the top and
   returns early. This practice tightens it for a state the function must refuse: the guard raises,
   and never returns silently. A guarantee that belongs to the function, such as an order of steps,
   idempotency or a check that must happen in the same step as the act, stays inside it too;
   hoisted to every caller, it stops being a guarantee. To tell: the guard raises, and its
   condition is about the function's own contract, not about which business branch to take.
4. **A type at the boundary does not replace a check at the point of use when the two can
   drift.** In CrowdStrike's public root-cause analysis of its July 2024 outage, the content
   validator expected 21 input fields, the sensor supplied 20, and the bad file passed
   validation. A boundary is a place to state a constraint, not a reason to delete the assertions
   that protect memory, money or permissions. To tell: for each assertion you are about to
   delete, name what it protects; if the answer is memory, money or permissions, it stays.
5. **Related code stays together, and a function or a layer is earned.** Splitting a function
   whose halves can only be read together makes it harder to read, not easier (Ousterhout). A doer
   that is one line around a single client call earns no function of its own: the use case makes
   the call. A repository class and a unit of work are added when orchestration starts to creep
   into the callers, not on the first day; the authors who teach them say so, and count fifteen
   files touched to add one field when they were added too early. When code gets a file or a folder
   of its own is [file-structure.md](../file-structure/file-structure.md) sections 3 and 6. To tell:
   before you add a doer, name what it does besides the call; before you add a layer, name the
   duplication it removes.

A comment is not where a rule or a decision lives; what a comment is for is
[readability.md](../readability/readability.md) section 4.

**Check.** Open the use case of one business operation and read it with the functions it calls.

- Every `if` in the use case tests a value a named rule returned, or refuses a state at the top
  with a raise. Its branches are calls, and it returns a value that names the path it took.
- No function it calls has an `if` on a business question, a boolean argument that switches what
  it does, a `return` that skips its job, or a client it imports instead of receiving.
- The rule's file imports no client and no adapter. The file that defines the types imports
  neither the rule nor any client: `grep -n "^from\|^import"` on it shows only the standard library
  and the library that builds the types (pydantic, attrs, msgspec), and `grep -n "json\|request"`
  shows nothing.
- `grep -rln` the threshold's name in the source tree prints one file, the rule's
  ([file-structure.md](../file-structure/file-structure.md) section 3). A second file is the rule
  stated again, unless it is a point-of-use assertion condition 4 keeps.
- For a `match` on a closed set, count the arms: one per member plus the `assert_never` arm, and
  the checker's command is in CI.

The same checkout, first with its decision hidden inside a doer, then with the business `if` in
the use case and the rule in its own file:
[explicit-constraints-example.md](explicit-constraints-example.md).

Sources, by the name used above: PEP 20, "The Zen of Python" (Tim Peters, 2004) and Guido van
Rossum, "Python's Design Philosophy" (2009); the Python design FAQ, "Why must 'self' be used
explicitly"; Brett Cannon, "Why Python 3 exists" (2015); Aaron Turon, "Rust's language ergonomics
initiative" (2017); Michał Nazarewicz, "Explicit isn't better than implicit" (2021); Alyssa
Coghlan, PEP 642 (2020); PEP 8, on comparisons; Robert C. Martin, "The Single
Responsibility Principle" (2014), "The Clean Architecture" (2012) and "Clean Code Tip of the
Week" #12 (2009), on boolean arguments; Mark Seemann, "Design Smell: Temporal Coupling" (2011) and
"Refactoring registration flow to functional architecture" (2019); Alex Kladov, "Push ifs up and
fors down" (2023); Harry Percival and Bob Gregory, *Architecture Patterns with Python* (2020,
cosmicpython.com, chapters 1 and 4); Brandon Rhodes, "The Clean Architecture in Python" (PyOhio
2014) and "Hoist Your I/O" (PyWaw 2015); Martin Fowler, the refactoring catalog (Separate Query
from Modifier, guard clauses, Decompose Conditional), "Flag Argument" (2011); Brett Slatkin,
*Effective Python*, 3rd ed. (2024), item 32; Glyph Lefkowitz, "Python option types" (2015) and "The
Active Enum Pattern" (2025); Alexis King, "Parse, don't validate" (2019); Andy Hunt and Dave
Thomas, "Orthogonality and the DRY Principle"; Sandi Metz, "The Wrong Abstraction" (2016); Joshua
Kerievsky, *Refactoring to Patterns* (preface); Bertrand Meyer, "The manhood test" (2012) and the
Eiffel reference on Design by Contract; John Ousterhout, "A Philosophy of Software Design vs Clean
Code" (2024–2025); CrowdStrike, "External Technical Root Cause Analysis — Channel File 291" (2024);
the CPython docs for `typing.assert_never`, the `match` statement, `re.match` and the `enum`
module; the mypy and pyright documentation on exhaustiveness checking.

## 3. Strict types: the checker reads every signature

When you write a function or a class in application code, annotate its signature and its fields,
so that the one type checker in strict mode that
[static-checks.md](../static-checks/static-checks.md) section 2 sets up can read them. This section
says what the code looks like; which checker runs, in which mode, and where, is static-checks; a
setting a rule here relies on is named next to that rule.

A checker finds real bugs: in a study of 210 Python projects, about 15% of the fixed defects were
ones mypy would have caught, and the authors call that a lower bound (Khan et al., 2021). It also
helps the agents that write code: Meta reported at PyCon US 2026 that coding agents succeeded more
often on well-typed code and gained nothing on lightly typed code. Types in half the code check
half the code.

What enforces it: with mypy in strict mode, a function with a missing or partial annotation fails
(`disallow_untyped_defs`, `disallow_incomplete_defs`), and a second assignment to a `Final` name
fails in any mode. pyright's strict mode infers a missing return type instead, so with pyright turn
on ruff's `ANN` rules as well. Everything else in this section is review.

### Where annotations go

- **Every signature, every field.** Annotate each parameter and return, and each class field.
  Leave local variables and module-level names to inference, except an empty container
  (`orders: list[Order] = []`) and a named constant (`Final`, below): the checker already knows the
  rest, and the Typing Council's advice is to add types while they pay for themselves.
- **A data parameter takes the widest type the body uses; a return gives the concrete type.** Take
  `Iterable[Order]`, `Sequence`, `Mapping`, or `object` when any value will do; return
  `list[Order]`. A union return makes every caller write an `isinstance` check, so a function
  returns a union only for a documented "no result", `X | None` (section 2), or as a tagged union
  whose members the caller tells apart by one literal field. Guido van Rossum named over-narrow
  parameters, `list[str]` where `Sequence[str]` would do, as a common habit at PyCon US 2026. A
  client the unit calls is annotated with its concrete class instead
  ([readability.md](../readability/readability.md) section 6).

### Closed sets and ids

- **A value from a closed set is never a bare `str`.** A closed set is a fixed list of values a
  field or parameter can hold, all declared in your code, whether the code branches on them or
  only passes them on: a status, a kind, a mode, an event name, a provider. Declare it once;
  section 2 picks `StrEnum` or `Literal`, and every signature and field that carries it uses that
  type.
- **Compare with a member of a set you own, never with a string**:
  `order.status is OrderStatus.SHIPPED`, not `order.status == "shipped"`, and branch on the whole
  set with one `match` (section 2). Do not count on a checker to catch a string compared with a
  `StrEnum` member: mypy accepts it, since a `StrEnum` member is a `str`; pyright's strict mode
  reports only some such comparisons; ruff's `PLR2004` skips strings by default, and set to check
  them it catches `==` only, never `in` or a `match` case. A misspelled member name fails every
  checker, so the member is what turns a typo into an error.
- **A vocabulary another party owns stays that party's strings.** The `type` of an ASGI message
  is the protocol's word, not a set you declare, and section 2 already picks `Literal` for it.
  Type the value with the party's own types where a package ships them (`asgiref.typing` declares
  `type: Literal["http.response.start"]`), and compare with that literal at the boundary: the
  checker narrows a union of such types on `==`, which the mypy documentation calls a tagged union.
- **A string from outside is parsed once, at the edge** (section 2): a JSON field, an environment
  variable, a command-line argument. A value outside a set you own fails there, with a named error.
  A set another party owns can grow, so its parser keeps a branch for a value it does not know yet
  instead of failing.
- **An open set is one named constant**: a header name, a key in a wire format, the name of an
  environment variable. Every user imports it; which file holds it is
  [file-structure.md](../file-structure/file-structure.md) section 3.
- **An id passed between functions gets `NewType` when two kinds of id could be swapped
  silently**: `OrderId = NewType("OrderId", str)`. Not for a quantity you compute with, where
  arithmetic returns the base type and drops the label; not for a column an ORM maps, where
  SQLAlchemy 2.1 rejects an implicit `NewType` in `Mapped[]`. There, use the library's own type.
- **A named constant is `NAME: Final = value`**, such as the threshold or rate section 2 asks a
  rule to read: the checker rejects a second assignment and an override in a subclass.

### `Any`, narrowing and untyped libraries

- **`Any` stays inside the parser.** A function that accepts any value takes `object` and narrows
  it with `isinstance`. No recursive JSON alias: raw input is untyped only inside the parser that
  returns the typed value (section 2).
- **`TypeIs` only when `True` means exactly "is a T".** A narrowing function whose check is
  stricter than the type, such as `is_positive_int`, returns `TypeGuard[int]`: `TypeIs` also
  narrows the other branch, and there it would be wrong. On 3.11, `TypeIs` comes from
  `typing_extensions`; `TypeGuard` is in `typing`.
- **A library that ships no types**: upgrade it first, in case a newer release has types; then add
  its stub package (`types-requests`) as a dev dependency; then write partial local stubs with
  `stubgen`. When stubs would cost more than the few calls you make to it, silence that one module
  the way [static-checks.md](../static-checks/static-checks.md) section 6 says.

### Overrides, decorators, aliases and the future import

- **`@override` on a method that replaces a method of a parent class your code defines**
  (`typing_extensions` on 3.11): renaming or removing the parent's method then fails the check. A
  framework's hook methods need none: the settings that force the decorator on every override,
  mypy's `explicit-override` and pyright's `reportImplicitOverride`, stay off, since they flag every
  method a framework subclass defines.
- **A decorator keeps the signature it wraps**: type it with `ParamSpec`,
  `def retry(func: Callable[P, R]) -> Callable[P, R]`, and use `functools.wraps`. Strict mode
  rejects an untyped decorator.
- **On a 3.11 floor an alias is `Money: TypeAlias = Decimal`.** When the floor reaches 3.12, an
  alias that pydantic or FastAPI reads at runtime stays a plain assignment rather than
  `type Money = Decimal`: FastAPI misread a `type` alias of an `Annotated` dependency until 0.128.2
  (early 2026), and pydantic ignores field-specific metadata, such as `alias` or `default`, inside
  one.
- **No `from __future__ import annotations`.** On 3.11, `list[int]` and `int | None` already work
  at runtime. The import turns every annotation into a string, so code that reads annotations
  while it runs has to resolve them later, and that fails in some cases: a name imported only under
  `TYPE_CHECKING`, a class defined inside a function, `typing_extensions.ClassVar` on a dataclass.
  Quote a forward reference instead: `def parent(self) -> "Category":`. From 3.14 the language
  defers annotations by itself.

### Where it stops holding

- **Code no change touches** reaches the checker the way
  [refactoring.md](../refactoring/refactoring.md) section 10 says.

**Check.** Open each function and class the change adds. Every parameter, return and field is
annotated; no parameter or field that carries a value of a closed set is a bare `str`; `Any`
appears only inside a parser.

Sources: Khan et al., "An Empirical Study of Type-Related Defects in Python Projects", IEEE TSE
(2021); the PyCon US 2026 Typing Summit (Guido van Rossum on parameter types; Meta on coding agents
and typed code), as recapped by Bernát Gábor (bernat.tech); Talk Python #539 with the Typing Council
(2026); typing.python.org: "Typing best practices", "Type narrowing",
"Modernizing superseded typing features"; PEP 698 (`override`), PEP 742 (`TypeIs`), PEP 613
(`TypeAlias`), PEP 612 (`ParamSpec`), PEP 749 (deferred annotations); mypy documentation:
"The mypy command line", "Running mypy and managing imports", "Final names", "Literal types" (tagged
unions); pyright `configuration.md` (strict mode, `reportImplicitOverride`); ruff's `ANN` rules; the
`asgiref.typing` module; SQLAlchemy 2.1 documentation on `type_annotation_map`; FastAPI pull request
#13920; the pydantic documentation on named type aliases; ruff's `PLR2004` settings; mypy pull
request #20492 (narrowing a `StrEnum` compared with a `str`); pyright discussion #7230.
