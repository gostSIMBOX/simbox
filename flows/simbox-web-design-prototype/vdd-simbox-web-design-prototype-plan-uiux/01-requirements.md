# Requirements: Plans editor UI/UX

> Version: 1.0  
> Status: REVIEW  
> Last Updated: 2026-09-02

## Problem Statement

The Flutter prototype currently shows only three guessed plan rows in one very wide table. The
rows are not backed by the legacy registry and cannot be created, cloned, deleted or meaningfully
edited. Legacy contains a much larger plan catalogue and a real relationship in which one command
set can own many plans, while each plan selects exactly one command set.

The legacy page is authoritative for behavior and meaning, not for layout. With every information
group enabled it mixes roughly 80 editable columns, current daily counters, undocumented aliases
and obsolete/test artifacts in one horizontal form. The new prototype must preserve verified plan
behavior without reproducing that UI or inventing new telephony policy.

## Evidence Summary

- `www/simbox/plan.php` is the legacy editor and defines the editable field families.
- `actions/set_plan_set.sh` assigns a plan ID to a SIM; `actions/set_plan_copy.sh` copies plan
  policy into SIM settings and limits.
- `system/get_args_plan_nabor.sh` confirms the model: SIM -> Plan -> Command set (`.nabor`).
- `var/simbox/plan09042014.tar.gz/plan/plan.list` contains 37 non-separator plan IDs.
- The archive contains 47 `.nabor` records: 37 listed plans, one visual separator artifact and
  nine unlisted test/orphan records.
- The existing Flutter `planRows` contains only `default`, `beeline_spb` and `tele2_spb`; those
  guessed rows are not an adequate source of truth.

## Domain Boundary

```text
Command set 1 ---- * Plan 1 ---- * SIM
                         |
                         +-- reusable policy/configuration
```

- A plan belongs to exactly one command set.
- A command set can have zero or many plans.
- A SIM stores one selected plan ID.
- The plan owns configured limits, schedules, modes and generation policy.
- Current SIM counters and current state remain SIM/runtime data, even when legacy displayed them
  next to plan limits.
- Daily reset execution remains scheduler/runtime behavior; the plan stores policy values only.

## Canonical Initial Registry

The recommended initial product seed is the 37 non-separator entries from archived `plan.list`, in
their original order. Separators (`-----------`) are presentation artifacts and are not plans.

| Command set | Plans |
| --- | --- |
| `default` | `default`, `localrostel_sms` |
| `tele2_spb` | `tele2_spb_good`, `tele2_spb_max`, `tele2_trash`, `tele2_sms`, `tele2_spb_last`, `tele2_spb_normal`, `tele2_spb_main`, `tele2_spb_bad`, `tele2_spb_new`, `tele2_spb_60min` |
| `beeline_spb` | `beeline_spb_vip`, `beeline_spb_good`, `beeline_spb_normal`, `beeline_spb_main`, `beeline_spb_bad`, `beeline_spb_max`, `beeline_spb_new`, `beeline_spb_old`, `beeline_spb_new_safe` |
| `megafon_spb` | `megafon_spb_vip`, `megafon_spb_good`, `megafon_spb_normal`, `megafon_spb_main`, `megafon_spb_max_safe`, `megafon_spb_max`, `megafon_spb_bad` |
| `megafon_msk` | `megafon_msk_good`, `megafon_msk_bad`, `megafon_msk_main` |
| `mts_spb` | `mts_spb_good`, `mts_spb_safe`, `mts_spb_60min` |
| `rostel_spb` | `rostel_sms`, `rostel_trash`, `rostel_good` |

The unlisted `kievstar_test`, `local`, `mts_spb_test`, `noname`,
`nonamevelcom_test`, `nonamevelcom_testvelcom_test`, `tele2`, `velcom_test` and
`velcom_test2` are retained in the development audit, not shown as active product plans by
default. This needs explicit owner confirmation before specifications.

## Editable Policy Families

The UI must expose verified configuration in semantic sections rather than as one 100-column row.

1. **Identity and ownership**
   - stable plan ID;
   - selected command set;
   - priority;
   - PRO routing tag. It is copied from Plan to SIM; a call request can carry its own `pro` tag;
     direction algorithms `P`, `p` and `v` use tag matching to admit/filter a SIM. It is not a
     product tier or tariff. Empty is the normal value for most plans; verified legacy examples
     include `2`, `GUR` and `VIK`.
2. **Capacity**
   - maximum online SIMs;
   - maximum add/reserve operations.
