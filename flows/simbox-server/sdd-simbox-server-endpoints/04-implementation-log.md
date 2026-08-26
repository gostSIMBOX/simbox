# Implementation Log: sdd-simbox-server-endpoints

## Summary

All 12 plan tasks completed. 18 new endpoints implemented across 6 route
modules, replacing the missing `src/routes/simbox.js` the codebase was
already broken on. Verified with unit tests, supertest integration tests,
lint, and a live end-to-end smoke test against a running server.

## Task-by-task

1. **Test harness fix** — `npm install` (no lockfile/`node_modules`
   existed). Fixed `tests/health.test.js` to build the app via
   `new (require('../src/app'))().app` instead of `require('../src/index')`
   (which exports nothing and binds a real port). Confirmed via
   `git stash`/`git stash pop` that the app boots and this fix is
   independent of the simbox work.
2. **`callOutcome.js`** — ported `deriveInboundCallOutcome` and
   `deriveOutboundCallOutcome` from `callendin.sh`/`callendout.sh`
   verbatim, preserving the independent-`if`-block overwrite ordering.
   18 unit tests in `tests/callOutcome.test.js`, all passing, including
   the acceptance-criteria example and the
   `NOANSWER_USERALERTING`-overwrite quirk.
3. **`calls.js`** — `/calls/attempts`, `/calls/found-today`,
   `/calls/inbound/end`, `/calls/outbound/end`. 9 tests passing, including
   an explicit case sending an imb123-style payload (hardcoded placeholder
   fields) through the merged outbound-end endpoint.
4. **`sms.js`** — `/sms/delivery-reports`, `/sms/outbox/next`,
   `/sms/outbox/:id/sent`, `/sms/outbox/:id/failed`. 11 tests passing.
5. **`sim.js`** — `/sim/ki/next`, `/sim/imei/next`, `/sim/ki/uploads`.
   5 tests passing, including pool-exhaustion (`available: false`) after
   the single seeded item is consumed.
6. **`stats.js`** — `/stats/balance|operator|tariff|number|group`, single
   shared `statsLog` implementation. 10 table-driven tests passing.
7. **`recognition.js`** — `POST /recognition`. 2 tests passing.
8. **`mag.js`** — `GET /mag/next`. 1 test passing.
9. **`src/routes/simbox/index.js`** — mounts all 6 sub-routers. Confirmed
   Node resolves the existing `require('./simbox')` in
   `src/routes/index.js` to this directory's `index.js` with zero changes
   to that require line.
10. **Mount path** — `src/routes/index.js`: `router.use('/simbox', ...)` →
    `router.use('/v2/simbox', ...)`, and the info-endpoint JSON's
    `endpoints.simbox` value updated to `/api/v2/simbox`.
11. **Swagger discovery** — `src/middleware/swagger.js`'s `apis` array
    gained `'./src/routes/simbox/*.js'`. Verified by requiring the built
    spec directly (`require('./src/middleware/swagger').paths`) — all 18
    new paths present with correct methods/tags.
12. **Full verification**:
    - `npx jest --forceExit`: **58/59 passing.**
    - `npx eslint src/routes/simbox/`: clean (0 errors) — fixed 4
      `prefer-const` violations in my own new files (`mag.js`, `sim.js`,
      `sms.js` used `let` for arrays only ever mutated via `.shift()`,
      never reassigned).
    - Live smoke test: started the real server on port 4501, exercised
      `POST /calls/attempts`, `POST /calls/outbound/end` (confirmed
      `ccCause=16/endStatus=29/billSec=5/answered=1` → `dialStatus:
      ANSWER, endParty:1`, matching the acceptance criteria), `GET
      /sim/ki/next` twice (confirmed pool-exhaustion → `available:
      false` on the second call), `GET /sms/outbox/next` with no match,
      and a validation failure (400) — all behaved as specified.

## Deviations from plan

None. All 12 tasks completed as planned, in order.

## The one known-failing test (pre-existing, out of scope)

`tests/health.test.js › 404 Handler › GET /nonexistent should return 404`
fails because `src/app.js` never registers a catch-all 404 route —
`errorHandler.js` only handles errors explicitly passed to `next(err)`,
so unmatched paths fall through to Express's default HTML 404 instead of
the JSON `{error: 'Route not found', path}` the test expects. Confirmed
via `git stash` (temporarily reverting to the pre-flow `src/routes/index.js`,
`tests/health.test.js`, `src/middleware/swagger.js`) that this failure is
unrelated to any change in this flow — it's a second pre-existing gap in
this codebase's test suite (the first being the `src/index.js` export
issue fixed in Task 1). Left unfixed as it's outside this flow's scope
(adding legacy-compatible simbox endpoints); worth its own small follow-up
(add `app.use((req, res) => res.status(404).json({ error: 'Route not
found', path: req.path }))` before `setupErrorHandling()` in `app.js`).

## Files changed

**Created:**
- `src/routes/simbox/index.js`
- `src/routes/simbox/calls.js`
- `src/routes/simbox/sms.js`
- `src/routes/simbox/sim.js`
- `src/routes/simbox/stats.js`
- `src/routes/simbox/recognition.js`
- `src/routes/simbox/mag.js`
- `src/routes/simbox/callOutcome.js`
- `tests/callOutcome.test.js`
- `tests/simbox.calls.test.js`
- `tests/simbox.sms.test.js`
- `tests/simbox.sim.test.js`
- `tests/simbox.stats.test.js`
- `tests/simbox.recognition.test.js`
- `tests/simbox.mag.test.js`
- `package-lock.json` (from `npm install`)

**Modified:**
- `src/routes/index.js` (mount path `/simbox` → `/v2/simbox`; info JSON)
- `src/middleware/swagger.js` (apis glob)
- `tests/health.test.js` (require app from `../src/app` correctly)

**Untouched (per constraints):** `src/routes/auth.js`, `src/routes/device.js`,
`src/app.js`, `src/config/config.js`, `src/middleware/errorHandler.js`.
