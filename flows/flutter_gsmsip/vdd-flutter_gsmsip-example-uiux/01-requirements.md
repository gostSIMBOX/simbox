# Requirements: flutter_gsmsip-example-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-31

## Problem Statement

`libsFlutter/flutter_gsmsip/example` was just brought back to a genuinely
working state by `sdd-flutter_gsmsip-example` (Setup/Dashboard/Settings/
Call/SMS/Logs, wired to the real `GatewayService` API). But it only
demonstrates `flutter_gsmsip` as a **one-line SIP↔GSM bridge orchestrator**
— it does not demonstrate the **gateway product shape** that two prior
implementations of this same idea converged on independently:

- **`reactntive/react-native-gsm-sip-gateway`** (`telon-gateway-app`) — a
  React Native app wrapping `react-native-tele` (GSM leg) +
  `react-native-sip2` (SIP leg) behind one `Gateway` class, with
  per-device config profiles (`tConfig`/`sConfig` keyed by
  `DeviceInfo.getDeviceId()`), a `ReplaceDialer`+`Permissions` bootstrap
  flag pair, and a bare-bones Magisk module (`magisk/gateway/`) that
  exists but does nothing yet (`module.prop` only, no install scripts).
- **`3rdparty/gsm2sip`** — its native-Kotlin successor (`com.callagent.gateway`),
  materially more complete: `CallOrchestrator` bridges GSM
  (`GsmCallManager`, `InCallService`, `ConnectionService`) to SIP
  (`SipClient`, `RtpSession` with G.722), runs as a foreground
  `GatewayService` with `BootReceiver` auto-start, and — critically —
  ships a **working Magisk module** (`gsm2sip/magisk/`) that installs the
  APK as a priv-app, force-grants runtime permissions
  (`RECORD_AUDIO`, `READ_PHONE_STATE`, `CALL_PHONE`, `ANSWER_PHONE_CALLS`,
  location, notifications), hides `PermissionController` at the
  filesystem level so grants can't be silently revoked, and stages
  `tinymix`/`tinycap` for direct ALSA mixer control.

Both are single-purpose native/JS apps; `flutter_gsmsip` is the
Flutter/Dart reincarnation of the same "GSM↔SIP gateway" concept, but its
example has never shown the **gateway operating mode** (auto-answer GSM →
bridge to SIP, or SIP INVITE with a forward header → dial out over GSM;
per-device/profile config; Magisk-dependent capability state; default-
dialer status) — only manual "make one test call" / "send one test SMS"
actions.

Separately, Anton asked a direct question that this flow must answer, not
defer: **are all the Android permissions `flutter_gsmsip`-based apps need
actually declared inside the libraries themselves, or only copy-pasted
into the example's manifest?** Investigated already (see **Permission
Audit** below) — the answer is "no, there's a real gap," and closing it
belongs partly to sibling libraries, not to this flow alone.

### Relationship to other flows (read before writing specs)

This flow is scoped to **`libsFlutter/flutter_gsmsip/example`'s UI/UX
only** — it visualizes and wires screens using APIs the libraries already
expose (extending them only where a real gap blocks the demo, per the
precedent set by `sdd-flutter_gsmsip-example`, which touched the example
only). Three adjacent concerns are explicitly **out of scope** here and
must be filed/cross-referenced against their own flows instead of
reimplemented inline:

| Concern | Owning flow | What this flow does instead |
|---|---|---|
| Replacing the system dialer (`ACTION_CHANGE_DEFAULT_DIALER`, `InCallService`, `ConnectionService`) | **`flows/flutter_replace_dialer/`** (tracks the **`flutter_dialer`** package — the old `tdd-replace-dialer` doc there is legacy React-Native content describing `react-native-replace-dialer`'s `ReplaceDialerModule.java`/`RC_DEFAULT_PHONE`; it needs a Flutter-era pass, which is this flow's cue to open that work, not a reason to duplicate default-dialer UI here). **New finding**: this duplication already exists in code, not just in docs — `flutter_gsm/android/.../ReplaceDialerModule.kt` implements `isDefaultDialer`/`setDefaultDialer`/`canSetDefaultDialer` over its own channel (`flutter_gsm/replace_dialer`), completely separately from `flutter_dialer`'s plugin. `flutter_replace_dialer` needs to resolve which package owns this (recommend: consolidate into `flutter_dialer`, delete the duplicate from `flutter_gsm`) — not something to decide inside this UI/UX flow. | Example surfaces a **"Default Dialer" status card** reading whichever module `flutter_replace_dialer` designates as canonical, and links out to Setup instructions; no new dialer-replacement logic is written inside `flutter_gsmsip` |
| Magisk-granted privileged capabilities (`CAPTURE_AUDIO_OUTPUT`, disabling Qualcomm audio-concurrency locks, priv-app permission grants) | **`flows/flutter_gsmsip/sdd-voiceline-mode-magisk`** + **`sdd-voiceline-mode-magisk-v2`** (already DRAFT/REVIEW, own the actual Magisk module spec) | Example surfaces a **"System Capabilities" panel** (magisk installed? which privileged perms are actually granted right now, via `PermissionController`/`dumpsys` semantics already documented in `-v2`) that reads capability flags — it does not design a new Magisk module. **Dependency to flag, not silently assume**: a Magisk module is scoped to one installed app's `applicationId` (see Permission Audit below), so demonstrating a *real* granted capability in this example requires `sdd-voiceline-mode-magisk-v2` to ship a variant targeting `org.telon.flutter_gsmsip_example` (its current applicationId) rather than the spec's existing `one.telefon.gateway` target. |
| Voice-line access methods (TTY/Telecom/Enhanced-Mode/Dongle selection) and hardware adapters (TRRS/USB differential signaling) | `sdd-pjsip-mode-inversion`, `sdd-voiceline-mode-direct`, `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-voiceline-uiux` (umbrella UI flow), `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-zatychka-uiux` (dongle-specific UI, referenced by voiceline-uiux) | Not touched by this flow — those already have their own approved UI (both at PLAN phase). **Overlap to resolve, not silently duplicate**: voiceline-uiux's "Enhanced Mode" screen and this flow's "System Capabilities panel" (AC3 below) both surface Magisk-derived capability flags — coordinate before implementing either. |
| `flutter_gsmsip` library API gaps: public config save/clear, multi-profile storage, whether a Magisk-capability model belongs in the library, and documenting the permission contract the library can't enforce itself | **`flows/flutter_gsmsip/sdd-flutter_gsmsip-lib/`** (new — split out of this flow's own drafting once these turned out to be library-code items, not UI/UX) | This flow's Setup/Capabilities screens are written *against* whatever public API that flow decides on — no example-local workarounds re-invented once it ships (see AC2/AC3 below, both now depend on it) |

