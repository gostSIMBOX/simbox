# Specifications: sdd-simbox-server-endpoints

## Architecture

### File layout

`src/routes/index.js` already does `require('./simbox')`. Node's module
resolution tries `./simbox.js` first, then `./simbox/index.js` — since
`simbox.js` doesn't exist, creating a **directory** `src/routes/simbox/`
with an `index.js` satisfies the existing `require('./simbox')` with zero
changes to that line.

```
src/routes/simbox/
  index.js          # mounts the 6 sub-routers below
  calls.js          # /calls/*
  sms.js            # /sms/*
  sim.js            # /sim/*
  stats.js          # /stats/*
  recognition.js    # /recognition
  mag.js            # /mag/*
  callOutcome.js    # pure functions: deriveInboundCallOutcome, deriveOutboundCallOutcome
```

Each route file follows the existing `device.js`/`auth.js` pattern:
`express.Router()`, `logger` from `../../utils/logger`, `@swagger` JSDoc
blocks, try/catch per handler, `{ success, data }` / `{ success, error }`
envelope.

### Mount path — `/api/v2/simbox`

`src/routes/index.js` currently has:
```js
router.use('/simbox', simboxRoutes);   // -> /api/simbox (never worked, file was missing)
```
Change to:
```js
router.use('/v2/simbox', simboxRoutes);   // -> /api/v2/simbox
```
and update the info-endpoint JSON (`simbox: '/api/simbox'` →
`simbox: '/api/v2/simbox'`). `/api/simbox` never returned anything but a
404 (the file didn't exist), so this is not a breaking change to any
working behavior — it's fixing a dangling reference while landing it at
the agreed `/api/v2/simbox` prefix. `auth.js` and `device.js` and their
mounts (`/api/auth`, `/api/device`) are untouched.

### Swagger discovery

`src/middleware/swagger.js` globs `apis: ['./src/routes/*.js', './src/app.js']`
— this will **not** pick up files under `src/routes/simbox/`. Add
`'./src/routes/simbox/*.js'` to the `apis` array so the new endpoints show
up in `/api-docs`.

## Consolidations vs. legacy (documented deviations)

Per the requirements' translation model, three legacy path pairs collapse
into one endpoint each because they represent the same business action
reached from two legacy code paths:

| New endpoint | Legacy paths merged | Why safe to merge |
|---|---|---|
| `POST /calls/attempts` | `trycall.php` (triggered directly from old dialplan, `system/trycall.sh`) + `svistok/calltry.php` (triggered from the compiled `svistok-aa/stat.c` binary) | Both mean "a call attempt is starting"; `calltry` just adds one optional field (`spec`). Confirmed via grep that these are two different legacy *callers* invoking the same conceptual event, not two different events. |
| `POST /calls/outbound/end` | `svistok/callendout.php` + `svistok/callendout_imb123.php` | `callendout_imb123.sh` sends the exact same field set with several values hardcoded to `"123"` (numbermy, serial, dongle, imei, imsi) — it's a caller-side simplification, not a different schema. |
| `POST /sim/ki/uploads` | `reader/upload_new_ki.php` + `readers/upload_new_ki.php` | Identical params (`iccid, imsi, ki`, plus optional `seller, note` on the `reader/` variant); legacy has both a singular and plural path for the same operation. |

This drops the endpoint count from 21 legacy paths to **18 new endpoints**.

## Endpoint Specifications

Response envelope for all endpoints: `{ success: true, data: {...} }` on
success, `{ success: false, error: "message" }` on failure (400 for
validation, 404 for unknown resource id, 500 for unexpected errors) —
matches `device.js`/`auth.js`.

"Queue-style" GETs (an SMS/Ki/IMEI/mag item may or may not be available)
respond `200` with `data.available: false` instead of an error, replacing
legacy's `"NOTHING NEW"` / non-`OK` status-string convention (see
Requirements acceptance criteria).

### `calls.js` — mounted at `/calls`

| Method & path | Body / query | Response `data` | Legacy source |
|---|---|---|---|
| `POST /attempts` | body: `imsi*, numberA*, numberB*, spec?` | `{ id, imsi, numberA, numberB, spec, receivedAt }` | `trycall.php`, `svistok/calltry.php` |
| `GET /found-today` | — | `{ imsis: string[] }` | `svistok/foundgettoday.php` |
| `POST /inbound/end` | body: `imsi*, imei*, numberB*, numberMy*, serial*, dongle*, gateway*, durationSec*, billSec*, ccCause*, endStatus*, lac?, cell?` | `{ id, dialStatus, endParty, receivedAt, ...echoed body }` | `svistok/callendin.php` |
| `POST /outbound/end` | body: `imsi*, imei*, numberA*, numberB*, numberMy*, serial*, dongle*, gateway*, durationSec*, billSec*, answered*, ccCause*, endStatus*, lac?, cell?, spec?, vip?, pdd?, pddc?, uid?, pro?, fas?, epdd?, fpdd?, hem?, hoa?, epoch?, fasSec?, pddcSec?, emType?` | `{ id, dialStatus, endParty, billSec, receivedAt, ...echoed body }` | `svistok/callendout.php`, `svistok/callendout_imb123.php` |

