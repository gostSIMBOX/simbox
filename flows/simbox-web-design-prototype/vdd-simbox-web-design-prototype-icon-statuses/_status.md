# Status: vdd-simbox-web-design-prototype-icon-statuses

## Current Phase

DOCUMENTATION

## Phase Status

REVIEW

## Last Updated

2026-09-02 by Codex

## Blockers

- None.

## Progress

- [x] Requirements drafted
- [x] Requirements approved
- [x] Visual mockups drafted
- [x] Revised visual approved
- [x] Specifications drafted
- [x] Specifications approved
- [x] Plan drafted
- [x] Plan approved
- [x] Implementation started
- [x] Implementation complete
- [x] Documentation drafted
- [ ] Documentation approved

## Context Notes

- Target: `design/simbox-web-design-prototype-v2026`.
- Scope: status-icon names, labels, tooltips and the Icons reference page across all tables.
- Semantic sources of truth: legacy admin/runtime code and `libsCpp/asterisk-chan-svistok/src`.
- Icon assets must follow the GostSimBox taxonomy and Fugue 16×16/32×32 density contract.
- Visual appearance alone is not sufficient evidence for a status meaning.
- Deep MAY/MON/MSM audit complete: call MAY, command MAY, command MON and MSM fallback are four
  separate semantic entries; MSM is not Multiple-SIM and automatic MON is disabled in legacy.
- Owner-confirmed global MON semantic: request asking another person to top up this SIM's balance;
  Beeline service detail is the free “Пополни мой счёт”.
- Owner-confirmed SOU semantic: internal call from one managed SIM to another managed SIM;
  incoming/outgoing assets represent the two call legs, not a SIM calling itself.
- BUSY legacy trace complete: active call-result renderer uses `recog_types/30.png`, derived from
  Fugue `cup-empty.png`; call BUSY, recognition 30 and live resource busy remain separate meanings.
- **Visual 2.0 owner correction (2026-09-02):** keep the current Icons page geometry and behavior;
  correct labels/tooltips only. Withdraw search/filter/expanded-registry UI. Name the content
  “Icon legend / Легенда иконок” and add a separate Glossary reference destination.
- **Visual 2.0 approved (2026-09-02):** Specifications revised to preserve `IconsPage`, type the
  existing catalog without changing order/count, centralize terminology, add separate Glossary,
  and use verified Fugue `book-open-list.png` 16×16/32×32 for its navigation item.
- **Specifications 2.0 approved (2026-09-02):** Plan 2.0 drafted in eight guarded tasks. It starts
  with a frozen legend structure test, then shared terminology, text-only legend/table corrections,
  separate Glossary, verified Fugue pair/navigation, and visual regression validation.

- **Resumed 2026-09-02 by Claude** (flow originally drafted by a different agent, "Codex").
  Independently spot-verified the requirements doc's factual claims against the actual repo
  before treating it as ground truth — all checked out exactly:
  - `html.php:142` really renders `DIALSTATUS=BUSY` via `imgs/recog_types/30.png`, and the same
    file's `recog_types_sim`-style mapping reuses `30.png` for recognition code `30` too —
    confirms the dual-axis-reuse claim precisely.
  - `sim.php:2215-2218` confirms group `333`/`334`/`335`/`336` legacy comments verbatim
    (DATT/ACDL/balance-SMS/blocked).
  - `dongle.php:451-456`'s RSSI bucket boundaries match the doc's 0 / 1–6 / 7–14 / 15–19 / 20–31
    buckets exactly (including `rssi==31` folding into bucket 4).
  - `select.c`'s `uu_nos/uu_goo/uu_nor/uu_new/uu_ne0/uu_nec/uu_nem/uu_rob/uu_blo/uu_sou` variables
    and `qos==0/1/3/40/41/42` confirm the QoS code family the doc describes.
  - Read the current `lib/data/icon_map.dart`/`icons_catalog.dart`/`icons_page.dart` end to end
    and found the exact defects the requirements doc predicts already exist in code, not just in
    theory: `Ico.simst()` has no `case 3` (falls to "simst неизвестен" — matches "`SIMST=3` must
    not disappear"); `Ico.cfun(4)` is literally labeled "только приём" (must be "SIM removed"
    per the doc); `Ico.simst(4)` is literally labeled "SIM занята" (forbidden label per the doc);
    `Ico.group()`'s `300-399` fallback labels *any* unassigned 3xx as "низкий ACDL" (the doc's
    exact warning); `Ico.srvst()` has no composite `srvst/112` case at all; `Ico.im()` labels
    every code "мульти-сим $v" (the exact forbidden terminology); `icons_catalog.dart` literally
    contains `'msm.png|msm|мультисим'` and `'91|ошибка 91'` — the doc's own named-bad-example
    strings, verbatim, in the current code. This is strong independent confirmation the
    requirements doc is accurate and not speculative — safe to build on.
  - One evidence path from the doc, `nativemind-adminka/assets/adminka/adminka-to-fugue-map.json`,
    doesn't exist as a repo-relative path — it's a `nativemind-adminka` *skill* resource, not a
    project file. Low-stakes (cited only for BUSY asset provenance detail); not a defect in the
    doc's core analysis, just an evidence-citation format quirk worth knowing about later.
  - Remaining true open item: Open Question 2 (does the Icons page default to
    "used in current tables" with a separate historical/all filter, or open on the full legacy
    catalog?) — Open Question 1 reads as resolved via "Legacy Addition 1.1" (required Russian/
    English labels stated for all four MAY/MON/MSM concepts) and owner clarifications 1.2/1.3 are
    already recorded as answered in the doc itself.

- **Open Question 2 resolved 2026-09-02 (owner decision, asked directly):** Icons page defaults
  to the **full legacy catalog** (not used-only) — overrides this document's own earlier
  recommendation. Recorded in `01-requirements.md`'s Open Questions section and its "Should Have"
  bullet under Icons Page Requirements.
- **Legacy Addition 1.5 (2026-09-02, Claude)** — user asked whether "Давность предыдущего
  соединения" (`VERY`/`FAST`/`SLOW`/`NEVER`/`SPAM`) relates to one specific bound SIM. Traced
  every `.qos`-file writer in the active tree: **only** `[macro-incoming-full]` in
  `extensions_incoming_full.conf` ever writes `/var/svistok/sim/state/<IMSI>.qos`, and it can
  only write `SPAM`/`NEVER`/`VERY`/`FAST`/`SLOW`/`SOU` — never `VIP`/`GOO`/`NOR`/`BAD`/`NEW`/
  `NOS`/`ROB`/`BLO`/`NE0`/`NEC`/`NEM` (those stay transient outgoing-call channel variables in
  `[macro-checknumber]`/`select.c`, never persisted per-SIM). The query is scoped to one SIM by
  construction (`conn_getstat.php?numberb=<this SIM's own number>&imsi=<this SIM's IMSI>`).
  `sim.php`'s live-call cell reads this same file for *both* directions, so during an active
  outgoing call the operator sees stale incoming-classification data, never the outgoing
  source class. `design/simbox-web-design-prototype-v2026/lib/pages/sims_page.dart`'s `io`
  column (`Ico.io`+`Ico.qos`) is a faithful port of that exact cell — meaning **6 of 7 of its
  current mock `Sim.qos` seed values (`GOO`/`NOR`/`BLO`/`VIP`/`BAD`/`NEW`) are values that cell
  can never legitimately hold**; only `FAST` among the current seeds is valid. Full writeup +
  new acceptance criteria #13-16 in `01-requirements.md`'s Legacy Addition 1.5.

- **Legacy Addition 1.6 (2026-09-02, Claude)** — finished the NE0/NEC/NEM trace a prior session
  (Codex) started but got interrupted mid-way (hit usage limit). `extensions_dial.conf:255-257`:
  only the `NEC` dispatch (`GotoIf $[qos+cap == "NEWOK"]`) is active; `NE0`/`NEM`'s dispatch
  lines are commented out, so those two are dead code today (Historical/unresolved), while
  `NEC` is live and means "NEW number that just passed a CAPTCHA" — not a "no-response variant"
  as originally framed. Also noted the `res` string these are `CUT()` from comes from
  `CALLERID(name)` in the active code, not a live HTTP call — the classification is computed
  upstream of this macro, out of scope to trace further here.
- **User asked for the full consolidated icon list (2026-09-02)** — compiled and delivered in
  chat (13-section table, matching the structure a prior Codex session had built up piece by
  piece), reconciling all corrections above (SOU, BUSY, MAY/MON/MSM split, qos per-SIM
  restriction, NE0/NEC/NEM). Not yet copied into a flow file as a standalone artifact — exists
  as this session's chat response plus the source corrections already in the sections above.

- **Legacy Addition 1.7 (2026-09-02)** — user correctly pushed back that outgoing `qos` is
  genuinely produced in `extensions_dial.conf`/`extensions_dial_zones.conf`. Traced full chain:
  `select.c:258` reads the same "qos" channel var the dialplan sets; `select.c:125-139` maps it
  to numeric + `billing_pay` (SYS/NOS collide at 0); `select.c:1048`→`at_response.c:1110`→
  `callendout.sh:36` writes it into 4 **call-log files** (`.calls`/`.calls2`/`calls.full`/
  `calls.<naprstr>`), read by `log/calls.php`. This closes Legacy Addition 1.5's "if shown
  anywhere" — confirmed: outgoing qos shows in the call log, never the Sims table's live cell.
  Also mapped all 18 `simserver:8122` endpoints found in the active tree (incoming/outgoing/SMS/
  captcha/KI/recognition), flagging `calltry.sh`/`trycall.sh` as orphaned (unreferenced anywhere).
- **Legacy Addition 1.8 (2026-09-02)** — deep dive on recognition codes per user's guesses.
  Found the recognition axis is **two mechanisms**: DSP/acoustic (0/10/20/30/50-59, textbook
  AMD-classifier shape) vs ASR phrase-matching on the calling SIM's *own* carrier announcements
  (`dorecog.php`→`simserver:8122/recog/recog_save.php`, which computes the numeric code
  **server-side, not in this checkout**). Confirmed 110-119=insufficient-funds and
  120-129=blocked-number families via `recog_types_sim.php`'s code comments + phrase dictionary
  — but these are about *this SIM's own* balance/block status (its own carrier's announcement),
  not the called party's, correcting the user's framing. Discovered a previously-undocumented
  second path into groups 335/336 via `ai/recog/parse/all.php`'s phrase-triggered
  `dongle setgroupimsi`. Explicitly could NOT confirm 90/91/92's exact meaning or that 10/30 are
  spoken-phrase results (10="тишина"/silence per existing evidence, 30 shares its asset with
  protocol-level BUSY per Addition 1.4) — the server-side classifier isn't in this repo.

- **Legacy Addition 1.10 (2026-09-02)** — traced the pre-call `simserver:8122` boundary. Archived
  dialplan directly calls `start_v2.php`; active dialplan's `start_v3.php` curl is commented and
  consumes the upstream result through `CALLERID(name)`, with `specstr` in `CALLERID(RDNIS)`.
  Proven envelope: `OK/qos/IMB-history/fas/epdd/fpdd/hem/cap/note`. `GOO/...` are remote
  classifications; `NEC` and IM `B/C/D/E/N` are derived locally. `_IMA2` is not consumed by the
  active selector. Missing/malformed QoS can fall through numeric zero and loosen IM affinity.
  The server implementation/database rules are not present in this checkout; the current Node
  server only documents the legacy compatibility endpoint.

- **Legacy Addition 1.11 (2026-09-02)** — owner supplied a server SQL fragment for
  `total_numberb`; an identical copy exists under `patch_2.9/TODO.md` after `opt/replica`.
  Confirmed number-B aggregates (`total_billsec`, `total_answered`, `total_calls`) and a ranged
  top-1000 extraction. The range-only list has 35 ranges/6,238,567 values; the actual SELECT has
  34/5,838,567 and omits `79006200000..79006599999`. This proves aggregate evidence but not the
  missing mapping to `GOO/NOR/...`; client-side inference from those columns is prohibited.

- **Legacy Addition 1.12 (2026-09-02)** — owner confirmed `GOO` requires number-B ACD at the
  300-second level and ASR at 80%; ACD is `total_billsec / total_answered`, ASR is
  `total_answered / total_calls * 100`. Owner then confirmed inclusive comparisons and constants:
  `ACD >= GOO_ACD` (`300`) and `ASR >= GOO_ASR` (`80%`). Updated label/tooltip and retained the
  server-authoritative class.

## Fork History

N/A — new flow.

## Next Actions

1. Review the implemented Icons labels/tooltips and separate Glossary page.
2. Approve documentation or request corrections.
3. On approval, close the VDD flow.
