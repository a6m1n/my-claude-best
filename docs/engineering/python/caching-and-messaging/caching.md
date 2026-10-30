# Caching

Rules for Python code that keeps copies of data in a cache, so that a request still gets the right
answer when the copy is missing, old or out of reach.

**Navigation**

- [1. Purpose and scope](#1-purpose-and-scope)
- [2. Which cache](#2-which-cache)
- [3. Cache-aside: read through the cache, write to the store](#3-cache-aside-read-through-the-cache-write-to-the-store)
- [4. Expiry](#4-expiry)
- [5. Many requests rebuilding one key](#5-many-requests-rebuilding-one-key)
- [6. What goes into the cache](#6-what-goes-into-the-cache)
- [7. An instance of its own, and its eviction policy](#7-an-instance-of-its-own-and-its-eviction-policy)
- [8. The client: built once, closed at shutdown](#8-the-client-built-once-closed-at-shutdown)
- [9. Timeouts and retries](#9-timeouts-and-retries)
- [10. When the cache is down](#10-when-the-cache-is-down)
- [11. Common mistakes](#11-common-mistakes)
- [12. Where the rules stop holding](#12-where-the-rules-stop-holding)
- [13. Alternatives considered](#13-alternatives-considered)
- [14. Security and personal data](#14-security-and-personal-data)
- [15. Checks](#15-checks)
- [16. Sources](#16-sources)

## 1. Purpose and scope

A cache keeps a copy of an answer that costs time to get again: a slow query, a call to another
service. This file is for the programmer who puts a cache in front of such a call in a Python
service, people and AI agents alike. Read it before you add a cache, change what it holds or for
how long, or build the client of a shared cache.

A service that follows this file saves the cost of the slow call on most reads, and still answers
right when a copy is missing, old or out of reach: every copy expires, every change to the data
removes its copy, and a cache that fails counts as a miss.

**The one rule: the cache holds copies; the data store holds the truth.** Any value in the cache
can be gone at any moment, and the code then reads the store. Azure's caching guidance puts it as
"don't use the cache as the authoritative store of critical information" [1].

What this file covers: an in-process cache (`functools`, cachetools) and a shared cache on Valkey
or Redis, from Python code. The code assumes Python 3.11 or newer and the asyncio clients
valkey-py 6.2.0 and redis-py 8.1.0, the versions read for it. The sync clients take the same
arguments, and redis-py 8.1.0's sync client has the same timeout and retry defaults as its asyncio
one [2], [3].

Left out on purpose: running the cache server (clustering, replication, persistence, upgrades);
HTTP caching in browsers and CDNs; the session store of a web application, which
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2
owns; task queues that run on Valkey or Redis, which [task-queues.md](task-queues.md) owns; and
the general retry rule for calls between services: which layer retries, how many retries a call
may spend, and the shape of the backoff. Section 9 keeps only what a cache call on a request path
needs: each client's defaults and a small retry count.

Not covered yet, because the research found no owner source: a rule for adding random jitter to
expiry times; a version of the value's shape in the cache key, and what to do with old copies
after the model changes; a timeout value for a cache on the request path (section 9); an
independent test of current Valkey; when Memcached fits a Python service better than Valkey; and
how many teams use each tool, since the surveys do not ask and downloads include CI runs.

How existing code moves to these rules, and the line a project's `CLAUDE.md` gets for them, are in
[README.md](README.md).

## 2. Which cache

### In-process first

The simplest cache is memory inside the process. It is enough while each process may keep its own
copy. With several instances of the service, each instance then holds its own copy of the data,
and the same query can return different results on two instances [1]. Move to a shared cache
when the instances must see the same copy, or one change must clear the copy for all of them: a
shared cache gives every instance the same view [1]. Until that need appears, a shared cache is
too much: it is slower to reach than local memory, and it is one more service to run [1].

| Tool | Use it when | Too much, or the risk |
|---|---|---|
| `functools.lru_cache`, `functools.cache` | A function of hashable arguments whose answer never goes stale. The cache is thread-safe [4]. | It has no expiry. It does not promise one call per key: another thread can call the function again before the first call finishes [4]. |
| cachetools `TTLCache` | The copy must expire after a set time. | Its classes are not thread-safe [5]. Guard the cache with the decorator's `lock`, or with `condition`, which also makes a thread that asks for the same key wait for the call already running, at some cost in speed [5]. |

The excerpt below keeps exchange rates for ten minutes inside the one client of the rates provider.
It leaves out the call that fetches a rate.

```python
"""The one client of the exchange-rates provider: every call to it goes through here."""

import threading
from decimal import Decimal
from typing import Final

import httpx
from cachetools import TTLCache, cachedmethod

from acme.core.schemas import Currency

# The quote page may show a rate up to ten minutes old; rates change a few times a day.
RATE_TTL_SECONDS: Final = 600


class RatesClient:
    def __init__(self, http: httpx.Client) -> None:
        self._http = http
        self._rates: TTLCache[Currency, Decimal] = TTLCache(
            maxsize=64, ttl=RATE_TTL_SECONDS
        )
        # cachetools caches are not thread-safe. The condition guards this one and
        # makes a second thread wait for a rate already being fetched
        # (caching.md section 2).
        self._rates_ready = threading.Condition()

    @cachedmethod(lambda self: self._rates, condition=lambda self: self._rates_ready)
    def rate(self, currency: Currency) -> Decimal:
        ...
```

It is good because the cache lives in the one client of the provider and is built with it
([file-structure.md](../../any-language/file-structure/file-structure.md) section 4), so a test gets a
fresh cache with each client. The expiry has a name and a reason, the thread safety comes from
cachetools' own `condition`, and the currency is a closed set, not a bare `str`
([python.md](../language/python.md) section 3).

### A shared cache: Valkey or Redis

| Tool (Python client) | Use it when | Too much, or the risk |
|---|---|---|
| Valkey (valkey-py) | A new shared cache. Valkey is under the BSD 3-Clause licence [6] and is an open community project under LF Projects [7]. Its governance file allows no more than one third of its Technical Steering Committee to come from one organisation [8]. AWS prices ElastiCache for Valkey 20% below Redis OSS on nodes, and its serverless Valkey 33% below the other engines it offers [9]. Google offers Memorystore for Valkey, beside Memorystore for Redis Cluster [10]. | One process is enough (above). Valkey cannot read the data files of Redis CE 7.4 and later [11]. No independent test of current Valkey was found (section 1). |
| Redis (redis-py) | Redis already runs and its licence is accepted. redis-py ships an asyncio client [12]. | The licence changed twice: BSDv3 up to 7.2, RSALv2 or SSPLv1 for 7.4 to 7.8, and from 8.0 a choice of RSALv2, SSPLv1 or AGPLv3 [13]. |

**Valkey for a new cache, Redis where it runs.** Valkey says it is compatible with Redis OSS 7.2
and all earlier open-source versions [11], so the commands in this file work on both. A cache
holds only copies, so a later move from Redis to Valkey starts with an empty cache and needs no
data migration; the data files Valkey cannot read [11] are not needed.

**The client against Valkey: valkey-py in new code, redis-py where the code already has it.**

| Client | Use it when | Too much, or the risk |
|---|---|---|
| valkey-py | New code against Valkey. It is one of the two Python clients on Valkey's client page [14], and it was created as a fork of redis-py [15]; the rules below were read in the source of both. | Fewer downloads, CI runs included: about 4.75 million in the month before 2026-10-29, against about 200 million for redis-py [16], [17]. Its docs give no timeout, retry or close guidance [18], and its defaults differ from redis-py's (section 9). |
| redis-py | Code that already uses it, against Redis or after a move to Valkey. Valkey says existing Redis client libraries connect to Valkey without code changes [11], and AWS's list of behaviour changes between Valkey versions names no break for redis-py [19]. | Valkey's client page does not list it [14], and its README names only Redis server versions [20]. Its README says redis-py 8.2.0 needs Python 3.11 or newer [20]. Its default retries can hold a request while the cache is down (section 9). |

Weighed against each other, redis-py has three things for it: it checks the server's name by
default, where valkey-py 6.2.0 does not [35], [34]; redis.io gives it the timeout and retry
guidance that valkey-py's docs lack [39], [18]; and Valkey says existing Redis clients connect
without code changes [11]. Against it, its README names only Redis server versions [20], so its
work against Valkey rests on Valkey's word, not on its own. valkey-py stays the pick for new code
against Valkey: it is on Valkey's client page [14], and it is maintained, with 6.2.0
released on 12 October 2026 [42]. Its one unsafe default is closed in the code: section 9's
client writes `ssl_check_hostname=True`.

valkey-glide, the other client on Valkey's page, is named here and not described: its Python
package supports Python 3.9 to 3.13 and does not support Alpine Linux (musl) [21], and it
supports Redis open source only up to 7.2 [22].

## 3. Cache-aside: read through the cache, write to the store

Cache-aside is the default. On a read, the code tries the cache; on a miss, it reads the store,
adds the copy to the cache and returns it. On a change, it writes the store and then removes the
copy [23].

Do not cache an item when, in Azure's list [23]:

- it is sensitive or security related, above all when several applications or users share the
  cache: read it from the store every time;
- the whole data set is static and fits in the cache: load it at startup with no expiry instead;
- most requests miss: checking and filling the cache then costs more than it saves;
- it is the session state of a web application on several servers:
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2
  owns the session store.

The rules:

- **On a read, try the cache; on a miss, read the store, write the copy with its expiry
  (section 4), and return it.** The cache then fills with what readers ask for, and nothing else.
- **On a change, update the store first, then remove the copy.** Azure's note on the pattern:
  "Update the data store *before* removing the item from the cache" [23]. If the copy goes first,
  a reader can miss in between, load the old value from the store and put it back [23]. Remove the
  copy after the store's transaction commits, since before the commit a reader still loads the old
  value.
- **Expect a window of old data after a change.** Between the write and the next read, a
  reader can miss or briefly see the old value; for a read path that needs the new value at once,
  Azure points to write-through caching [23] (section 13). The window can last until the expiry:
  a reader that loaded the value before the change can write it back after the removal
  (section 4).

The file below holds the catalog's copies of products in the shared cache. Both catalog modules
use it and neither owns it, so it sits in `src/acme/core/product_cache.py`, and the `Product` and
`ProductId` types it names sit in `core/schemas.py`
([file-structure.md](../../any-language/file-structure/file-structure.md) section 4).

```python
"""The catalog's copies of products in the shared cache."""

import logging
from typing import Final

from valkey import exceptions as cache_errors
from valkey.asyncio import Valkey

from acme.core.schemas import Product, ProductId

logger = logging.getLogger(__name__)

# The errors of a cache that cannot be reached; any other error is a bug and is raised.
CACHE_DOWN: Final = (cache_errors.ConnectionError, cache_errors.TimeoutError)

# A product page may show a price up to five minutes old. This is the real bound: a
# failed removal, or a reader that loaded before a change, leaves an old copy until
# it ends (caching.md section 4).
PRODUCT_TTL_SECONDS: Final = 300


def _cache_key(product_id: ProductId) -> str:
    return f"catalog:product:{product_id}"


async def read_product(cache: Valkey, product_id: ProductId) -> Product | None:
    """The cached copy, or None: no copy, or the cache is down (a miss either way)."""
    try:
        cached = await cache.get(_cache_key(product_id))
    except CACHE_DOWN:
        # Departs from python.md section 2 (a failure turned into None): a cache outage
        # must not become a service outage (caching.md section 10). The cost: every
        # read goes to the database while the cache is down.
        logger.warning("Cache read failed, product %s comes from the store", product_id)
        return None

    if cached is None:
        return None

    # A copy from the cache is outside data: parse it once (python.md section 4).
    return Product.model_validate_json(cached)


async def store_product(cache: Valkey, product: Product) -> None:
    try:
        # JSON, never pickle (caching.md section 6); the expiry goes in the same
        # SET (caching.md section 4).
        await cache.set(
            _cache_key(product.id), product.model_dump_json(), ex=PRODUCT_TTL_SECONDS
        )
    except CACHE_DOWN:
        # Departs from python.md section 2 (an except that carries on): a cache outage
        # must not become a service outage (caching.md section 10). The cost: no copy
        # is stored, so the next read goes to the database again.
        logger.warning("Cache write failed for product %s", product.id)


async def forget_product(cache: Valkey, product_id: ProductId) -> None:
    try:
        await cache.delete(_cache_key(product_id))
    except CACHE_DOWN:
        # Departs from python.md section 2 (an except that carries on): a cache outage
        # must not become a service outage (caching.md section 10). The cost: the old
        # copy lives until PRODUCT_TTL_SECONDS ends it.
        logger.warning("Cache delete failed for product %s", product_id)
```

The two use cases, each the `usecase.py` of its own module; the excerpts leave out the imports and
the case of a product that does not exist.

```python
# src/acme/catalog/get_product/usecase.py
async def get_product(
    product_id: ProductId, cache: Valkey, session: AsyncSession
) -> Product:
    cached = await product_cache.read_product(cache, product_id)
    if cached is not None:
        return cached

    product = await repository.load_product(session, product_id)
    await product_cache.store_product(cache, product)

    return product
```

```python
# src/acme/catalog/change_price/usecase.py
async def change_price(
    product_id: ProductId, price: Decimal, cache: Valkey, session: AsyncSession
) -> None:
    await repository.update_price(session, product_id, price)
    await session.commit()

    # After the commit: removing the copy first lets a reader put the old price
    # back (caching.md section 3).
    await product_cache.forget_product(cache, product_id)
```

They are good because each step the rules name is at its own line: the miss falls through to the
store, the copy is written with its expiry, and the copy is removed only after the commit. The
cache file catches only the errors of a cache that cannot be reached and logs one `WARNING` where
it falls back ([logging.md](../logging/logging.md) sections 4 and 5); the line names the product id
and no value ([logging.md](../logging/logging.md) section 10). The client and the session are
parameters, built once by the adapter (section 8).

## 4. Expiry

- **Write every copy with its expiry, in the same command:** `set(key, value, ex=seconds)`, where
  `ex` is the expiry in seconds [24]. Redis clears a key's timeout when a command overwrites
  the key, `SET` included [25], so an expiry set apart from the write is lost at the next
  write, and a copy written without one stays until it is evicted.
- **Pick the expiry from how old a copy its reader may see.** No owner gives a number, only the
  trade-off: too short, and the application keeps reloading from the store; too long, and the copy
  goes stale [23], [1]. Use one default expiry for the cache's items [1], and a longer one for an
  item that costs a lot to load again [23].
- **Let the expiry bound every old copy.** Section 3 removes the copy on every change, but two
  old copies outlive that removal: one whose removal failed, and one written back by a reader that
  loaded the value before the change. Nishtala et al., describing Facebook's memcached, call the
  second a stale set, which "can occur when concurrent updates to memcache get reordered" [28].
  The expiry ends both, so it is the real bound on how old a copy can be: set it no longer than
  the oldest value the page may show.

Adding random jitter to expiry times has no owner source yet (section 1).

## 5. Many requests rebuilding one key

This section holds only for a key that many requests read at the same time. When such a key
expires, every request that misses starts to rebuild it at once. Vattani, Chierichetti and
Lowenstein call this a cache stampede and write that it "severely limits the performance of
databases and web servers" [26]; AWS's Builders' Library calls it the "thundering herd" [27].
A key that few requests read at once, or that is cheap to load, does not need this section: the
plain read of section 3 is enough.

- **In one process, let one call per key run.** cachetools' `condition` makes the other threads wait
  for the call already running, while a lock alone "may still be subject to cache stampede issues
  under high load" [5]. `functools` gives no such promise [4].
- **In a shared cache, let one request per key rebuild it.** At Amazon, the Builders' Library says,
  services use request coalescing, where "the servers or external cache ensure that only one
  pending request is out for uncached resources" [27]. In the memcached deployment Facebook describes, the servers did this
  with leases: a server gives one client a token to fill a missing key and tells the others to wait
  a short time [28]. Leases live in the memcached server; with Valkey or Redis the application
  takes a lock per key instead:
  1. On a miss, try to take the key's lock: `set(lock_key, token, nx=True, ex=lock_seconds)`, where
     `nx=True` writes only if the key does not exist yet [24].
  2. The request that gets the lock loads the value, writes the copy and releases the lock.
  3. The others wait a short time and read the cache again, as Facebook's clients do without a
     lease [28]. A request that still finds no copy after its wait reads the store.

  Build the lock's expiry, its holder's own value and the release that checks that value the way
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2
  builds the lock around a token refresh.

Probabilistic early expiration is the named alternative: in Vattani et al.'s algorithm, each reader
may rebuild the value a little before it expires, with a chance that grows as the expiry nears, and
the value is stored with the time its last rebuild took [26] (section 13).

## 6. What goes into the cache

- **Store the Pydantic model's JSON (`model_dump_json`), and parse what you read back with the same
  model (`model_validate_json`).** A value read from the cache is outside data
  ([python.md](../language/python.md) section 4), and JSON can be read by a service in another
  language.
- **Never pickle a value for a shared cache.** Whoever can write to the cache could then run code in
  your process: Python's docs warn that "It is possible to construct malicious pickle data which will
  execute arbitrary code during unpickling", and suggest formats such as `json` for data you do not
  trust [29].

A version of the value's shape in the key, for the day the model changes, has no owner source yet
(section 1).

## 7. An instance of its own, and its eviction policy

- **Give the cache an instance of its own.** Keep a task queue, or any other data that must not
  vanish, on another instance. Redis's docs say to consider two separate instances over one that
  holds both cache keys and persistent keys, and Valkey's say two instances are "usually a better
  idea" [30], [31].
- **On the cache instance, set `maxmemory` and `maxmemory-policy allkeys-lru`.** Every key there is a
  copy, so any key may go: Redis's docs call `allkeys-lru` "a good default option if you have no
  reason to prefer any others" [30], and Valkey's give the same advice for requests whose
  popularity follows a power law [31]. The shipped config files set no memory limit and the policy
  `noeviction` [32], [33], and a limit of zero means no limit on 64-bit systems [30].
  With `noeviction`, a full server returns an error to every command that would add data [30].

```text
# valkey.conf of the cache instance; on a managed service, the same two parameters.
# 2gb stands for the memory this cache may use. Without a limit it grows until the
# machine runs out (caching.md section 7).
maxmemory 2gb
# Every key here is a copy of stored data, so any key may be evicted
# (caching.md section 7).
maxmemory-policy allkeys-lru
```

It is good because both values are set, each with its reason, and the memory limit is marked as the
number to size for the machine.

| Field | What it means | Set it when | Leave it out when |
|---|---|---|---|
| `maxmemory` | The most memory the data may use. `0`, the default on 64-bit systems, means no limit [30]. | Always on a cache instance (required). | Never on a cache instance. |
| `maxmemory-policy` | Which keys go when `maxmemory` is reached. The shipped default is `noeviction`: no key goes, and writes fail with an error [32], [30]. | Always on a cache instance (required): `allkeys-lru`. | The instance holds data that must not vanish; then it is not your cache instance. |

## 8. The client: built once, closed at shutdown

- **Build one client per process at startup, and hand it in.**
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 4 asks this of the
  client of every external system. A client built without a pool builds its own and is expected to
  close it [34], [35], so one instance serves every request.
- **Close the asyncio client at shutdown, with `await cache.aclose()` or an `async with` around its
  life.** redis-py's docs: "Using asyncio Redis requires an explicit disconnect of the connection
  since there is no asyncio deconstructor magic method" [12]. Closing the client closes the pool
  it built [34], [35]. In both clients `async with` calls `aclose()` on exit, and redis-py
  closes only when the last of several nested `async with` blocks ends [34], [35].
- **When several clients share one pool, build the pool yourself and close it yourself.**
  `Valkey(connection_pool=pool)` and `Redis(connection_pool=pool)` never close a pool they are given
  [35], [34]. `from_pool(pool)` makes the client the pool's owner, and closing the client
  closes the pool [35], [34]. So never build two clients from one pool with `from_pool`:
  redis-py's source warns that "when one client is closed it will disconnect connections still in
  use by the others" [34]. A single client needs no pool of its own making.

The excerpt below is the app factory of a FastAPI service; it leaves out the imports and the
routes.

```python
def build_app(settings: Settings) -> FastAPI:
    cache = build_cache(
        host=settings.cache_host,
        port=settings.cache_port,
        user=settings.cache_user,
        password=settings.cache_password,
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        yield
        # The asyncio client has no destructor that closes it (caching.md section 8).
        await cache.aclose()

    app = FastAPI(lifespan=lifespan)
    app.include_router(build_catalog_router(cache))

    return app
```

It is good because the adapter is the one place that turns settings into the client
([python.md](../language/python.md) section 5), builds it once per process and closes it when the
process stops. The routes get the client as a parameter, never the settings.

## 9. Timeouts and retries

**Set the timeouts and the retry on the client yourself; never take the defaults.** The two clients'
defaults differ, and redis-py's can hold a request for a long time while the cache does not answer:

- redis-py 8.1.0 waits 5 s for a connection and 5 s for an answer, and retries up to ten times
  after the first try, with a random backoff capped at 1 s [34], [3], [36]. A cache that does not
  answer can then hold one request for about a minute: eleven tries of up to 5 s each, plus the
  pauses.
- valkey-py 6.2.0 waits 5 s for an answer, takes the same value for the connection, and does not
  retry unless it is given a `Retry` [35], [37].

The rules:

- **On a request path, keep the retry count small, and never negative.** One retry covers a dropped
  connection. A negative count retries forever in both clients [36], [38].
- **Pick the timeout from what the request can spend; no owner gives a number.** redis.io's guide
  names the trade-off: too long, and "your app might hang unnecessarily while waiting for a response
  that will never arrive"; too short, and redis-py "might retry commands that would have succeeded
  if given more time" [39]. A cache read pays only while it is faster than the store read it
  saves.
- **Leave `retry_on_timeout` out.** redis-py has deprecated it since 6.0.0, because `TimeoutError` is
  retried by default [34]; valkey-py 6.2.0's `Retry` retries `TimeoutError` by default too [38].
- **If a worker's connections sit idle between bursts, set `health_check_interval`.** The client then
  sends a `PING` on a connection idle for longer than the interval, before its next command
  [39]. The default 0 turns it off [34], [35]. Health checks are retried like any other
  command [39].

| Field | What it means | Set it when | Leave it out when |
|---|---|---|---|
| `socket_timeout` | How long one command waits for the answer. Default 5 s in both clients [3], [35]. | Always (required): below what the caller can spend on the cache. | Never. |
| `socket_connect_timeout` | How long opening a connection may take. Default 5 s in redis-py [3]; in valkey-py, the value of `socket_timeout` [37]. | Always (required). | Never. |
| `retry` | A `Retry(backoff, retries)`: how many times a command is tried again after a connection error or a timeout [36], [38]. Default: ten retries in redis-py 8.1.0 [3], none in valkey-py 6.2.0 [37]. | Always (required): a small count on a request path. | Never. A negative count retries forever [36], [38]. |
| `retry_on_timeout` | An older switch that adds `TimeoutError` to the retried errors. | Never. | Always: deprecated in redis-py [34], and already in valkey-py's `Retry` [38]. |
| `health_check_interval` | Seconds a connection may sit idle before the client pings it ahead of the next command [39]. Default 0, off [34], [35]. | Workers and jobs whose connections sit idle between bursts. | A web service whose connections are in use all the time. |

```python
"""The one client of the shared cache: every call to it goes through here."""

from typing import Final

from pydantic import SecretStr
from valkey.asyncio import Valkey
from valkey.asyncio.retry import Retry
from valkey.backoff import FullJitterBackoff

# No owner gives a number. A cache read must cost less than the database read it
# saves; this service's database answers in about 0.1 s (caching.md section 9).
CACHE_TIMEOUT_SECONDS: Final = 0.2


def build_cache(host: str, port: int, user: str, password: SecretStr) -> Valkey:
    return Valkey(
        host=host,
        port=port,
        # An ACL user that may run only the commands this service sends
        # (caching.md section 14).
        username=user,
        password=password.get_secret_value(),
        # TLS, with the server's name checked: valkey-py 6.2.0 does not check it
        # unless told to (caching.md section 14).
        ssl=True,
        ssl_check_hostname=True,
        socket_timeout=CACHE_TIMEOUT_SECONDS,
        socket_connect_timeout=CACHE_TIMEOUT_SECONDS,
        # One retry, after a pause of at most 50 ms, covers a dropped connection;
        # more would hold the request while the cache is down (caching.md section 9).
        retry=Retry(FullJitterBackoff(cap=0.05, base=0.01), retries=1),
    )
```

It is good because every value that decides how long a request can wait is set at the one place
the cache client is built, each with its reason, and the password stays a `SecretStr` until the one
line that needs its text ([python.md](../language/python.md) section 5). The timeout is this
service's choice, and the comment says so.

## 10. When the cache is down

- **Treat a failed cache call as a miss, and read the store.** Azure's guidance: "An application
  should be able to continue functioning if the shared cache is unavailable" [1]. It should "fall
  back to the original data store if the cache is inaccessible" [1]. Catch the client's connection
  and timeout errors around each cache call, log one `WARNING` where the code falls back
  ([logging.md](../logging/logging.md) sections 4 and 5), and go on, as section 3's cache file does.
  A write or a removal that fails is logged the same way, and the expiry ends the old copy
  (section 4).
- **Make sure the store can carry the reads alone.** While the cache recovers, "the original data
  store could be swamped with requests for data, resulting in timeouts and failed connections"
  [1]. Short timeouts and one retry (section 9) keep each request from waiting on the cache. Azure
  suggests the Circuit Breaker pattern for this case [1]; this file does not describe it.
- **Never keep data only in the cache.** Then an outage loses nothing, and the application goes on
  with the data store [1].

## 11. Common mistakes

| Mistake | Why it happens | What it costs | Fix |
|---|---|---|---|
| The copy is removed before the store is updated | The two calls look independent | A reader loads the old value and puts it back until its expiry [23] | Section 3: the store first |
| A copy written without `ex=`, or an expiry set in a separate call | `set` and `expire` look like two steps | The next `SET` clears the expiry, and the copy never expires [25] | Section 4: the expiry in the same `set` |
| The cache instance runs on the shipped settings | The server starts without a warning | No memory limit; with a limit but no policy, writes fail once memory is full [32], [30] | Section 7 |
| Values stored with `pickle` | `pickle` stores any Python object in one call | Whoever can write to the cache can run code in your process [29] | Section 6: JSON |
| redis-py's default retries on a request path | The client works with no settings at all | Each request can wait through ten retries while the cache does not answer [3] | Section 9 |
| Two clients built from one pool with `from_pool` | `from_pool` reads like a way to share a pool | Closing one client disconnects the other's connections [34] | Section 8 |
| The asyncio client is never closed | Python closes most objects by itself | The asyncio client has no destructor that disconnects it [12] | Section 8 |
| A cache error fails the request | The cache call has no `except` | An outage of the cache becomes an outage of the service [1] | Section 10 |

## 12. Where the rules stop holding

- **A read that must see a change at once.** Cache-aside shows old data for a moment after a change
  (section 3). Use write-through caching for that path [23], or no cache.
- **A static data set that fits in memory.** Load it at startup and let it never expire [23]; the
  read and change rules of section 3 have nothing to do then.
- **Most requests miss.** Do not cache [23].
- **One process is enough.** Use an in-process cache (section 2); sections 7 to 10 do not apply.
- **The data lives only in Valkey or Redis.** A session store or a task queue holds the only copy of
  its data, so it is not a cache in this file's sense: see
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2
  and [task-queues.md](task-queues.md).

Following the rules costs a fallback on every read path and a removal on every change. For data that
is read rarely, that cost buys nothing.

## 13. Alternatives considered

- **Write-through caching.** The write updates the store and the cache in one operation, so readers
  see the new value at once [23]. Not the default, because every write path must then also write
  the cache; Azure points to it for read paths that need the new value right after a write [23].
- **Leases**, as Facebook's memcached servers give them [28]. They live in the server, so with
  Valkey or Redis section 5 uses a lock per key.
- **Probabilistic early expiration** (Vattani et al.'s algorithm, research with a formal
  analysis) [26]. It needs no lock, but each value carries its rebuild time. The lock stays
  the default because it follows the one-request-per-key practice AWS describes [27] and changes
  nothing in the stored value.
- **A local cache in front of the shared one.** The code checks its own memory, then the shared
  cache, then the store; the local copy keeps serving when the shared cache cannot be reached, and
  needs care so it does not get too stale against the shared one [1]. Use it when the store cannot
  carry the reads during an outage (section 10).
- **A circuit breaker around the cache.** Azure suggests one for an outage of the cache [1]; its
  own page was not read for this file, so it is not described.
- **valkey-glide.** Named with its limits in section 2.
- **Memcached.** No owner source on when it fits a Python service better than Valkey was found
  (section 1).

## 14. Security and personal data

This section covers four threats: someone on the network who reads or changes the traffic, a client
that reaches the server and should not, a value written into the cache that makes your process run
code, and sensitive data in a cache many users share. Hardening the server itself, such as its
network rules and its ACL files, is running the server and is left out. The shared rules for data
that leaves the process in a message are in [delivery.md](delivery.md) section 10, and the lock
around a token refresh and the session store are in
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2.

- **Keep the cache on a network that only your services reach.** Both servers are "designed to be
  accessed by trusted clients inside trusted environments" [40], [41]. Protected mode is no
  substitute: it only keeps out clients from other hosts while the default user has no password
  [33].
- **Connect as a named ACL user that may run only the commands your service sends.** ACLs are the
  recommended way to authenticate [40], [41]. The password is a `SecretStr` in the settings
  class, never part of a URL ([python.md](../language/python.md) section 5), and never in a log line
  ([logging.md](../logging/logging.md) section 10).
- **Turn TLS on, and check the server's name.** TLS is optional in both servers [40], [41] and
  off in the shipped config files [32], [33]. Without it, the password crosses the network in
  clear text: the `AUTH` command "is sent unencrypted" [40]. Pass `ssl=True`, and in valkey-py also
  `ssl_check_hostname=True`: valkey-py 6.2.0 does not check the server's name by default, while
  redis-py 8.1.0 does [35], [34].
- **Never pickle what you cache** (section 6).
- **Do not put sensitive data in a shared cache.** Read it from the store every time [23].

A copy of personal data in the cache is personal data like the original. After a change, the
expiry is the longest an old copy lives, whether its removal failed or a reader that loaded it
before the change wrote it back (section 4). Never log a cached value
([logging.md](../logging/logging.md) section 10).

## 15. Checks

- When you review the client file: does it set `socket_timeout`, `socket_connect_timeout`, `retry`
  and `ssl` itself (sections 9 and 14)?
- When you review a change that writes to the store: does every `set` on the cache pass `ex=`
  (section 4)?
- When you review a change that writes to the store: is the copy removed after the commit
  (section 3)?
- `grep -rnE "import pickle|from pickle|pickle\." src/` prints no line in code that reads or
  writes the cache (section 6).
- On the cache instance, `valkey-cli CONFIG GET maxmemory-policy` prints `allkeys-lru`, and
  `valkey-cli CONFIG GET maxmemory` prints a value above 0 (section 7).
- An integration test stops the cache container, started with testcontainers
  ([libraries.md](../testing/libraries.md) section 2), and asserts that a read still returns the
  stored value (section 10).

## 16. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Microsoft — Azure Architecture Center: Caching guidance — https://learn.microsoft.com/en-us/azure/architecture/best-practices/caching
- [2] redis-py — `redis/client.py`, v8.1.0 — https://github.com/redis/redis-py/blob/v8.1.0/redis/client.py
- [3] redis-py — `redis/_defaults.py`, v8.1.0 — https://github.com/redis/redis-py/blob/v8.1.0/redis/_defaults.py
- [4] Python — functools: Higher-order functions and operations on callable objects, Python 3.15.2 documentation — https://docs.python.org/3/library/functools.html
- [5] cachetools — cachetools: Extensible memoizing collections and decorators, 7.2.7 — https://cachetools.readthedocs.io/en/latest/
- [6] Valkey — `COPYING`, the licence file (branch `unstable`) — https://github.com/valkey-io/valkey/blob/unstable/COPYING — checked 2026-10-30
- [7] Valkey — README (branch `unstable`) — https://github.com/valkey-io/valkey
- [8] Valkey — `GOVERNANCE.md` (branch `unstable`) — https://github.com/valkey-io/valkey/blob/unstable/GOVERNANCE.md
- [9] AWS — Amazon ElastiCache Pricing — https://aws.amazon.com/elasticache/pricing/
- [10] Google Cloud — Google Cloud Blog: Unlock 3x QPS and microsecond latency with Memorystore for Valkey 9.1, September 26, 2026 — https://cloud.google.com/blog/products/databases/memorystore-for-valkey-9-1-3x-qps-caching
- [11] Valkey — Valkey Documentation: Migration from Redis to Valkey — https://valkey.io/topics/migration/
- [12] redis-py — Asyncio Examples, redis-py 8.1.0 documentation — https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html
- [13] Redis — README (branch `unstable`) — https://github.com/redis/redis
- [14] Valkey — Clients — https://valkey.io/clients/
- [15] valkey-py — README (branch `main`) — https://github.com/valkey-io/valkey-py
- [16] pypistats.org — Recent downloads: valkey — https://pypistats.org/api/packages/valkey/recent
- [17] pypistats.org — Recent downloads: redis — https://pypistats.org/api/packages/redis/recent
- [18] valkey-py — `docs/connections.rst` (branch `main`) — https://github.com/valkey-io/valkey-py/blob/main/docs/connections.rst
- [19] AWS — Amazon ElastiCache User Guide: Major version behavior and compatibility differences for Valkey (AWS sells managed Valkey) — https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/VersionManagementConsiderations-valkey.html
- [20] redis-py — README (default branch) — https://github.com/redis/redis-py
- [21] Valkey GLIDE — `python/README.md` (branch `main`) — https://github.com/valkey-io/valkey-glide/blob/main/python/README.md
- [22] Valkey GLIDE — wiki, home page (marked as being deprecated) — https://github.com/valkey-io/valkey-glide/wiki
- [23] Microsoft — Azure Architecture Center: Cache-Aside pattern — https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside
- [24] valkey-py — `valkey/commands/core.py`, v6.2.0 — https://github.com/valkey-io/valkey-py/blob/v6.2.0/valkey/commands/core.py
- [25] Redis — Docs: EXPIRE — https://redis.io/docs/latest/commands/expire/
- [26] Andrea Vattani, Flavio Chierichetti and Keegan Lowenstein — Optimal Probabilistic Cache Stampede Prevention (Proceedings of the VLDB Endowment 8(8), 2015; research) — https://www.vldb.org/pvldb/vol8/p886-vattani.pdf — checked 2026-10-30
- [27] Jas Chhabra — Caching challenges and strategies (Amazon Builders' Library, 2019; case) — https://builder.aws.com/content/3K9TeXp6strMiJ4vhakpRD7BQWO/caching-challenges-and-strategies
- [28] Rajesh Nishtala et al. — Scaling Memcache at Facebook (USENIX NSDI, 2013; case) — https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf — checked 2026-10-30
- [29] Python — pickle: Python object serialization, Python 3.15.2 documentation — https://docs.python.org/3/library/pickle.html
- [30] Redis — Docs: Key eviction — https://redis.io/docs/latest/develop/reference/eviction/
- [31] Valkey — Valkey Documentation: Key eviction — https://valkey.io/topics/lru-cache/
- [32] Redis — `redis.conf` (branch `unstable`) — https://github.com/redis/redis/blob/unstable/redis.conf
- [33] Valkey — `valkey.conf` (branch `unstable`) — https://github.com/valkey-io/valkey/blob/unstable/valkey.conf
- [34] redis-py — `redis/asyncio/client.py`, v8.1.0 — https://github.com/redis/redis-py/blob/v8.1.0/redis/asyncio/client.py
- [35] valkey-py — `valkey/asyncio/client.py`, v6.2.0 — https://github.com/valkey-io/valkey-py/blob/v6.2.0/valkey/asyncio/client.py
- [36] redis-py — `redis/retry.py`, v8.1.0 — https://github.com/redis/redis-py/blob/v8.1.0/redis/retry.py
- [37] valkey-py — `valkey/asyncio/connection.py`, v6.2.0 — https://github.com/valkey-io/valkey-py/blob/v6.2.0/valkey/asyncio/connection.py
- [38] valkey-py — `valkey/asyncio/retry.py`, v6.2.0 — https://github.com/valkey-io/valkey-py/blob/v6.2.0/valkey/asyncio/retry.py
- [39] Redis — Docs: redis-py guide, Production usage — https://redis.io/docs/latest/develop/clients/redis-py/produsage/
- [40] Redis — Docs: Redis security — https://redis.io/docs/latest/operate/oss_and_stack/management/security/
- [41] Valkey — Valkey Documentation: Security — https://valkey.io/topics/security/
- [42] valkey-py — GitHub release, v6.2.0 — https://github.com/valkey-io/valkey-py/releases/tag/v6.2.0