`*` = required. `dialStatus`/`endParty` (and, for outbound, a possibly
bumped `billSec`) are **computed server-side** from `ccCause`/`endStatus`
(/`answered` for outbound) — see "Call outcome derivation" below. This
is a deliberate behavior addition vs. legacy (where the *shell script*
computed these before calling the URL): centralizing it server-side means
one place to fix/extend the cause-code table later.

`GET /found-today` mock returns a stub array (e.g. `['250011234567890']`)
matching `device.js`'s pattern of hardcoded example data.

### `sms.js` — mounted at `/sms`

| Method & path | Body / query | Response `data` | Legacy source |
|---|---|---|---|
| `POST /delivery-reports` | body: `imsi*, numberB*, statusReport*` | `{ id, receivedAt }` | `sms/smsout_status_report.php` |
| `GET /outbox/next` | query: `imsi*, group?, priority?` (`priority` ∈ `public`\|`private`\|`spam`, default `public`; maps legacy `private=0\|1\|2`) | available: `{ available: true, id, numberB, text }`; empty: `{ available: false }` | `sms/smsout_getnew.php` |
| `POST /outbox/:id/sent` | body: `imsi*` | `{ id, status: 'sent' }` (404 if `id` unknown) | `sms/smsout_sended.php` |
| `POST /outbox/:id/failed` | — | `{ id, status: 'failed' }` (404 if `id` unknown) | `sms/smsout_failed.php` |

Mock: seed `smsOutbox` with 1-2 example pending items (id, imsi, group,
priority, numberB, text, status: 'pending') so `/outbox/next` has
something to return, and `/outbox/:id/sent`/`failed` have a real id to
exercise against.

### `sim.js` — mounted at `/sim`

| Method & path | Body / query | Response `data` | Legacy source |
|---|---|---|---|
| `GET /ki/next` | query: `gateway*, dongle*, owner*` | available: `{ available: true, imsi, iccid, ki, smsp, imei }`; empty: `{ available: false }` | `sim/get_new_ki.php` |
| `GET /imei/next` | — | available: `{ available: true, imei }`; empty: `{ available: false }` | `sim/get_new_imei.php` |
| `POST /ki/uploads` | body: `iccid*, imsi*, ki*, seller?, note?` | `{ id, receivedAt }` | `reader/upload_new_ki.php`, `readers/upload_new_ki.php` |

Legacy's `KIOK|imsi|iccid|ki|smsp|imei|imsi|iccid|ki|smsp` response
duplicated every field twice (an artifact of two format revisions being
concatenated); the new response has each field once.

### `stats.js` — mounted at `/stats`

One shared in-memory `statsLog` array tagged by `type`, exposed through 5
thin endpoints (keeps legacy's 5 separate URLs, since they're genuinely 5
distinct upload kinds, but avoids 5 near-identical files):

| Method & path | Body | `type` tag | Legacy source |
|---|---|---|---|
| `POST /balance` | `imsi*, iccid*, balance*` | `balance` | `stat/upload_balance.php` |
| `POST /operator` | `imsi*, iccid*, operatorType*, operatorData*` | `operator` | `stat/upload_op.php` (`op_t`, `op_d`) |
| `POST /tariff` | `imsi*, iccid*, tariff*` | `tariff` | `stat/upload_tarif.php` |
| `POST /number` | `imsi*, iccid*, number*` | `number` | `stat/upload_number.php` |
| `POST /group` | `imsi*, iccid*, group*` | `group` | `stat/upload_group.php` |

All respond `{ id, receivedAt }`.

### `recognition.js` — mounted at `/recognition`

| Method & path | Body | Response `data` | Legacy source |
|---|---|---|---|
| `POST /` | `uid*, preIn?, preOut?, ansIn?, ansOut?, pddSec?, billSec?, numberB*, dialStatus*` | `{ id, receivedAt }` | `recog/recog_save.php` |

### `mag.js` — mounted at `/mag`

| Method & path | Body / query | Response `data` | Legacy source |
|---|---|---|---|
| `GET /next` | — | available: `{ available: true, payload }`; empty: `{ available: false }` | `mag/get_new_mag.php` |

Mock: stub returns a fixed opaque `payload` string once, then
`available: false` — same "hand out one item" shape as `ki/next` /
`imei/next` / `outbox/next`, so tests can exercise both branches.

## Call outcome derivation (`callOutcome.js`)

Ported from `system/svistok/callendin.sh` and `system/svistok/callendout.sh`.
Both scripts execute a sequence of **independent** `if` blocks (not
`if/elif`), so a later matching block can overwrite a field set by an
earlier one — this ordering must be preserved exactly, not converted to a
switch/first-match.

