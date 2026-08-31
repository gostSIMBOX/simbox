# Implementation Plan: flutter_gsmsip-example-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-31
> Specifications: [03-specifications.md](03-specifications.md) (APPROVED)

## Summary

Covers AC1, AC4–AC8 only — everything `03-specifications.md` locked.
AC2 (multi-profile Setup) and AC3 (System Capabilities) are **not**
planned here; they get their own plan once `sdd-flutter_gsmsip-lib`
reaches Specifications and the Deferred sketch types are replaced with
real ones (see that document's Deferred section).

Order: data-layer pieces with no UI dependency first (Default Dialer
source, DS tokens), then the screen that consumes them (Gateway), then
the smaller cross-cutting items (permission manifest comments, splash).
This lets each phase be independently verified — a DS token swap doesn't
need to wait for the Gateway screen rewrite to be checkable, and vice
versa.

## Task Breakdown

### Phase 1: Default Dialer Data Layer (AC4)

#### Task 1.1: DefaultDialerStatusSource

- **Description**: Abstract interface + `flutter_gsm`-backed
  implementation reading `flutter_gsm/replace_dialer`'s existing
  `MethodChannel` (`isDefaultDialer`/`canSetDefaultDialer`/
  `setDefaultDialer` — already implemented and working in
  `ReplaceDialerModule.kt`, no native changes needed).
- **Files**:
  - `example/lib/data/default_dialer_status_source.dart` — Create
- **Dependencies**: None
- **Verification**: Unit test with `TestDefaultBinaryMessengerBinding`
  mocking the channel (no new dev-dependency needed — Flutter's test
  framework covers this); confirms all three methods map to the right
  channel method names and a `PlatformException` (e.g. channel absent on
  non-Android) surfaces as a clean "unsupported" result rather than an
  uncaught exception.
- **Complexity**: Low

#### Task 1.2: DialerWarningLevel

- **Description**: Session-scoped enum (`none`/`needsAlert`/`cardOnly`)
  and the small piece of state-machine logic around it (transitions on
  `isDefaultDialer()` result + "has the arm-time alert been shown this
  session").
- **Files**:
  - `example/lib/data/dialer_warning_level.dart` — Create
- **Dependencies**: Task 1.1
- **Verification**: Unit test covering the transition table in
  03-specifications.md's Behavior Specifications (including the
  fail-toward-`needsAlert` case when the `isDefaultDialer()` future
  hasn't resolved yet).
- **Complexity**: Low

---

### Phase 2: Design System Restyle (AC6)

Done before the Gateway screen rewrite so Phase 3 is written against
final tokens/widgets, not touched twice.

#### Task 2.1: DS color tokens

- **Description**: Replace `AppColors`' bespoke palette with the DS's
  Green/Simple accent (`--brand-light: #34E89E`, `--brand: #0CA678`) +
  shared neutrals (`--bg`/`--surface`/`--fg-1`/etc., light and dark) from
  `~/.claude/skills/nativemind-designsystem/tokens/colors.css`. Keep the
  existing `AppColors` class name and static-field structure (re-skin,
  not replace) so every call site in the six existing screens keeps
  compiling unchanged.
- **Files**:
  - `example/lib/theme/app_colors.dart` — Modify
- **Dependencies**: None
- **Verification**: `flutter analyze` passes with zero new errors (proves
  no call site broke); manual visual check against 02-visual.md's
  colorway intent.
- **Complexity**: Medium (careful 1:1 mapping of ~15 existing named
  colors to DS tokens, not a wholesale rewrite)

#### Task 2.2: DS gradients — collapse to one accent gradient

- **Description**: Per 03-specifications.md's re-skin table, delete
  every gradient in `AppGradients` except the one reserved for the
  single primary CTA (candidate: whichever button ends up as "Turn On
  Gateway Mode" / "Set as Default Dialer" — confirm exact widget in Task
  3.1). All other gradients (`cardGradient`, `chipGradient`,
  `navigationGradient`, `progressGradient`, status gradients, etc.)
  become flat single-color values pulled from `AppColors`.
- **Files**:
  - `example/lib/theme/app_gradients.dart` — Modify (delete ~20 of the
    ~25 existing gradient constants, keep 1)
  - `example/lib/theme/app_widgets.dart` — Modify (update
    `gradientCard`/`gradientButton`/`gradientProgressIndicator`/
    `gradientChip` internals to use flat colors except the kept one)
- **Dependencies**: Task 2.1
- **Verification**: Grep for `LinearGradient` usage across
  `example/lib/**` outside the one kept constant — should return zero
  hits (proves no scattered gradient survived); `flutter analyze` clean.
- **Complexity**: Medium

#### Task 2.3: Re-skin purpose-built indicator widgets

- **Description**: `signalIndicator`, `connectionIndicator`,
  `callStatusIndicator`, `statusCard` keep their exact method signatures
  (re-skin, not replace); only their internal color lookups
  (`_getSignalColor`, `_getConnectionColor`, `_getCallColor`, the
  `statusColor` default) change to reference `AppColors`' now-DS-mapped
  semantic values (`success`/`warning`/`danger`/`info`).
- **Files**:
  - `example/lib/theme/app_widgets.dart` — Modify
- **Dependencies**: Task 2.1
- **Verification**: No signature changes (grep call sites in the 6
  existing screens — zero should need edits); visual check of each
  indicator's 5-band/tri-state color output against DS semantic hexes.
- **Complexity**: Low

#### Task 2.4: Shadow + icon-set alignment

- **Description**: Collapse any divergent shadow definitions in
  `app_theme.dart` to DS's single app-wide shadow
  (`0 1px 32px rgba(156,178,194,0.10)`). Note-only for icons this pass:
  vendor `assets/adminka/` glyphs are a separate asset-import task, not
  blocking the token/widget re-skin — flagged as an Open Implementation
  Question below rather than silently deferred.
- **Files**:
  - `example/lib/theme/app_theme.dart` — Modify
- **Dependencies**: Task 2.1
- **Verification**: Visual diff — one consistent shadow across all
  existing cards.
- **Complexity**: Low

---

### Phase 3: Gateway Screen (AC1)

#### Task 3.1: Rename DashboardScreen → GatewayScreen

- **Description**: File + class rename, no behavior change yet — isolates
  the rename from the larger rework in Task 3.2 so a diff reviewer can
  tell "moved" from "changed."
- **Files**:
  - `example/lib/screens/dashboard_screen.dart` → `example/lib/screens/gateway_screen.dart` — Rename (`DashboardScreen`/`_DashboardScreenState` → `GatewayScreen`/`_GatewayScreenState`)
  - `example/lib/main.dart` — Modify (import path, `DashboardScreen()` → `GatewayScreen()`, tab label `'Dashboard'` → `'Gateway'`, icon `Icons.dashboard` → an icon reflecting the gateway/bridge concept, e.g. `Icons.swap_calls`/`Icons.router` — confirm exact choice against DS/adminka icon set in Task 2.4's follow-up)
- **Dependencies**: None (can run in parallel with Phase 1/2)
- **Verification**: App builds and launches unchanged (pure rename) —
  bottom nav shows "Gateway" instead of "Dashboard", same screen content
  as before.
- **Complexity**: Low

#### Task 3.2: Active Routings list

- **Description**: Subscribe to `_gateway.routingStream`, maintain
  `Map<String, CallRouting>` keyed by `CallRouting.id`; entries with
  `state == ended` are removed after a short delay (per
  03-specifications.md's edge-case table), entries with `state ==
  failed` persist until the user taps `[Dismiss]`. Render each entry as
  the Bridge Status card from 02-visual.md (SIP leg / GSM leg / Bridge,
  direction-aware label "GSM ──► Gateway ──► SIP" vs "SIP ──► Gateway
  ──► GSM").
- **Files**:
  - `example/lib/screens/gateway_screen.dart` — Modify
  - `example/lib/screens/widgets/active_routing_card.dart` — Create
- **Dependencies**: Task 3.1
- **Verification**: Unit test the routing-list reducer against
  `routingStream` fixtures covering all four `CallRoutingState` values ×
  both `CallRoutingDirection` values (8 cases, per 03-specifications.md's
  Testing Strategy); manual test by placing/receiving a real bridged call
  if a test SIP account is available.
- **Complexity**: Medium

#### Task 3.3: Empty / idle / disarmed states

- **Description**: Render 02-visual.md's "Idle" (armed, no routings),
  "Loading" (gateway starting), and "Empty/disarmed" (gateway mode off)
  states based on `GatewayStatus.isRunning` and whether any routings
  exist.
- **Files**:
  - `example/lib/screens/gateway_screen.dart` — Modify
- **Dependencies**: Task 3.2
- **Verification**: Manual check of each state by toggling gateway
  on/off with zero active calls.
- **Complexity**: Low

---

### Phase 4: Default Dialer UI (AC4)

#### Task 4.1: Persistent Default Dialer card

- **Description**: `DefaultDialerCard` widget reading
  `DefaultDialerStatusSource`, showing 02-visual.md's "Not set" (precise
  consequence copy: incoming-call auto-answer/bridging breaks, nothing
  else does) or "Set" states. Embedded in `GatewayScreen` (below Gateway
  Status) and `SettingsScreen`.
- **Files**:
  - `example/lib/screens/widgets/default_dialer_card.dart` — Create
  - `example/lib/screens/gateway_screen.dart` — Modify (embed)
  - `example/lib/screens/settings_screen.dart` — Modify (embed)
- **Dependencies**: Task 1.1, Task 2.1 (uses DS-mapped warning color)
- **Verification**: Manual test toggling default-dialer status via
  Android Settings and confirming the card updates on
  `didChangeAppLifecycleState(resumed)` without a manual refresh; test
  `canSetDefaultDialer() == false` path shows the no-dead-end-button copy
  variant from 03-specifications.md's edge cases.
- **Complexity**: Medium (lifecycle-observer wiring is the fiddly part)

#### Task 4.2: Arm-time alert

- **Description**: `DefaultDialerArmAlert` modal, shown once per app
  session the first time `GatewayStatus.isRunning` flips false→true while
  `DialerWarningLevel == needsAlert`. "Continue Anyway" dismisses to
  `cardOnly` (persistent card stays visible); "Set Default Dialer" calls
  `DefaultDialerStatusSource.requestDefaultDialer()`.
- **Files**:
  - `example/lib/screens/widgets/default_dialer_arm_alert.dart` — Create
  - `example/lib/screens/gateway_screen.dart` — Modify (wire the
    false→true transition trigger)
- **Dependencies**: Task 1.2, Task 4.1
- **Verification**: Unit test the trigger condition (status-transition
  edge, not level-triggered — must not re-fire on every rebuild while
  already running); manual test of both alert actions.
- **Complexity**: Medium

---

### Phase 5: Permission Manifest (AC5)

#### Task 5.1: Manifest ownership comment block

- **Description**: Add the comment block from 03-specifications.md
  mapping each of `example`'s manifest permissions to its owning flow —
  no permissions removed in this task.
- **Files**:
  - `example/android/app/src/main/AndroidManifest.xml` — Modify (comments only)
- **Dependencies**: None
- **Verification**: Manifest still parses/builds unchanged; diff shows
  comments only, zero `<uses-permission>` lines touched.
- **Complexity**: Low

#### Task 5.2: Confirm RECEIVE_MMS/RECEIVE_WAP_PUSH removal with Anton

- **Description**: 03-specifications.md flagged these two as unbacked
  cruft but explicitly deferred removal pending Anton's confirmation —
  this task is that confirmation checkpoint, not a code change by
  default.
- **Files**: None (decision checkpoint)
- **Dependencies**: Task 5.1
- **Verification**: Anton's explicit yes/no recorded in this plan's
  Approval section or a follow-up note; if yes, becomes a one-line manifest
  diff, otherwise closed as "keep, revisit if MMS ever becomes a real
  feature."
- **Complexity**: Low

---

### Phase 6: Splash (AC7)

#### Task 6.1: Invoke /nativemind-flutter-splash

- **Description**: Confirm a usable app logo asset exists for
  `flutter_gsmsip/example`; if not, use
  `~/.claude/skills/nativemind-designsystem/uploads/logo_nativemind.svg`
  as a placeholder. Then run the splash skill's install steps verbatim —
  no hand-written splash code per that skill's own rule.
- **Files**: Whatever the splash skill's install steps generate (native
  Android launch screen resources, no `example/lib/**` splash code)
- **Dependencies**: Task 2.1 (splash bg colors `#F8F9FA`/`#0F1419`
  already match DS neutrals — confirm no conflict once tokens land)
- **Verification**: Cold-launch the app, confirm the branded splash shows
  before Flutter's first frame, matches the skill's own verification
  steps.
- **Complexity**: Low (skill does the work; this is invocation +
  asset-sourcing)

---

### Phase 7: Verification & Polish

#### Task 7.1: Full manual walkthrough

- **Description**: Run through 03-specifications.md's Manual
  Verification checklist end-to-end on a real device: default-dialer
  toggle + card/alert behavior, visual diff against 02-visual.md's Green
  accent with no scattered gradients outside the one kept CTA.
- **Files**: None (verification only)
- **Dependencies**: All prior phases
- **Verification**: Checklist in 03-specifications.md fully checked off.
- **Complexity**: Low

#### Task 7.2: Update sibling-flow status files

- **Description**: Once this flow's implementation lands, update
  `vdd-flutter_gsmsip-example-voiceline-uiux`'s `_status.md` blocker note
  about the Enhanced-Mode/System-Capabilities overlap — it's no longer
  purely theoretical once one side has real code.
- **Files**:
  - `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-voiceline-uiux/_status.md` — Modify
- **Dependencies**: Task 7.1
- **Verification**: N/A (documentation task)
- **Complexity**: Low

## Dependency Graph

```
Task 1.1 ──┬──────────────────────────────► Task 4.1 ──► Task 4.2
           └──► Task 1.2 ────────────────────────────────────┘

Task 2.1 ──┬──► Task 2.2 ──► Task 2.3
           ├──► Task 2.4
           └──────────────────────────────► Task 4.1
                                             Task 6.1

Task 3.1 ──► Task 3.2 ──► Task 3.3

Task 5.1 ──► Task 5.2

(Task 3.x, Task 4.x, Task 5.x, Task 6.1 all converge on)
                                             ▼
                                        Task 7.1 ──► Task 7.2
```

Phases 1, 2, 3 (up to 3.1), and 5.1 have no cross-dependencies and can
run in parallel; Phase 4 needs both Phase 1 (data) and Phase 2 (tokens);
Phase 3.2/3.3 needs 3.1's rename done first; Phase 6 only needs Phase
2.1's colors settled to avoid redoing the splash-bg confirmation.

## File Change Summary

| File | Action | Reason |
|---|---|---|
| `example/lib/data/default_dialer_status_source.dart` | Create | AC4 — Task 1.1 |
| `example/lib/data/dialer_warning_level.dart` | Create | AC4 — Task 1.2 |
| `example/lib/theme/app_colors.dart` | Modify | AC6 — Task 2.1 |
| `example/lib/theme/app_gradients.dart` | Modify | AC6 — Task 2.2 |
| `example/lib/theme/app_widgets.dart` | Modify | AC6 — Task 2.2/2.3 |
| `example/lib/theme/app_theme.dart` | Modify | AC6 — Task 2.4 |
| `example/lib/screens/dashboard_screen.dart` → `gateway_screen.dart` | Rename + Modify | AC1 — Task 3.1/3.2/3.3 |
| `example/lib/screens/widgets/active_routing_card.dart` | Create | AC1 — Task 3.2 |
| `example/lib/screens/widgets/default_dialer_card.dart` | Create | AC4 — Task 4.1 |
| `example/lib/screens/widgets/default_dialer_arm_alert.dart` | Create | AC4 — Task 4.2 |
| `example/lib/screens/settings_screen.dart` | Modify | AC4 — Task 4.1 (embed card) |
| `example/lib/main.dart` | Modify | AC1 — Task 3.1 (rename wiring) |
| `example/android/app/src/main/AndroidManifest.xml` | Modify | AC5 — Task 5.1 (comments only) |
| `libsFlutter/flutter_gsmsip/lib/**` | **None** | AC8 — verified untouched throughout |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| DS color re-skin (Task 2.1) breaks a call site relying on a color constant being removed rather than remapped | Medium | Medium | Keep every existing `AppColors` field name, only change hex values — `flutter analyze` catches removed fields immediately |
| Gradient collapse (Task 2.2) picked the wrong widget as "the one kept CTA" | Low | Low | Purely cosmetic if wrong — swap which button keeps the gradient is a one-line change, not a rearchitecture |
| Lifecycle-observer for Default Dialer re-check (Task 4.1) leaks or double-registers | Medium | Medium | Standard `WidgetsBindingObserver` dispose pattern, same as any other lifecycle-aware widget in Flutter — no novel risk, just needs the usual dispose discipline |
| Arm-time alert (Task 4.2) re-fires more than once per session due to a state-management bug | Medium | Low (annoying, not breaking) | Explicit unit test on the trigger condition (Task 4.2's Verification) before manual testing |
| `RECEIVE_MMS`/`RECEIVE_WAP_PUSH` removal (Task 5.2) breaks an undiscovered feature | Low | Medium | Gated behind Anton's explicit confirmation — not removed by default |

## Rollback Strategy

Each phase is independently revertable since files are scoped per-phase
(File Change Summary above has no file touched by two unrelated phases
except `gateway_screen.dart`, which is touched by Phase 3 and Phase 4 in
an additive way — reverting Phase 4's embed doesn't require reverting
Phase 3's rename).

1. DS restyle (Phase 2) can be reverted independently by restoring
   `app_colors.dart`/`app_gradients.dart`/`app_widgets.dart` from git —
   no data-layer dependency.
2. Gateway screen (Phase 3) rename can be reverted by reversing the
   rename + `main.dart` edit; no persisted state involved.
3. Default Dialer UI (Phase 4) has no persisted state (`DialerWarningLevel`
   is in-memory only) — reverting is a pure code revert, no migration
   needed.
4. Manifest comment block (Phase 5) is comments-only — trivially
   revertable, and Task 5.2's actual permission removal (if approved) is
   the only line with real rollback weight (re-add the two
   `<uses-permission>` lines).

## Checkpoints

After each phase, verify:

- [ ] `flutter analyze` clean (zero new errors/warnings)
- [ ] Existing tests still pass (`example_config_store_test.dart` +
      any new tests added this phase)
- [ ] Behavior matches `02-visual.md` mockups for that phase's screens
- [ ] No file under `libsFlutter/flutter_gsmsip/lib/**` touched (AC8 —
      check `git status` scope after every phase, not just at the end)

## Open Implementation Questions

- [ ] Which existing button becomes the DS's one allowed accent
      gradient (Task 2.2)? Candidate: "Turn On Gateway Mode" primary CTA
      on the new Idle/disarmed Gateway screen state — confirm during
      Task 3.3, not before (the button doesn't exist yet at Task 2.2
      time).
- [ ] `assets/adminka/` icon vendoring (03-specifications.md's
      iconography note) — not scheduled as its own task above; decide at
      Task 3.1 whether the tab-icon change needs a vendored glyph or a
      stock Material icon suffices for this iteration.
- [ ] Task 5.2's Anton confirmation — open until answered.

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:

---

*Created by /vdd - flutter_gsmsip-example-uiux implementation plan*
