# Requirements: sdd-simbox-server-endpoints

## Problem

`apps/simbox-server/src/routes/index.js` requires `./simbox`, but
`src/routes/simbox.js` does not exist — a gap already flagged as CRITICAL in
this repo's own `flows/legacy/mapping.md`. Meanwhile, the legacy
`legacy/simbox-desktop-v2015` codebase defines a real, battle-tested protocol
(the SIM box hardware/Asterisk scripts talking to a central `simserver:8122`)
covering call tracking, SMS dispatch, SIM/IMEI provisioning, and stats
upload. That protocol encodes real domain knowledge (call end-cause
mapping, SMS retry/queue semantics, Ki/ICCID/IMEI provisioning flow) that
the new server should preserve even though it's being re-platformed.

This flow designs and implements the missing `simbox.js` (and any sibling
route modules needed) so the new `apps/simbox-server` exposes the same
business capabilities as the legacy `simserver`, on a modern JSON/REST
surface, so simbox devices and provisioning tools can be migrated onto the
new backend without losing functionality.

## Legacy Protocol Inventory

All legacy calls are plain HTTP GET with query-string params against
`http://simserver:8122/...`, expecting plain-text (often `|`-pipe-delimited)
responses. Source: `legacy/simbox-desktop-v2015` (paths below relative to
that root).

| # | Legacy path | Callers | Params (query string) | Legacy response |
|---|---|---|---|---|
| 1 | `GET /trycall.php` | `system/trycall.sh` | `numbera, numberb, imsi` | fire-and-forget (ignored) |
| 2 | `GET /svistok/calltry.php` | `system/svistok/calltry.sh` | `numbera, numberb, imsi, spec` | fire-and-forget |
| 3 | `GET /svistok/callendin.php` | `system/svistok/callendin.sh` | `numberb, numbermy, serial, dongle, gateway, durationsec, billsec, dialstatus, imei, imsi, lac, cell, end_status, cc_cause, end_party` | fire-and-forget |
| 4 | `GET /svistok/callendout.php` | `system/svistok/callendout.sh` | `numberb, numbera, numbermy, serial, dongle, gateway, duration, billsec, dialstatus, imei, imsi, lac, cell, end_status, cc_cause, end_party, spec, vip, pdd, pddc, uid, pro, fas, epdd, fpdd, hem, hoa, epoch, fassec, pddcsec, em_type` | fire-and-forget |
| 5 | `GET /svistok/callendout_imb123.php` | `system/svistok/callendout_imb123.sh` | subset of #4 with several fields hardcoded (`numbermy=123`, `serial=123`, `dongle=123`, `imei=123`, `imsi=123`) | fire-and-forget |
| 6 | `GET /svistok/foundgettoday.php` | `system/found/getfound.sh` | none | whitespace-separated list of IMSIs flagged "found" today |
| 7 | `GET /sms/smsout_status_report.php` | `system/cds.php` | `numberb, imsi, status_report` | ignored (SMS delivery/CDS report) |
| 8 | `GET /sms/smsout_getnew.php` | `ai/sms/sendsms_imsi.php`, `ai/sms/sendsms_spam_2.php` | `imsi, group, private` (0=public, 1=private, 2=spam) | `"NOTHING NEW"` or `ACTION\|smsoutid\|numberb\|text` |
| 9 | `GET /sms/smsout_failed.php` | `ai/sms/sendsms_spam_2.php` | `smsoutid` | ignored |
| 10 | `GET /sms/smsout_sended.php` | `ai/sms/sendsms_imsi.php`, `ai/sms/sendsms_spam_2.php` | `smsoutid, imsi` | ignored |
| 11 | `GET /sim/get_new_ki.php` | `system/new_ki.php`, `system/new_ki_on.php` | `gateway, dongle, owner` | `status` or `KIOK\|imsi\|iccid\|ki\|smsp\|imei\|imsi\|iccid\|ki\|smsp` |
| 12 | `GET /sim/get_new_imei.php` | `modules/imei.php`, `actions/changeimei.php` | none | `status\|imei` (status `IMEIOK` on success) |
| 13 | `GET /reader/upload_new_ki.php` | `readers/upload_all_ki.php` | `iccid, imsi, ki, seller, note` | ignored |
| 14 | `GET /readers/upload_new_ki.php` | `readers/upload_new_ki.php` | `iccid, imsi, ki` | ignored — **near-duplicate of #13**; legacy has both a singular (`reader`) and plural (`readers`) path, functionally the same upload. Treat as one endpoint going forward. |
| 15 | `GET /stat/upload_balance.php` | `modules/sim.php: upload_balance()` | `imsi, iccid, balance` | ignored |
| 16 | `GET /stat/upload_op.php` | `modules/sim.php: upload_op()` | `imsi, iccid, op_t, op_d` | ignored |
| 17 | `GET /stat/upload_tarif.php` | `modules/sim.php: upload_tarif()` | `imsi, iccid, tarif` | ignored |
| 18 | `GET /stat/upload_number.php` | `modules/sim.php: upload_number()` | `imsi, iccid, number` | ignored |
| 19 | `GET /stat/upload_group.php` | `ai/recog/parse/all.php` | `imsi, iccid, group` | ignored |
| 20 | `GET /recog/recog_save.php` | `ai/recog/dorecog.php`, `dorecog_old.php` | `uid, pre_in, pre_out, ans_in, ans_out, pdds, billsec, numberb, dialstatus` | ignored |
| 21 | `GET /mag/get_new_mag.php` | `ai/automag/automag.php` | none | raw magstripe payload (opaque string) |

