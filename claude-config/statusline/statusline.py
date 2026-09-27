#!/usr/bin/env python3
"""Claude Code status line: ctx | model+effort | 5h | 7d | cache | burn speedometer."""
from __future__ import annotations  # lets `str | None` hints run on Python 3.9

import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime

RESET = "\033[0m"
DIM = "\033[2m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
GRAY = "\033[90m"
DIM_FG = "\033[39m"  # reset foreground only — keeps an enclosing DIM alive

SEP = f" {DIM}│{RESET} "
CACHE_WINDOW = 10
# The interesting usage entries always live in the transcript tail — never
# scan the full file (it can reach tens of MB at high context; the docs want
# the whole script under ~100ms). 2 MB comfortably holds the recent entries
# even with very large tool results in between.
TRANSCRIPT_TAIL_BYTES = 2 * 1024 * 1024
NARROW_COLS = 110  # below this terminal width, drop the "(in ...)" suffixes

# Cmd/Ctrl-click the 5h/7d usage segment to open the account usage page. Rendered
# as an OSC 8 terminal hyperlink — terminals that support it (iTerm2, Kitty,
# WezTerm, Ghostty, VS Code) make it clickable; those that don't (macOS
# Terminal.app) just render the text normally, un-clickable.
USAGE_URL = "https://claude.ai/new#settings/usage"

# Prompt-cache TTL countdown. Transcript usage entries carry a cache_creation
# breakdown ({"ephemeral_1h_input_tokens": N, "ephemeral_5m_input_tokens": M});
# the TTL is detected from whichever bucket the session actually writes to,
# falling back to Anthropic's 5m default when no breakdown is present. Every
# API call (read or write) refreshes the TTL, so the countdown runs from the
# LAST call's timestamp.
CACHE_TTL_FALLBACK_S = 300
CACHE_TTL_WARN_S = 60  # highlight the countdown when expiry is this close

# Burn state is PER-SESSION (keyed by session_id), not shared. Every session
# sees the same account-wide 5h percentage, but each session's payload carries
# the rate_limits of ITS OWN last API response — an idle session refreshing on
# a timer reports a stale (lower) percentage. With a shared state file that
# stale report looked like a window rollover and wiped the history the active
# session had just built; with refreshInterval=300s the wipe recurred exactly
# as often as the minimum-history threshold, so the old shared design never
# left the "collecting" state. A per-session file has a single writer whose
# percentage is monotone within a rate-limit window.
BURN_MAX_SAMPLES = 120
BURN_MIN_SPAN_S = 180  # need >=3 min of history before the slope is trustworthy
BURN_SLOPE_WINDOW_S = 3600  # slope over the last hour of samples
BURN_RESET_JITTER_S = 120  # resets_at drift below this is the same 5h window
BURN_PCT_DROP_RESET = 5.0  # pct drop larger than this means the window rolled over

TOKEN_RATE_WINDOW_S = 1800  # tok/h measured over the last 30 min of transcript
TOKEN_RATE_MIN_SPAN_S = 120

# Speedometer thresholds — projected usage at window reset, % of the 5h budget:
# below 100 we fit inside the window (green); 100..200 we hit the limit before
# the reset (yellow); above 200 we'd need more than double the budget (red).
SPEED_ON_PACE_PCT = 100.0
SPEED_DANGER_PCT = 200.0


def osc8_link(url: str, text: str) -> str:
    """Wrap text in an OSC 8 hyperlink so supporting terminals make it clickable.

    Terminals without OSC 8 support (e.g. macOS Terminal.app) ignore the escape
    sequence and render `text` unchanged — just not clickable. SGR color codes
    already embedded in `text` are preserved inside the link.
    """
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


def format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def format_window(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:g}M"
    if n >= 1_000:
        return f"{n / 1_000:g}k"
    return str(n)


def format_duration(seconds: float) -> str:
    seconds = max(int(seconds), 0)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    if days > 0:
        return f"{days}d {hours}h"
    if hours > 0:
        return f"{hours}h {minutes:02d}m"
    return f"{minutes}m"


