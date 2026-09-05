# Requirements: Icon statuses and tooltips

> Version: 1.0  
> Status: APPROVED
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
- [ ] The reference **defaults to the full preserved asset catalog** (owner decision, 2026-09-02
      — see Open Question 2), with a filter to narrow down to "used in current tables".

### Won't Have in This Flow

- Changing modem protocol, `chan_svistok` selection logic or legacy dialplan behaviour.
- Inventing meanings for unresolved numeric recognition subcodes or undocumented abbreviations.
- Editing plans, command sets or zone routing logic.
- Redrawing the full custom GostSimBox status icon family.
- Treating the Icons page as an asset editor.

## Open Questions for Owner Review

1. ~~Recommended: keep `MAY` expanded as "callback request (beacon)"...~~ — **Resolved** by
   Legacy Addition 1.1 below (four distinct semantic IDs with required Russian/English labels).
2. ~~Should the default Icons view show only entries used by the current prototype...~~ —
   **Resolved 2026-09-02 (owner decision):** the Icons page opens on the **full legacy catalog**
   by default (all preserved assets, including historical/unresolved entries), with "used in
   current tables" available as a filter rather than as the default view. This overrides this
   document's own earlier recommendation (used-only default) — the "Should Have" bullet under
   Icons Page Requirements below is amended accordingly.

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

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-02
- [x] Notes: Approved as amended through Legacy Addition 1.5, with Open Question 2 resolved
  (Icons page defaults to the full legacy catalog). Visual phase scoped down to just the Icons
  page's new layout — table corrections are label/tooltip/data-model swaps in already-existing
  cells and need no new mockup.

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

## Legacy Addition 1.5 — the per-SIM `.qos` file is incoming-recency-only, never the
outgoing source classification (2026-09-02)

This addition resolves the question of whether "Давность предыдущего соединения"
(`VERY`/`FAST`/`SLOW`/`NEVER`, plus `SPAM`) is scoped to one specific bound SIM. **It is —
more precisely and more narrowly than the existing taxonomy entry implies.**

### The write path is a closed, single-producer file

`grep`-ing every `.qos` write across the active legacy tree (dialplan `Set(FILE(...))`, shell,
PHP) finds exactly one producer: `[macro-incoming-full]` in
`legacy/simbox-desktop-v2014/asterisk/extensions/extensions_incoming_full.conf` (lines 44-84).
It is the **only** code path anywhere in the repository that ever writes
`/var/svistok/sim/state/<IMSI>.qos`, and it can only ever write one of six literal values:
`SPAM`, `NEVER`, `VERY`, `FAST`, `SLOW`, or `SOU` (line 84 — an incoming call recognized as
internal SIM-to-SIM also stamps `qos=SOU` into this same file). **`VIP`, `GOO`, `NOR`, `BAD`,
`NEW`, `NOS`, `ROB`, `BLO`, `NE0`, `NEC`, `NEM` are never written to this file by any active
code** — those values exist only as transient Asterisk channel variables inside the *outgoing*
call macros (`[macro-checknumber]` in `extensions_dial.conf`, `select.c`'s in-memory SIM
selection), used purely to help pick which SIM should place an outgoing call, and are not
persisted anywhere the UI reads.

### The classification is scoped to one specific SIM, by construction

`[macro-incoming-full]` runs once a call has already landed on one specific SIM's own dongle
channel. It queries an external endpoint with **both** identifiers of that one SIM:

```
exten => s,n,Set(url=...conn_getstat.php?numberb=${numberb}&imsi=${DONGLEIMSI})
```

`numberb` here is this SIM's *own* phone number (the number the external caller dialed to reach
it) and `${DONGLEIMSI}` is this SIM's IMSI — not the caller's number and not some other SIM. The
returned `minutesago` therefore answers "how long ago was there a previous connection event
*for this SIM*," not "for this destination, regardless of which SIM answered." The result is
written back keyed by `${DONGLEIMSI}` — i.e. per-SIM, unambiguously.

### The Sims-table cell this actually feeds is live-call-only, and can show stale data

`legacy/simbox-desktop-v2014/www/simbox/sim.php:1449-1474` renders one cell (`html_io($io)` +
`html_qos($qos,$io)`) **only while that SIM currently has an active call** (`.state_in==1` or
`.state_out==1`), reading `.qos` from the same file for *both* directions. Since nothing in the
outgoing path ever writes this file, **the value shown during an active outgoing call is
leftover data from that SIM's most recent incoming-call classification** — it is never a live
signal about the number currently being dialled. `legacy/simbox-desktop-v2014/system/svistok/
callendin.sh:27` independently re-reads this same file right after each incoming call ends and
feeds it into post-call automation — this is the exact `qos` value gating `try_mon.sh`'s
disabled `qos == SLOW` branch already documented in Legacy Addition 1.1's MON research, tying
the two investigations together.

