# Status: sdd-simbox-server-endpoints

## Current Phase

IMPLEMENTATION

## Phase Status

COMPLETE

## Last Updated

2026-08-24 by Claude

## Blockers

None. One pre-existing, out-of-scope test failure documented in
`04-implementation-log.md` (missing catch-all 404 handler in `app.js`,
unrelated to this flow — confirmed via git-stash that it predates these
changes).

## Progress

- [x] Legacy protocol surveyed (`legacy/simbox-desktop-v2015`, 21 endpoints
      across svistok/sms/sim/reader/stat/recog/mag)
- [x] Current app surveyed (`apps/simbox-server` — confirmed
      `src/routes/simbox.js` referenced by `routes/index.js` but missing,
      matches this app's own `flows/legacy/mapping.md` CRITICAL finding)
- [x] Scope clarified with user: all endpoint groups in scope, mock/stub
      persistence (matches `device.js`/`auth.js` pattern), translated
      `/api/v2/simbox/...` REST paths (not wire-compatible with legacy
      `.php` URLs)
- [x] Requirements drafted (`01-requirements.md`)
- [x] Requirements approved (2026-08-24)
- [x] Specifications drafted (`02-specifications.md`)
- [x] Specifications approved (2026-08-24)
- [x] Plan drafted (`03-plan.md`)
- [x] Plan approved (2026-08-24)
- [x] Implementation started
- [x] Implementation complete  ← current (all 12 tasks done, 58/59 tests
      passing, lint clean on new files, live smoke test passed)

## Context Notes

- Legacy calls are all GET with query params, pipe-delimited plain-text
  responses; new endpoints will use JSON + REST verbs by design decision.
- Resolved at spec time: `reader/`+`readers/upload_new_ki.php` merged into
  `POST /sim/ki/uploads`; `callendout.php`+`callendout_imb123.php` merged
  into `POST /calls/outbound/end` (imb123 was confirmed to be a
  caller-side hardcoded-field variant, not a different schema);
  `trycall.php`+`svistok/calltry.php` merged into `POST /calls/attempts`
  (confirmed via grep these are two legacy *callers* — old dialplan vs
  `svistok-aa/stat.c` — of the same conceptual event). 21 legacy paths →
  18 new endpoints.
- `src/routes/simbox/` will be a **directory** (not a single
  `simbox.js`), relying on Node resolving `require('./simbox')` to
  `./simbox/index.js` — zero change needed to that require line in
  `routes/index.js`. Mount path changes from (broken) `/api/simbox` to
  `/api/v2/simbox` by editing the `router.use('/simbox', ...)` line to
  `router.use('/v2/simbox', ...)`.
- `src/middleware/swagger.js`'s `apis` glob must gain
  `'./src/routes/simbox/*.js'` or the new endpoints won't appear in
  `/api-docs`.
- Call-end endpoints (`/calls/inbound/end`, `/calls/outbound/end`) port
  the exact cause-code → dialStatus/endParty derivation logic from
  `callendin.sh`/`callendout.sh` into a pure, unit-testable
  `callOutcome.js` module — including the legacy quirk where independent
  (non-elif) `if` blocks let a later block overwrite an earlier one's
  `dialStatus` (see 02-specifications.md for the exact ordered rules).
- Existing app conventions to follow: Express `Router()` per resource,
  `logger` util, `{ success, data|error }` JSON envelope, wired via
  `src/routes/index.js`.
- Pre-flight (plan phase) found: `apps/simbox-server` has no
  `node_modules`/lockfile (`npm install` needed before tests run), and
  `tests/health.test.js` requires `../src/index` as if it exported an
  Express app, but `src/index.js` exports nothing and just calls `main()`
  — pre-existing bug, blocks `npm test` entirely. Plan Task 1 fixes this
  minimally (point the test at `new (require('../src/app'))().app`
  instead) so the whole suite (old + new) can actually run green.
- 12-task plan drafted in `03-plan.md`: Task 1 fixes test harness, Tasks
  2-8 build `callOutcome.js` + the 6 route modules (each with its own test
  file), Task 9 wires them into `simbox/index.js`, Tasks 10-11 do the
  2 small edits to `routes/index.js` (mount path) and `swagger.js` (apis
  glob), Task 12 is full-suite verification.
