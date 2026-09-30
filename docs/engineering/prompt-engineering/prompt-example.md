# Example: one call site, from the constants to the parsed answer

A worked example for [prompt-engineering.md](prompt-engineering.md). A support module,
`support/triage/`, reads a customer's ticket and returns two things: whether it reports a bug or
asks for a feature, and the date the problem first occurred. Code reads the answer, so the prompt
has no role (section 3). Every name is a placeholder, and the model ids are invented: use your
vendor's.

The example is also the template for a base prompt with a thin layer per model (section 16):

- `consts.py` holds the settings of the current model: `TRIAGE_LLM_MODEL` and
  `TRIAGE_LLM_REASONING_EFFORT`;
- `prompts.py` holds the base prompt, the same for every model, and `MODEL_NOTES`, the
  instructions only one model needs;
- the service joins the base and the model's notes and hands the request to the one client of the
  vendor, which adds the cache switch, passes the effort and parses the answer into a type.

The files follow [file-structure.md](../file-structure/file-structure.md) sections 3 and 4. The
vendor's SDK call is left out, as the comment in `_send` says: what it sends is named there, and
section 15 of the rules lists each vendor's parameter for the effort.

## `core/schemas.py` and `core/config.py`: what the client and every module share

```python
# core/schemas.py
from dataclasses import dataclass
from enum import StrEnum, unique
from typing import Literal, TypeAlias

# The vendor owns the ids; this is the set this project has tested its prompts on.
LlmModel: TypeAlias = Literal["acme-large-2", "acme-small-3"]


@unique
class ReasoningEffort(StrEnum):
    """This project's levels. The vendor's client maps each to what the current model accepts."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@unique
class StopReason(StrEnum):
    """Why the model stopped, in the client's words; the client maps the vendor's reasons to these."""

    END = "end"
    REFUSAL = "refusal"
    OUTPUT_LIMIT = "output_limit"
    UNKNOWN = "unknown"  # a reason the vendor added after this client was written


@dataclass(frozen=True)
class RawReply:
    stop_reason: StopReason
    text: str
```

`core/config.py` holds the one setting this client needs. The settings class's `model_config` and
its other fields are left out; they are
[python/settings-example.md](../python/settings-example.md)'s.

```python
# core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ACME_DISABLE_PROMPT_CACHE=true only while debugging or measuring
    disable_prompt_cache: bool = False
```

The model ids are the vendor's words, so they are a `Literal`; the levels are this project's own
set, so they are an enum ([python.md](../python/python.md) section 2). A misspelt model or level
fails the type checker, not the first call.

## `core/acme_ai_client.py`: the one client of the vendor

```python
# core/acme_ai_client.py
"""The one client of the model vendor: every model call goes through here."""

import uuid
from collections.abc import Callable
from typing import TypeVar, assert_never

from acme_ai import AcmeAiSdk
from pydantic import BaseModel, ValidationError

from acme.core.errors import ModelAnswerInvalid, ModelOutputCutOff, ModelRefused
from acme.core.schemas import LlmModel, RawReply, ReasoningEffort, StopReason

AnswerT = TypeVar("AnswerT", bound=BaseModel)


class AcmeAiClient:
    def __init__(
        self,
        sdk: AcmeAiSdk,
        *,
        disable_prompt_cache: bool,
        new_request_uuid: Callable[[], uuid.UUID],
    ) -> None:
        self._sdk = sdk
        self._disable_prompt_cache = disable_prompt_cache
        self._new_request_uuid = new_request_uuid

    def complete(
        self,
        *,
        model: LlmModel,
        reasoning_effort: ReasoningEffort,
        system: str,
        user: str,
        answer_type: type[AnswerT],
    ) -> AnswerT:
        reply = self._send(
            model, reasoning_effort, self._apply_cache_switch(system), user, answer_type
        )

        match reply.stop_reason:
            # An unknown reason may still end on a whole answer; the parse decides.
            case StopReason.END | StopReason.UNKNOWN:
                return _parse_answer(model, reply.text, answer_type)
            case StopReason.REFUSAL:
                raise ModelRefused(model)
            case StopReason.OUTPUT_LIMIT:
                raise ModelOutputCutOff(model)
            case _ as unreachable:
                assert_never(unreachable)

    def _apply_cache_switch(self, system: str) -> str:
        if not self._disable_prompt_cache:
            return system

        # First in the system prompt: a cache matches from the request's start, so
        # nothing from here on hits.
        return f"Request UUID: {self._new_request_uuid()}\n{system}"

    def _send(
        self,
        model: LlmModel,
        reasoning_effort: ReasoningEffort,
        system: str,
        user: str,
        answer_type: type[BaseModel],
    ) -> RawReply:
        # Left out: the SDK call. It passes the model; the effort under the vendor's own name and
        # values; system as the system prompt and user as the one user message;
        # answer_type.model_json_schema() through the vendor's structured-output feature; and the
        # vendor's no-cache switch, where one exists, when self._disable_prompt_cache is on. It maps
        # the vendor's stop reason to StopReason: a content-filter stop maps to REFUSAL, and a
        # reason it does not know yet to UNKNOWN. Any SDK error becomes
        # ModelUnavailable(model, status), raised from None, because the vendor's message can
        # quote the prompt (logging.md section 10).
        ...


def _parse_answer(model: LlmModel, text: str, answer_type: type[AnswerT]) -> AnswerT:
    try:
        return answer_type.model_validate_json(text)
    except ValidationError:
        # from None: pydantic's message can quote the answer
        raise ModelAnswerInvalid(model) from None
```