## Scope Decision (confirmed with user)

- **Endpoint groups in scope**: all of the above — call tracking
  (`svistok`/`trycall`), SMS dispatch (`sms`), SIM/IMEI/Ki provisioning
  (`sim`/`reader`), and stats/recognition/mag (`stat`/`recog`/`mag`).
- **Persistence**: follow this app's existing mock pattern
  (`src/routes/device.js`, `src/routes/auth.js` — in-memory/stub data with
  `// TODO: Implement database` markers). Real persistence is a separate,
  later concern.
- **Routing/compatibility model**: endpoints are **translated**, not
  wire-compatible. They live under a new versioned prefix
  `/api/v2/simbox/...` using REST conventions (resource nouns, proper HTTP
  verbs, JSON bodies/responses) — not the legacy root-level `.php` paths or
  pipe-delimited plain text. "Compatible with legacy" means **same data
  captured and same business semantics** (call end-cause mapping, SMS
  queue/retry states, Ki/IMEI provisioning flow), not byte-for-byte URL or
  response-format compatibility. Legacy shell/PHP callers are not expected
  to hit these new paths unmodified.

## User Stories

### Call tracking
- As the simbox call-handling logic, I want to notify the server when a
  call attempt starts (outbound "try" and "svistok try" variants), so the
  server can correlate later end-of-call events.
- As the simbox call-handling logic, I want to report inbound and outbound
  call completion (duration, dial status, end-cause codes, IMEI/IMSI,
  cell/lac), so the server has full CDR-equivalent data.
- As a provisioning/monitoring tool, I want to fetch the list of IMSIs
  flagged "found" (detected/blocked) today, so I can act on them.

### SMS dispatch
- As the simbox SMS-sending logic, I want to ask the server for the next
  outbound SMS for a given IMSI/group/priority tier (public/private/spam),
  so I know what to send next.
- As the simbox SMS-sending logic, I want to report an SMS as sent or
  failed, so the server's outbound queue reflects reality.
- As the simbox, I want to submit SMS delivery status reports (CDS), so
  delivery confirmation is recorded.

### SIM / IMEI provisioning
- As a SIM-programming tool, I want to request the next Ki/ICCID (and
  associated IMSI/SMSC) to burn onto a SIM, so bulk SIM provisioning can
  continue uninterrupted.
- As a device, I want to request the next IMEI to assign, so IMEI rotation
  can continue.
- As a SIM reader/uploader tool, I want to upload a newly read
  ICCID/IMSI/Ki (optionally with seller/note metadata), so new SIM stock
  gets registered.

### Stats & recognition
- As the simbox, I want to upload per-IMSI balance, operator, tariff,
  number, and group readings, so operational dashboards have current data.
- As the recognition subsystem, I want to save call-recognition results
  (ring/answer timing, dial status), so downstream analytics can use them.
- As a magstripe reader integration, I want to request the next magstripe
  payload to write, so card programming can continue.

## Acceptance Criteria (representative)

- **Given** a device reports a completed outbound call with
  `cc_cause=16, end_status=29, billsec>0`, **when** it POSTs to the
  outbound call-end endpoint, **then** the server records `dialstatus:
  ANSWER` and the correct `end_party`, mirroring the legacy cause-code
  mapping in `system/svistok/callendout.sh`.
- **Given** no SMS is queued for an IMSI/group/priority, **when** the
  client asks for the next outbound SMS, **then** the server responds with
  a clear "nothing pending" result (equivalent to legacy `"NOTHING NEW"`),
  not an error.
- **Given** a Ki/IMEI/ICCID provisioning request succeeds, **when** the
  client requests the next Ki or IMEI, **then** the response includes all
  fields the legacy response carried (imsi, iccid, ki, smsp, imei),
  structured as JSON instead of pipe-delimited text.
- **Given** any of these endpoints is called with missing/invalid required
  params, **when** the request is processed, **then** the server returns a
  4xx JSON error consistent with this app's existing error-handling
  middleware (`src/middleware/errorHandler.js`), rather than silently
  succeeding as legacy PHP often did.

## Constraints

- Must follow this app's existing conventions: Express `Router()` modules
  under `src/routes/`, `logger` for logging, `{ success, data }` /
  `{ success, error }` JSON envelope (matches `device.js`, `auth.js`), and
  routes wired through `src/routes/index.js`.
- New routes are additive — do not change existing `auth.js` or
  `device.js` behavior.
- No real database work in this flow; stub/in-memory data structures only
  (matching `device.js`'s `// TODO: Implement database query` style).

## Non-Goals

- Byte-for-byte URL or wire-format compatibility with the legacy PHP
  endpoints (explicitly rejected in favor of translated `/api/v2/simbox`
  REST paths — see Scope Decision).
- Updating the legacy shell/PHP scripts themselves to call the new API.
- Real persistence, auth/authz on these endpoints, or rate limiting beyond
  what already exists globally.
- Implementing the actual telephony/SMS/SIM-programming logic that
  *consumes* this data (e.g. Asterisk dialplan) — this flow only covers
  the server-side API surface.

## Open Questions

- None outstanding — scope, persistence approach, and routing model were
  confirmed with the user during requirements elicitation.

## Next Step

Awaiting explicit **"requirements approved"** before moving to
Specifications (path/method naming per endpoint, request/response JSON
shapes, file layout for `src/routes/simbox.js` vs. splitting into
sub-modules).