**Confirmed already implemented, not a gap** (found while drafting the
lib-split above, recorded here so a future pass doesn't redo it): GSM→SIP
auto-bridging — the actual "gateway mode" behavior both
`react-native-gsm-sip-gateway` and `gsm2sip` implement — already exists
in `GatewayService._handleIncomingGsmCall()`, gated by
`GatewayConfig.routeGsmToSip`/`.autoAnswer`, producing `CallRouting`
events on the already-public `routingStream`/`activeRoutings`. AC1's
Gateway screen is a pure visualization task over existing public API, not
a `sdd-flutter_gsmsip-lib` dependency.

## User Stories

### Primary

**As a** developer evaluating `flutter_gsmsip` as a gateway product
**I want** the example to demonstrate the same "gateway mode" that
`react-native-gsm-sip-gateway` and `gsm2sip` implement — auto-bridge an
inbound GSM call to a SIP leg, and dial outbound over GSM on a SIP
request — with a device/profile-aware config screen
**So that** I can evaluate `flutter_gsmsip` for the actual product it's
meant to replace, not just a manual test-call/test-SMS toy.

**As** Anton
**I want** a definitive, written answer to "are the required Android SDK
permissions declared inside the libraries, or only in the example app?"
**So that** a real product built on these libraries doesn't ship broken
because a permission was only ever present in example boilerplate.

### Secondary

**As a** developer setting up a physical gateway phone
**I want** the example to show whether the device has the Magisk module
installed and which privileged capabilities are actually active (not
just "requested")
**So that** I know if I need to flash the Magisk module before the
gateway will work, consistent with `sdd-voiceline-mode-magisk-v2`'s
`LineInfo.canRecordVoiceToRadio`-style capability flags.

**As a** developer
**I want** the example to show current default-dialer status and a clear
path to fix it if not set
**So that** GSM call auto-answer/bridging (which requires being the
default phone app on gsm2sip's model) actually works, while the real
implementation work is tracked in `flutter_replace_dialer`/`flutter_dialer`
rather than bolted onto `flutter_gsmsip`.

**As a** designer/reviewer
**I want** the example restyled on the NativeMind design system (not its
current bespoke `theme/app_*.dart` files) with a proper branded splash
screen
**So that** it reads as a NativeMind product demo, consistent with
`simbox-app` and other Flutter apps in this repo.

## Acceptance Criteria

### Must Have

1. **Given** the example app, **when** reviewing its screen set, **then**
   there is a **Gateway** screen (new, or an evolution of Dashboard) that
   models the RN-gateway/gsm2sip concept explicitly: inbound-bridge state
   (GSM call → SIP leg), outbound-bridge state (SIP-initiated → GSM leg),
   and a visible **bridge/route indicator** (mirrors `vdd-dialer`'s
   already-approved "Bridge call status: SIP leg + GSM leg" visual
   language — reuse it, don't reinvent).
2. **Given** `gsm2sip`'s per-device config pattern (`DeviceInfo` →
   `tConfig`/`sConfig` profile), **when** designing the Setup screen,
   **then** it supports naming/saving more than one gateway profile —
   **gated on `sdd-flutter_gsmsip-lib`'s decision** on whether
   multi-profile storage lives in `flutter_gsmsip` itself or is
   example-local on top of its (also pending) public save/clear API.
   Do not build a parallel example-local workaround while that flow is
   open; wait for its Specifications, or explicitly re-scope this AC if
   blocked.
3. **Given** the Magisk-dependent capabilities this example wants to
   surface (originally scoped from `sdd-voiceline-mode-magisk-v2`'s
   §FR-6 `LineInfo` flags), **when** the user opens Settings or a new
   System/Capabilities screen, **then** each flag's current state is
   shown with an honest "not available — install the Magisk module"
   fallback when false — **reading whatever capability-reporting API
   `sdd-flutter_gsmsip-lib` decides on** (a `flutter_gsmsip`-owned
   proxy, or a direct `permission_handler` call if that flow concludes
   the library shouldn't own this). Don't design a third, competing
   capability check here.
4. **Given** `flutter_dialer` is already a transitive dependency,
   **when** the example checks default-dialer status, **then** it shows
   granted/not-granted plainly and — if not granted — explains the user
   must set it via Android Settings, without this flow adding new native
   dialer-replacement code to `flutter_gsmsip`. **Confirmed with Anton
   (2026-08-31)**: this is a warn, not a hard block on the UI — but the
   warning must state the real functional consequence precisely, not a
   generic "some features may not work": without default-dialer status,
   **incoming GSM calls cannot be auto-answered/bridged to SIP**
   (`GatewayService._handleIncomingGsmCall()`'s `InCallService` hook never
   fires), while everything else keeps working — outbound SIP→GSM
   dial-out, manual test calls/SMS, Logs, Settings. This must be
   **proactively surfaced to the user**, not just a passive status row the
   user has to notice: a persistent banner on the Gateway screen while
   unset, plus a one-time in-context alert the first time gateway mode is
   armed with default-dialer still unset (see 02-visual.md for the
   mockup).
5. **Given** the **Permission Audit** findings below, **when**
   Specifications are written, **then** they include a concrete
   permission-declaration fix plan scoped per package (which permissions
   move into which library's own `android/src/main/AndroidManifest.xml`
   vs. which stay documented as "consuming app must declare") — and file
   any fix outside `flutter_gsmsip/example` as a note for the owning
   library's own flow (`flows/flutter_gsm/`, etc.), not implemented here
   silently. `flutter_gsmsip`'s own half of this (documenting, in its
   `README.md`, the permission contract it can never enforce itself) is
   `sdd-flutter_gsmsip-lib`'s deliverable, not this flow's — this AC
   covers only the example's own manifest and cross-references.
6. **Given** `/nativemind-designsystem`, **when** the example is
   restyled, **then** it adopts the DS's neutral+semantic tokens with a
   single accent colorway — **confirmed with Anton (2026-08-31): Green**
   — replacing the bespoke `example/lib/theme/app_*.dart` files, and
   respects the DS's rules (one shadow, no scattered accent gradient,
   Lucide-style icons, no emoji in product copy). The existing
   purpose-built widgets (`signalIndicator`, `connectionIndicator`,
   `callStatusIndicator`, `statusCard`) are **re-skinned with DS tokens,
   not replaced** — confirmed with Anton, same date.
7. **Given** `/nativemind-flutter-splash`, **when** the example is
   restyled, **then** it gets the standard NativeMind splash treatment
   (native launch screen on Android — zero hand-written splash code
   per that skill's own rule — matching the `#F8F9FA`/`#0F1419`
   background + centered logo spec), replacing whatever default Flutter
   launch background currently ships.
8. **Given** all of the above, **when** this flow completes,
   **then** `libsFlutter/flutter_gsmsip/lib/**` remains untouched unless
   Specifications explicitly justify and flag an exception (same
   constraint `sdd-flutter_gsmsip-example` operated under) — this is a
   UI/UX flow for the example app, not a library-capability flow.

### Should Have

- Visual parity with `gsm2sip`'s dialer-style tab layout (Dialer / Calls /
  Settings) *reinterpreted* through the NativeMind DS, not copied
  pixel-for-pixel from its Material/XML screens.