3. **Call modes and quality eligibility**
   - incoming/outgoing/service-out permissions;
   - VIP/not-VIP, quality/status and IM-mode eligibility flags preserved from active legacy
     fields.
4. **Timing and schedule**
   - global and state-specific minimum intervals;
   - workday and holiday wake/sleep values;
   - legacy disabled value `-1` represented as a clear disabled state.
5. **Directions**
   - four legacy direction policies (`alg.1..4`, `nodiff.1..4`, soft/max and hard limits); these
     direction controls are only one family inside the wider legacy row;
   - algorithm from the finite legacy value set;
   - difference behavior (`nodiff` semantics must be translated into positive UI wording);
   - soft/max and hard limits.
6. **Incoming-call generation**
   - request threshold/range;
   - answer/duration and incoming/outgoing ACD ranges;
   - forwarding, outgoing-to-incoming, connection, randomization, wait and sound flags.
7. **SMS and beacon generation**
   - MAY, MON and MSM limits without inventing unverified commercial meanings;
   - outgoing SMS soft/hard limits;
   - SMS generation soft/hard current/day/total policy;
   - no-spam mode.

Alias/typo fields found only in stored files (`capnnew`, `capyes`, `diff_vip`, double-underscore
ACD names and similar) must be audited and normalized only when equivalence is evidenced. Raw files
and arbitrary key/value editing are not part of the operational UI.

## User Stories

### Browse and understand

**As an** operator administrator  
**I want** to see every active legacy plan grouped/filterable by its command set  
**So that** regional policies are discoverable without navigating a giant horizontal table.

### Edit safely

**As an** operator administrator  
**I want** to edit one plan in semantic sections with units, ranges and validation  
**So that** I can change policy without remembering legacy filenames or numeric encodings.

### Create from a known plan

**As an** operator administrator  
**I want** to clone an existing plan or create a blank plan for a selected command set  
**So that** regional variants can reuse verified settings without manual re-entry.

### Delete safely

**As an** operator administrator  
**I want** deletion to explain which SIMs use a plan and prevent broken references  
**So that** removing a plan cannot silently orphan SIM configuration.

## Recommended Interaction Model

Use a responsive master-detail workspace consistent with the approved Command Sets editor:

- persistent searchable list of plans on desktop, compact selector on narrow screens;
- search plus command-set filter in the list;
- selected-plan header with ID, command set, usage count and Edit/Clone/Delete actions;
- semantic sections in the detail pane, with Save/Cancel for one atomic draft;
- Clone as the primary creation path and Blank as the secondary path;
- no always-visible 100-column grid and no modal containing the entire plan.

There is no plan-comparison mode. Legacy has no separate compare operation, and reliable CRUD plus
complete policy editing does not require one.

## Acceptance Criteria

### Must Have

1. The initial registry contains every approved canonical legacy plan with its exact ID, command-set
   relationship and preserved configuration values.
2. Every canonical plan file/value has an explicit structured target, normalized alias target or
   audit-only disposition; data may not disappear silently.
3. Selecting a command set shows all of its plans, and a plan can never reference a command-set ID
   absent from the live Command Sets controller.
4. A user can search plans and filter them by command set.
5. A user can edit all verified policy families through typed controls with units, constraints and
   actionable validation.
6. A user can create a plan by Clone or Blank, with a unique stable ID and selected command set.
7. A user can duplicate an existing plan without sharing mutable state with the source.
8. `default` is protected. A plan used by SIMs cannot be deleted until those SIMs are reassigned;
   an unreferenced plan requires explicit confirmation.
9. Changing selection, navigation or reset while dirty requires Save, Discard or Keep editing.
10. Saving is atomic in the prototype; invalid partial values do not replace the stored plan.
11. Current counters such as `online_day`, `add_day`, `reserv_day` and per-SIM current limits are
    not editable plan fields.
12. Existing SIM plan selection uses the same live plan registry rather than a separate mock list.
13. Desktop and narrow layouts remain usable without hiding fields or requiring page-level
    horizontal scrolling.
14. Feature actions use the existing Fugue density contract: 16 logical pixels backed by exact
    16×16 and 32×32 pairs; no emoji, Lucide or 48px tier.
15. The existing blue-gradient Save action remains the only primary gradient CTA in the workspace.

### Should Have

- Registry counts by command set and plan usage count.
- Reset seeded plan or reset all plans with an explicit dirty-state guard.
- Search within settings of the selected plan for expert users.
- Plain-language labels with the legacy key shown in tooltip/help where needed.
- Compact summaries on collapsed sections so important limits remain scannable.

