# Status line

A free status line for Claude Code. It helps you use the whole 5-hour budget without hitting the limit early, stop paying to write a cold cache again, and see which agent is stuck or running out of room.

**Navigation**

- [What it gives you](#what-it-gives-you)
- [What each segment shows](#what-each-segment-shows)
- [The agent panel](#the-agent-panel)
- [Sources](#sources)

Files: [install.md](install.md) (how to set it up, by hand or with one paste) · [statusline.py](statusline.py) (the script) · [img/](img/) (the pictures)

![The status line under the Claude Code prompt: context, model and effort, 5-hour and weekly limits, cache, burn](img/statusline.svg)

It is one Python file and two keys in `settings.json`: no packages beyond the standard library, no network calls ([what it does on your machine](install.md#what-the-script-does-on-your-machine)). Set it up [by hand](install.md#set-it-up-by-hand) or [with one paste](install.md#install-with-one-paste); to remove it, see [Undo](install.md#undo).

`5h`, `7d` and `burn` need a Pro or Max plan and appear only after the first answer in a session; the rest works with any account.

## What it gives you

Claude Code has most of these numbers, but you see them only when you go and ask for them. The line keeps them in front of you on every message, and that changes how you work:

- Use the whole 5-hour budget without hitting the limit an hour early. `burn` works like a speedometer: it shows how fast you are spending the budget and how much of it you will have used by the reset at this pace. Aim for 100 to 120%. It pays off most in long sessions and in dynamic workflows where many agents run at once.
- Stop paying for a cold cache. After the cache goes cold, the cached part of a message costs 12.5 to 80 times more, because it is written again. The countdown tells you how long you can step away, and when a long session has gone cold, it is often cheaper to run `/compact` first.
- Compact when you choose. `ctx` shows the window filling up, before Claude Code compacts by itself and may lose early details.
- See the limit coming. `5h` and `7d` show how much of each limit you have used and when it resets.
- Spot the stuck agent. Each agent row has a small chart of its token use; when it stays empty, the agent produces nothing and has most likely hung.
- Watch each agent's size. An agent can be resumed or sent a follow-up, and then it starts from its whole history, so its context number tells you what that will cost.
- Give each agent the right model. Claude Code's own row does not show the model; this one does, so you see which agents run on an expensive model and can set the model that fits the task in the agent's definition.
- Know what you are paying for. The model and the effort level stay in view, so a quick question does not run at top effort on an expensive model by accident.

## What each segment shows

### `ctx`: how full the context is

![ctx at 12%, 70% and 91%](img/segment-ctx.svg)

| Part | What it means |
|---|---|
| `ctx` | The session's context window. |
| `120.4k` | Tokens in the window now. |
| `/1M` | The window size: 1 million tokens. |
| `12%` | The share used. Yellow from 60%, red from 85%. |

Every message sends the whole context again, so a fuller window costs more per message.
At yellow, run `/compact` yourself with a focus (`/compact focus on the API changes`); at red, compact now or start a new session. Otherwise Claude Code compacts by itself when the window is nearly full, and details from early on may be lost.

### Model and effort

![Opus at xhigh effort, Sonnet at medium, Haiku without an effort level](img/segment-model.svg)

| Part | What it means |
|---|---|
| `Opus 5.5` | The model the session runs on. |
| `·xhigh` | The effort level: `low`, `medium`, `high`, `xhigh` or `max`. More effort helps on hard tasks and uses more tokens. Not shown when Claude Code sends no level. |

Change the model or the effort between tasks, with `/model` and `/effort`: a model switch writes the whole cache again, and on most models so does an effort change.

### `5h`: the 5-hour usage limit

![5h at 2%, 76% and 94%](img/segment-5h.svg)

| Part | What it means |
|---|---|
| `5h` | Your 5-hour usage limit. |
| `2%` | The share of it you have used. Yellow from 70%, red from 90%. |
| `(in 4h 44m)` | Time until the reset. |

At 100% you are blocked until the reset, so at red finish the current task and leave the rest for later.
Cmd-click or Ctrl-click the segment to open the usage page, in terminals that support links.

### `7d`: the weekly limit

![7d at 27%, 81% and 96%](img/segment-7d.svg)

| Part | What it means |
|---|---|
| `7d` | Your weekly usage limit. |
| `27%` | The share of it you have used. Same colors as `5h`. |
| `(in 4d 22h)` | Time until the reset. |

It resets less often, so a red `7d` with days left before the reset means: keep the expensive model for the work that needs it.

### `cache`: keep the cache warm

![cache warm, yellow, red, warming, about to expire, and cold](img/segment-cache.svg)

| Part | What it means |
|---|---|
| `cache` | The prompt cache: the API keeps the long start of every message for 1 hour on a Claude subscription within plan usage, and for 5 minutes with an API key, after usage credits start, and for subagents. |
| `100%` | The share of cached tokens read rather than written again, over the main conversation's last 10 API calls. Green from 75%, yellow from 50%, red below. |
| `warming` | Shown instead of a red number right after the cache was written again. Fine in a moment. |
| `56m` | Time until the cache goes cold. Every call starts the clock again. It moves only when the line redraws, so take it as the most time you have. Yellow in the last minute. |
| `cold` | The cache has expired: the next message writes it all again. |

A read from the cache costs a tenth of the normal input price or less, and writing it again costs 1.25 or 2 times the normal price. So after the cache goes cold, the cached part of a message costs 12.5 to 20 times more on most models, 25 to 40 times on Opus 5.5, and up to 80 times only on Fable 5.1 and Mythos 5.1 with the 1-hour cache. If you step away, come back before `cold`.
When a long session's cache has already gone cold, the next message pays for the whole history either way. That is a good moment to run `/compact`: after it, each message carries a short summary instead of the full history.
A percentage that stays low for many calls means something keeps changing the start of the prompt: a model switch, an effort change (on most models), a compaction, many images. `/usage` shows the session's hit ratio and names the likely cause of the last miss (Claude Code 2.1.260 or later).

### `burn`: the speedometer for your 5-hour limit

![burn at five readings: below 100%, the sweet spot, too fast, far too fast, and collecting](img/segment-burn.svg)

Claude Code tells the status line only how much of the 5-hour limit is used right now. It does not say whether your pace will run you into the limit before the reset. `burn` answers that. The script keeps a short history of the used percentage for each session, fits a line through the last hour of it to get your pace, and projects that pace to the reset:

```text
projected share at the reset = used now + pace × hours until the reset
```

Take this reading, with 8% of the 5-hour limit used and the reset in 4h 35m:

```text
burn: ▸104% ⚠100% in 4h 23m (~21%/h, 40.66M tok/h)
```

| Part | What it means |
|---|---|
| `▸104%` | At this pace you will have used 104% of the budget by the reset: 8% now, plus 21% per hour for the 4h 35m left (4.58 hours), gives 104.2%, shown as 104%. |
| `⚠100% in 4h 23m` | At this pace you reach the limit in 4h 23m, about 12 minutes before the reset. It appears only when the projection is 100% or more. |
| `~21%/h` | Your pace: the share of the 5-hour budget you use per hour. |
| `40.66M tok/h` | The tokens the main conversation processes per hour, cache reads included. Subagents are not counted, while the percentages count everything: your agents and your other sessions. |

How to read the number:

| Reading | What it means | What to do |
|---|---|---|
| below 100% (green) | You will not use the whole budget before the reset. | There is room for more: a stronger model, higher effort, more agents at once. |
| 100% to about 120% | The sweet spot: you use the whole budget, and the limit comes shortly before the reset. | Keep this pace. |
| about 120% to 200% | The limit comes well before the reset, and you wait until the reset. | Slow down: fewer agents at once, a cheaper model for subagents. |
| 200% and more (red) | More than twice the budget. | Slow down now, or plan for a long wait. |
| `— (2m)` | Still collecting: the first reading needs three minutes of history, and `(2m)` is the time until it. It also returns for three minutes after each 5-hour reset. | Wait. |
| `— (no history)` | The script keeps no readings: it could not create or write its [state folder](install.md#what-the-script-does-on-your-machine). | Run `claude --debug` to see why. |

The script colors everything from 100% to 200% yellow. In the sweet spot, yellow means you are right on budget, not that something is wrong.

`burn` is a straight-line forecast. A burst of parallel agents pushes it up and a quiet stretch pulls it down, so read it as a trend. Each session shows the numbers from its own last answer: read `5h` and `burn` in the session you work in. `burn: ~21%/h` with no `▸` means Claude Code sent no reset time: pace only, no forecast.

Below 110 columns the `(in …)` times and the `burn` details drop, and `⚠100% in 4h 23m` shortens to `⚠`.

## The agent panel

When Claude Code runs subagents, it lists them in a panel under the footer. By default a row shows the agent's name or type, its description and a token count. The script redraws each row so you can compare agents at a glance.

![Agent panel with five agent rows; the last one has been paused for 1m35s](img/agent-panel.svg)

The five agent rows are what the script prints for invented agents; the footer line, the `● main` row and the `○` marks stand in for Claude Code's own panel.

### One row, part by part

```text
opus-5-5·high · Comparing two retry strategies · 6m · █▁▂▅▁▂▇ ▁▁ · ↓ 131.7k/1M 13%
```

| Part | What it means |
|---|---|
| `opus-5-5` | The model the agent runs on. The color shows the cost: yellow for Opus and Fable, green for Sonnet, gray for Haiku. A yellow model name on a simple task: set a cheaper model in that agent's definition. An agent Claude gave a name to shows that name first — Claude can reach it by that name later. |
| `·high` | The agent's effort, set in its definition or in the call that started it. It can also be a number: a token budget. No effort shown: the agent uses the session's effort. |
| `Comparing two retry strategies` | What the agent is doing right now. Claude Code updates this summary as the agent works; before the first update it is the task description. |
| `6m` | How long the agent has run. Shown only while it runs. |
| `█▁▂▅▁▂▇ ▁▁` | The token chart: how busy the agent was over roughly the last minute. See below. |
| `↓ 131.7k` | The tokens in the agent's context now; `↓` marks tokens. |
| `/1M` | The agent's window size. |
| `13%` | The share used. Yellow from 60%, red from 85%. See below. |

A row keeps the default look until Claude Code knows which model the agent runs on. A finished agent's row is removed at once; a failed or stopped one stays for 30 seconds, without its time and chart.

### The token chart: is the agent working or stuck?

Claude Code samples each agent's token count every few seconds. Each bar covers a few seconds and shows how much the count grew in them; the tallest bar in view is full height, and the chart covers about the last minute. It shows the shape of the work, not a rate.

- Tall bars: the agent is working, reading files and writing answers.
- `▁` bars: no new tokens: the agent is thinking, or waiting on a tool call (a test run, a search, a web page).
- A gap before a run of `▁` at the end, as in `█▁▂▅▁▂▇ ▁▁`: no new tokens since that point.
- An empty chart, only `▁` or `⏸`: the agent is producing no tokens at all. For a short while that is thinking or a tool call; if it stays empty, the agent has most likely hung and is doing nothing.
- A yellow `⏸1m35s`: no new tokens for 40 seconds or more, and the number is how long. `⏸` first replaces only the flat end of the chart; once the whole chart is flat, `⏸` stands alone. The number counts the whole pause, even past the chart's minute.

Why it matters: a growing `⏸` may be long thinking, a slow command, or a stuck agent. If it grows well past what its task should take, run `/tasks` and open the agent to see what it waits on; stop it only if it is stuck.

### The agent's context: how much room is left

Every subagent has its own context window, sized by its own model, not by the main session: an agent on Haiku gets a smaller window than one on Opus.

Why it matters:

- A red percentage on an agent that still has work to do means little room is left: next time, give it a narrower task, or a model with a larger window.
- Every call the agent makes sends its whole context again, so a full window costs more per call, as in the main session. Split a long job across several agents with short briefs, so no single context grows large.
- An agent can be resumed or sent a follow-up, and then it starts from its full history: note its number while it runs, since its row goes when it finishes. A small number means a cheap follow-up; with a large one, a fresh agent with a short brief may cost less.

## Sources

- Anthropic, "Customize your status line": https://code.claude.com/docs/en/statusline (the stdin fields, `rate_limits` only on Pro and Max plans, `subagentStatusLine` and its per-agent fields, including an effort that can be a token budget or absent when the agent uses the session's, ANSI colors and OSC 8 links)
- Anthropic, "How Claude Code works": https://code.claude.com/docs/en/how-claude-code-works (what happens when the context fills up, and `/compact` with a focus)
- Anthropic, "Prompt caching": https://platform.claude.com/docs/en/build-with-claude/prompt-caching (the cache lifetimes, and the read and write prices against the normal input price)
- Anthropic, "How Claude Code uses prompt caching": https://code.claude.com/docs/en/prompt-caching (what breaks the cache, the 1-hour and 5-minute cache lifetimes, the `/usage` cache line)
- Anthropic, "Create custom subagents": https://code.claude.com/docs/en/sub-agents (a subagent's context window is sized by its own model; a named subagent can get a follow-up; a resumed subagent keeps its full history; a finished agent's row is removed at once, a failed or stopped one stays for 30 seconds)
- Anthropic, "Plugins reference": https://code.claude.com/docs/en/plugins-reference (a plugin can set `subagentStatusLine` but not `statusLine`, which is why this is a file and two settings keys, not a plugin)