- A "Getting Started as a Gateway" README section (this flow's eventual
  Documentation phase) walking through: install Magisk module → set
  default dialer → configure SIP profile → start gateway — cross-linking
  each step's owning flow.

### Won't Have (This Iteration)

- Any new Magisk module content or scripts (owned by `sdd-voiceline-
  mode-magisk*`).
- Any new default-dialer/`InCallService`/`ConnectionService` native code
  (owned by `flutter_replace_dialer` / `flutter_dialer`).
- Actual G.722/RTP audio bridging implementation (that's `flutter_nmsip`
  + `flutter_gsm` territory, already the subject of other SDD flows).
- Non-Android platforms for the *gateway-mode* screens specifically —
  the gateway concept (GSM leg) is inherently Android/Linux-modem only,
  per `sdd-flutter_gsmsip-example`'s already-documented capability table.

## Constraints

- **Technical**: must build on `GatewayService`, `SipRepositoryImpl`,
  `ModemRepositoryImpl`/`ModemRepository`, `SmsService` — the real public
  APIs already inventoried by `sdd-flutter_gsmsip-example`. No inventing
  methods that don't exist.
- **Scope boundary**: `libsFlutter/flutter_gsmsip/lib/**` stays untouched
  by default (see AC8).
- **Design**: NativeMind design system tokens + splash template are
  mandatory, not optional polish — use the live skills, not the pinned
  `_ds/` snapshot inside the splash skill.
- **Cross-flow discipline**: dialer-replacement and Magisk work gets
  filed/cross-referenced against `flutter_replace_dialer` and
  `sdd-voiceline-mode-magisk*` respectively — this flow may *read and
  link* those flows but must not fork their scope.
- **Platform**: Android is the primary target for every new gateway-mode
  screen (GSM leg requirement); Linux/macOS keep the existing honest
  "not supported here" messaging pattern already established.

## Permission Audit (answers Anton's direct questions)

**Q: "Can permissions live in the lib, or must they be in the example?"**
They **can and should** live in the plugin's own manifest for any normal/
dangerous-level permission — Gradle's manifest merger automatically
unions every `<uses-permission>` tag from every dependency's
`AndroidManifest.xml` into the final app manifest at build time; a
consuming app needs zero copy-pasting. `flutter_nmsip`, `flutter_smsussd`,
`flutter_tele`, and `flutter_dialer` already do this correctly (see
table). The one class of permission that genuinely can't be satisfied by
a manifest merge alone is signature/privileged-level
(`CALL_PRIVILEGED`, `MODIFY_PHONE_STATE`, `CAPTURE_AUDIO_OUTPUT`,
`READ_PRIVILEGED_PHONE_STATE`) — declaring these anywhere is necessary
but not sufficient; Android only honors them for apps installed as
system/priv-app, which is an OS-level allow-list mechanism (see next
question), orthogonal to Gradle merging.

**Q: "Should Magisk target the example or the lib?"**
Neither, precisely — **Magisk targets one specific installed app's
package name (`applicationId`)**, because there is no such thing as
"installing a library" on a device; only a compiled app gets installed.
`gsm2sip`'s module hardcodes `com.callagent.gateway`; the existing
`sdd-voiceline-mode-magisk-v2` spec hardcodes a *different* package,
`one.telefon.gateway`; `flutter_gsmsip/example`'s actual applicationId
today is **`org.telon.flutter_gsmsip_example`**. None of these match.
If this flow wants the example to show a real (not simulated) Magisk-
granted capability, `sdd-voiceline-mode-magisk-v2` needs a variant keyed
to `org.telon.flutter_gsmsip_example` — flagged as a cross-flow
dependency above, not assumed or built here.