`design/simbox-web-design-prototype-v2026/lib/pages/sims_page.dart:80-88` (the `io` column,
titled "направление и качество") is a direct, faithful port of this exact `sim.php` cell —
`Ico.io(s.io)` + `Ico.qos(s.qos, s.io)` together. Its current mock data
(`lib/data/mock.dart`'s `Sim.qos` values: `GOO`, `NOR`, `BLO`, `VIP`, `BAD`, `NEW`, `FAST`)
therefore has 6 of 7 sample values that **cannot legitimately appear in this cell** — only
`FAST` (and `VERY`/`SLOW`/`NEVER`/`SPAM`/`SOU`) are values this file can ever hold.

### Correction to the registry

The existing taxonomy note ("`VERY`, `FAST`, `SLOW`, `NEVER` and `SPAM` belong to the legacy
incoming-call recency/routing axis... must not be... mixed with the `chan_svistok` source
classifications without a subgroup") was directionally correct but understated the boundary: it
is not just a different *subgroup* needing separate labeling — it is a **structurally distinct,
single-producer, per-SIM persistent field** that mechanically cannot ever hold a
`chan_svistok`-sourced value. The two families:

| Axis | Semantic ID prefix | Producer | Persistence | Possible values |
|---|---|---|---|---|
| Incoming-call recency (per-SIM) | `sim.incomingQos.*` | `[macro-incoming-full]` only | `sim/state/<IMSI>.qos` — the exact field `Sim.qos`/`Ico.qos()`/the Sims table's "io+качество" cell must model | `SPAM`, `NEVER`, `VERY`, `FAST`, `SLOW`, `SOU` |
| Outgoing source classification (per call attempt) | `call.sourceClass.*` | `[macro-checknumber]` / `select.c`, per outgoing call | Not persisted per-SIM; call-log rows only (`showlog`/`calls.php`), if shown anywhere | `VIP`, `GOO`, `NOR`, `BAD`, `NEW`, `NOS`, `ROB`, `BLO`, `NE0`, `NEC`, `NEM` |

Additional acceptance criteria:

13. `Ico.qos()`/`Sim.qos` (the Sims table's "io+качество" cell) must only ever accept
    `SPAM`/`NEVER`/`VERY`/`FAST`/`SLOW`/`SOU` — the registry/type must make the other 11 values
    structurally unrepresentable in this cell, not merely undocumented.
14. Mock data seeding this cell must be corrected to only use the six legitimate values.
15. If `VIP`/`GOO`/`NOR`/`BAD`/`NEW`/`NOS`/`ROB`/`BLO`/`NE0`/`NEC`/`NEM` are surfaced anywhere in
    the UI at all (e.g. a future call-log page), they must live in a visibly separate
    per-call-attempt context, never the per-SIM table's live-call cell.
16. The Icons page must group these two families under visibly distinct headings (e.g. "Давность
    предыдущего соединения (по SIM)" vs "Классификация исходящего вызова (по попытке)"), not one
    "QoS" bucket, and each entry's provenance detail should cite whether it is ever actually
    persisted or is call-attempt-transient only.

Evidence:

- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_incoming_full.conf:20-84`
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_dial.conf:229-262` (transient
  outgoing `qos`, never written to a file)
- `legacy/simbox-desktop-v2014/system/svistok/callendin.sh:27`
- `legacy/simbox-desktop-v2014/www/simbox/sim.php:1449-1474`
- `design/simbox-web-design-prototype-v2026/lib/pages/sims_page.dart:80-88`
- `design/simbox-web-design-prototype-v2026/lib/data/icon_map.dart` (`_qosMap`, `Ico.qos()`)
- `design/simbox-web-design-prototype-v2026/lib/data/mock.dart` (`Sim.qos` seed values)

## Legacy Addition 1.6 — NE0/NEC/NEM: one live, two dead (2026-09-02)

A prior session (a different agent) found the literal comment strings defining these suffixes
in `[macro-checknumber]`, `extensions_dial.conf`, but was interrupted before verifying which
branches are actually reachable. Verified here:

```
exten => s-OK,n,GotoIf($[ "${qos}${cap}" = "NEWOK" ]?s-OK-NEC,1)
;exten => s-OK,n,GotoIf($[ "${qos}${note}" = "NEWMAGOK" ]?s-OK-NEM,1)
;exten => s-OK,n,GotoIf($[ "${qos}${note}" = "NEWNO INFO AT ALL" ]?s-OK-NE0,1)
```

Only the `NEC` dispatch line is active; the `NEM` and `NE0` dispatch lines are commented out.
Per the Source Precedence rule (commented-out UI/logic is historical evidence, not active
functionality), this means:

- **`NEC` is live**: reached when the base classification is `NEW` (number absent from
  lists/history) **and** `cap` (the captcha-result field, `CUT(res,/,8)`) equals `OK` — i.e. a
  new/unknown number that has just passed a CAPTCHA challenge. This is a materially different
  and more specific meaning than the previous "no-response variant" framing — it is not about
  the server failing to respond at all, it is a **NEW-number sub-case gated by captcha success**.
- **`NE0` and `NEM` are dead code today**: their dispatch conditions (`note == "NEWNO INFO AT
  ALL"` / `note == "NEWMAGOK"`) can never be reached because the `GotoIf` that would jump to
  them is commented out. They remain in the registry as **Historical/unresolved**, not as live
  classifications, until an active producer is found elsewhere.
- Separately worth flagging for Specifications: the `res` string that `qos`/`cap`/`note` are all
  `CUT()` from is itself set via `Set(res=${CALLERID(name)})` in the active code — the
  HTTP-fetch alternative (`start_v3.php?numberb=...`) immediately above it is *also* commented
  out. This means the real classification computation happens upstream of this macro (something
  populates the calling channel's Caller ID name field with an encoded `qos/…/cap/…/note/…`
  string before `Dial()` reaches here) — out of scope to trace further for this flow, but
  worth recording so a future flow doesn't waste time looking for a live `start_v3.php` call.

Evidence:

- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_dial.conf:237-262`

## Legacy Addition 1.7 — the outgoing `qos` chain is real and consequential; it ends in the
call log, not the per-SIM state file (2026-09-02)

The user correctly pushed back that outgoing `qos` (`GOO`/`NOR`/etc.) is genuinely "produced"
in `extensions_dial.conf`/`extensions_dial_zones.conf` and asked for a full trace of the
`simserver:8122` interaction. Legacy Addition 1.5's conclusion (the per-SIM **state** file
`sim/state/<IMSI>.qos` is incoming-only) still holds — nothing new contradicts it — but it
undersold how real and active the outgoing side is. Full producer→consumer→destination chain:

**Producer**: `[macro-makecall]` (`extensions_dial_zones.conf:1-21`) initializes `qos=NOS` as
the default, then calls `Macro(checknumber,${numberb})`. `[macro-checknumber]`
(`extensions_dial.conf`) sets `qos=${CUT(res,/,2)}` from `res`, which in the *active* code is
`${CALLERID(name)}` — the `start_v3.php` HTTP fetch that would have populated `res` from
`simserver:8122` directly is commented out, so today the classification arrives pre-encoded in
the channel's Caller-ID-name field by whatever sets it before `Dial()` runs (out of scope to
trace further here — see Additional Notes below).

**Consumption for SIM selection/billing**: `libsCpp/asterisk-chan-svistok/src/select.c:258`
reads this same channel variable directly — `ast_channel_get_var(requestor,"qos",cr->qos_str)`
— confirming the dialplan and the C driver share one variable. `select.c:125-139` then maps the
string to a small integer AND a `billing_pay` flag:

| String | Numeric | `billing_pay` |
|---|---|---|
| NOS | 0 | 1 |
| GOO | 1 | 1 |
| BAD | 2 | 1 |
| NOR | 3 | 1 |
| NEW | 4 | 1 |
| NE0 | 40 | 1 |
| NEC | 41 | 1 |
| NEM | 42 | 1 |
| SOU | 5 | **0** |
| IMO | 6 | 1 |
| SYS | 0 | **0** |
| VIP | 7 | 1 |
| ROB | 8 | 1 |
| BLO | 9 | 1 |

Note `SYS` and `NOS` collide at numeric `0` — distinguishable only by `billing_pay` (`SYS` is
free, `NOS` is billed). This numeric value then gates the `uu_*` SIM-eligibility booleans found
in Legacy Addition's earlier QoS section (`select.c:505-524`) — i.e. `qos` genuinely determines
which candidate SIMs are allowed to take the call and whether the call is billed. Not vestigial.

**Where it ends up, confirmed**: `select.c:1048` copies the string onto the winning SIM's live
in-memory struct (`strcpy(pvt->qos,cr->qos_str)`), and `at_response.c:1110` passes `pvt->qos`
as one argument of the `callendout(...)` call fired when that outgoing call ends. This reaches
`legacy/simbox-desktop-v2014/system/svistok/callendout.sh` as positional arg `$21` (`qos=$21`,
line 36), which appends it into four **call-log files**:
`/var/svistok/sim/log/<IMSI>.calls`, `<IMSI>.calls2`, `calls.full`, and `calls.<naprstr>` (lines
197-201) — the same log family `legacy/simbox-desktop-v2014/www/simbox/log/calls.php` reads.
**This is the definitive answer to Legacy Addition 1.5's "if shown anywhere" caveat**: yes,
outgoing `qos` is shown in the UI — in the **call-log page**, one row per call attempt, never
in the Sims table's live-call cell. The two-axis split from 1.5 stands; the destination for the
second axis is now confirmed rather than speculative.

**NE0/NEM refined**: `select.c` actively checks `cr->qos==40` (NE0) and `cr->qos==42` (NEM) in
its eligibility logic — the *consumer* side is fully wired, not dead. But since the only active
*producer* (`[macro-checknumber]`) can never emit the literal strings `"NE0"`/`"NEM"` (Legacy
Addition 1.6 — their dispatch `GotoIf`s are commented out), these branches are unreachable in
practice today: **orphaned at the producer end, still wired at the consumer end** — a more
precise characterization than a flat "dead code."

**`simserver:8122` endpoint map** (every reference in the active, non-`/old/` tree):

| Endpoint | Caller | Direction | Status |
|---|---|---|---|
| `/in.php` | `extensions_incoming.conf` (3 call sites) | incoming, call start | Active |
| `/conn/conn_getstat.php` | `extensions_incoming_full.conf` | incoming, recency classification | Active (Legacy Addition 1.5) |
| `/svistok/smsin.php` | `extensions_incoming_smsussd.conf` | incoming SMS | Active |
| `/captcha/captcha_start.php` | `extensions_captcha.conf` | captcha flow start | Active |
| `/captcha/captcha_end.php` (×2) | `extensions_captcha.conf` | captcha flow end | One active, one commented |
| `/captcha/captcha_check.php` | `extensions_captcha.conf` | captcha verify | **Commented out** |
| `/start_v3.php` | `extensions_dial.conf` (`[macro-checknumber]`) | outgoing, pre-call classification | **Commented out** — see above |
| `/end.php` | `extensions_dial.conf` (`[macro-savenumber]`) | outgoing, fire-and-forget end report | Active, response unused |
| `/svistok/callendin.php` | `system/svistok/callendin.sh` | incoming call end, full report | Active |
| `/svistok/callendout.php` | `system/svistok/callendout.sh` | outgoing call end, full report (incl. `qos`) | Active |
| `/svistok/callendout_imb123.sh`'s endpoint | `callendout_imb123.sh` | specialized/test variant | Active but narrow-purpose |
| `/svistok/calltry.php` | `system/svistok/calltry.sh` | pre-attempt notification | **Script itself is unreferenced anywhere in the active tree** — orphaned |
| `/trycall.php` | `system/trycall.sh` | pre-attempt notification (simpler) | **Also unreferenced** — orphaned |
| `/sim/get_new_ki.php` | `system/new_ki.php`, `new_ki_on.php` | SIM KI retrieval | Active |
| `/sms/smsout_status_report.php` | `system/cds.php` | SMS delivery report | Active |
| `/svistok/foundgettoday.php` | `system/found/getfound.sh` | "found numbers today" list | Active |
| `/recog/recog_save.php` | `ai/recog/dorecog.php` | uploads 4 transcribed audio segments, **receives back the numeric `recog_type` code** | Active — see Legacy Addition 1.8 |
| `/stat/upload_group.php` | `ai/recog/parse/all.php` | reports a manual group change after voice-triggered auto-block | Active |

**Additional note for a future flow**: none of these endpoints' server-side implementations
exist in this checkout — `simserver:8122` is an external backend not included in this repo.
Every conclusion above is about what legacy *sends to* or *reads back from* that server, not
about the server's own logic (which is opaque from here).

Evidence:

- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_dial_zones.conf:1-21`
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_dial.conf:229-262`
- `libsCpp/asterisk-chan-svistok/src/select.c:109-139,258,505-524,1048`
- `libsCpp/asterisk-chan-svistok/src/at_response.c:1090-1122`
- `legacy/simbox-desktop-v2014/system/svistok/callendout.sh:1-40,193-201`
- `legacy/simbox-desktop-v2014/system/svistok/calltry.sh`, `system/trycall.sh` (orphaned)
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_incoming.conf`,
  `extensions_incoming_smsussd.conf`, `extensions_captcha.conf`
- `legacy/simbox-desktop-v2014/system/new_ki.php`, `new_ki_on.php`, `cds.php`,
  `system/found/getfound.sh`

## Legacy Addition 1.8 — Recognition codes: two different mechanisms, one genuinely
unresolvable from this checkout (2026-09-02)

Traced the full recognition pipeline in response to the user's guesses for `REC=10/30/90/91/
92/100/110/120`. Finding: **the recognition axis is actually two independent mechanisms that
happen to share one numeric scale and one rendering function**, and the exact server-side
classifier for several codes is not present in this repository.

### Mechanism 1 — DSP/acoustic classification (likely 0/10/20/30/50–59)

`html_recog_type()` (`www/simbox/modules/html.php:157-174`) renders `recog_types/<n>.png` for
`0` (silence, blank/no icon), `10`, `20`, `30`, and the `50-59` range as one bucket. This
10→20→30→50+ sequence (silence → answering-machine → busy-tone → voice) is the textbook shape
of a classic telephony Answering-Machine-Detection/tone classifier, not a phrase-matching
system — reinforced by Legacy Addition 1.4's finding that `30` (busy) shares its asset with the
*protocol-level* `DIALSTATUS=BUSY` (an actual acoustic/signalling busy tone, confirmed via
`AST_CONTROL_BUSY` in `at_response.c`, nothing to do with recognized speech). **This makes `30`
most likely an acoustic busy-tone pattern match, not a spoken phrase such as "абонент
недоступен"** — no code in this repo defines that specific phrase as a `REC` producer; that
guess isn't supported by anything found here. Nothing in this repo names what exact acoustic
pattern maps to `10` either — "тишина" (silence, i.e. no usable audio) is the only textual
evidence (the base taxonomy's own label), which is a different concept from "abonent
unavailable" as a *spoken announcement* — a real "Абонент временно недоступен" announcement is
actual speech and would not be classified as silence.

### Mechanism 2 — ASR phrase-matching for the calling SIM's own carrier announcements (90–129?)

`ai/recog/dorecog.php` records four audio segments per call attempt — `pre-in`/`pre-out` (before
answer) and `ans-in`/`ans-out` (after answer) — transcribes them via an external ASR (Yandex
SpeechKit in the current version; `system/svistok/raspozn.php` shows an older Google
Speech-API-based predecessor doing the same four-segment split), and **uploads the transcripts
to `simserver:8122/recog/recog_save.php`, which sends back the numeric `$recog_type` code**
(`dorecog.php:44`: `list($status,$recog_type)=explode(";",$tmp);`). **The mapping from
transcribed text to a specific numeric code is computed server-side, and that server's code is
not part of this checkout** — this repository cannot fully resolve what distinguishes `90` from
`91` from `92`, or the exact subcode meanings within `110-119`/`120-129`, because the classifier
itself lives outside it.

What *is* independently confirmed from a parallel, separate automation
(`ai/recog/parse/all.php`, triggered by the same `dorecog.php` pipeline): it pattern-matches the
raw transcribed text of `pre-in`/`pre-out`/`ans-in`/`ans-out` against known Russian carrier
announcement phrases and, on a match, automatically runs `dongle setgroupimsi <imsi> 335` or
`336` — i.e. it **auto-transitions the calling SIM's own group** into "auto-block by balance-SMS
condition" (335) or "SIM blocked" (336) (the exact same groups from the Group/schedule section).
This is a previously-undocumented **second path into groups 335/336**, alongside the
SMS-triggered one already in the base requirements — triggered by recognizing the *carrier's own
spoken announcement on this SIM's line*, not anything related to the called party. The matched
phrases are explicitly about **this SIM's own balance/block status**, e.g. "на вашем счете
недостаточно средств" (insufficient funds — **this SIM's balance**, not the called party's),
"ваш номer заблокирован" (this SIM's own number blocked). `modules/recog_types_sim.php`'s
top-of-file comments (`// 110 - деньги`, `// 120 - блокировка`) and its phrase dictionary
(Beeline/MegaFon/Tele2/Velcom/life-specific announcement fragments, keyed 111-127) independently
corroborate this: **110-119 confirmed as "insufficient funds" family, 120-129 confirmed as
"number/SIM blocked" family — both about the calling SIM's own carrier-reported status, not the
destination's.**

### Direct answers to the user's guesses

| Code | User's guess | Verdict |
|---|---|---|
| `91` | Outgoing speech detected | **Unconfirmed** — no local evidence; the 90/91/92 exact split is computed server-side (`recog_save.php`), not in this repo |
| `92` | Speech on incoming audio | **Unconfirmed** — same reason |
| `90` | Also something speech-related | **Unconfirmed** — same reason; could equally be a technical/error subcode (e.g. upload/ASR failure) — a guess, not a finding |
| `100` | Normal dialogue | **Plausible, weakly supported** — taxonomy already calls it "успешный результат распознавания"; consistent but not separately re-derived here |
| `110` | Insufficient funds | **Confirmed** — but it's *this SIM's own* balance/carrier announcement, not the called party's |
| `120` | This SIM is blocked | **Confirmed** — same caveat, and it's this SIM's own number, not the called party's |
| `10` | Called party unavailable/out of coverage | **Not supported** — local evidence only calls this "silence" (no usable audio), a different concept from a spoken unavailability announcement |
| `30` (separate question) | Spoken "абонент недоступен" | **Not supported** — evidence points to an acoustic busy-tone pattern (shares its asset with protocol-level `DIALSTATUS=BUSY`), not a recognized phrase |

Evidence:

- `legacy/simbox-desktop-v2014/www/simbox/modules/html.php:157-174`
- `legacy/simbox-desktop-v2014/ai/recog/dorecog.php`
- `legacy/simbox-desktop-v2014/ai/recog/parse/all.php`
- `legacy/simbox-desktop-v2014/system/svistok/raspozn.php`
- `legacy/simbox-desktop-v2014/modules/recog_types_sim.php`

## Legacy Addition 1.9 — incoming recency is scoped to caller + receiving SIM; `.qos` is shared
with outgoing live classification (2026-09-02)

This addition supersedes the persistence and typing conclusions in Legacy Additions 1.5 and 1.7.
Those additions missed the C producers `select.c:1074` and `select.c:1369` and also misidentified
the incoming variable `numberb`.

### What `minutesago` is scoped to

The active incoming context assigns `numberb=${CALLERID(num)}` and normalizes that value before
calling `[macro-incoming-full]`. Therefore `numberb` is the **external calling number**, not this
SIM's own phone number. The recency request is:

```text
conn_getstat.php?numberb=<external caller>&imsi=<receiving SIM IMSI>
```

The checked-out repository does not contain `conn_getstat.php`, so its SQL/query implementation
cannot be proved locally. The strongest code-backed wording is consequently:

**«Давность предыдущего соединения для пары “звонящий номер ↔ эта принимающая SIM”».**

It is tied to the concrete SIM that received the call through `DONGLEIMSI`; it is not a global age
for the caller across all SIMs, and it is not a generic “last connection of this SIM” independent
of the caller. The endpoint also returns `numberc`, which the dialplan uses as a prior associated
interconnect destination. This supports the pair/history interpretation, but the missing server
implementation prevents a stronger claim about the exact database row selected.

The thresholds are confirmed locally:

- `minutesago=-2` -> `SPAM`;
- `minutesago=-1` -> `NEVER`;
- `<4` -> `VERY`;
- `4..29` -> `FAST`;
- `>=30` -> `SLOW`.

For an internal SIM-to-SIM incoming call, the prior-history query is bypassed and the same state
file receives `SOU`.

If the endpoint does not return `st=OK`, the dialplan takes the generic forwarding branch before
any incoming QoS write. In that failure path the file can retain an older value. A UI backed only
by the legacy file cannot truthfully present that retained value as a freshly calculated recency;
an adapter with request status should show “history unavailable”, while a raw-file-compatible view
must mark the value as potentially stale.

### The `<IMSI>.qos` file has two active producer families

Incoming dialplan branches write symbolic strings to
`/var/svistok/sim/state/<receiving IMSI>.qos`: `SPAM`, `NEVER`, `VERY`, `FAST`, `SLOW`, or `SOU`.

For an outgoing call, `chan_svistok` selects one concrete SIM and immediately calls
`pvt_select_stat()`. That function writes `cr->qos` to the **same** file with
`putfilei("sim/state", pvt->imsi, "qos", cr->qos)`. The persisted outgoing representation is
numeric: `0..9` or `40..42`; the raw string remains separately in `pvt->qos` and later reaches the
call log. The older/direct-IM branch also writes numeric `qos` at `select.c:1369`.

The active SIM table deliberately reads the shared file in both directions:

- while `state_in=1`, it renders incoming recency/SOU for the receiving SIM;
- while `state_out=1`, it renders the outgoing classification written for the selected SIM.

Thus the outgoing cell is not inherently stale incoming data. The direction icon is required to
interpret the adjacent QoS icon. Numeric `0` also loses the `NOS` versus `SYS` distinction in this
live file; the call log retains the original string and `billing_pay` remains separate.

### Corrected UI contract

1. Keep `incomingRecency` and `outgoingSourceClass` as different semantic axes on the Icons page.
2. Model the SIM-table value as a direction-aware union, not an incoming-only enum:
   `IncomingRecencyQos` for `io=I` and `OutgoingLiveQos` for `io=O`, with `SOU` valid on both legs.
3. The incoming tooltip must say **«Предыдущее соединение этого звонящего номера с этой SIM …»**,
   not merely «по SIM» and not «предыдущее соединение SIM».
4. Outgoing live values are valid in the SIM table. Their persisted numeric aliases must resolve
   to the same semantic entries as the raw strings used in call logs.
5. A direction/value mismatch from external data remains visible as an explicit diagnostic state;
   it must not be silently coerced to incoming recency.
6. A failed/unavailable `conn_getstat` response must not be represented as a fresh `VERY/FAST/
   SLOW/NEVER` result when response status is available.

Evidence:

- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_incoming.conf:1-95`
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_incoming_full.conf:1-85`
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_forwarding.conf:1-95`
- `legacy/simbox-desktop-v2014/svistok-aa/select.c:921-949,1017-1075,1320-1369`
- `legacy/simbox-desktop-v2014/www/simbox/sim.php:1445-1477`
- `legacy/simbox-desktop-v2014/www/simbox/modules/html.php:305-346`

## Legacy Addition 1.10 — pre-call `simserver:8122` classification and local IM derivation
(2026-09-02)

The outgoing source class and Multiple-SIM relationship do not have the same producer.

### Architecture transition proved by the dialplan

The archived dialplan calls the server directly before selecting a SIM:

```text
GET http://10.2.0.1:8122/start_v2.php
    ?numberb=<destination>
    &numbera=<calling account/uid>
    &gateway=<gateway id>
curl timeout: 3 seconds
```

The active dialplan still documents the equivalent `start_v3.php` URL, but both the URL assignment
and `curl` are commented. It instead assigns `res=${CALLERID(name)}`. `CALLERID(RDNIS)` separately
carries `specstr`. No active producer that fills these caller fields exists in this checkout.
Consequently the strongest code-backed architecture statement is:

1. `simserver:8122/start_v3.php` (or an equivalent upstream service) classifies the call before it
   reaches this SIM-box;
2. an external SIP/IAX/Asterisk ingress node serializes the classification into caller metadata;
3. the local dialplan parses that metadata and `chan_svistok` selects the physical SIM.

The upstream implementation and database queries are absent. `apps/simbox-server/README.md` lists
`start_v3.php` only as a legacy compatibility endpoint; the checked-in Node routes do not implement
it. Its description is interface documentation, not proof of the missing server algorithm.

### Proven response envelope

The active parser proves this positional envelope (not the internal server calculation):

```text
OK/<qos>/<IMB2 history>/<fas>/<epdd>/<fpdd>/<hem>/<cap>/<note>
```

| Position | Local use |
|---:|---|
| 1 | must start with `OK` |
| 2 | raw outgoing class: `NOS/GOO/BAD/NOR/NEW/SOU/IMO/SYS/VIP/ROB/BLO` |
| 3 | semicolon-separated IMSIs previously used to call number B; sentinel `999999999999999` means any SIM is allowed |
| 4–7 | call-signalling controls `fas/epdd/fpdd/hem`, copied into the selected modem state and end report |
| 8 | `cap`; `NEW + OK` is locally rewritten to `NEC` |
| 9 | `note`; historical `NEM/NE0` rewrite branches remain commented |

`GOO` and its peers are therefore **remote pre-call classifications**. `NEC` is a **local composite**
derived from remote `NEW + cap=OK`. The server does not return the final per-candidate IM letter.

### `IMA2` is not an active server result

Despite the inherited `_IMA2` channel variable, the active dialplan sets `IMA2` to the sentinel for
an accepted classification and `chan_svistok::call_request_create()` reads only `_IMB2`. No active
selection branch consumes `_IMA2`. UI copy must therefore not claim that `IMA` is fetched from
`start_v3.php`.

The server supplies the ordered IMB history. `chan_svistok::pvt_select_im()` then compares each
candidate SIM IMSI with that list and derives:

| Derived code | Meaning |
|---|---|
| `B` | this SIM is the first/primary IMSI in number B's history |
| `C` | this SIM occurs later in number B's history |
| `D` | this SIM is absent, but other history exists and any SIM is permitted |
| `E` | this SIM is absent and only listed IMSIs are permitted |
| `N` | no history list and any SIM is permitted |

These are **candidate-selection relationships**, and the chosen SIM's letter is subsequently saved
as its live `im` state. The operator-facing family name remains **Multiple-SIM relationship (IM)**.

### Selection consequences and failure behavior

- IM filtering runs before QoS filtering.
- A candidate classified `B` or `C` bypasses normal Plan QoS capability filtering for every class
  except `ROB` and `BLO`; previous number-to-SIM affinity is intentionally strong.
- Parsed `qos=0` forces `IMB_any=1`. Since the parser defaults unknown/empty QoS to numeric zero,
  a missing or malformed classification can become fail-open for IM affinity.
- Before the macro, the dialplan defaults to `qos=NOS` with an empty history. A non-`OK` response
  therefore does not expose an explicit classification-error value in the legacy UI.
- The old direct HTTP call had a three-second timeout. In the active topology that timeout and
  upstream failure policy are outside this checkout.
- `fas=1` locally schedules artificial progress and answer after `epdd` and `fpdd` sleeps;
  `fas=2` generates progress/answer when the modem reaches its alerting event. `hem` is copied,
  persisted and reported but has no behavioral reader in the checked-in driver, so its meaning
  remains unresolved rather than inferred from its name.

### Feedback loop

After a call, `chan_svistok` invokes `system/svistok/callendout.sh`, which performs a plain HTTP GET
to `/svistok/callendout.php` with the selected IMSI/device, numbers, durations, normalized result,
cause/end party, `spec`, `uid`, `pro`, `fas/epdd/fpdd/hem`, timing and recognition fields. The older
dialplan hangup path also contains active `/end.php` reporting. This is sufficient to prove a
pre-call-classification/post-call-reporting loop, but not the missing server rule that turns reports
into a later `GOO` class or IMB history order.

The transport is legacy-trust-boundary code: plain HTTP GET, no visible authentication/signature,
positional slash delimiters in caller metadata and no explicit schema/version field. The old start
request also interpolates values into a shell curl command. These are implementation risks for a
future server/API flow; the Icons UI should expose availability/provenance, not attempt to repair
or reinterpret this protocol.

### UI/UX contract

1. Icon registry entries expose provenance: `remotePreCall`, `localComposite`, `localCandidate`,
   `livePersisted` or `historical`.
2. Tooltips for `GOO/NOR/...` say “received from pre-call classification service”, not “measured by
   this SIM”.
3. IM tooltips say “derived locally from this candidate SIM's position in the number-B history”.
4. Diagnostics may show the raw envelope and upstream availability, but no invented server-side
   algorithm, migration status or confidence score is shown as business data.
5. Unknown/non-`OK` pre-call results remain explicit in the new adapter. They must not be silently
   presented as a trustworthy `NOS` classification even when legacy-compatible selection falls
   back to `NOS/any`.

Evidence:

- `legacy/simbox-desktop-v2014/asterisk/old/extensions/extensions_dial.conf:89-115`
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_dial.conf:229-270`
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_dial_zones.conf:1-37`
- `libsCpp/asterisk-chan-svistok/src/select.h:26-30`
- `libsCpp/asterisk-chan-svistok/src/select.c:120-146,179-200,247-260,395-536,1017-1075`
- `libsCpp/asterisk-chan-svistok/src/at_response.c:1081-1125`
- `libsCpp/asterisk-chan-svistok/src/stat.c:209-333`
- `legacy/simbox-desktop-v2014/system/svistok/callendout.sh:193-213`
- `apps/simbox-server/README.md:108-140`

## Legacy Addition 1.11 — `total_numberb` aggregate and ranged top-N extraction
(2026-09-02, server fragment supplied by owner)

The supplied simserver SQL proves a server-side aggregate keyed by destination number B:

```sql
SELECT *
FROM total_numberb
WHERE total_billsec < 2147483647
  AND total_billsec > 0
  AND (<34 inclusive numberb range predicates>)
ORDER BY total_billsec DESC, total_answered ASC, total_calls DESC
LIMIT 1000;
```

The same fragment is preserved verbatim in
`libsReactNative/react-native-sip2-builder-personal/src/patch_2.9/TODO.md:102-176`, immediately
after the note `opt/replica`. This corroborates the owner-provided server fragment, but the TODO is
not executable server code and does not by itself establish the job schedule or consumer.

### What is now proved

- `total_numberb` stores at least `numberb`, `total_billsec`, `total_answered` and `total_calls`.
- The unit of aggregation is number B, not a particular selected SIM/IMSI.
- Only rows with positive accumulated billable seconds are selected.
- `2147483647` is the signed 32-bit maximum boundary. The query excludes that value and above;
  whether this is overflow protection, a sentinel or data-cleaning policy is not proved.
- Ranking is lexicographic: greatest `total_billsec`; for ties, smallest `total_answered`; for
  further ties, greatest `total_calls`; then the first 1000 rows are returned.
- The leading range-only fragment contains 35 ranges covering 6,238,567 numeric values. The actual
  `SELECT` contains 34 ranges covering 5,838,567 values: it omits
  `79006200000..79006599999` (exactly 400,000 values).
- The hard-coded range set is a snapshot/scoping policy, not a general DEF-zone registry. Some
  clauses are adjacent and could be merged, while others have irregular boundaries.

### What remains unproved

This exact query is a batch/ranking extraction across many destination ranges, not the online
`WHERE numberb=<current call>` lookup expected inside `start_v3.php`. `ORDER BY ... LIMIT 1000`
strongly indicates preparation of a top-N list, replica, cache or offline analysis. The nearby
`opt/replica` note supports that interpretation but is not sufficient to choose one.

No available source proves:

- how `callendout.php` updates `total_numberb`;
- whether `total_answered` is a count, duration or another accumulated measure;
- the time window and reset/decay policy of any aggregate;
- which gateway/tenant/operator partitions, if any, are omitted from `SELECT *`;
- the thresholds or rule mapping aggregate rows to `GOO/NOR/BAD/NEW/VIP/ROB/BLO`;
- whether membership in the top 1000 directly affects `start_v3`, or feeds another intermediate
  list/table first.

Therefore the UI may accurately say that outgoing pre-call classification is backed by
server-maintained number-B history/aggregates, but it must not explain `GOO` as “highest billsec” or
derive a quality score from these columns until the missing classifier query/code is recovered.

### Data/API implication

The future API model should distinguish raw server evidence from the resulting class:

- `NumberBAggregate`: diagnostics/analytics data (`totalBillSec`, `totalAnswered`, `totalCalls`);
- `PreCallClassification.rawQos`: authoritative class returned for the call;
- `MultipleSimRelation`: separately derived from IMSI history.

The Icons page shows the status contract and provenance, not aggregate values. Aggregate metrics
belong in a call-history/diagnostics drill-down if that server feature is later restored.

Evidence:

- owner-supplied simserver SQL fragment, 2026-09-02;
- `libsReactNative/react-native-sip2-builder-personal/src/patch_2.9/TODO.md:102-176`.

## Legacy Addition 1.12 — owner-confirmed `GOO` quality rule (2026-09-02)

The product owner confirmed the server-side business meaning of `GOO`:

- ACD is calculated as `total_billsec / total_answered`;
- the number-B history qualifies as `GOO` when `ACD >= GOO_ACD`, where `GOO_ACD=300` seconds,
  and `ASR >= GOO_ASR`, where `GOO_ASR=80%`;
- ASR is calculated as `total_answered / total_calls * 100%`.

This resolves two uncertainties from Addition 1.11:

1. `total_answered` is the answered-call count used as the ACD denominator.
2. `GOO` is a derived server quality class, not merely membership in the ranked top-1000 extract.

The query's tie-break `total_answered ASC` is now explainable: for equal `total_billsec`, fewer
answered calls produce a higher ACD. The complete query still does not sort directly by ACD or ASR,
so it remains a batch/top-N extraction and must not be treated as the classifier expression itself.

The owner confirmed both formulas, constants and inclusive comparisons. In normalized form:

```text
ACD = total_billsec / total_answered
ASR = total_answered / total_calls * 100
GOO = ACD >= 300 && ASR >= 80
```

The server implementation must guard `total_answered=0` for ACD and the ASR denominator (normally
`total_calls=0`). The client never substitutes infinity/zero or independently assigns `GOO` when
aggregate inputs are incomplete.

### Corrected operator wording

- RU label: **Хорошая история соединений**.
- EN label: **Good connection history**.
- RU tooltip: **Серверная классификация номера B: ACD ≥ 300 с и ASR ≥ 80%.**
  Detailed diagnostics may show the authoritative ACD/ASR values and sample counts.
- Do not describe `GOO` as a live measurement of the selected SIM, a signal-quality status or a
  simple “known number” flag.

## Legacy Addition 1.13 — preserve Icons layout; add separate Glossary (2026-09-02)

The owner superseded the earlier Icons-page rebuild requirement:

1. Preserve the current Icons page layout and interaction exactly: title card, group cards, group
   path, fixed-width wrapped tiles and hover tooltips.
2. Correct only textual semantics: page/group titles, visible labels, raw-code notation and
   tooltip explanations. Existing icon assets, tile count, order, positions and groups remain
   unchanged; no icon tile is added, removed, moved or replaced in this flow.
3. Withdraw the proposed searchable/filterable registry UI, badges, expanded provenance rows,
   collapsible groups and mobile filter popover. Earlier Icons Page Requirements 1–6 and matching
   acceptance criteria are superseded wherever they require these visual changes.
4. The operator-facing name of the page content is **Icon legend / Легенда иконок**. Navigation may
   remain the shorter **Icons / Иконки**.
5. Add a separate **Glossary / Глоссарий** reference page for domain terms, formulas and
   abbreviations. It is not a tab, filter or expanded mode of the icon legend.
6. The Glossary initially covers call quality, number/SIM identity, classification, IM relations,
   call lifecycle, modem/network, routing/configuration and operator actions.
7. Icons tooltips remain concise. Definitions such as ACD/ASR formulas live in the Glossary; a
   tooltip may quote the relevant threshold without duplicating a long definition.

Updated acceptance criteria:

- [ ] A screenshot comparison shows no unintended Icons-page geometry/control changes.
- [ ] Every existing icon tile retains an icon, corrected visible label, raw code and corrected
      tooltip in the current composition.
- [ ] Glossary is a separate sidebar destination and uses grouped term/definition rows.
- [ ] Icon legend and Glossary share one terminology source so labels and definitions cannot drift.