def parse_epoch(value) -> float | None:
    """Epoch seconds from a unix number or an ISO-8601 string, else None."""
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return float(value)
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.timestamp()
    except (ValueError, TypeError, OSError):
        return None


def format_model(model: dict, effort: str | None, has_window: bool) -> str:
    name = model.get("display_name") or model.get("id", "?")
    name = name.removeprefix("Claude ").strip()
    if has_window:
        # ctx segment already shows the window size — drop the redundant tag
        name = re.sub(r"\s*[([]1m( context)?[)\]]$", "", name, flags=re.IGNORECASE)
    else:
        mid = model.get("id", "").lower()
        if "1m" in mid and "1m" not in name.lower():
            name = f"{name} (1M)"
    if effort:
        name = f"{name} {DIM}·{effort}{RESET}"
    return name


def read_transcript_usages(transcript_path: str) -> list[tuple[float, dict]]:
    """(epoch_seconds, usage) per API call from the transcript tail.

    A streamed assistant turn is split into one JSONL line per content block,
    each repeating the same `message.usage`. Consecutive lines sharing a
    requestId (or message id) are collapsed to the last one, so each API call
    is counted exactly once — without this, token totals double-count every
    multi-block turn.
    """
    if not transcript_path or not os.path.exists(transcript_path):
        return []
    try:
        size = os.path.getsize(transcript_path)
        with open(transcript_path, "rb") as f:
            if size > TRANSCRIPT_TAIL_BYTES:
                f.seek(size - TRANSCRIPT_TAIL_BYTES)
                f.readline()  # discard the partial first line
            data = f.read().decode("utf-8", errors="replace")
    except OSError:
        return []
    calls: list[tuple[float, dict]] = []
    prev_key = None
    for line in data.splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = entry.get("message")
        if not (isinstance(msg, dict) and isinstance(msg.get("usage"), dict)):
            continue
        ts = parse_epoch(entry.get("timestamp"))
        if ts is None:
            continue
        key = entry.get("requestId") or msg.get("id")
        if key is not None and key == prev_key and calls:
            calls[-1] = (ts, msg["usage"])
        else:
            calls.append((ts, msg["usage"]))
        prev_key = key
    return calls


def context_used(usage: dict) -> int:
    return (
        usage.get("input_tokens", 0)
        + usage.get("cache_creation_input_tokens", 0)
        + usage.get("cache_read_input_tokens", 0)
    )


def format_context(payload: dict, usages: list[dict]) -> tuple[str, bool]:
    """Render the ctx segment. Returns (text, has_window_size).

    Prefers the stdin `context_window` block (correct across /compact) and
    falls back to the transcript's last usage entry only when stdin lacks it.
    """
    cw = payload.get("context_window") or {}
    size = cw.get("context_window_size")
    has_window = isinstance(size, (int, float)) and size > 0

    used = None
    current = cw.get("current_usage")
    if isinstance(current, dict):
        used = context_used(current)
    if used is None and isinstance(cw.get("total_input_tokens"), (int, float)):
        used = int(cw["total_input_tokens"])
    if used is None and usages:
        used = context_used(usages[-1])

    pct = cw.get("used_percentage")
    if pct is None and used is not None and has_window:
        pct = used / size * 100

    if used is None and pct is None:
        return f"ctx: {GRAY}—{RESET}", has_window

    text = "ctx: "
    if used is not None:
        text += format_tokens(used)
        if has_window:
            text += f"{DIM}/{format_window(int(size))}{RESET}"
    if pct is not None:
        color = GREEN if pct < 60 else YELLOW if pct < 85 else RED
        text += f" {color}{pct:.0f}%{RESET}" if used is not None else f"{color}{pct:.0f}%{RESET}"
    return text, has_window


def format_rate_limit(window, label: str, show_reset: bool, now: float) -> str | None:
    if not isinstance(window, dict):
        return None
    pct = window.get("used_percentage")
    if pct is None:
        return None

    if pct >= 90:
        color = RED
    elif pct >= 70:
        color = YELLOW
    else:
        color = GREEN

    reset_str = ""
    if show_reset:
        reset_ts = parse_epoch(window.get("resets_at"))
        if reset_ts is not None:
            reset_str = f" {DIM}(in {format_duration(reset_ts - now)}){RESET}"

    return f"{label}: {color}{pct:.0f}%{RESET}{reset_str}"


