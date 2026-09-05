# Visual Mockups: simbox-web-design-prototype-table-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-09-05

## Overview

ASCII mockups for every column of the main SIM table (`legacy/simbox-desktop-v2014/www/simbox/sim.php`
→ `design/simbox-web-design-prototype-v2026/lib/pages/sims_page.dart`), grounded in a full re-read of:

- the entire `vdd-simbox-web-design-prototype-icon-statuses` flow (`01-requirements.md` 1331 lines,
  `03-specifications.md` 350 lines, `05-implementation-log.md`) — the approved semantic registry for
  every status icon;
- `flows/legacy/understanding/admin-ui-table-parity/_node.md` and `operator-command-sets/_node.md`;
- the full `legacy/simbox-desktop-v2014/www/simbox/modules/html.php` (every `html_*()` helper, not
  excerpts);
- the currently-shipped `lib/data/terminology.dart` and `lib/data/icon_map.dart` (to mockup with the
  *real* term IDs/labels already in the codebase, not invented ones);
- targeted producer/consumer tracing for fields the icon-statuses flow didn't cover (`pro`, `owner`,
  `PDDAS`, `ASRL`, `fas`, `vip`) in `plan.php`, `system/new_ki.php`, and the native driver
  `svistok-aa/{chan_dongle.h,cli.c}`.

Two corrections from earlier in this session are folded in below (flagged inline where they land):