**Q: "Is the needed stuff also factored into `flutter_tele` and
`flutter_smsussd`?"**
`flutter_tele`: yes, fully — see table, plus it registers real
components (`TeleService` as `InCallService`, `TeleBroadcastReceiver`),
not just permission strings. `flutter_smsussd`: permissions yes (5,
correctly scoped to what its one real class, `FlutterSmsussdPlugin.kt`,
needs), but `RECEIVE_MMS`/`RECEIVE_WAP_PUSH` — present only in the
example's manifest — have **no backing receiver anywhere in
`flutter_smsussd`'s source**. That's not a "move it to the lib" gap,
it's unbacked cruft in the example manifest; Specifications should
recommend deleting those two lines rather than relocating them, unless
MMS/WAP-push handling is an actual planned feature.

Full picture, read directly from each package's own
`android/src/main/AndroidManifest.xml` (not its example app) plus its
actual native source tree:

| Package | Own manifest declares permissions? | Native components registered? | Notes |
|---|---|---|---|
| `flutter_gsmsip` | **N/A — no `android/` folder at all** | N/A | Pure-Dart orchestrator by design (its `pubspec.yaml` comment confirms native android/linux platform code was intentionally removed). Can only inherit permissions transitively from `flutter_gsm`/`flutter_nmsip`/`flutter_dialer`. |
| `flutter_gsm` | **Empty manifest** (`<manifest package="org.telon.flutter_gsm"/>`, zero `<uses-permission>`) | **No** — `BootUpReceiver.kt` and `HeadlessService.kt` are real, compiled Kotlin classes with zero `<receiver>`/`<service>` manifest entries anywhere (checked the example's manifest too — not there either, despite a comment claiming boot auto-start). **Currently dead code.** Also owns a full duplicate dialer-replacement module, `ReplaceDialerModule.kt` (`isDefaultDialer`/`setDefaultDialer`/`canSetDefaultDialer`), separate from `flutter_dialer`'s — see cross-flow table above. | Biggest gap in the family: not just missing permissions, missing component wiring for code that already exists. Belongs to `flows/flutter_gsm/`. |
| `flutter_nmsip` | Declares 10 real permissions (INTERNET, RECORD_AUDIO, READ_PHONE_STATE, READ/WRITE_CALL_LOG, FOREGROUND_SERVICE, etc.) | Yes (`PjSipService`) | Correctly self-contained. |
| `flutter_smsussd` | Declares 5 (SEND/RECEIVE/READ/WRITE_SMS, READ_PHONE_STATE) | Only the plugin class itself; no SMS/MMS `BroadcastReceiver` | Correct for what exists; the example's extra `RECEIVE_MMS`/`RECEIVE_WAP_PUSH` are unbacked (see above). |
| `flutter_tele` | Declares 11 (telephony + `InCallService`) | Yes (`TeleService`, `TeleBroadcastReceiver`) | Correctly self-contained — the model to copy. |
| `flutter_dialer` | Declares 6 (`READ_PHONE_STATE`, `CALL_PHONE`, `READ_CALL_LOG`, `MODIFY_PHONE_STATE`, `ANSWER_PHONE_CALLS`, `MANAGE_OWN_CALLS`) | Yes (`MainActivity` DIAL/CALL/VIEW intent-filters, `TeleService` InCallService) | Correctly self-contained, but functionally overlaps `flutter_gsm`'s `ReplaceDialerModule` — resolve in `flutter_replace_dialer`. |

Additional permissions that exist **only** in `flutter_gsmsip/example`'s
manifest, with no owning library at all: `READ_CONTACTS`/
`WRITE_CONTACTS` (no contacts-lookup code exists in any plugin yet — a
candidate for wherever `vdd-dialer`'s already-approved contact
integration actually lands), `ACCESS_WIFI_STATE`/`CHANGE_WIFI_STATE`,
`READ_PHONE_NUMBERS`, `USE_SIP`, `FOREGROUND_SERVICE_DATA_SYNC`,
`SYSTEM_ALERT_WINDOW`, `RECEIVE_BOOT_COMPLETED` (permission present, but
see `flutter_gsm` row — the receiver it would gate isn't registered
anywhere), and `CALL_PRIVILEGED` (signature-level, meaningless without
the priv-app/Magisk path above).

**Implication for this flow**: fixing `flutter_gsm`'s empty manifest and
missing component registrations is correctness work on a *different*
package (belongs under `flows/flutter_gsm/`, referenced here, not fixed
here) — same for resolving the `ReplaceDialerModule` duplication
(`flutter_replace_dialer`) and re-targeting the Magisk module
(`sdd-voiceline-mode-magisk-v2`). What this flow *does* own:
Specifications should have the example's own manifest carry a comment
block mapping each permission to the package that *should* own it, and
the new Capabilities/System screen must present "declared vs. actually
grantable vs. actually wired up" honestly — three distinct states, not
two.

## Open Questions

- [x] **Resolved (2026-08-31)** — Which DS accent colorway: **Green**.
- [x] **Resolved (2026-08-31)** — Existing purpose-built widgets
      (`signalIndicator`, `connectionIndicator`, `callStatusIndicator`,
      `statusCard`, `theme/README.md`/`app_widgets.dart`): **re-skinned
      with DS tokens, not replaced**.
- [x] **Resolved (2026-08-31)** — Default Dialer card: **warn, not
      block**, but the warning must name the precise functional
      consequence (incoming-call auto-answer/bridging is dead; everything
      else still works) and be proactively surfaced, not passive. See
      updated AC4 above and 02-visual.md.
- [ ] Multi-profile config and the capability-model question are still
      owned by `sdd-flutter_gsmsip-lib`'s own Open Questions — tracked
      there, not duplicated here. This flow just waits on its answer.

## References

- `reactntive/react-native-gsm-sip-gateway/telon-gateway-app/src/Gateway.js` — bridge/profile pattern
- `3rdparty/gsm2sip/` (`README.md`, `app/src/main/java/com/callagent/gateway/**`, `magisk/`) — native successor + working Magisk module
- `flows/flutter_gsmsip/sdd-voiceline-mode-magisk/01-requirements.md`, `sdd-voiceline-mode-magisk-v2/01-requirements.md` + `02-specifications.md`
- `flows/flutter_gsmsip/sdd-flutter_gsmsip-lib/` — owns the library-code items split out of this flow (config save/clear API, multi-profile, capability model, permission-contract docs)
- `flows/flutter_replace_dialer/tdd-replace-dialer/` — legacy RN dialer-replacement tests, needs a Flutter-era successor for `flutter_dialer`
- `flows/flutter_gsmsip/sdd-flutter_gsmsip-example/` — prior flow that made the example genuinely functional (this flow builds on top, doesn't redo it)
- `flows/flutter_gsmsip/vdd-dialer/` — approved bridge/route visual language to reuse
- `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-voiceline-uiux/` — sibling UI/UX flow for the same example app, umbrella for TTY/Telecom/Enhanced-Mode/Dongle voice-line access; its "Enhanced Mode" screen overlaps this flow's System Capabilities panel (AC3) — coordinate before building either
- `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-zatychka-uiux/` — sibling UI/UX flow for dongle configuration, a dependency of voiceline-uiux
- `flows/flutter_gsmsip/sdd-gateway-answer-keyevent-magisk/`, `sdd-gateway-answer-itelephony-magisk/`, `sdd-gateway-answer-directmodem-magisk/` — parked (REQUIREMENTS-only, not to be implemented) documentation of non-standard ways to auto-answer a GSM call without default-dialer status; AC4's warn-only resolution stands regardless of these
- `~/.claude/skills/nativemind-designsystem/`, `~/.claude/skills/nativemind-flutter-splash/`

---

## Approval

- [x] Reviewed by: Anton
- [x] Approved on: 2026-08-31
- [x] Notes: 2026-08-31 — three Visual-phase Open Questions resolved:
      accent colorway = Green (AC6); existing purpose-built widgets
      re-skinned with DS tokens, not replaced (AC6); Default Dialer card
      warns rather than blocks, but must name the precise consequence
      (incoming-call auto-answer/bridging breaks; everything else keeps
      working) and be proactively surfaced to the user, not passive (AC4).