```python
# core/errors.py
from acme.core.schemas import LlmModel


class ModelUnavailable(Exception):
    """The vendor failed; the message names the model and the status, never the vendor's text."""

    def __init__(self, model: LlmModel, status: int | None) -> None:
        super().__init__(f"model {model} unavailable (status {status})")
        self.model = model
        self.status = status


class ModelRefused(Exception):
    """The model refused; the message names the model, never the prompt or the answer."""

    def __init__(self, model: LlmModel) -> None:
        super().__init__(f"model {model} refused")
        self.model = model


class ModelOutputCutOff(Exception):
    """The answer hit the model's output limit, so it may not match the schema."""

    def __init__(self, model: LlmModel) -> None:
        super().__init__(f"model {model} stopped at its output limit")
        self.model = model


class ModelAnswerInvalid(Exception):
    """The answer did not match the schema; the message names the model, never the text."""

    def __init__(self, model: LlmModel) -> None:
        super().__init__(f"model {model} gave an answer that does not match the schema")
        self.model = model
```

What it does for the rules:

- **Every call passes the effort** (section 15); it is never left to the vendor's default. The
  client is the one place that knows the vendor's name for the effort.
- **The cache switch is one `if`**, in `_apply_cache_switch`: it puts a fresh line at the very
  start of the system prompt. The setting is read once at startup and passed in (section 17), and
  so is the UUID source, `uuid.uuid4`, so a test can fix the UUID
  ([readability.md](../readability/readability.md) section 6).
- **The answer is parsed into the type the caller asked for** (section 11). The stop reason is a
  closed set, so `complete` branches on it in one `match` with an `assert_never` arm
  ([python.md](../python/python.md) section 2). Each arm is one line, so `complete` reads at one
  level of detail ([readability.md](../readability/readability.md) section 2). A refusal and a
  stop at the model's output limit become named errors before the parser sees the text. The parse
  sits in `_parse_answer`, where a reply that does not match the type becomes `ModelAnswerInvalid`.
  An SDK error becomes `ModelUnavailable`. The errors name the model, never the text, so they are
  safe in a log ([logging.md](../logging/logging.md) section 10).
- **`AcmeAiSdk`**, the vendor's SDK object from its package `acme_ai`, is built once by the
  adapter at startup and handed in ([file-structure.md](../file-structure/file-structure.md)
  section 4); it is not shown.

## `support/triage/consts.py`: the model and its effort

```python
# support/triage/consts.py
"""The settings of the triage call; they change together, when the model changes."""

from typing import Final

from acme.core.schemas import LlmModel, ReasoningEffort

TRIAGE_LLM_MODEL: Final[LlmModel] = "acme-small-3"
# low, not none: the task reads a date (prompt-engineering.md section 15);
# the sweep on the case set keeps or changes it.
TRIAGE_LLM_REASONING_EFFORT: Final = ReasoningEffort.LOW
```

The names follow `<purpose>_llm_model` and `<purpose>_llm_reasoning_effort`, so a search for
`_LLM_MODEL` lists every call site and the model it uses.

## `support/triage/schemas.py`: the answer's shape

```python
# support/triage/schemas.py
from datetime import date
from enum import StrEnum, unique

from pydantic import BaseModel, ConfigDict


@unique
class TicketKind(StrEnum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"


class TicketTriage(BaseModel):
    """The answer of the triage call; the client sends its JSON schema as the response format."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    reasoning: str  # first: the model writes top to bottom, so this leads to the kind
    kind: TicketKind
    # None is the way out: the ticket gives no date
    problem_first_occurred_on: date | None
```

`reasoning` comes before `kind` (section 12). Strict mode is safe here because `_parse_answer`
parses the raw text with `model_validate_json`. `kind` accepts two values and nothing else, and
the model config rejects a key the schema does not name
([python.md](../python/python.md) section 4). `problem_first_occurred_on` has no default, so the
model has to fill it, and `None` is a value the schema allows: the way out of section 8, with its
condition in the prompt below.

## `support/triage/prompts.py`: the base prompt and the layer per model