### `deriveInboundCallOutcome({ ccCause, endStatus, billSec })`

Defaults: `endParty = -1`, `dialStatus = "UNKNOWN"`. Then, in order:

1. `ccCause === 16 && endStatus === 29` → `endParty = 1`; `dialStatus = billSec > 0 ? "ANSWER" : "NOANSWER"`
2. `ccCause === 16 && endStatus === 104` → `endParty = 2`; `dialStatus = billSec > 0 ? "ANSWER" : "NOANSWER"`
3. `ccCause === 31 && endStatus === 104` → `endParty = 3`; `dialStatus = billSec > 0 ? "ANSWER" : "NOANSWER"`
4. `ccCause === 17` → `endParty = 2`; `dialStatus = "BUSY"`
5. `ccCause === 177 && endStatus === 100` → `dialStatus = "FAILED"`

Returns `{ dialStatus, endParty }`.

### `deriveOutboundCallOutcome({ ccCause, endStatus, answered, billSec })`

Defaults: `endParty = -1`, `dialStatus = "UNKNOWN"`, `billSec` passed
through (may be bumped to `1`). Then, in order:

1. `endStatus === 21` → `endParty = -1`; `dialStatus = "FAILED"`
2. `ccCause === 19 && endStatus === 104` → `endParty = 3`; `dialStatus = "NOANSWER"`
3. `ccCause === 1 && endStatus === 104` → `endParty = 3`; `dialStatus = "NOANSWER"`
4. `ccCause === 28 && endStatus === 104` → `endParty = 3`; `dialStatus = "NOANSWER"`
5. `ccCause === 0 && endStatus === 29` → `endParty = 1`; if `answered > 0`: `dialStatus = "ANSWER"`, and if `billSec === 0` then `billSec = 1`; else `dialStatus = "NOANSWER"`
6. `ccCause === 0 && endStatus === 100` → same as step 5 but no `endStatus` change (mirrors legacy's duplicate block)
7. `ccCause === 16 && endStatus === 29` → same effect as step 5, `endParty = 1`
8. `ccCause === 16 && endStatus === 104` → `endParty = 2`; `dialStatus = answered > 0 ? "ANSWER" : "NOANSWER"` (**no** billSec bump — matches legacy, which omits the bump only in this branch)
9. `ccCause === 31 && endStatus === 104` → `endParty = 3`; if `answered > 0`: `dialStatus = "ANSWER"`, bump `billSec` to `1` if `0`; else `"NOANSWER"`
10. `ccCause === 17` → `endParty = 2`; `dialStatus = "BUSY"`
11. `ccCause === 177 && endStatus === 100` → `dialStatus = "FAILED"`
12. `ccCause === 19 && endStatus === 104` → `dialStatus = "NOANSWER_USERALERTING"` **(runs after step 2 and overwrites its `dialStatus`, per legacy's independent-if ordering; `endParty` from step 2 is left as `3`)**

Returns `{ dialStatus, endParty, billSec }`.

Both functions must be pure (no I/O) and unit-testable in isolation —
this is where the CDR business logic lives, so it should be easy to
exercise standalone against the acceptance-criteria example
(`ccCause=16, endStatus=29, billSec>0` → `dialStatus=ANSWER`).

## Validation rules

- All fields marked `*` above are required; missing → `400
  { success: false, error: "<field> is required" }`.
- `ccCause`, `endStatus`, `answered`, `billSec`, `durationSec` are
  coerced to numbers; non-numeric input → `400`.
- `priority` (SMS) must be one of `public`/`private`/`spam` if provided;
  otherwise `400`.
- `POST /sms/outbox/:id/sent` and `/failed` → `404
  { success: false, error: "SMS outbox item not found" }` if `id` doesn't
  match a seeded/known item.
- All other unexpected errors caught in try/catch → `500` per existing
  pattern (not delegated to the global `errorHandler` middleware, to stay
  consistent with `device.js`/`auth.js`).

## Known limitations (explicitly out of scope, per Requirements Non-Goals)

- No concurrency control on "next available" endpoints (`sms/outbox/next`,
  `sim/ki/next`, `sim/imei/next`, `mag/next`) — two simultaneous callers
  could get the same mock item. Acceptable for the in-memory/stub scope;
  flagged for when real persistence lands.
- No auth/authz on any of these routes (matches `device.js` today).
- `svistok/foundgettoday.php`'s underlying "found" flag has no legacy
  upload endpoint in this codebase (it's populated by a process not
  present in `legacy/simbox-desktop-v2015`'s file set) — `GET
  /calls/found-today` is read-only mock data; no corresponding write
  endpoint is being added.

## Next Step

Awaiting explicit **"specs approved"** before moving to Plan (task
breakdown, file-by-file diff list, test strategy).