def format_cache(usages: list[dict]) -> str:
    """Compute and render the prompt-cache hit ratio.

    Formula
    -------
        hit_ratio = cache_read / (cache_read + cache_creation)

    We deliberately EXCLUDE `input_tokens` from the denominator. `input_tokens`
    represents fresh, uncached content that appears AFTER the cache breakpoint
    (e.g. the current user turn). Including it would conflate two unrelated
    things: "how effective is caching of the stable prefix?" (what we want)
    and "what fraction of the prompt is cacheable at all?" (not useful here —
    it mostly reflects turn size, not cache health).

    Windowing
    ---------
    We smooth over the last 10 API calls (CACHE_WINDOW), not the single
    most-recent call:
      - A single call can be 0% (pure creation, e.g. right after a cache
        invalidation) or 100% (pure read) depending on timing — point-in-time
        is too noisy for a glanceable UI signal.
      - 10 calls span ~30-60 seconds of active work, which captures real
        variance without over-smoothing stale data.

    Thresholds
    ----------
      * ≥75% → green ("healthy"): stable prefix is being reused well.
      * 50-74% → yellow ("watch"): cache is helping, but something is
        regularly invalidating part of the prefix (frequent CLAUDE.md edits,
        tool registry churn, parallel requests).
      * <50% → red ("regression"): prefix is churning. Common root causes:
        edits to CLAUDE.md / MEMORY.md during the session, adding/removing
        skills or MCP servers mid-session, frequent compactions, model
        switching via /model.

    Warming state
    -------------
    Anthropic's default cache TTL is 5 minutes. After idle time the cache
    expires; the next call then shows a large `cache_creation` and near-zero
    `cache_read`, which would flash red as a "regression" — but it's normal
    rebuild behaviour, not churn.

    Heuristic: if the windowed ratio is <50% AND the latest call's creation
    tokens dominate its read tokens, we label it "warming" (gray) instead of
    red. Once subsequent calls hit the freshly-written cache, the ratio
    climbs back into green on its own.
    """
    if not usages:
        return f"cache: {GRAY}—{RESET}"

    total_read = sum(u.get("cache_read_input_tokens", 0) for u in usages)
    total_creation = sum(u.get("cache_creation_input_tokens", 0) for u in usages)
    denom = total_read + total_creation

    if denom == 0:
        return f"cache: {GRAY}—{RESET}"

    ratio = total_read / denom * 100

    latest = usages[-1]
    latest_read = latest.get("cache_read_input_tokens", 0)
    latest_creation = latest.get("cache_creation_input_tokens", 0)
    if ratio < 50 and latest_creation > 0 and latest_creation >= latest_read:
        return f"cache: {GRAY}warming{RESET}"

    if ratio >= 75:
        color = GREEN
    elif ratio >= 50:
        color = YELLOW
    else:
        color = RED
    return f"cache: {color}{ratio:.0f}%{RESET}"


def cache_ttl_seconds(usages: list[dict]) -> int:
    """Prompt-cache TTL detected from the newest usage entry with a
    cache_creation breakdown; CACHE_TTL_FALLBACK_S when none is present."""
    for usage in reversed(usages):
        breakdown = usage.get("cache_creation")
        if isinstance(breakdown, dict):
            if breakdown.get("ephemeral_1h_input_tokens", 0) > 0:
                return 3600
            if breakdown.get("ephemeral_5m_input_tokens", 0) > 0:
                return 300
    return CACHE_TTL_FALLBACK_S