### Won't Have (This Iteration)

- Backend persistence, modem execution or deployment of `/var/simbox/plan` files.
- Bulk assignment of plans to SIMs beyond integration with the existing SIM selection surface.
- Live counters, counter resets, scheduler execution or fabricated runtime results.
- Arbitrary key/value, Shell, PHP or source-file editor.
- New routing algorithms, inferred carrier tariffs or invented MAY/MON/MSM meaning.
- A migration-status column or UI for raw orphan/test artifacts.
- A plan-comparison mode.
- A new generic schema designer for user-defined plan field types.

## Constraints

- Logic source of truth: `legacy/simbox-desktop-v2014`, especially `www/simbox/plan.php`,
  `actions/set_plan*.sh`, `system/get_args_plan_nabor.sh` and the archived plan tree.
- Visual source of truth: `design/simbox-design-prototype-v2026-dc`; the existing Flutter Command
  Sets workspace is the closest interaction precedent.
- Target: `design/simbox-web-design-prototype-v2026`.
- Legacy remains read-only.
- The implementation remains a local interactive prototype unless later requirements explicitly
  authorize persistence.
- Existing user/generated changes in the nested target repository must be preserved.

## Open Questions

- [ ] Confirm the recommended active seed: import the 37 `plan.list` plans and keep the nine
  unlisted test/orphan IDs audit-only.
- [ ] Confirm deletion policy: protect `default`, block deletion while any SIM references a plan,
  and require confirmation for an unused plan.
- [ ] May the command-set association of an existing plan be edited, or should changing ownership
  require Clone into the target command set?
- [ ] Group ownership needs reconfirmation. The previously approved Command Sets amendment placed
  lifecycle group mappings in Plan, but direct tracing now shows that Plan files contain no group
  mapping, operator/region `GROUP_*` values live in command-set `config.sh`, concrete target group
  numbers live in dialplan route resources, and the current group lives on SIM. Recommended
  correction: keep group routing/mapping outside Plan policy and let Plan display it as read-only
  route context only.

## Legacy Addition 1.1 — DEF direction zones

The product owner's term **DEF directions** refers to the number-prefix classifiers in
`asterisk/extensions/zones`, not to Plan fields `alg.1..4` themselves.

The verified legacy chain is:

```text
called number
  -> Asterisk pattern in zones/*.conf
  -> named zone in Macro(makecall, <zone>, ...), stored as naprstr
  -> zone/mode route in extensions_dial_zones.conf
  -> resource descriptor such as L1D=NS101 or L3D_BS210
  -> Plan/SIM policy slot selected by the L number
```

- `zones/*.conf` owns DEF/prefix masks and their named routing zones, for example `tele2_spb`,
  `meg_spb`, `bee_msk`, `all_ua` and `rostel_spb_gor`.
- The already approved Zones VDD flow has normalized all 25 source files into 18 canonical zones
  containing 6,073 DEF patterns. Abbreviated/full operator aliases such as `bee_msk` and
  `beeline_msk` are merged only for the same operator and region; canonical IDs follow the live
  Zones registry (`beeline_*`, `megafon_*`, and so on).
- `extensions_dial_zones.conf` turns the named zone into one or more resource descriptors. The
  current descriptor parser in `libsCpp/asterisk-chan-svistok/src/select.c` reads the `L` digit as
  `limitnum`, the next character as the selection modifier and the two-letter segment as
  `billing_direction`; the archived `svistok-aa/select.c` contains the same legacy scheme.
- Plan owns reusable policy for the numbered slots (`alg`, `nodiff`, `limit_max`, `limit_hard`);
  it does not own or edit thousands of destination-prefix masks.
- Slot 0 and the partially propagated slot 5 occur in runtime/copy paths but are not complete
  editable Plan families in `plan.php`. They require explicit compatibility treatment and must not
  be silently presented as ordinary Plan directions 1–4.

For this Plan iteration, the **Directions** section should therefore show each Plan policy slot
with read-only routing context derived from the zone-to-resource map (zone names and billing
direction codes that can reach the slot). It must consume the shared live Zones registry created
by `vdd-simbox-web-design-prototype-zones-uiux`, not copy a second zone catalogue into Plans.
Editing zone names and DEF masks stays on that separate **Направления** screen; raw Asterisk
configuration remains outside Plan CRUD.

Additional acceptance criteria:

16. UI labels and help distinguish a DEF zone, a billing direction code and a Plan limit slot;
    these concepts may not be collapsed into one field called "direction".