```python
# support/triage/prompts.py
"""The triage prompt: one base for every model, and a thin layer per model."""

from collections.abc import Mapping
from typing import Final

from acme.core.schemas import LlmModel

# The base: the goal, the steps, the definitions and the way out. It holds for every model, and a
# model change runs it unchanged first.
SYSTEM: Final = """\
Classify the support ticket in <ticket>, and find the date its problem first occurred.

1. Find what the customer expected to happen, and what happened instead.
2. Decide the kind:
   bug: the product does something it claims to do, and the result is wrong.
     Includes: an error message, a crash, a wrong number, a feature that
     stopped working.
     Excludes: a request for behaviour the product never had.
     Near miss: "export should also support Excel" is not a bug, even when
     the customer calls it one.
   feature_request: the customer asks for something the product does not
     do today.
   If the ticket does both, decide by the first problem it describes.
3. Find the date the problem first occurred, as YYYY-MM-DD. If the ticket
   gives no date for it, set problem_first_occurred_on to null. A guess such
   as "about a week ago" is not a date: set it to null.
"""

# The part that changes on every call: the ticket in its tag, then the question, last.
USER: Final = """\
<ticket>
{ticket_text}
</ticket>

Classify this ticket."""

# The layer: what only one model needs. An entry starts empty and gains a line only when the case
# set shows that model needs it. A model with no entry cannot run this prompt.
MODEL_NOTES: Final[Mapping[LlmModel, str]] = {
    "acme-large-2": "",
    "acme-small-3": "Write the reasoning in three sentences or fewer.",
}
```

Why it looks like this:

- **The base follows sections 2, 4 and 8.** The goal comes first, then the steps in the order they
  apply. `bug` has its include rule, its exclude rule and a near miss, and the way out is a
  condition the model can check in the ticket, with its nearest neighbour, a vague date, decided
  in advance.
- **The ticket is inserted material** (section 5): it sits in a named tag, and the instruction has
  no wrapper. It is untrusted all the same.
- **The static part is first and the question last** (section 10). `SYSTEM` is the same on every
  call, so it is what the cache keeps; `USER` changes per ticket and ends on the question.
- **The layer holds one line for one model.** The smaller model's long reasoning drifted from the
  steps and failed cases on the case set, so its entry asks for less; the larger one needs nothing.
  That line is the only thing to revisit when that model goes.
- **No "think step by step" and no role**: the depth is the effort setting (section 2), and code
  reads the answer (section 3).

## `support/triage/services/service_triage.py`: the call

```python
# support/triage/services/service_triage.py
from acme.core.acme_ai_client import AcmeAiClient
from acme.core.schemas import LlmModel, ReasoningEffort
from acme.support.triage.prompts import MODEL_NOTES, SYSTEM, USER
from acme.support.triage.schemas import TicketTriage


def triage_ticket(
    ticket_text: str,
    client: AcmeAiClient,
    *,
    model: LlmModel,
    reasoning_effort: ReasoningEffort,
) -> TicketTriage:
    # Indexing, not .get(): a model never added to MODEL_NOTES fails instead of running with no layer.
    notes = MODEL_NOTES[model]
    system = f"{SYSTEM}\n{notes}" if notes else SYSTEM

    return client.complete(
        model=model,
        reasoning_effort=reasoning_effort,
        system=system,
        user=USER.format(ticket_text=ticket_text),
        answer_type=TicketTriage,
    )
```

The model and its effort are parameters, not read from `consts.py` here
([readability.md](../readability/readability.md) section 6). The use case, not shown, passes the
two constants; the case-set test of section 18 passes the old model and the new one, and runs
both through the same function. `MODEL_NOTES[model]` raises `KeyError` for a model that has no
entry, so a model never added here fails on its first call instead of running with no layer.

The value checks section 11 asks for after the parse belong to the use case, not shown: it gets
`today` from the adapter, so it rejects a date in the future
([readability.md](../readability/readability.md) section 6).

## Changing the model

A new model comes out, and the team wants `acme-large-2` for triage. The template turns the change
into four steps, each one a small diff:

1. **Add the model with an empty layer.** `"acme-large-2"` is already in `LlmModel`; its entry in
   `MODEL_NOTES` is `""`. A model not yet in the project gets both lines in this step.
2. **Run the base unchanged.** The case set runs the current setup, `acme-small-3` at `low` with
   its notes, against `acme-large-2` with the base alone, at each effort level the model offers,
   with repeats (sections 15 and 18). The prompt text does not change in this step, so the result
   measures the model.
3. **Tune only the layer.** Where the new model fails cases the old one passed, add a line to its
   entry in `MODEL_NOTES`, and run the set again. The base does not change unless every model
   needs the change; then it is a prompt change, tested as one.
4. **Switch the constants.** One commit sets `TRIAGE_LLM_MODEL` and `TRIAGE_LLM_REASONING_EFFORT`
   to what the case set chose. The old model's entry stays until no call site uses it.