def format_cache_countdown(timed_usages: list[tuple[float, dict]], now: float) -> str | None:
    """Remaining prompt-cache lifetime: '42m' dim, '38s' yellow, 'cold' gray.

    The cache-hit ratio says how WELL the cache works; this says how LONG it
    keeps working: once the countdown hits zero, the next call rebuilds the
    prefix at full cache-write price. Every API call refreshes the TTL, so
    the clock runs from the last transcript usage entry. Purely local
    arithmetic on data already parsed — no extra I/O, no shared state, safe
    at any number of parallel sessions. Caveat: it only ticks when the
    statusline re-renders, so an idle session's countdown is as stale as the
    refreshInterval allows.
    """
    if not timed_usages:
        return None
    last_ts = timed_usages[-1][0]
    ttl = cache_ttl_seconds([usage for _, usage in timed_usages])
    remaining = ttl - (now - last_ts)
    if remaining <= 0:
        return f"{GRAY}cold{RESET}"
    if remaining < CACHE_TTL_WARN_S:
        return f"{YELLOW}{int(remaining)}s{RESET}"
    minutes, seconds = divmod(int(remaining), 60)
    text = f"{minutes}m{seconds:02d}s" if minutes < 10 else f"{minutes}m"
    return f"{DIM}{text}{RESET}"


def burn_state_path(session_id: str) -> str:
    session_key = re.sub(r"[^A-Za-z0-9_-]", "", session_id) or "default"
    return os.path.join(tempfile.gettempdir(), f"claude_statusline_burn_{session_key}.json")