17. Each Plan slot shows a compact read-only summary of the canonical zones/routes that can select
    it, with details available on demand; the Plan form never renders all 6,073 masks inline.
18. Plan zone references use the same 18-record live registry as the approved Zones feature; alias
    normalization is not reimplemented in the Plans feature.
19. The requirements/specification audit records the compatibility disposition of slots 0 and 5
    before implementation.

## Legacy Addition 1.2 — Dialplan route and group-based SIM selection

The source-of-truth chain continues beyond the DEF zone:

```text
Zone / naprstr
  -> extensions_dial_zones.conf chooses a route resource
  -> resource encodes Plan slot + route modifier + limit mode + billing code + group
  -> libsCpp/asterisk-chan-svistok/src/select.c parses the resource
  -> candidate SIMs are filtered by current group, dial availability and selected-slot limit
  -> Plan-derived eligibility and sorting rules choose one available SIM
```

For example, `L1D=NS101` is parsed as:

| Segment | Verified meaning |
|---|---|
| `L1` | numbered policy/limit slot 1 |
| `D` | route selection modifier stored as `cr->alg`; not the same field as a Plan's persisted `alg.1` |
| `=` | limit-use mode (`limittype`) |
| `NS` | two-character billing direction |
| `101` | required current SIM group |

`get_cr_group()` performs this parse. `pvt_select_create()` then admits a device only when
`CONF_SHARED(pvt, group) == cr->group`, `can_dial(...)` succeeds and the selected limit permits
the call. Later stages apply IM history, QoS, PRO/capability, work-state and difference filters,
then shuffle/sort and lock the selected device.

The current group is loaded from `sim/settings/<IMSI>.group` and can be changed through
`dongle setgroup` / `dongle setgroupimsi`. Operator/region configs contain lifecycle constants
that correspond directly to major dialplan groups—for example MegaFon SPb `GROUP_WORK_OK=101`,
Beeline SPb `=102`, MTS SPb `=103`, MegaFon Moscow `=104`, Tele2 SPb `=109`, Kyivstar `=111`
and Rostelecom SPb `=220`. The dialplan also references additional operational groups not fully
described by those constants, so the UI must not infer a complete group taxonomy from
`GROUP_WORK_OK` alone.

Consequences for the Plan UI:

- Plan does not choose a SIM group and does not edit the dialplan resource.
- A Plan policy slot may show the routes and target groups that use it as read-only operational
  context.
- Route resources belong to the routing/dialplan model associated with Directions; current group
  belongs to SIM runtime.
- Until group ownership is reconfirmed, no editable lifecycle-group mapping is added to Plan.

Additional acceptance criteria:

20. A route-context row keeps zone, slot, modifier, limit mode, billing code and target group as
    separate typed values; the compact resource string may be shown only as technical provenance.
21. The Plan editor does not promise that changing a Plan changes group membership or dialplan
    routing.
22. Route context is derived from `extensions_dial_zones.conf`, while candidate-selection meaning
    is derived from `libsCpp/asterisk-chan-svistok/src`; neither is reverse-engineered from labels.

## References

- `legacy/simbox-desktop-v2014/www/simbox/plan.php`
- `legacy/simbox-desktop-v2014/actions/set_plan_set.sh`
- `legacy/simbox-desktop-v2014/actions/set_plan_copy.sh`
- `legacy/simbox-desktop-v2014/system/get_args_plan_nabor.sh`
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_zones.conf`
- `legacy/simbox-desktop-v2014/asterisk/extensions/extensions_dial_zones.conf`
- `legacy/simbox-desktop-v2014/asterisk/extensions/zones/`
- `legacy/simbox-desktop-v2014/svistok-aa/select.c`
- `legacy/simbox-desktop-v2014/nabor/*/config.sh`
- `libsCpp/asterisk-chan-svistok/src/select.c`
- `libsCpp/asterisk-chan-svistok/src/share.c`
- `libsCpp/asterisk-chan-svistok/src/svistok/cli.c`
- `flows/simbox-web-design-prototype/vdd-simbox-web-design-prototype-zones-uiux/`
- `legacy/simbox-desktop-v2014/var/simbox/plan09042014.tar.gz`
- `design/simbox-web-design-prototype-v2026/lib/pages/plan_page.dart`
- `design/simbox-design-prototype-v2026-dc/index.html`

---

## Approval

- [ ] Requirements approved by product owner
- [ ] Approved on: 2026-09-01
- [ ] Notes: pending answers to the open questions above
