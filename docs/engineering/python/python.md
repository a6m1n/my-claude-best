# Python rules

## 1. Purpose

This file is for everyone who writes Python in the repository: people and AI agents alike.
Read it before you add a module, a type, or a check.

Each section below is one principle. Each says when it fires, what you do, and how anyone
tells that it happened.

The code here assumes Python 3.11 or newer (`python --version`); `typing.assert_never` and
`enum.StrEnum` are the newest features used.

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
| `typing.NewType("Cents", int)` | a type checker only | nothing at runtime; it returns its argument unchanged |
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
