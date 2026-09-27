# Python rules

## 1. Purpose

This file is for everyone who writes Python in the repository: people and AI agents alike.
Read it before you add a module, a type, or a check.

Each section below is one principle. Each says when it fires, what you do, and how anyone
tells that it happened.

The code here assumes Python 3.11 or newer (`python --version`); `datetime.fromisoformat`
reading a `Z` suffix is the newest feature used.

## 2. Explicit is better than implicit: the rule is written where it is read

That first phrase is a line from the Zen of Python, which states it and argues nothing.

**The rule.** "Explicit is better than implicit" means the rule a value obeys is readable from the
line in front of you — an explicit `self`, a named import, a keyword argument, a named exception
instead of a silent default, a written conversion instead of a coercion: what happens is written
where it happens. So never leave that rule to a convention — a name, a docstring, a comment,
"everyone knows amounts are in cents" — when a construct can carry it: an enum for a closed set, a
distinct type for a unit, a non-optional field for a thing that always exists. The parse function
follows from that; it is not the principle. A construct is built somewhere, and the honest place
is where the untrusted value first arrives: placement is a consequence, visibility is the rule.
The move has a name — parse, don't validate — and what it buys has another: an illegal state that
cannot be built.

Not one module that owns the type, the parser and the format: the type belongs to the domain that
uses it and names no sender and no format, the parser to the edge where the format is known, and
the parser imports the type — a module that only uses the value never imports the parser. Not six
signatures that each spell out amount and currency either: that re-states the pairing six times,
which is the failure the example is about.

What goes wrong without it has a name — shotgun parsing. Checks land in whichever function
happened to need one, so the program cannot reject bad input before acting on it: by the time
the fifth module rejects an order, the first four have already written to the database, billed
the customer, and sent mail. A type carries what the check learned to every place the value
goes, so there is nowhere else to state it.

### What Python actually enforces

Choose the mechanism knowing what stands behind it. Half of the obvious answers are enforced
by nobody unless you run a checker.

| What you write | Enforced by | What a bad value does |
|---|---|---|
| `enum.Enum` | CPython, at runtime | `Currency("usd")` raises `ValueError`; `Currency["usd"]` raises `KeyError` |
| `@dataclass(frozen=True)` | CPython, at runtime | assignment raises `FrozenInstanceError` |
| a pydantic model | pydantic, at runtime | `__init__` and `model_validate` raise `ValidationError` |
| `typing.Literal["USD", "EUR"]` | a type checker only | nothing at runtime; any value is accepted |
| `typing.NewType("Cents", int)` | a type checker only | nothing at runtime; it returns its argument unchanged |
| a docstring, a comment, a naming convention | nobody | nothing |

The bottom two rows are enforced only where a checker runs; name the tool and the command in CI.

- **Give an enum its own members, and do not rely on aliasing.** Two members sharing a value
  makes the second a silent alias for the first rather than an error. `@enum.unique` turns that
  into a `ValueError` at class creation; use it. `IntFlag` is the exception to the value half of
  that row: `Perm(8)` accepts a value outside its members instead of raising, while name lookup
  still raises `KeyError`. It aliases like any other enum, so `@enum.unique` still applies.

### Where it stops holding

Three conditions. Outside them, state the constraint anyway; inside them, this rule costs more
than it returns.

1. **The type has to carry something a caller could not otherwise work out.** A wrapper whose
   only content is the parameter name already next to it adds a type with nothing to check.
   Wrap a value when the wrapper answers a question the call site would otherwise guess at —
   which unit, which of two same-shaped ids, whether it has been escaped. To tell: name the
   value the wrapper rejects. If there is none, it is a rename with extra steps.
2. **Parse at the edge, not at every hop.** Re-validating data that is already typed is not
   merely slow, it is wrong: a validation error is a sensible answer at an entry point and an
   unrecoverable bug three layers in, where there is no bad input left to reject. To tell: read
   the call sites of the function holding the check. If every one of them already passes the
   type, the check has no bad input left to reject and belongs at the edge.
3. **A type at the boundary does not replace a check at the point of use when the two can
   drift.** A validator believed a payload had 21 fields; the code that read it expected 20, and
   the validator let it through. The fix was a bounds check at the point of use. A boundary is a
   place to state a constraint, not a reason to delete the assertions that protect memory, money,
   or permissions. To tell: for each assertion you are about to delete, name what it protects; if
   the answer is memory, money, or permissions, it stays.

**Check:** open the consumer furthest from the boundary and read one line that uses the value, with
the signature above it. The type the value carries there is a named one — `PaidOrder`, `Money` —
and the only file you open to learn the rule is the module named on that type's import line. If the
rule is not there either, or the type is `dict`, `str` or `int`, the constraint is still implicit.
Then take the constraint's own literal — the allowed string, the `/ 100`, the `is None` — and
`grep -rn` it: one hit is the type, or the function that builds it; a second hit in another file is
the rule stated again — a hit that only names the type, `Currency.USD`, is the type being used, not
the rule restated; grep the literal with its quotes — unless it is a point-of-use assertion
condition 3 keeps. Last, `grep -n "json\|request"` the module that holds the type: it returns
nothing, or the type is in the wrong module.

The same six modules with their rules first in people's heads and then in the type every signature
past the webhook names: [explicit-constraints-example.md](explicit-constraints-example.md).