def load_state_file(state_path: str) -> dict:
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state if isinstance(state, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_state_file(state_path: str, state: dict) -> None:
    tmp = f"{state_path}.{os.getpid()}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f)
        os.replace(tmp, state_path)
    except OSError:
        try:
            os.remove(tmp)
        except OSError:
            pass


def update_burn_samples(five_h: dict, now: float, state_path: str) -> list[list[float]]:
    """Append the current (time, used_pct) sample and return the history.

    History resets ONLY on a genuine 5h-window rollover: resets_at moving by
    more than BURN_RESET_JITTER_S, or the percentage dropping sharply. Small
    resets_at drift between API responses and one-point pct wobble must NOT
    wipe the history — over-eager wiping is exactly what kept the old design
    stuck in the "collecting" state forever.
    """
    pct = float(five_h["used_percentage"])
    resets_at = parse_epoch(five_h.get("resets_at"))
    state = load_state_file(state_path)
    samples = state.get("samples")
    if not isinstance(samples, list):
        samples = []
    samples = [s for s in samples if isinstance(s, list) and len(s) == 2]

    prev_reset = state.get("resets_at")
    reset_moved = (
        isinstance(prev_reset, (int, float))
        and resets_at is not None
        and abs(resets_at - prev_reset) > BURN_RESET_JITTER_S
    )
    pct_dropped = bool(samples) and pct < samples[-1][1] - BURN_PCT_DROP_RESET
    if reset_moved or pct_dropped:
        samples = []

    if not samples or pct != samples[-1][1] or now - samples[-1][0] >= 60:
        samples.append([now, pct])
        samples = samples[-BURN_MAX_SAMPLES:]
        save_state_file(state_path, {"resets_at": resets_at, "samples": samples})

    return samples


def compute_burn(samples: list[list[float]], now: float) -> float | None:
    """%-per-hour slope over the recent samples, or None if too little data.

    Least-squares fit over every sample in the window, not just the endpoints:
    used_percentage is integer-quantised, so an endpoint delta jumps a whole
    point at a time — the fit smooths that staircase. Clamped at 0 (a small
    negative slope is quantisation noise, not un-burning).
    """
    recent = [s for s in samples if now - s[0] <= BURN_SLOPE_WINDOW_S]
    if len(recent) < 2 or recent[-1][0] - recent[0][0] < BURN_MIN_SPAN_S:
        return None
    n = len(recent)
    mean_t = sum(t for t, _ in recent) / n
    mean_p = sum(p for _, p in recent) / n
    var_t = sum((t - mean_t) ** 2 for t, _ in recent)
    if var_t == 0:
        return None
    cov = sum((t - mean_t) * (p - mean_p) for t, p in recent)
    return max(cov / var_t * 3600, 0.0)


def compute_token_rate(timed_usages: list[tuple[float, dict]], now: float) -> float | None:
    """Session token throughput in tokens/hour over the recent transcript.

    Counts every token the API processed (input + output + cache read/write) —
    raw throughput, not the opaque rate-limit weighting. The span runs from the
    first in-window call to NOW, so the rate decays while the session idles
    instead of freezing at the last burst's pace.
    """
    recent = [(t, u) for t, u in timed_usages if now - t <= TOKEN_RATE_WINDOW_S]
    if not recent:
        return None
    span = now - recent[0][0]
    if span < TOKEN_RATE_MIN_SPAN_S:
        return None
    total = sum(
        u.get("input_tokens", 0)
        + u.get("output_tokens", 0)
        + u.get("cache_creation_input_tokens", 0)
        + u.get("cache_read_input_tokens", 0)
        for _, u in recent
    )
    return total / span * 3600


def format_burn(
    five_h,
    now: float,
    show_detail: bool,
    session_id: str,
    token_rate: float | None,
) -> str | None:
    """Render the burn speedometer: will this pace fit inside the 5h window?

    The headline number — "▸63%" — is the PROJECTED usage of the 5h budget at
    the moment the window resets, assuming the current pace holds:

        speed = used_pct_now + rate_pct_per_hour × hours_until_reset

    Reading it:
      * ▸63%  green  — at this pace, by the reset we'll only have used 63% of
                       the budget. Comfortable.
      * ▸100%        — we hit the limit EXACTLY at the reset. The boundary.
      * ▸150% yellow — we'd need 1.5× the budget: the limit arrives before the
                       reset does. "⚠100% in 42m" shows when the lockout lands
                       at the current pace.
      * ▸240% red    — more than double the budget: flagrant overshoot. Slow
                       down, offload to a lighter model, or accept the pause.

    The projection is adaptive by construction: it uses the ACTUAL time left
    until the window resets (48 minutes left → 48 minutes of projected burn,
    not a 5-hour constant) and the ACTUAL usage already accumulated — both
    demanded by how the 5h limit really behaves.

    Where the numbers come from
    ---------------------------
    Claude Code reports only the CURRENT used_percentage — no history. Every
    statusline invocation appends a (timestamp, pct) sample to a per-session
    state file in the user tempdir (update_burn_samples), and the pace is a
    least-squares slope over the last hour of samples (compute_burn). The
    dim detail shows that raw pace (~N%/h) plus the session's raw token
    throughput from the transcript (tok/h, compute_token_rate).

    Display states
    --------------
      * "burn: — (2m)" (gray)  — collecting: fewer than 3 minutes of history
                                 (session start or a window rollover); the
                                 countdown shows time until the first reading.
      * "burn: ▸N% (…)"        — the speedometer, colored green/yellow/red at
                                 the 100 / 200 thresholds; detail is dropped on
                                 narrow terminals, "⚠100% in X" collapses to "⚠".
      * "burn: ~N%/h"          — no resets_at in the payload: pace only, no
                                 projection.

    Caveats
    -------
    A linear extrapolation of a bursty process: parallel agent fan-outs spike
    it, idle stretches flatten it. The slope window smooths the noise, but the
    projection is a trend indicator, not a promise — ±20-30% drift is normal,
    and the first reading after warmup leans on whatever burst it saw first.
    The percentage is account-wide, so other concurrent sessions' burn shows
    up here too (correct for "when do I hit MY limit"); tok/h, by contrast,
    counts only this session's transcript.
    """
    if not isinstance(five_h, dict) or five_h.get("used_percentage") is None:
        return None  # no rate-limit data (e.g. API billing) — hide the segment

    samples = update_burn_samples(five_h, now, burn_state_path(session_id))
    rate = compute_burn(samples, now)

    if rate is None:
        span = samples[-1][0] - samples[0][0] if len(samples) >= 2 else 0.0
        wait_min = max(int((BURN_MIN_SPAN_S - span) // 60) + 1, 1)
        return f"burn: {GRAY}— ({wait_min}m){RESET}"

    detail_bits = [f"~{rate:.0f}%/h" if rate >= 10 else f"~{rate:.1f}%/h"]
    if token_rate is not None:
        detail_bits.append(f"{format_tokens(int(token_rate))} tok/h")
    detail = f" {DIM}({', '.join(detail_bits)}){RESET}"

    pct = float(five_h["used_percentage"])
    reset_ts = parse_epoch(five_h.get("resets_at"))
    if reset_ts is None:
        return f"burn: {detail_bits[0]}"  # can't project without a reset time

    hours_left = max(reset_ts - now, 0.0) / 3600
    speed = pct + rate * hours_left  # projected usage at window reset, % of budget
    # Color from the ROUNDED value — the number actually shown — so a 99.7
    # that displays as "▸100%" is never painted green.
    speed_shown = round(speed)

    if speed_shown < SPEED_ON_PACE_PCT:
        color = GREEN
    elif speed_shown < SPEED_DANGER_PCT:
        color = YELLOW
    else:
        color = RED

    text = f"burn: {color}▸{speed_shown}%{RESET}"
    if speed_shown >= SPEED_ON_PACE_PCT and rate > 0 and pct < 100:
        eta = format_duration((100 - pct) / rate * 3600)
        text += f" {color}⚠100% in {eta}{RESET}" if show_detail else f" {color}⚠{RESET}"
    if show_detail:
        text += detail
    return text


def terminal_cols() -> int:
    try:
        return int(os.environ.get("COLUMNS", ""))
    except ValueError:
        return 999


ROW_SEP = f" {DIM}·{RESET} "
# Cost tier at a glance: fable/opus expensive (yellow), sonnet mid (green),
# haiku cheap (gray). Unrecognized families render uncolored.
MODEL_TIER_COLORS = {"fable": YELLOW, "opus": YELLOW, "sonnet": GREEN, "haiku": GRAY}

SPARK_BARS = "▁▂▃▄▅▆▇█"
SPARK_WIDTH = 12  # bars shown; each bar is one tokenSamples interval
# A pause under this many seconds renders as a gap in the sparkline (the
# agent is probably thinking or inside a tool call); past it, the flat tail
# collapses into a yellow ⏸ marker with the REAL stall age. The age is
# measured by persisting each task's last tokenCount change per session —
# the ~80s tokenSamples window alone cannot say how long a stall has lasted.
SPARK_STALL_WARN_S = 40


def format_task_model(model_id: str) -> str:
    """Short colored form of a resolved model ID: claude-sonnet-5 -> sonnet-5."""
    # Strip date stamps and the "[1m]" window tag — the per-task ctx percent
    # already shows the window size.
    short = re.sub(r"\[\d+m\]$", "", re.sub(r"-20\d{6}$", "", model_id.removeprefix("claude-")))
    color = MODEL_TIER_COLORS.get(short.split("-", 1)[0], "")
    return f"{color}{short}{RESET}" if color else short


def format_task_elapsed(start_time, now: float) -> str | None:
    started = parse_epoch(start_time)
    if started is None:
        return None
    if started > 1e12:  # epoch milliseconds
        started /= 1000.0
    elapsed = now - started
    if elapsed < 0:
        return None
    return f"{int(elapsed)}s" if elapsed < 60 else format_duration(elapsed)


def task_state_path(session_id: str) -> str:
    session_key = re.sub(r"[^A-Za-z0-9_-]", "", session_id) or "default"
    return os.path.join(tempfile.gettempdir(), f"claude_statusline_agents_{session_key}.json")


def update_task_activity(tasks, session_id: str, now: float) -> dict[str, float]:
    """Seconds since each task's tokenCount last grew, keyed by task id.

    tokenSamples covers only ~80s of history, so a stall's true age must be
    measured here: the per-session state file remembers (tokenCount, ts of
    last change) per task. Entries for tasks no longer in the payload are
    pruned, and the file is rewritten only when something changed — a fully
    stalled panel costs zero writes. Single writer per session (each session
    renders its own panel), so 20 parallel sessions never contend.
    """
    state = load_state_file(task_state_path(session_id))
    entries = state.get("tasks")
    if not isinstance(entries, dict):
        entries = {}
    fresh: dict[str, list[float]] = {}
    stall_ages: dict[str, float] = {}
    for task in tasks:
        if not isinstance(task, dict) or not task.get("id"):
            continue
        count = task.get("tokenCount")
        if not isinstance(count, (int, float)):
            continue
        task_id = str(task["id"])
        prev = entries.get(task_id)
        if isinstance(prev, list) and len(prev) == 2 and prev[0] == count:
            fresh[task_id] = prev
            stall_ages[task_id] = max(now - float(prev[1]), 0.0)
        else:
            fresh[task_id] = [count, now]
            stall_ages[task_id] = 0.0
    if fresh != entries:
        save_state_file(task_state_path(session_id), {"tasks": fresh})
    return stall_ages


def format_stall_age(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}m{secs:02d}s" if minutes < 10 else format_duration(seconds)


def format_token_sparkline(samples, stall_age_s: float) -> str | None:
    """Activity sparkline with an explicit pause tail.

    tokenSamples (undocumented; verified against a live 2.1.220 payload and
    the Claude Code bundle) is a monotone cumulative token counter sampled
    every ~5s, capped at 16 entries — bundle-derived numbers that may change,
    so this draws the SHAPE of the deltas, never an absolute rate. Bursts
    mean the agent is consuming tokens; zero growth means thinking or a tool
    call. The trailing zero-run is split off with a space — `▂▅█▃ ▁▁▁` — so
    the eye sees WHERE activity stopped; once the pause outlives
    SPARK_STALL_WARN_S it collapses into a yellow `⏸<age>` carrying the real
    stall duration from update_task_activity. Rendered inside the DIM tail,
    so the yellow run ends with DIM_FG to keep the tail dim.
    """
    counts = (
        [s for s in samples if isinstance(s, (int, float))] if isinstance(samples, list) else []
    )
    deltas = [max(later - earlier, 0) for earlier, later in zip(counts, counts[1:])]
    deltas = deltas[-SPARK_WIDTH:]
    trailing = 0
    for delta in reversed(deltas):
        if delta > 0:
            break
        trailing += 1
    active = deltas[: len(deltas) - trailing]
    bars = ""
    if active:
        peak = max(active)
        top = len(SPARK_BARS) - 1
        bars = "".join(
            SPARK_BARS[0] if delta <= 0 else SPARK_BARS[max(1, round(delta / peak * top))]
            for delta in active
        )
    if stall_age_s >= SPARK_STALL_WARN_S:
        pause = f"{YELLOW}⏸{format_stall_age(stall_age_s)}{DIM_FG}"
        return f"{bars} {pause}" if bars else pause
    if bars and trailing:
        return f"{bars} {SPARK_BARS[0] * trailing}"
    return bars or None


def format_subagent_row(task, now: float, stall_age_s: float = 0.0) -> dict | None:
    """Build one {"id", "content"} override for an agent-panel row.

    Tasks without a resolved `model` (absent until resolution, Claude Code
    >= 2.1.205) return None and keep the default rendering — without the
    model there is nothing to add over what the panel already shows. `type`
    is never rendered: the panel filter only ever passes local_agent tasks
    (verified against the 2.1.220 bundle), so it carries no information.
    """
    if not isinstance(task, dict) or not task.get("id") or not task.get("model"):
        return None
    model_str = format_task_model(str(task["model"]))
    effort = task.get("effort")
    if effort is not None:
        model_str += f"{DIM}·{effort}{RESET}"
    # A real `name` exists only for addressable agents; otherwise lead with
    # the model instead of repeating a constant filler word on every row.
    agent_name = task.get("name")
    segments = [f"{agent_name} {model_str}" if agent_name else model_str]
    # `label` carries the live progress summary for agent tasks (Claude Code
    # itself falls back to the static description); newlines in model-authored
    # text would break the one-row output contract, so flatten them.
    description = task.get("label") or task.get("description")
    if description:
        segments.append(str(description).replace("\n", " "))
    tail_bits = []
    # Elapsed is computed from startTime on every refresh, so it would keep
    # ticking after the task ends — show it only while the task runs.
    if task.get("status") in (None, "running"):
        elapsed = format_task_elapsed(task.get("startTime"), now)
        if elapsed:
            tail_bits.append(elapsed)
        spark = format_token_sparkline(task.get("tokenSamples"), stall_age_s)
        if spark:
            tail_bits.append(spark)
    tokens = task.get("tokenCount")
    if isinstance(tokens, (int, float)) and tokens > 0:
        window = task.get("contextWindowSize")
        if isinstance(window, (int, float)) and window > 0:
            # Same thresholds as the main ctx segment. The tail is wrapped in
            # DIM, so the colored percent ends with DIM_FG, not RESET.
            pct = tokens / window * 100
            color = GREEN if pct < 60 else YELLOW if pct < 85 else RED
            tail_bits.append(
                f"↓ {format_tokens(int(tokens))}/{format_window(int(window))}"
                f" {color}{pct:.0f}%{DIM_FG}"
            )
        else:
            tail_bits.append(f"↓ {format_tokens(int(tokens))} tok")
    if tail_bits:
        segments.append(f"{DIM}{' · '.join(tail_bits)}{RESET}")
    return {"id": task["id"], "content": ROW_SEP.join(segments)}


def print_subagent_rows() -> None:
    """subagentStatusLine mode (--subagents): re-render each agent-panel row.

    Replaces the default `agentType · description · token count` row with
    `[name ]model·effort · live summary · elapsed · sparkline · ↓ used/window %`,
    so the resolved model and the agent's health are visible at a glance.

    stdin: one JSON object with a `tasks` array (`id`, `name`, `type`,
    `status`, `description`, `label`, `startTime`, `model`, `effort`,
    `tokenCount`, ...). `model` is the RESOLVED model ID (needs Claude Code
    >= 2.1.205) and is absent until resolution — such tasks are skipped, and
    per the output protocol a task without an override line keeps Claude
    Code's default rendering.

    stdout: one {"id", "content"} JSON line per overridden row; `content` is
    rendered as-is, ANSI colors included.
    """
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        return
    now = time.time()
    try:
        stall_ages = update_task_activity(tasks, str(payload.get("session_id") or ""), now)
    except Exception:
        stall_ages = {}
    for task in tasks:
        # One malformed task must never cost the whole tick: a nonzero exit
        # (or an uncaught exception) makes Claude Code drop EVERY row's
        # decoration for this refresh, not just this one.
        try:
            row = format_subagent_row(
                task, now, stall_ages.get(str(task.get("id") or ""), 0.0)
            )
        except Exception:
            continue
        if row:
            print(json.dumps(row, ensure_ascii=False))


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        payload = {}

    now = time.time()
    model = payload.get("model") or {}
    effort = (payload.get("effort") or {}).get("level")
    session_id = payload.get("session_id") or ""
    transcript_path = payload.get("transcript_path", "")
    rate_limits = payload.get("rate_limits") or {}
    show_detail = terminal_cols() >= NARROW_COLS

    timed_usages = read_transcript_usages(transcript_path)
    usages = [usage for _, usage in timed_usages[-CACHE_WINDOW:]]

    ctx_str, has_window = format_context(payload, usages)
    parts = [ctx_str, format_model(model, effort, has_window)]
    rate_segments = []
    for key, label in (("five_hour", "5h"), ("seven_day", "7d")):
        seg = format_rate_limit(rate_limits.get(key), label, show_detail, now)
        if seg:
            rate_segments.append(seg)
    if rate_segments:
        # One clickable link spanning the whole "5h … │ 7d …" run (separator
        # included), so clicking anywhere on it opens the usage page.
        parts.append(osc8_link(USAGE_URL, SEP.join(rate_segments)))
    cache_seg = format_cache(usages)
    countdown = format_cache_countdown(timed_usages, now)
    if countdown:
        cache_seg += f" {countdown}"
    parts.append(cache_seg)
    burn = format_burn(
        rate_limits.get("five_hour"),
        now,
        show_detail,
        session_id,
        compute_token_rate(timed_usages, now),
    )
    if burn:
        parts.append(burn)
    print(SEP.join(parts))


if __name__ == "__main__":
    # Windows pipes default to the ANSI code page: printing │ ↓ · or reading a
    # non-ASCII path from the payload would crash the script (a blank status
    # line). Claude Code talks UTF-8 both ways, so use it on both streams.
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    if "--subagents" in sys.argv:
        print_subagent_rows()
    else:
        main()