1. **SOU is not a self-call.** Owner clarification 1.3 in the icon-statuses flow is explicit: SOU
   means one managed SIM calls **another** managed SIM in the system, never itself. The words
   "self-call"/"звонок самому себе" are explicitly prohibited in UI copy. (I used "self-test call"
   in this session's prior turn, going only off the `makecallsebe.sh` filename — that was wrong;
   the owner's clarification overrides the filename.)
2. **The `io`+`qos` cell is a direction-aware union, not incoming-only.** Legacy Addition 1.9
   supersedes Addition 1.5 in the same document: while `io=I` the cell shows incoming recency
   (`SPAM/NEVER/VERY/FAST/SLOW/SOU`), while `io=O` it shows the outgoing live classification
   (`NOS/GOO/BAD/NOR/NEW/NE0/NEC/NEM/SOU/IMO/SYS/VIP/ROB/BLO`) — both are legitimate or the value
   is stale-but-not-fabricated. A mock/prototype must be able to render both families depending on
   `io`, not restrict the field to one family.

Where source evidence runs out, the cell mockup says **"⚠ OPEN Q<n>"** and the exact question is
listed in the consolidated **Open Questions** section at the end — nothing past that marker is
invented.

---

## Screen: Симки — full row (compact form)

One row, legacy column order left to right, each cell shown at the width it actually needs (not to
scale with the real table — this is a semantic strip, not a pixel mockup):

```
+--+-------+----+----+----+------------------+----+---------------+--------+---------------+
|☑ | GROUP |PRO |CAP | IM |   SPEC (5 icons) |STAT| STATE (live)  |NAPR|PLAN/NABOR/TARIF|NUM |
+--+-------+----+----+----+------------------+----+---------------+--------+---------------+
|  |  ▶ 101|  A |✓OK |[B] |[VIP][pre][pos][●][LOC]| →I [FAST]     | RU |default        |9219|
+--+-------+----+----+----+------------------+----+---------------+--------+---------------+

+---------------+--------------------+----------+-----+-----+-----------------+---------+
| OPERATOR/OWNER| BALANCE / bal_diff |MODEL+CFUN|SIMST|DONGLE|  log            | TOT     |
+---------------+--------------------+----------+-----+-----+-----------------+---------+
| МТС           | 3с назад 42.10 ОП:…| 📶 ⏻     | ✓📡 |dongle0| 🗨 ussd&sms  📞 calls | 12 ...|
+---------------+--------------------+----------+-----+-----+-----------------+---------+

+-------+-------+------+------+------+------+------+---------------+------+------+-----+
| a-o/i | m-o/i |ACD-o |ACD-i | ACDL | DATT | IATT | SATT | MAY/MON/MSM+SMS      |ASRL |
+-------+-------+------+------+------+------+------+---------------+------+------+-----+
| 8 / 3 |12:03/…| 1:30 | 2:04 | 1:12 |  3   |  1   |  0   |MAY 2/5 MON 0/3 MSM…  |0.85 |
+-------+-------+------+------+------+------+------+---------------+------+------+-----+

+-------+------+------+-----+---------------------------------------+--------+--------+-----+-----+
|PDDAS  |PDDL0 |PDDL1 | pri |LIMIT0..LIMIT5 (6 separate columns)     | LAC/CELL| IMEI  |IMSI |LOG  |
+-------+------+------+-----+---------------------------------------+--------+--------+-----+-----+
|⚠OpenQ | 0:04 | 0:07 |  —  |[🚩]120/150 |80/100|—|—|—|—                 |A1B2/07C3| 35...  |2500…|↗   |
+-------+------+------+-----+---------------------------------------+--------+--------+-----+-----+

+------------------------------------------+
| DATES: засунут / 1й / посл. / автоблок    |
+------------------------------------------+
| 12.03 / 12.03 / 29.07 / —                 |
+------------------------------------------+
```

### Elements

| Symbol | Meaning |
|--------|---------|
| `☑` | Row selection checkbox |
| `[X]` | An icon glyph (bracket = icon boundary, not literal chrome) |
| `✓ / ⚠ / 🚩` | Ok / warning-color text / over-limit flag icon (`ipalevo.png`) |
| `→I` / `→O` | Direction icon (`state_in.png` / `state_out.png`) |
| `📶⏻ 📡 dongle0 🗨📞` | Placeholders for existing Fugue/GostSimBox glyphs — real assets, not new ones |
| `⚠ OPEN Q<n>` | Field has no source-confirmed meaning/value; see Open Questions |

---

## Component: GROUP (col 2)

Legacy `html_group()` / current `Ico.group()`. The current codebase only wires **half** of the
6-way pause matrix documented in the icon-statuses registry (`groupSchedule` table) — workday
variants (1/11/21) exist, **holiday variants (2/12/22) are not wired** (`icon_map.dart:48-90` has
no `pause==2/12/22` branch — verified by direct read, not the registry alone).

```
┌────────────┐   ┌────────────┐   ┌────────────┐
│  ▶          │   │ ⏸ ☀        │   │ ⏸ 🌙        │
│  101        │   │ 101         │   │ 101         │
│ working     │   │ pause+      │   │ pause+      │
│ (100-299)   │   │ workday (1) │   │ HOLIDAY (2) │
└────────────┘   └────────────┘   └── currently missing icon combo ──┘

┌────────────┐   ┌────────────┐
│ 🚦 333      │   │ ⛔ 5xx      │
│ auto-stop:  │   │ blocked    │
│ high DATT   │   │ (500-599)  │
└────────────┘   └────────────┘
```

Group family reference (icon-statuses `groupSchedule`, confirmed):
`100-299`=working · `1/2/11/12/21/22`=pause/waking/sleeping × workday/holiday · `300`=manual stop ·
`333`=auto-stop high DATT · `334`=auto-stop low ACDL · `335`=auto-block by balance-SMS **or**
carrier-announcement voice recognition (two independent trigger paths, icon-statuses Legacy
Addition 1.8) · `336`=SIM blocked (same dual-trigger) · other `3xx`=generic stop/service ·
`4xx`=low balance · `5xx`=blocked.

---

## Component: PRO (col 3 — currently missing entirely)

```
┌──────┐        ┌──────┐
│  A   │        │  A   │  ← blue (T.brandDeep): SIM's copy ≠ plan's current value
└──────┘        └──────┘
plain: matches   differs: pending re-copy
current plan     (set_plan_copy.sh hasn't run since the plan's `.pro` changed)
```

Mechanism is fully traced (`plan.php:432` single-char per-plan field → `set_plan_copy.sh:52-53`
copies it to `sim/settings/<imsi>.pro` → `sim.php:1361-1366` compares against
`sim/state/<imsi>.pro` and colors blue on mismatch) — but **what the character itself represents
is not documented or referenced by any active branch anywhere in this repo.** It is, however, one
of the fields forwarded per-call to the external server (`system/svistok/callendout.sh`'s posted
field list includes `pro`, per icon-statuses Legacy Addition 1.10) — so it's real, consumed
upstream, just not interpretable locally. **⚠ OPEN Q1 — descoped.** *Ships as:* the raw value plus
the confirmed mismatch mechanism only, labeled exactly as bare as legacy's own unlabeled "pro"
header — no invented explanation of what the character means.

---

## Component: CAP (col 4)

```
┌──────┐   ┌──────┐   ┌──────┐
│ ✓OK  │   │ ✗FAIL│   │  —   │
└──────┘   └──────┘   └──────┘
capOk       capFail     (neither — blank, matches legacy's blank-when-neither behavior)
```

Confirmed via `terminology.dart`'s `captcha.ok`/`captcha.new`/`captcha.fail` — already shipped.
Legacy only ever renders OK/FAIL in this column (sim.php only checks `cap=="OK"`/`"FAIL"`); `NEW`
exists as a term but has no producer wired into *this* cell in legacy — it belongs to the
captcha-flow's own state, not this column. Carry `capOk`/`capFail` only here, matching legacy 1:1.

---

## Component: IM (col 5) — "Destination–SIM affinity"

```
┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  (┌─────┐)
│ IMB │  │ IMC │  │ IMD │  │ IME │  │ IMN │  │ IMA │
└─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘
primary   later    new-SIM  only-    empty    historical —
in Number in Nr.B  allowed  listed   history  no active
B history history  (others  SIMs     (any SIM producer found;
                    exist)  allowed) allowed) do not treat
                                              as confirmed-live
```

All six already have `im.*` terms in `terminology.dart`; `Ico.im()` already wires A/B/C/D/E/N.
No gap — this column is fully correct today, just confirming it for completeness.

---

## Component: SPEC cluster (col 6) — legacy renders up to 5 stacked icons here, current code renders 1

Legacy's single `<td>` for this header cell actually stacks, in order: a per-SIM `vip` tier icon, a
`pre` flag icon, a `pos` flag icon, an `fas` flag icon, and finally the `spec` code icon
(`sim.php:1402-1441`). The current `Sim.spec` model/column only has the last of these five.

```
┌───────────────────────────────────┐
│ [ivip1] [pre] [pos] [fas] [LOC]   │   full legacy stack (all flags active)
└───────────────────────────────────┘
┌───────────────────────────────────┐
│                                    │   nothing active — blank, matches legacy
└───────────────────────────────────┘
```

- `vip==11→ivip1.ico`, `vip==12→ivip2.ico`, `vip>0→ivip.png` (three tiers). This is a **SIM-level
  capability flag**, distinct from the call-level `qos.vip` ("Trusted source" classification,
  different asset `qos/ivip.png` vs this cluster's plain `ivip.png`) — confusingly similar names,
  confirmed-different assets/files, but the exact business distinction between tier 11 vs. 12 vs.
  generic >0 is undocumented anywhere found. **⚠ OPEN Q2 — descoped.** *Ships as:* the exact
  3-way icon branch and its three real assets, tooltip showing only the raw `vip=11/12/N` value —
  no invented tier-meaning copy.
- `pre`/`pos`: icon-statuses registry confirms these are "independent pre-/post-processing flags"
  and that legacy's `html_spec()` has a **duplicate `PRE` condition that is a rendering typo, not
  intended semantics** — already corrected in that flow. But note: `sim.php`'s spec-cluster reads
  them from **separate per-SIM state files** (`.pre`/`.pos`), not through `html_spec()` at all — a
  second, independent pre/pos concept from the `spec=="PRE"` call-mode value. The current
  codebase's own `icon_map.dart` labels these "предоплата"/"постоплата" (prepayment/postpayment),
  which is a plausible-sounding guess **not corroborated by any source found** — the icon-statuses
  registry only ever says "pre-/post-processing," not a billing model. **⚠ OPEN Q3 — descoped.**
  *Ships as:* the already-approved, already-shipped `special.pre`/`special.pos` terminology entries
  ("Pre-processing"/"Post-processing") — not the current codebase's unverified
  "предоплата"/"постоплата" guess, and no new business-meaning claim invented.
- `fas`: **resolved**, not open — icon-statuses Legacy Addition 1.10 traces it precisely: part of
  the proven `OK/qos/IMB2/fas/epdd/fpdd/hem/cap/note` pre-call envelope; `fas=1` schedules
  artificial ring/answer progress after `epdd`/`fpdd` sleeps, `fas=2` on the modem's real alerting
  event. Render as a plain boolean-present icon (`fas.png`), no further ambiguity.
- `spec` code icon: unchanged, existing `Ico.spec()` — but see the Special-Modes note below for a
  labeling gap (`icon_map.dart`'s `_specMap` bypasses `terminology.dart` entirely, using inline
  Russian strings instead of the already-shipped `special.*` term IDs — an internal consistency
  gap worth fixing while this column is touched, not a meaning gap).

---

## Component: STATE / live call (col 7) — entirely missing today

This is the single biggest gap. Legacy stacks, conditionally: a waiting icon, direction+QoS icons,
an outgoing `em_type` raw value, one of four live-call icons with an elapsed-seconds counter, and —
only while busy — two numbers.

```
┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐
│ →I  [FAST]            │   │ →O  [state_dial]       │   │ →O  [state_active]    │
│                       │   │ ( 14 сек.)             │   │ ( 62 сек.)            │
└───────────────────────┘   └───────────────────────┘   └───────────────────────┘
 incoming, recency=FAST      dialing, elapsed since       talking, elapsed since
 (icon-statuses:             stat_call_start              stat_call_connected
  incoming.recency.fast)     (call.live.dial — ⚠ term      (call.live.active — ⚠ term
                             not yet in terminology.dart)   not yet in terminology.dart)

┌───────────────────────┐   ┌───────────────────────┐
│ ⏳ ( 8/120 сек.)       │   │ →O  [state_ring]      │
│  post-call cooldown    │   │ busy → 89261112233    │
│  (call.live.wait)       │   │       89031234567     │  ← numberb / numbera
└───────────────────────┘   └───────────────────────┘     (see SOU variant below)
```

Direction-aware QoS union (icon-statuses Legacy Addition 1.9, supersedes 1.5 in the same doc):

```
io = I  →  qos ∈ {SPAM, NEVER, VERY, FAST, SLOW, SOU}          (incoming recency, per caller+SIM pair)
io = O  →  qos ∈ {NOS, GOO, BAD, NOR, NEW, NE0, NEC, NEM,       (outgoing live classification,
                  SOU, IMO, SYS, VIP, ROB, BLO}                  numeric 0-9/40-42 on the wire)
```

`Ico.qos()` today already handles the SOU in/out split correctly, but its `_qosMap` is **missing
`SPAM`** (present in the registry's `incomingRecency` table, absent from `icon_map.dart`) and
**missing `IMO`/`SYS`** (present in `outgoingSourceClass`, absent from `icon_map.dart`) — three
legitimate values this cell can show today have no icon mapping at all.

Busy-state number pair, **SOU variant** (corrected from last turn — SIM-to-SIM, not self-call):

```
┌───────────────────────┐
│ →O  [state_sout_out]  │
│ busy → 89261112233#SOU│   raw numberb before parsing strips the trailing
│       250020112233445 │   15-digit IMSI of the OTHER managed SIM being called
└───────────────────────┘   (sim.php:1543-1548 — `substr(numberb,-19,4)=="#SOU"`)
```

Three separate "busy" concepts must not share one tooltip (icon-statuses Legacy Addition 1.4):
completed-call result `DIALSTATUS=BUSY` (`call.result.busy`, asset `cup-empty.png`/`recog_types/
30.png`), recognized acoustic busy tone (`recognition.busyTone`, same asset, different axis), and
this column's **live resource-occupancy flag** `sim/state/<IMSI>.busy=1` (a different concept from
both — must not borrow the "Абонент занят" completed-call tooltip).

Two gaps beyond icon wiring:

- `em_type` (raw value echoed with zero interpretation at `sim.php:1474-1476`, printed as-is, no
  `html_*()` helper, no mapping anywhere in this repo). **⚠ OPEN Q4 — descoped.** *Ships as:* the
  raw string, uninterpreted, no icon — this is not a compromise, it's exactly what legacy itself
  does; there is no "richer" version being left on the table.
- Not an open question, just not yet built: `terminology.dart` is missing five term IDs its own
  approved specification (`03-specifications.md`'s `callLiveResult` table) calls for —
  `call.live.dial`, `call.live.active`, `call.result.busy`, `call.result.failed_unknown`, and
  `call.end.unknown` (EP=-1). These are fully source-confirmed (they're rows in an already-approved
  manifest, just never implemented) and are in scope: Specifications will add them by extending the
  existing catalog, not duplicating it.

---

## Component: NAPR (col 8) — billing direction

```
┌──────┐   ┌──────┐   ┌──────┐
│ 🇷🇺 SR │   │ 🇧🇾 VB │   │ ❓ HZ │
└──────┘   └──────┘   └──────┘
ambiguous!   Velcom BY   unresolved/
SR = MTS RU              not classified
  OR Rostelecom SPB
  mobile (`rostel_spb_mob`)
  — legacy's own renderer
  overwrites MTS with
  Rostelecom for this code
  (html.php:78,82 — MTS RU
  assigned then immediately
  reassigned to Rostelecom
  two lines later, same key)
```

`icon_map.dart`'s `_naprMap['SR'] = 'mts_ru'` presents this as unambiguous — the icon-statuses
registry (Direction/zone icons section) already flags this exact collision and requires showing an
explicit ambiguous/route-context-required state rather than confidently picking one. This column's
rebuild inherits that same requirement (not a new finding, just confirming it applies here too).

---

## Component: PLAN / NUMBER (cols 9-10) — unchanged, already correct

```
┌────────────┐   ┌────────────┐
│ default    │   │ 9219981122 │
│ nabor_x    │   └────────────┘
│ tarif_y    │
└────────────┘
```

No gaps found.

---

## Component: OPERATOR / SIM (col 11) — owner line descoped

```
┌──────────────────┐
│ МТС               │
│ МТС Москва         │
└──────────────────┘
 (no owner line — see below)
```

**Descoped 2026-09-05 — owner is not added.** `sim.php:1585` reads
`sim/settings/809<imsi>.owner`, but the only active writer (`system/new_ki.php:15`) writes
`sim/settings/<imsi>.owner` — no writer anywhere targets the "809"-prefixed path, so the legacy
column is very likely always empty in production. Whether to faithfully reproduce that always-blank
bug or fix the path and show real data is a product decision (**OPEN Q5**), and per this session's
scope instruction, open questions are not pursued this iteration — so the third line is simply
omitted rather than guessed at either way.

`owner` itself (when the path bug doesn't swallow it) is traceable: `new_ki.php` receives it as a
CLI argument sent on to the external `simserver:8122/sim/get_new_ki.php?...&owner=$owner` when
requesting a new KI, and persists it on success — so it is a real, externally-supplied identifier
(reseller/customer tied to this SIM's KI request), just broken in the display path. Kept here for
provenance only — not implemented this iteration.

---

## Component: BALANCE / bal_diff (col 12) — unchanged, already correct

`html_op()` fully traced and unambiguous: "ОП" = a promised-payment/credit status
(`get_dover`/"Get dover" action elsewhere on the page = "Подключить обещанный платеж"), rendered as
`нет, траты<50` / `нет, баланс` / `до <date>` / `через N дн.` / `можно`. Existing `s.op`/`s.balAge`/
`s.balDiff` fields already model this correctly — no gap.

---

## Component: MODEL+CFUN / SIMST+SRVST (cols 12-13) — unchanged, already correct

All values (`CFUN 1/4/5/6`, `SIMST 0/1/3/4/16/255`, `SRVST 0/1/2/112`) already have confirmed
`terminology.dart` entries and are already wired in `Ico.cfun/simst/srvst`. No gap.

---

## Component: DONGLE + hub port label (col 14)

```
┌──────────────┐          ┌──────────────┐
│ dongle3       │          │ dongle0      │
└──────────────┘          │ hub2/port3   │  ← dongle_a, only for
                            └──────────────┘     `dongle0*` (hub-connected)
```

`dongle_a` is self-explanatory from source (`file_get_contents_def2($path.'.imei_name')`, hub-port
label) — fold in as a sub-line per the requirements doc's resolved open question, shown only when
non-empty (i.e., only for hub-attached dongles).

---

## Component: TOT / a-o·a-i / m-o·m-i / ACD / ACDL / DATT / IATT / SATT — unchanged, already correct

All already wired with correct legacy semantics (out-call totals, IM breakdown, per-direction
minute/answer counters, ACD, alarm flags for ACDL/DATT/IATT/SATT). No gaps found in this cluster.

---

## Component: MAY / MON / MSM + SMS quota (col 25) — currently 2 of 4 lines shown

```
┌──────────────────────┐
│ MAY  2 / 5            │  ← command.operatorCallbackRequest, "attempts / limit", not
│ MON  0 / 3            │    confirmed delivery (icon-statuses Legacy Addition 1.1
│ MSM  1 / 2            │    acceptance criteria #3: tooltip must say so explicitly)
│ SMS  4 / [0;10]        │  ← command.callback_sms_fallback quota (currently missing)
└──────────────────────┘     smsout_sended / [smsout_soft;smsout_hard] — the fallback's
                              own separate gate (currently missing)
```

This is a confirmed, named data-loss defect, not a guess — icon-statuses Legacy Addition 1.1,
acceptance criterion #4: **"`MSM` must be added back to the SIM and Plan parity manifests; the
current prototype's omission is a data-loss defect."** Also per that addition: `spec=MAY` (the
short-call beacon, a live **call**) is a *different* concept from the `command.operatorCallbackRequest`
counter shown here (a USSD **command**) — both are named "MAY" in raw legacy but must not be
conflated in copy. Tooltip must state attempts are not confirmed-delivered (executor increments the
counter and clears `need_sms` regardless of success/failure).

---

## Component: ASRL / PDDAS / PDDL0 / PDDL1 (cols 26-29)

```
┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
│ 0.85 │  │ ⚠OpenQ│  │ 0:04 │  │ 0:07 │
└──────┘  └──────┘  └──────┘  └──────┘
 ASRL      PDDAS      PDDL0     PDDL1
```

Two independent, source-grounded findings neither this session's earlier pass nor the icon-statuses
flow surfaced (that flow didn't cover this numeric-stats cluster at all):

- **`PDDAS` is real in the native driver, but legacy's PHP table has always shown the wrong value
  for it.** `svistok-aa/cli.c:256,266-291` proves the Asterisk CLI table has a genuine `PDDAS`
  column computed as `getACD(stat_out_calls[1], stat_wait_duration[1])` — average post-dial delay
  across all outgoing attempts, **distinct** from `PDDL0`/`PDDL1` (`stat_pddl[0/1][1]/1000` — raw
  per-answered/unanswered PDD sums). `sim.php`'s web table, however, prints `stat_asrl` twice (once
  for `ASRL`, again for `PDDAS`) — its own PHP-layer copy-paste bug, confirmed by cross-referencing
  against the C driver's real, differently-computed value. **This resolves what was an open
  question last turn**: PDDAS is a real, distinct, definable metric; only the PHP UI's specific
  implementation of it was ever broken. **⚠ OPEN Q6 — descoped.** *Ships as:* the `PDDAS` column
  exists (already decided, not itself open) with a plausible distinct mock number; no claim which
  of the two real-world formulas (PHP's buggy copy vs. the driver's real average) it represents.
- **`ASRL`'s own name is misleading.** Its column letters read like "Answer-Seizure Ratio, Last N,"
  but `chan_dongle.h:129` stores it in `stat_asrl[3]` immediately below `stat_acdl[3]` with the
  **identical, verbatim, copy-pasted C comment** ("Последние ACD для ACDL звонков" applies to both
  fields), and `cli.c:290` formats it exactly like a duration (`/1000`, i.e. milliseconds→seconds),
  the same treatment as the actual ACDL field. **⚠ OPEN Q7 — descoped.** *Ships as:* the column is
  already correctly implemented and unchanged; no rename, no new tooltip claim about what it
  measures.

---

## Component: pri (col 30) — unchanged (kept per user decision)

No new evidence found beyond what was already known (legacy never renders this column live —
commented out). Kept as-is per the earlier approved decision; no visual change needed.

---

## Component: LIMIT0..LIMIT5 (cols 31-36) — six separate columns, per approved decision

```
┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│ 🚩120 / 150│ │ 80 / 100   │ │  —  / —    │ │  —  / —    │ │  —  / —    │ │  —  / —    │
│ LIMIT0     │ │ LIMIT1     │ │ LIMIT2     │ │ LIMIT3     │ │ LIMIT4     │ │ LIMIT5     │
└────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘
  🚩 = ipalevo.png, shown when this slot's `.palevo` (slot 0) / `.N.palevo` (slots 1-5) is "1"
```

The `ipalevo.png` flag icon is the **same asset** used for the still-unresolved `captcha.pal`
("PAL") term — the icon-statuses flow explicitly left `PAL`'s operator-facing name as an open
question ("нормальное имя не найдено") even after its own deep dive, and nothing found in this
session's research resolves it either. A plausible-sounding Russian slang etymology exists
("спалиться"/"палево" = "getting caught/detected [as a SIM-box] by the carrier") but **this is a
guess, not a finding** — flagging it only as a hypothesis worth testing with the product owner, not
as confirmed meaning. **⚠ OPEN Q8 — descoped.** *Ships as:* the existing, already-approved
`captcha.pal` unresolved term reused verbatim for all six `LIMITn` flags — no new name, no slang
etymology surfaced in the UI.

---

## Component: LAC/CELL, IMEI/IMSI, log, dates — unchanged, already correct

No gaps. IMEI blacklist bold-red styling already modeled via `imeiWarn`.

---

## State: row with SOU internal call in progress

```
┌────┬───────┬────┬────┬────┬───────────────┬────┬────────────────────────┬─────┐
│ ☑  │ ▶ 101 │ A  │✓OK │[B] │ [ivip][pre][…]│ →O │[state_sout_out]         │ RU  │
│    │       │    │    │    │               │    │busy→ 89261112233#SOU   │     │
│    │       │    │    │    │               │    │      250020112233445  │     │
└────┴───────┴────┴────┴────┴───────────────┴────┴────────────────────────┴─────┘
Label: "Внутренний звонок между SIM" (icon-statuses required RU label) — never
"звонок самому себе" / "self-call".
```

## State: row with over-limit + blacklisted IMEI + pro pending

```
┌────┬───────┬───────┬────────────────┬─────────────────┬──────────────────────┐
│ ☑  │ ▶ 101 │ A(blue)│ [🚩]120/150   │ ... │ 35...(red/bold)│ 2500...         │
└────┴───────┴───────┴────────────────┴─────────────────┴──────────────────────┘
 pro differs      LIMIT0 palevo         IMEI on blacklist file, bold red
 from plan         flag active          (already modeled via imeiWarn)
```

## State: empty table (filtered to zero rows)

```
+------------------------------------------------------------+
| Симки            Всего: 0                                  |
+------------------------------------------------------------+
|         фильтр по группе/плану вернул пустой результат       |
|         [Сбросить фильтр]                                    |
+------------------------------------------------------------+
```

---

## Consolidated Open Questions — descoped 2026-09-05

**Scope decision: none of the items below are pursued in this iteration.** The user's instruction
was explicit — implement only what's confirmed by legacy code; skip everything still open. Each
item's "what ships instead" note says exactly what the confirmed-only implementation does. This
list stays for provenance/future reference, not as pending work.

1. **`pro`** — mechanism (set-vs-current, blue on mismatch) is fully traced; the single-character
   *value*'s business meaning is not defined anywhere active in this repo. It is forwarded to the
   external server per-call (`callendout.sh`) but its server-side interpretation is outside this
   checkout. Cannot be resolved from source alone — needs the product owner or the external server.
2. **`vip` tiers** (`vip==11→ivip1.ico`, `vip==12→ivip2.ico`, `vip>0→ivip.png`) — three visually
   distinct capability-tier icons with no documented distinction anywhere found, and a name
   collision with the unrelated call-level `qos.vip` classification (different asset paths,
   confirmed different concepts, but confusingly similar labels).
3. **`pre`/`pos` dual meaning** — icon-statuses confirms these are "pre-/post-processing flags" as
   a `spec` value; but `sim.php`'s spec-cluster reads them from independent per-SIM state files,
   and the current codebase's own guess-label ("предоплата"/"постоплата," i.e. prepayment/
   postpayment) is not corroborated by any source found. Are these the same concept in two
   producers, or genuinely two different `pre`/`pos` ideas that happen to share a name?
4. **`em_type`** — raw value echoed with zero interpretation anywhere in legacy; no `html_*()`
   helper, no comment, no other consumer found.
5. **`owner` display bug** — `sim.php` reads `sim/settings/809<imsi>.owner`; the only active writer
   (`system/new_ki.php`) writes `sim/settings/<imsi>.owner` (no "809" prefix). No writer anywhere
   targets the prefixed path, so the legacy column is very likely always empty in production today.
   Product decision needed: reproduce this bug faithfully (owner sub-line always blank), or treat it
   as a defect and show the real value the way the feature obviously intended?
6. **`PDDAS` implementation choice** — meaning is now resolved (average post-dial delay across all
   outgoing attempts, per the native driver's own CLI), but legacy's *web* table has always shown a
   copy-paste bug (repeats the `ASRL` value) instead. Faithfully reproduce the web bug, or compute
   the real driver-defined metric?
7. **`ASRL`'s true meaning** — name suggests an answer-seizure ratio (a percentage), but its native
   storage/format (`/1000`, duration-shaped, identical treatment to `ACDL`) and its C struct's own
   copy-pasted comment both point to a duration metric instead. Unresolved from any source read.
8. **`PAL` / `ipalevo.png`** — carried forward unresolved from the icon-statuses flow's own open
   question (their deep dive didn't resolve it either); now also relevant to all six `LIMITn`
   over-limit flags, which reuse the same asset. A Russian-slang etymology guess exists but is
   explicitly flagged as unconfirmed, not a finding.
9. *(Carried forward from the icon-statuses flow, unresolved there and still unresolved here since
   they touch this table's icon set)*: exact operator-facing names for `SPE`/`MAG`/`NAV`/`MON`
   (as a `spec` value, distinct from the `command.balance_topup_request` action of the same raw
   name); `IMA`'s producer; `REC=90/91/92` and the exact `110-119`/`120-129` subcode boundaries
   (computed server-side, likely permanently unresolvable from this checkout).
10. **Direction code collisions** (`SR`=MTS RU vs. Rostelecom SPB mobile) — already flagged by the
    icon-statuses flow as needing an explicit ambiguous-state UI treatment; applies directly to
    this table's `napr` column and is not yet fixed in `icon_map.dart`'s `_naprMap`.

---

## Notes

- This document deliberately does not yet propose Dart types/widget changes (e.g. how `Cell` grows
  to fit a 5-icon spec cluster, or how `terminology.dart` gains the five missing `call.live.*`/
  `call.result.*`/`call.end.unknown` entries) — that belongs in 03-specifications.md once this
  visual is approved.
- Every "unchanged, already correct" cluster above was independently re-verified against source in
  this pass, not assumed from the earlier gap table.

---

## Approval

- [ ] Reviewed by:
- [ ] Approved on:
- [ ] Notes:
