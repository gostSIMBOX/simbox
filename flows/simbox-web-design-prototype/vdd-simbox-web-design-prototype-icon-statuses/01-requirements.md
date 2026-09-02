# Requirements: Icon statuses and tooltips

> Version: 1.0  
> Status: DRAFT — awaiting owner review  
> Last Updated: 2026-09-02

## Problem Statement

The prototype currently treats an icon filename and a short Russian caption as the status
definition. That has caused several kinds of semantic drift:

- raw modem values, derived/composite states, call results, plan capabilities, actions and
  decorative icons are mixed into one flat Icons page;
- several labels contradict the code that produces the value;
- the tables and the Icons page keep separate mappings, so their tooltips can diverge;
- some legacy image reuse is presented as if it meant the same state (for example the same
  dialing image is used for live dialing and the final `NOANSWER` result);
- unknown values and missing assets can become a blank 16×16 area with no diagnostic text;
- direction codes are presented as globally unique although legacy contains collisions.

The redesign must preserve the operational meaning established by the legacy runtime and
`chan_svistok`, while making every status understandable without reading the source.

## Goals

1. Establish one code-backed name and tooltip contract for every status icon used by a table.
2. Make the Icons page a reliable reference for operators and developers rather than an asset
   contact sheet.
3. Generate table icons and the Icons page from one semantic registry.
4. Keep raw codes visible for diagnostics without forcing an operator to decode them.
5. Clearly distinguish protocol values, derived/composite states, historical values, plan
   capabilities and UI actions.

## Source Precedence

When sources disagree, use this order:

1. the place where the runtime value is assigned or derived in
   `libsCpp/asterisk-chan-svistok/src`;
2. active Asterisk dialplan and active shell/PHP runtime logic in
   `legacy/simbox-desktop-v2014`;
3. active legacy rendering helpers and help text;
4. filenames and visual appearance only as supporting evidence.

Commented-out legacy UI is historical evidence, not active functionality. An obvious rendering
typo may be corrected when the surrounding runtime proves the intended value; it must be noted
in provenance rather than copied as behaviour.

## Users and User Stories

- As an operator, I can hover or focus any status icon and first read its operational meaning,
  then its exact raw code or condition.
- As an operator, I can distinguish a current/live state from a completed call result even when
  legacy reused one picture for both.
- As a support engineer, I can open Icons, search by visible name, raw value, legacy filename or
  semantic axis, and find the same meaning used in tables.
- As a developer, I can trace each non-generic status to the legacy/driver expression that creates
  it and can see whether it is raw, derived, composite, configured or historical.
- As a keyboard or assistive-technology user, I receive the same accessible name without relying
  on pointer hover.

## Status Taxonomy

Every registry item must declare exactly one kind:

| Kind | Meaning | Examples |
|---|---|---|
| Raw status | value received or persisted unchanged | `CFUN=1`, `SIMST=255`, `DIALSTATUS=BUSY` |
| Derived status | range/rule calculated from raw data | RSSI bucket 0–4, group family 4xx |
| Composite status | condition made from two or more fields | PIN required, network reported while SIM invalid |
| Live state | transient current activity | dialing, ringing, active call, cooldown |
| Result | completed operation/call outcome | answered, no answer, busy, failed |
| Classification | request/caller/recognizer class | QoS, Destination–SIM affinity, recognition result |
| Capability/policy | configured permission or plan flag | iGOO enabled, can receive SMS |
| Action/navigation | clickable command or destination | call log, power, refresh |
| Hardware/decoration | equipment identity or tree grammar | E173, USB hub, tree branch |
| Historical/unresolved | asset/value retained for audit only | IM `A` unless an active producer is found |

The Icons page must not present a capability, action or decoration as a current device status.

## Registry Contract

There must be one typed semantic registry used by both `Ico`/table rendering and the Icons page.
Each entry must be able to carry:

- stable semantic ID and semantic axis;
- kind from the taxonomy above;
- exact raw value, range or composite condition;
- concise operator label;
- full tooltip/accessibility text;
- legacy 16×16 asset and, for Fugue generic icons, the matching 32×32 density asset;
- table/page contexts where the icon is valid;
- aliases and legacy filenames;
- evidence/provenance reference and confidence (`confirmed`, `derived`, `unresolved`);
- localisation key; protocol codes remain unchanged in every language.

An entry may deliberately reuse an image, but it must retain a context-specific semantic ID and
tooltip. Asset identity must never imply semantic identity.

## Naming and Tooltip Rules

1. Operational meaning comes first; raw code or condition comes second.
2. A table tooltip uses the format `Meaning · AXIS=value` or
   `Meaning · condition`, without exposing an asset filename.
3. The Icons reference adds kind, source/condition, contexts and asset provenance.
4. Use sentence case and concrete nouns/verbs. Avoid labels such as `нормальные`, `быстрый`,
   `мульти-сим B`, `ошибка 91` or a bare `MAY`.
5. Keep established protocol abbreviations (`CFUN`, `SIMST`, `SRVST`, `QoS`, `IMB`, `ACDL`,
   `DATT`) in technical detail, not as the only human label.
6. For a composite state, show the actual condition rather than inventing a raw value.
7. Critical/unknown states retain accompanying text or raw value; the icon is not the only signal.
8. Missing assets and unknown raw values show an explicit unknown glyph plus the raw value; never
   an empty box.
9. Tooltip content must also be available via semantics/focus; hover alone is insufficient.

## Code-backed Corrections Required

### Group and schedule

- Support all active pause combinations rendered by legacy:
  `1 = pause + workday`, `2 = pause + holiday`, `11 = waking + workday`,
  `12 = waking + holiday`, `21 = sleeping + workday`, `22 = sleeping + holiday`.
- `333`: automatic stop for high consecutive-failure/DATT condition; `334`: automatic stop for
  low ACDL; `335`: automatic block following the balance-block SMS condition; `336`: SIM blocked.
- Unknown `3xx` values must be called a stopped/service group, not automatically “low ACDL”.
  Group `300` is used as manual stop in configurations.
- `4xx` is the low-balance family; `5xx` is the blocked family. Do not classify every value
  `>=500` as blocked.
- The numeric group remains visible; the icon describes the group/schedule state, not its routing
  destination.

### Live call state vs call result

Use separate semantic entries even where legacy reused a PNG:

- live dialing — dialing is currently in progress;
- live remote ringing/ringback — the outgoing call is alerting;
- live active call — a conversation is active;
- live wait/cooldown — the SIM is waiting before it may be selected again;
- result `ANSWER` — call answered;
- result `NOANSWER` and `NOANSWER_USERALERTING` — call was not answered;
- result `BUSY` — remote party busy;
- result `FAILED`/unknown — failed or unclassified result.

`NOANSWER` must never be labelled “dialing”. `RING` must not use the ambiguous label “rings”
without identifying the side/context.

### Call end party

This axis answers **who/what ended the connection**. Use the Russian heading
**«Источник завершения соединения»** and the compact table tooltip wording
**«Соединение завершено …»**. Legacy scripts explicitly define
`we=1`, `other=2`, `network=3`:

- `END_PARTY=1` — connection ended by our/local side / «Соединение завершено нашей стороной»;
- `END_PARTY=2` — connection ended by the remote party / «Соединение завершено удалённой стороной»;
- `END_PARTY=3` — connection ended by the network / «Соединение завершено сетью»;
- `END_PARTY=-1` — source of connection termination not determined / «Источник завершения не определён».

The wording must not hard-code “caller/callee”, because the same values are logged for incoming
and outgoing calls. `END_PARTY` identifies the source/initiator of termination, not the full
telephony cause. When `CC_CAUSE` and `END_STATUS` are available, the call-result tooltip must
combine all three, for example:

`Connection ended by network · END_PARTY=3 · CC_CAUSE=31 · END_STATUS=104`.

This lets the operator understand why the connection ended without incorrectly expanding one
field beyond what the legacy code proves.

### Modem function, SIM and network

- `CFUN=1` — modem/radio in full operating mode.
- `CFUN=5` — modem offline. PIN-required is a separate composite condition.
- `CFUN=4` — driver state labelled `SIM removed`; the driver immediately schedules `CFUN=6`.
  It must not be labelled “receive only”.
- `CFUN=6` — restarting/resetting.
- `SIMST=255` — no SIM, explicitly handled by the driver.
- `SIMST=1`, `3` and `4` are accepted by this driver as SIM-present states. `SIMST=4` must not be
  labelled “SIM busy”, and `SIMST=3` must not disappear.
- PIN required is derived from `pinrequired` (legacy renders it with the `simst/16` asset when
  `SIMST=0`); it is not a raw `SIMST=16` protocol value.
- `SRVST=0/1/2` remain raw modem network-service values; operator wording must remain conservative
  where local code only proves the raw value.
- the `srvst/112` picture represents the composite condition `SRVST=1` with an invalid/missing SIM;
  it is not raw `SRVST=112`.

For rows containing CFUN, SIM and network, the registry/rendering API must accept the relevant
fields together so that composite states can actually be selected.

### Signal strength

Legacy derives five icon buckets from raw CSQ:

- bucket 0: CSQ 0;
- bucket 1: CSQ 1–6;
- bucket 2: CSQ 7–14;
- bucket 3: CSQ 15–19;
- bucket 4: CSQ 20–31.

The tooltip must identify a displayed value as a derived signal bucket and include raw CSQ and/or
dBm when available. It must not imply that the modem protocol itself returns only 0–4.

### QoS/request classification

The active `chan_svistok` selector recognises:

- `VIP` — trusted-source call;
- `GOO` — known number with very high historical call quality;
- `NOR` — known number with normal historical indicators;
- `BAD` — known number with poor historical indicators;
- `NEW` — number absent from the lists;
- `NOS` — classification unavailable because the server did not respond;
- `NE0`, `NEC`, `NEM` — distinct server/classifier no-response variants; retain their raw suffix
  and mark the human expansion unresolved until a producer definition is found;
- `SOU` — internal SIM-to-SIM call: one managed SIM calls another managed SIM; the asset depends
  on whether the displayed row is the originating or receiving leg;
- `IMO` — IM-related request class;
- `SYS` — system request class;
- `ROB` and `BLO` — suspicious automated/call-through classifications, with `BLO` the stronger
  blocked class. Avoid claiming that the callee literally is “a robot”.

Plan flags named iVIP/iGOO/etc. are capabilities to accept these request classes, not the current
request status, and must appear under Policy/Plan when shown on Icons.

`VERY`, `FAST`, `SLOW`, `NEVER` and `SPAM` belong to the legacy incoming-call recency/routing axis:

- `VERY`: previous connection was under 4 minutes ago;
- `FAST`: previous connection was under 30 minutes ago;
- `SLOW`: previous connection was 30 minutes ago or more;
- `NEVER`: no previous connection (`minutesago=-1`);
- `SPAM`: suspicious result (`minutesago=-2`).

They may retain their legacy assets, but must not be labelled merely as QoS speed levels or mixed
with the `chan_svistok` source classifications without a subgroup.

### Destination–SIM affinity (IM)

Use the operator-facing Russian term **«Привязка SIM к номеру по истории вызовов»**. The compact
English heading is **Destination–SIM affinity**. Do not use “Multiple-SIM”, “Multi-SIM” or
«мультисим»: those terms can be mistaken for a multi-SIM card/device/service, while this axis
classifies one candidate SIM relative to the destination number's call history.

The selected SIM affinity is code-defined as:

- `IMN` — destination has no previously associated SIM in the supplied history;
- `IMB` — this SIM is the first/primary previously used SIM for the destination;
- `IMC` — this SIM was previously used for the destination, but is not the first entry;
- `IMD` — a different SIM for a new session when the previously used SIMs are unavailable;
- `IME` — a different SIM allowed for the old session, including the risky overlap/steal path.

The short table labels may be IMN/IMB/etc., but tooltips must explain the relationship. `IMN`
must not be labelled simply “none”. `IMA` remains historical/unresolved because the active
selection path audited here does not assign type `A`; it must not be presented as a confirmed
runtime state until an active producer is cited.

### Recognition result

- `0` — no recognition result;
- `10` — silence;
- `20` — answering-machine/recorded response;
- `30` — busy signal;
- `50–59` — detected voice/speech family;
- `100` — successful recognition/result;
- `110–119` and `120–129` must follow the actual recognition dictionaries, not the current broad
  labels. The legacy dictionary shows operator-specific subcodes and even conflicting comments,
  so the tooltip must show the exact subcode and use only a verified family name.
- `90`, `91`, `92` require conservative technical labels until their producer definitions are
  found; “error 91” is not an acceptable final human explanation.

Unresolved recognition codes remain visible in the audit/reference page with evidence and
confidence, but must not acquire invented meanings.

### Special modes and policy markers

- `PRE` and `POS` are independent pre-/post-processing flags. The duplicate `PRE` condition in
  legacy `html_spec()` is a rendering typo, not intended semantics.
- Runtime `spec` must include active values/aliases `NO`, `MAY/20`, `NAV/30`, `SOU/50`, `SOU2/51`,
  `MAG/200`, `FOR`, `WAI`, `SPE`, `CAROUSEL`, `INTER`, `LOC`, `LO2` where their active producer is
  present.
- `INTER` means an interconnected forwarded call and uses the connection asset.
- `MAY` must be named as the callback-request/beacon route rather than a bare code.
- `MAG`, `NAV`, `LOC`, `LO2`, and `SPE` require a code-backed operator description in the reference
  registry; filename guesses such as “shop” or “navigation” alone are insufficient.
- `MON`, `NOTVIP`, `may.png`/`mon.png` counters and similar plan/header icons must be categorised as
  capabilities/policy/action unless an active runtime `spec` producer is proven.

### Direction/zone icons

- A DEF zone/`naprstr` identifier, a two-character billing direction and its route context are
  separate fields and must not be collapsed into one global map.
- Legacy uses `SR` for both MTS Russia and Rostelecom Saint Petersburg mobile routes; its PHP
  renderer ultimately overwrites the former with the latter. Current prototype label `SR — MTS
  Russia` therefore cannot be treated as globally correct.
- Invented `RM`/`RG` codes for Rostelecom must not be presented as legacy billing codes; active
  dialplan uses `SR`/`PR` in relevant routes.
- Prefer a zone/`naprstr` semantic ID when available. If only an ambiguous two-character code is
  known, show the code and an explicit ambiguous/route-context-required tooltip rather than a
  confidently wrong operator.
- The Icons reference must show zone ID, billing code(s), route context and collisions separately.

## Icons Page Requirements

1. Replace the fixed-width flat contact sheet with a responsive, searchable reference registry.
2. Default groups are operational axes: Device/SIM/Network, Live call, Call result, End party,
   Group/schedule, Direction/zone, QoS classification, Destination–SIM affinity, Recognition, Special mode,
   Policy/capability, Actions/navigation, Hardware, and Historical/unresolved.
3. Each card/row shows icon, operator name, raw code/condition and kind. Expanded detail shows
   source/provenance, contexts and asset name.
4. Provide filters for kind, semantic axis, usage context and confidence, plus search by label,
   raw code and filename.
5. Ambiguous, composite, deprecated and unresolved items have visible badges; uncertainty is not
   hidden in tooltip-only text.
6. The layout must work at narrow widths without truncating the only explanation. Long content
   wraps or opens inline detail.
7. The page uses the same renderer and registry lookup as operational tables, so displayed asset,
   label and tooltip cannot drift.
8. The page explicitly distinguishes native GostSimBox 16×16 status glyphs from generic Fugue
   UI icons. Fugue uses exact 16×16 at normal density and matching 32×32 at high density while
   retaining a 16 logical-pixel footprint.

## Asset Policy

- Preserve the GostSimBox icon for a confirmed legacy status axis when the asset is legible and
  semantically established.
- Use Fugue for generic actions/navigation or a genuinely missing generic glyph, following the
  exact 16×16/32×32 density pair contract.
- Do not replace a custom protocol status with an approximate Fugue picture solely for visual
  consistency.
- Do not use emoji, Lucide or platform-dependent fallbacks.
- If no exact Fugue glyph exists, record the requested concept in the Fugue wishlist; keep an
  explicit unresolved/unknown state meanwhile.
- All status assets included by the registry must be verified to exist and be 16×16 at 1×.

## Localisation

- Operator labels and tooltips follow the active UI language (English default, Thai, Russian,
  Hindi, Chinese as established for the prototype).
- Raw protocol codes, filenames and source expressions are never translated.
- A missing translation falls back to English and is visibly testable; it must not silently fall
  back to a stale Russian hard-coded string.

## Acceptance Criteria

### Must Have

- [ ] One typed registry drives every table status icon and the Icons page.
- [ ] Every table icon has a context-correct operator label, raw code/condition and accessible
      tooltip.
- [ ] All corrections listed in this document are represented, including pause 2/12/22, `SIMST=3`,
      composite PIN/network states, QoS `IMO/SYS/NE*`, IM meanings and call live/result separation.
- [ ] Unknown values and missing assets remain visible with their raw value.
- [ ] Direction collisions are surfaced; `SR`, `RM` and `RG` are not misrepresented.
- [ ] Icons page separates status/classification/policy/action/hardware/history and supports search
      and filters.
- [ ] GostSimBox and Fugue density/asset policies are respected.
- [ ] Automated registry validation checks unique semantic IDs, existing assets, 16×16 1× source
      dimensions, required text/provenance fields and known raw/composite mappings.
- [ ] Representative widget tests prove that tables and Icons resolve the same semantic entry and
      tooltip.

### Should Have

- [ ] Inline expanded detail on the Icons page exposes provenance without making dense table
      tooltips verbose.
- [ ] Confidence and historical/deprecated badges help distinguish facts from unresolved legacy
      artifacts.
- [ ] The reference can filter to “used in current tables” versus the full preserved asset catalog.

### Won't Have in This Flow

- Changing modem protocol, `chan_svistok` selection logic or legacy dialplan behaviour.
- Inventing meanings for unresolved numeric recognition subcodes or undocumented abbreviations.
- Editing plans, command sets or zone routing logic.
- Redrawing the full custom GostSimBox status icon family.
- Treating the Icons page as an asset editor.

## Open Questions for Owner Review

1. Recommended: keep `MAY` expanded as “callback request (beacon)” and keep `MON` out of runtime
   Special modes until an active producer is proven. Confirm the preferred short Russian names.
2. Should the default Icons view show only entries used by the current prototype, with a separate
   “Historical/all assets” filter (recommended), or open on the full legacy catalog?

## Evidence References

- `libsCpp/asterisk-chan-svistok/src/select.c`
- `libsCpp/asterisk-chan-svistok/src/chan_dongle.c`
- `libsCpp/asterisk-chan-svistok/src/svistok/at_response.c`
- `legacy/simbox-desktop-v2014/www/simbox/modules/html.php`
- `legacy/simbox-desktop-v2014/www/simbox/sim.php`
- `legacy/simbox-desktop-v2014/system/svistok/callendout.sh`
- `legacy/simbox-desktop-v2014/system/svistok/callendin.sh`
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_dial.conf`
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_incoming_full.conf`
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_forwarding.conf`
- `legacy/simbox-desktop-v2014/modules/recog_types_sim.php`
- `design/simbox-web-design-prototype-v2026/lib/data/icon_map.dart`
- `design/simbox-web-design-prototype-v2026/lib/data/icons_catalog.dart`
- `design/simbox-web-design-prototype-v2026/lib/pages/icons_page.dart`

---

## Approval

- [ ] Reviewed by: Anton Dodonov
- [ ] Approved on:
- [ ] Notes:

## Legacy Addition 1.1 — MAY, MON and MSM semantic split (2026-09-02)

This addition supersedes Open Question 1 above. A full source trace proves that the three raw
labels do not form one homogeneous status family and that `MAY` itself names two different legacy
mechanisms.

### Four distinct concepts

| Stable semantic ID | Raw legacy value | Proven source meaning | Required Russian label | Required English label |
|---|---|---|---|---|
| `call.special.shortBeacon` | call `spec=MAY` / numeric `spec=20` | asynchronous short outgoing call through the `MAY` dialplan route | Короткий звонок-маяк | Short-call beacon |
| `command.operatorCallbackRequest` | `send_may` / `may_*` | operator-specific USSD request sent to a destination number | Операторский запрос перезвонить | Operator callback request |
| `command.balanceTopUpRequest` | `send_mon` / `mon_*` | request asking another person to top up this SIM's balance | Просьба пополнить счёт | Balance top-up request |
| `command.callbackSmsFallback` | `MSM` / `msm_*` | ordinary outbound SMS with a randomized callback-request text, used only as a MAY fallback | SMS с просьбой перезвонить | Callback-request SMS |

`MSM` must never be expanded or translated as Multiple-SIM. It is unrelated to the separately
defined Destination–SIM affinity / IM relationship. The exact expansion of the historical
abbreviation is not recoverable from source, so UI copy describes the proven behaviour and keeps
`MSM` only as a raw technical code.

### `spec=MAY`: short-call beacon route

- `extensions_dial.conf` parses the `#MAY` suffix and assigns `spec=MAY`.
- `extensions_dial_zones.conf` labels the route `;mayak` and calls `makecall-may`.
- `extensions_may.conf` queues a call through `L1D=HZ298`; `makecall5.sh` gives the Asterisk spool
  job `WaitTime: 7` and a post-answer `wait5` context.
- `WaitTime: 7` is the call-file answer timeout, not a seven-second USSD transition or `W` delay.
  The same spool file requests extension `100`, but `wait5` defines only extension `s`; the audited
  dialplan therefore contains no matching post-answer continuation for `100`.
- The spawned `makecall4` path resets `spec` to `LOC`, so the original request and spawned short
  call may not retain the same recorded special mode. The UI must not merge their history rows or
  claim end-to-end MAY propagation.
- `chan_svistok/select.c` recognizes `MAY` as special code `20`, but the audited selector contains
  no additional MAY-specific policy beyond preserving the special value; the route descriptor and
  group `298` perform the practical selection.

Tooltip: **Короткий исходящий звонок-маяк, созданный маршрутом `MAY`. Технический код:
`spec=MAY` (`20`).** It must not describe an SMS or USSD command.

### Automatic MAY command path

After an outgoing call, `callendout.sh` invokes the MAY automation only when billed seconds are
zero and total duration is greater than 10 seconds. The stale diagnostic text says `> 30`, but the
executable condition is `> 10`. It waits a randomized 3–8 seconds and `try_may.sh` waits another
randomized 4–14 seconds, producing a combined post-call delay of 7–22 seconds.

`try_may.sh` proceeds only when `<IMSI>.need_sms == 1`. That flag is set when `stat_satt` exceeds
`satt_soft`; `stat_satt` is explicitly documented in `chan_dongle.h` as the number of consecutive
outgoing calls without SMS. It increments on answered outgoing calls and is reset by an SMS/USSD
send helper. Consequently this is an automated traffic-mix/SMS-generation request, not a generic
action after every failed call.

`send_maymon.php` resolves the SIM's Plan and command set, then either executes that set's
`send_may.sh` or substitutes MSM. Proven active MAY commands are:

| Command set | Active request |
|---|---|
| `beeline_spb` | USSD `*144*<number>#` |
| `megafon_spb` | USSD `*144*<number>#` |
| `life` | USSD `*120*2*<number>#` |
| `velcom` | USSD `*131*<number>#` |
| `tele2_spb` | intended `*118*<number>#`, but the actual send is commented out |

The remaining seeded sets have no active `send_may.sh`. Availability must therefore be derived
per command set and shown as active, inactive/no-op or unavailable; the mere presence of a MAY
limit does not prove an executable command.

### MON is implemented as a command but automatic use is disabled

`callendin.sh` calls `try_mon.sh` after an incoming call, but `try_mon.sh` prints
`DISABLED IN SOFT !!!`; its intended `qos == SLOW`, delayed `send_maymon.php ... mon` branch is
fully commented. `extensions_incoming_full.conf` assigns `SLOW` when the previous matching
connection is 30 minutes old or older. No other active repository caller was found. The only
active MON scripts are
`beeline_spb` and `megafon_spb`, both using `*143*<number>#`; Life, Velcom and Tele2 scripts are
commented/no-op and also contain copied configuration mistakes.

The repository proves that MON is an operator-specific USSD request to a number and contains no
callback bridge, charging, billing or answer-handling path that would justify the label
“paid callback”. The product owner confirms the global MON business meaning as a request asking
another person to transfer money to the requesting SIM's balance when funds are insufficient.
For Beeline this is the free service **«Пополни мой счёт»** using `*143*<number>#`. The visible
MON label for every supported command set must therefore be
**Просьба пополнить счёт** / **Balance top-up request**, with tooltip:
**Отправляет указанному абоненту просьбу пополнить баланс этой SIM. MON · команда выбранного
набора.** Operator-specific detail may additionally show the service name, charging note and raw
USSD; for Beeline: **Бесплатная услуга «Пополни мой счёт» · `*143*номер#`.** Automatic MON
triggering remains disabled in legacy for every set.

### MSM is a constrained MAY fallback

`send_maymon.php` accepts only `may` or `mon` as input. For MAY, it changes the mode internally to
`msm` before checking the MAY limit when both `msm_sended < msm_limit` and
`smsout_sended < smsout_soft`. It selects a random phrase such as “Позвони” or “Перезвони” from
`sms_text_callback`, sends a regular SMS with `spec=LO2`, and increments both `msm_sended` and
`smsout_sended`. It does not consume `may_sended`.

Consequences:

- MSM is not a directly invocable command and not a third operator service.
- MSM may be used even when the MAY limit is exhausted because fallback selection precedes the
  MAY-limit check.
- `msm_limit` alone is insufficient: `smsout_soft` must also allow another SMS. A default
  `smsout_soft=0` disables the fallback.
- The Plan owns configured limits; the SIM row owns the current runtime counters.

### Counters, reset and delivery truthfulness

The executor increments `may_sended`, `mon_sended` or `msm_sended` before running the chosen
command and never checks its exit status or an operator response. It also clears `need_sms`
regardless of success. Therefore all three values mean **attempts counted against a legacy quota**,
not confirmed requests or delivered messages.

The reset period must not be globally labelled “daily”: Beeline and Tele2 reset all three values,
MegaFon SPb leaves the MSM reset commented, and other command sets have no equivalent reset in
their package. Tooltips must say “within the configured reset period” and expose the actual reset
policy when known.

Before any quota check or command execution, the executor writes a shared destination lock
`sim/state/<number>.maymon=1`. No reset/removal was found in the repository. It is shared by MAY
and MON and is not scoped to IMSI. A failed, quota-blocked or no-op attempt can therefore suppress
both future request types for that number. This is a legacy defect/compatibility warning, not a
successful-delivery state.

### UI and icon requirements

1. The Icons page must show the four concepts as separate entries; it must not group them under one
   generic MAY/MON/MSM status.
2. `spec=MAY` may appear in call-special-mode filters. MAY/MON/MSM counters belong to Plan/SIM
   quota presentation and command availability belongs to Command Sets.
3. Counter cells use `attempts / limit`, with a tooltip that explicitly says delivery is not
   confirmed by legacy.
4. `MSM` must be added back to the SIM and Plan parity manifests; the current prototype's omission
   is a data-loss defect.
5. The current catalog label `msm | мультисим` is invalid and must be replaced with the callback
   SMS semantic entry.
6. MAY and MON command icons must communicate operator request/USSD; MSM must communicate an SMS
   message; the short-call MAY icon must communicate a phone call. Reusing one glyph for all four
   would be semantically false.
7. Raw abbreviations remain searchable aliases, while localized visible labels describe proven
   behaviour.
8. MON always resolves to “Просьба пополнить счёт”. Command sets may override only the operator
   service name, charging note and USSD operation, not the core MON meaning.

### Owner clarification 1.2 — MON business meaning (2026-09-02)

The product owner explicitly confirms that MON means a request to top up the SIM's balance. Beeline
`*143#` belongs to the free “Пополни мой счёт” service. This clarification is authoritative for
the global MON label; operator-specific metadata remains attached to each command implementation.

### Owner clarification 1.3 — SOU internal SIM-to-SIM call (2026-09-02)

The product owner confirms that `SOU` does not mean a SIM calling itself. It means an internal
call where one managed SIM calls another managed SIM:

- `SOU+O` — originating leg: this SIM calls another SIM in the system;
- `SOU+I` — receiving leg: this SIM receives the call from another SIM in the system;
- bare `SOU` — internal SIM-to-SIM call when the leg/direction is not shown separately;
- `SOU2/51` — a second legacy variant of the same internal SIM-to-SIM class; its additional
  distinction remains technical until the producer path is differentiated.

Required Russian label: **Внутренний звонок между SIM**. Required English label:
**Internal SIM-to-SIM call**. The wording “звонок самому себе”, “self-call” and «свой-себе» is
prohibited in UI labels and tooltips.

### Additional evidence

- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_may.conf`
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_wait.conf`
- `legacy/simbox-desktop-v2014/system/makecall5.sh`
- `legacy/simbox-desktop-v2014/ai/sms/send_maymon.php`
- `legacy/simbox-desktop-v2014/ai/sms/try_may.sh`
- `legacy/simbox-desktop-v2014/ai/sms/try_mon.sh`
- `legacy/simbox-desktop-v2014/ai/sms/find_need_sms.sh`
- `legacy/simbox-desktop-v2014/www/simbox/modules/sms_texts.php`
- `legacy/simbox-desktop-v2014/nabor/*/commands/send_may.sh`
- `legacy/simbox-desktop-v2014/nabor/*/commands/send_mon.sh`
- `libsCpp/asterisk-chan-svistok/src/chan_dongle.h`
- `libsCpp/asterisk-chan-svistok/src/at_response.c`
- `libsCpp/asterisk-chan-svistok/src/helpers.c`

## Legacy Addition 1.4 — BUSY icon and dual-axis reuse (2026-09-02)

This addition corrects the earlier review statement that `DIALSTATUS=BUSY` needs a new Fugue icon.
Active legacy rendering already defines the BUSY glyph explicitly:

```php
if($ds=="BUSY") $ds_html="<img src=imgs/recog_types/30.png>";
```

`www/simbox/modules/html.php::html_dialstatus()` is used by the active call-log table in
`www/simbox/log/calls.php`. The same helper file also maps recognition result `30` to the same
`recog_types/30.png` asset. This is intentional image reuse across two semantic axes, not proof
that the values are interchangeable.

Required registry entries:

| Semantic ID | Raw value | Label | Tooltip | Glyph |
|---|---|---|---|---|
| `call.result.busy` | `DIALSTATUS=BUSY` | Абонент занят | Удалённая сторона занята · `DIALSTATUS=BUSY` · normally `CC_CAUSE=17` | Fugue `cup-empty.png` |
| `recognition.busyTone` | `REC=30` | Распознан сигнал «занято» | Аудиораспознавание обнаружило сигнал «занято» · `REC=30` | Fugue `cup-empty.png` |

The call result is derived in both outgoing and incoming end handlers when `CC_CAUSE=17`; those
handlers also set `END_PARTY=2`. The modem driver independently translates an actual modem `BUSY`
response into `AST_CONTROL_BUSY`. The final tooltip may add `END_STATUS`, `CC_CAUSE` and
`END_PARTY` from the row, but it must not present `REC=30` unless recognition actually produced it.

There is a third unrelated busy concept: `sim/state/<IMSI>.busy=1` means the SIM/modem resource is
currently occupied by a call. It is a live resource-occupancy flag and must not use the completed
call-result tooltip “Абонент занят”.

### Asset provenance and density

- Legacy asset: `www/simbox/imgs/recog_types/30.png`, 16×16.
- Current prototype asset: `assets/imgs/recog_types/30.png`, 16×16. When composited on a light
  background it is pixel-identical to the visible legacy rendering; differing file hashes come
  from RGB values in fully transparent pixels.
- Fugue origin: `cup-empty.png`. The legacy rendition is a grayscale modification of the upstream
  glyph, with 27 source pixels differing from canonical Fugue.
- Canonical Fugue provides verified `cup-empty.png` files at both 16×16 and 32×32.

Because the product requires Fugue density pairs, implementation should vendor canonical
`cup-empty.png` under its upstream filename in the 1× and 2× folders and render it in the same
16-logical-pixel box. It must not retain the current single-resolution asset or introduce a new
approximate BUSY glyph. If exact grayscale legacy coloration is later required, that becomes an
explicit custom redraw decision rather than being mislabeled as an unmodified Fugue pair.

Additional acceptance criteria:

9. `DIALSTATUS=BUSY` resolves to `cup-empty.png`, not to an unresolved/missing-icon slot.
10. `DIALSTATUS=BUSY`, `REC=30` and live resource `busy=1` have separate registry IDs and tooltips.
11. The Icons page visibly lists the shared glyph twice under Call result and Recognition, while
    provenance detail explains intentional reuse.
12. Both 16×16 and 32×32 canonical Fugue files exist and are selected by display density without
    changing the 16px logical footprint.

Evidence:

- `legacy/simbox-desktop-v2014/www/simbox/modules/html.php:137-165`
- `legacy/simbox-desktop-v2014/www/simbox/log/calls.php:246-259`
- `legacy/simbox-desktop-v2014/system/svistok/callendout.sh:169-172`
- `legacy/simbox-desktop-v2014/system/svistok/callendin.sh:74-77`
- `libsCpp/asterisk-chan-svistok/src/at_response.c:2553-2556`
- `libsCpp/asterisk-chan-svistok/src/stat.c:20-35,120-153`
- `nativemind-adminka/assets/adminka/adminka-to-fugue-map.json`
