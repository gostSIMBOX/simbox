# Plan: sdd-simbox-server-endpoints

## Pre-flight findings

- `apps/simbox-server` has **no `node_modules`, no lockfile** — `npm test`
  currently fails with `jest: command not found`. `npm install` is a
  required first step before any test can run (not itself a code task,
  just an environment prerequisite).
- `tests/health.test.js` does `require('../src/index')` and treats the
  result as an Express app for `supertest`. But `src/index.js` never
  `module.exports` anything — it just calls `main()`, which asynchronously
  binds a real port. This test has likely never actually passed. It's a
  **pre-existing bug**, unrelated to this flow's scope, but it blocks
  `npm test` from ever going green, which blocks verifying *this* flow's
  new tests too. Fix is a 2-line, low-risk change (see Task 1) — including
  it as a small enabling task rather than leaving the whole suite red.

## Task Breakdown

Tasks 2–8 (route modules) have no dependencies on each other and could be
done in any order; `callOutcome.js` (Task 2) must land before `calls.js`
(Task 3) since the latter imports it. Task 9 depends on Tasks 3–8. Task 10
depends on Task 9 existing (so the require resolves to a real router).
Each task is verified with its own test file before moving to the next,
per one-test-at-a-time.

| # | Task | Files | Complexity |
|---|---|---|---|
| 1 | Fix test harness so `npm test` can run at all | `tests/health.test.js` (require `../src/app` + instantiate, not `../src/index`); `npm install` | S |
| 2 | Port call-outcome derivation logic | CREATE `src/routes/simbox/callOutcome.js`; CREATE `tests/callOutcome.test.js` | M (business logic fidelity, needs careful unit tests) |
| 3 | Call tracking endpoints | CREATE `src/routes/simbox/calls.js`; CREATE `tests/simbox.calls.test.js` | M |
| 4 | SMS dispatch endpoints | CREATE `src/routes/simbox/sms.js`; CREATE `tests/simbox.sms.test.js` | S |
| 5 | SIM/IMEI provisioning endpoints | CREATE `src/routes/simbox/sim.js`; CREATE `tests/simbox.sim.test.js` | S |
| 6 | Stats upload endpoints | CREATE `src/routes/simbox/stats.js`; CREATE `tests/simbox.stats.test.js` | S |
| 7 | Recognition endpoint | CREATE `src/routes/simbox/recognition.js`; CREATE `tests/simbox.recognition.test.js` | XS |
| 8 | Mag endpoint | CREATE `src/routes/simbox/mag.js`; CREATE `tests/simbox.mag.test.js` | XS |
| 9 | Wire sub-routers together | CREATE `src/routes/simbox/index.js` (mounts `/calls`, `/sms`, `/sim`, `/stats`, `/recognition`, `/mag`) | XS |
| 10 | Mount at `/api/v2/simbox` + fix info endpoint | MODIFY `src/routes/index.js` (`/simbox` → `/v2/simbox`; `endpoints.simbox` value) | XS |
| 11 | Swagger discovery | MODIFY `src/middleware/swagger.js` (`apis` array gains `'./src/routes/simbox/*.js'`) | XS |
| 12 | Full-suite verification | run `npm test`, `npm run lint`, manually hit `/api-docs` to confirm new paths render | S |

## Testing Strategy

- **`callOutcome.test.js`**: table-driven tests covering every branch in
  both `deriveInboundCallOutcome` and `deriveOutboundCallOutcome` from
  02-specifications.md, including the acceptance-criteria example
  (`ccCause=16, endStatus=29, billSec>0` → `ANSWER`) and the
  overwrite-quirk case (`ccCause=19, endStatus=104` →
  `NOANSWER_USERALERTING`, `endParty=3`).
- **Per-route supertest files**: happy path (2xx + correct `data` shape),
  validation failure (400 on missing required field), and where
  applicable the `available: false` / 404 branches (empty SMS outbox,
  unknown outbox id, exhausted Ki/IMEI/mag pool).
- **`tests/health.test.js`**: after Task 1's fix, confirms `/health`,
  `/api`, and 404 handling still work — also a smoke check that adding the
  simbox routes didn't break app bootstrap.
- No test touches real network/filesystem — everything runs against
  in-memory mock data seeded per module.

## Rollback

All changes are additive except the two small edits in Tasks 1, 10, 11.
Revert = `git revert` the commit(s) or delete the 8 new `src/routes/simbox/*`
files + `tests/simbox.*.test.js`/`tests/callOutcome.test.js` and revert the
3 modified files to their prior content. No migrations, no data to unwind
(everything is in-memory).

## Next Step

Awaiting explicit **"plan approved"** before starting implementation
(Task 1 first).
