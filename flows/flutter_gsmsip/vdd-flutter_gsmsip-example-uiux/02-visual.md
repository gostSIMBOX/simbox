# Visual Mockups: flutter_gsmsip-example-uiux

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-31
> Requirements: [01-requirements.md](01-requirements.md) (APPROVED)

## Overview

ASCII mockups for the "gateway product" screens this flow adds/evolves on
top of `libsFlutter/flutter_gsmsip/example`'s already-functional six
screens (Setup, Dashboard, Settings, Call, SMS, Logs). Grounded in the
real domain types already in `flutter_gsmsip/lib` — `CallRoutingState`
(`connecting`/`active`/`ended`/`failed`), `CallRoutingDirection`
(`sipToGsm`/`gsmToSip`), `GatewayConfig.autoAnswer`/`.routeGsmToSip` —
not invented state names.

**New/evolved screens (this doc):**
1. Gateway — AC1, replaces/extends Dashboard as the gateway-mode home
2. Setup (multi-profile) — AC2, evolution of the existing Setup screen
3. System Capabilities — AC3, new screen off Settings
4. Default Dialer status — AC4, a component embedded in Gateway + Settings

**Explicitly not re-mocked here** (see Notes at the end): DS restyle of
the existing 6 screens (layout doesn't change, only tokens — AC6) and the
splash screen (AC7, owned entirely by `/nativemind-flutter-splash`).

---

## Screen 1: Gateway (AC1 — new gateway-mode home)

Reuses `vdd-dialer`'s approved "Bridge Status" visual language
(`flows/flutter_gsmsip/vdd-dialer/02-visual.md`, "Bridge Call (SIP → GSM)"
section) rather than inventing new vocabulary for the SIP-leg/GSM-leg
pairing.

### Idle (gateway armed, no active routing)

```
+----------------------------------------------------------+
|  = GATEWAY                                         [≡]   |
+----------------------------------------------------------+
|                                                            |
|  Gateway Status                                            |
|  +------------------------------------------------------+ |
|  |  ● Armed        SIP: Registered   GSM: 4G (85%)      | |
|  |  Auto-answer: ON     Route GSM→SIP: ON                | |
|  +------------------------------------------------------+ |
|                                                            |
|  Active Routings (0)                                       |
|  +------------------------------------------------------+ |
|  |                                                        | |
|  |            No active bridge right now.                | |
|  |     Incoming GSM calls auto-bridge to SIP.             | |
|  |     SIP INVITE with forward header dials out GSM.      | |
|  |                                                        | |
|  +------------------------------------------------------+ |
|                                                            |
|  Profile: [Office Line ▼]              [Edit Profiles]    |
|                                                            |
|  ⚠ Default Dialer: Not Set                                |
|    Incoming GSM calls will NOT auto-answer/bridge          |
|    to SIP until this is set. Everything else works.        |
|                                        [Open Settings]     |
|                                                            |
+----------------------------------------------------------+
|  [Gateway] [Setup] [SMS] [Logs] [Settings]                |
+----------------------------------------------------------+
```

### Active — GSM → SIP bridge (inbound GSM auto-bridged out to SIP)

```
+----------------------------------------------------------+
|  = GATEWAY                                         [≡]   |
+----------------------------------------------------------+
|                                                            |
|  Gateway Status                                             |
|  +------------------------------------------------------+ |
|  |  ● Armed        SIP: Registered   GSM: 4G (85%)      | |
|  +------------------------------------------------------+ |
|                                                            |
|  Active Routings (1)                                        |
|  +------------------------------------------------------+ |
|  |  +7 (999) 123-45-67          GSM ──► Gateway ──► SIP  | |
|  |  ---------------------------------------------------  | |
|  |  GSM Leg:  ● connected                                | |
|  |  SIP Leg:  ● active            01:14                  | |
|  |  Bridge:   ● active                                   | |
|  |                                          [End Bridge]  | |
|  +------------------------------------------------------+ |
|                                                            |
|  Profile: [Office Line ▼]              [Edit Profiles]    |
+----------------------------------------------------------+
|  [Gateway] [Setup] [SMS] [Logs] [Settings]                |
+----------------------------------------------------------+
```

### Active — SIP → GSM bridge (SIP INVITE dials out over GSM)

```
+----------------------------------------------------------+
|  = GATEWAY                                         [≡]   |
+----------------------------------------------------------+
|                                                            |
|  Active Routings (1)                                        |
|  +------------------------------------------------------+ |
|  |  +7 (495) 987-65-43          SIP ──► Gateway ──► GSM  | |
|  |  ---------------------------------------------------  | |
|  |  SIP Leg:  ● active            00:42                  | |
|  |  GSM Leg:  ○ connecting...                            | |
|  |  Bridge:   ○ connecting                               | |
|  |                                          [End Bridge]  | |
|  +------------------------------------------------------+ |
|                                                            |
+----------------------------------------------------------+
```

### Routing failed

```
+------------------------------------------------------+
|  +7 (495) 987-65-43          SIP ──► Gateway ──► GSM  |
|  ---------------------------------------------------  |
|  SIP Leg:  ● active            00:03                  |
|  GSM Leg:  ✕ failed — no signal                       |
|  Bridge:   ✕ failed                                   |
|                                            [Dismiss]   |
+------------------------------------------------------+
```

### Loading (gateway starting up)

```
+----------------------------------------------------------+
|  = GATEWAY                                         [≡]   |
+----------------------------------------------------------+
|  Starting gateway...                                       |
|  [======>              ]                                   |
+----------------------------------------------------------+
```

### Empty / disarmed (gateway mode off)

```
+----------------------------------------------------------+
|  = GATEWAY                                         [≡]   |
+----------------------------------------------------------+
|                                                            |
|                    (gateway icon, dim)                     |
|              Gateway mode is off.                          |
|          Calls are handled manually, as before.            |
|                                                            |
|                  [Turn On Gateway Mode]                    |
|                                                            |
+----------------------------------------------------------+
```

---

## Screen 2: Setup — Multi-Profile (AC2)

**Depends on `sdd-flutter_gsmsip-lib`'s decision** on where profile
storage lives — this mockup shows the UI shape only; wiring is deferred
in Specifications until that flow reaches its own Specifications.

### Profile List (evolution of current Setup screen)

```
+----------------------------------------------------------+
|  [<] SETUP                                        [+]    |
+----------------------------------------------------------+
|                                                            |
|  Gateway Profiles                                           |
|  +------------------------------------------------------+ |
|  |  ● Office Line              (active)        [Edit]    | |
|  |    SIP: sip:office@pbx.example.com                    | |
|  +------------------------------------------------------+ |
|  |  ○ Warehouse Line                            [Edit]    | |
|  |    SIP: sip:wh1@pbx.example.com                       | |
|  +------------------------------------------------------+ |
|  |  ○ Backup Line                               [Edit]    | |
|  |    SIP: sip:backup@pbx.example.com                    | |
|  +------------------------------------------------------+ |
|                                                            |
|                    [+ Add New Profile]                     |
|                                                            |
+----------------------------------------------------------+
```

### Add/Edit Profile

```
+----------------------------------------------------------+
|  [<] Edit Profile: Office Line                    [✕]    |
+----------------------------------------------------------+
|                                                            |
|  Profile Name: [Office Line________________]              |
|                                                            |
|  SIP Account                                                |
|  Username:  [office_____________]                          |
|  Domain:    [pbx.example.com____]                          |
|  Password:  [••••••••••________]                           |
|                                                            |
|  Gateway Behavior                                            |
|  [✓] Auto-answer incoming GSM calls                        |
|  [✓] Route GSM → SIP automatically                         |
|  [ ] Allow SIP → GSM outbound dial-out                      |
|                                                            |
|              [Delete Profile]        [Save]                 |
|                                                            |
+----------------------------------------------------------+
```

### Empty state (no profiles yet)

```
+----------------------------------------------------------+
|  [<] SETUP                                        [+]    |
+----------------------------------------------------------+
|                                                            |
|              No gateway profiles yet.                       |
|         Add one to start bridging calls.                    |
|                                                            |
|                 [+ Add New Profile]                          |
|                                                            |
+----------------------------------------------------------+
```

### Error state (save failed)

```
+----------------------------------------------------------+
|  [<] Edit Profile: Office Line                    [✕]    |
+----------------------------------------------------------+
|  ! Could not save profile.                                  |
|    SIP domain is required.                                  |
|                                                            |
|  ... (form fields, invalid field highlighted) ...           |
|                                                            |
|                              [Retry]  [Cancel]               |
+----------------------------------------------------------+
```

---

## Screen 3: System Capabilities (AC3 — new, off Settings)

Presents the **three distinct states** the requirements insist on
(01-requirements.md §Permission Audit implication): declared vs.
actually grantable vs. actually wired up. Reads whatever capability API
`sdd-flutter_gsmsip-lib` settles on — this mockup doesn't assume its
shape beyond a flag name + tri-state.

**Coordinate with `vdd-flutter_gsmsip-example-voiceline-uiux`'s "Enhanced
Mode" screen before implementing** — flagged in 01-requirements.md as an
overlap risk, not resolved here.

### Magisk module installed, capabilities granted

```
+----------------------------------------------------------+
|  [<] SYSTEM CAPABILITIES                                  |
+----------------------------------------------------------+
|                                                            |
|  Magisk Module                                               |
|  +------------------------------------------------------+ |
|  |  ● Installed for org.telon.flutter_gsmsip_example      | |
|  +------------------------------------------------------+ |
|                                                            |
|  Capabilities                                                |
|  +------------------------------------------------------+ |
|  |  Capture Audio Output                                  | |
|  |    Declared: ✓   Grantable: ✓   Wired up: ✓            | |
|  |  ---------------------------------------------------   | |
|  |  Disable Audio-Concurrency Lock                        | |
|  |    Declared: ✓   Grantable: ✓   Wired up: ✓            | |
|  |  ---------------------------------------------------   | |
|  |  Priv-App Permission Grants                             | |
|  |    Declared: ✓   Grantable: ✓   Wired up: ✓            | |
|  +------------------------------------------------------+ |
|                                                            |
+----------------------------------------------------------+
```

### Magisk not installed (honest fallback, required by AC3)

```
+----------------------------------------------------------+
|  [<] SYSTEM CAPABILITIES                                   |
+----------------------------------------------------------+
|                                                            |
|  Magisk Module                                               |
|  +------------------------------------------------------+ |
|  |  ○ Not installed                                        | |
|  |    Some capabilities are unavailable until the          | |
|  |    Magisk module is installed for this app.             | |
|  |                              [How to Install]           | |
|  +------------------------------------------------------+ |
|                                                            |
|  Capabilities                                                |
|  +------------------------------------------------------+ |
|  |  Capture Audio Output                                   | |
|  |    Declared: ✓   Grantable: ✕   Wired up: —             | |
|  |    ⓘ not available — install the Magisk module          | |
|  |  ---------------------------------------------------    | |
|  |  Disable Audio-Concurrency Lock                          | |
|  |    Declared: ✓   Grantable: ✕   Wired up: —             | |
|  |    ⓘ not available — install the Magisk module          | |
|  +------------------------------------------------------+ |
|                                                            |
+----------------------------------------------------------+
```

### Declared-but-not-wired (documents a real gap honestly, per Permission Audit)

```
+------------------------------------------------------+
|  Boot Auto-Start (RECEIVE_BOOT_COMPLETED)             |
|    Declared: ✓   Grantable: ✓   Wired up: ✕           |
|    ⓘ permission present, but no receiver registered   |
|      in any package yet — tracked in flows/flutter_gsm/|
+------------------------------------------------------+
```

### Loading

```
+----------------------------------------------------------+
|  [<] SYSTEM CAPABILITIES                                   |
+----------------------------------------------------------+
|  Checking capabilities...                                    |
|  [========>          ]                                       |
+----------------------------------------------------------+
```

---

## Component: Default Dialer Status Card (AC4)

Embedded in the Gateway screen (below Gateway Status) and in Settings.
Reads whichever module `flutter_replace_dialer` designates as canonical
— no new dialer logic here, this is a read-only status + link-out.

**Confirmed with Anton (2026-08-31): warn, don't block.** But the warning
must say exactly what breaks — **incoming GSM calls can't be
auto-answered/bridged to SIP** — not a vague "some features unavailable".
Everything else (outbound SIP→GSM dial-out, manual calls/SMS, Logs,
Settings) keeps working, and the copy must say so too, so the user isn't
left guessing what's actually broken.

### Not set (persistent warning card — precise consequence, not generic)

```
+------------------------------------------------------+
|  ⚠ Default Dialer: Not Set                            |
|    Incoming GSM calls will NOT auto-answer/bridge       |
|    to SIP until this is set. Everything else            |
|    (outbound calls, SMS, logs) still works.              |
|                                        [Open Settings]  |
+------------------------------------------------------+
```

### Set (confirmed)

```
+------------------------------------------------------+
|  ✓ Default Dialer: Set                                |
+------------------------------------------------------+
```

### Proactive alert — first time gateway mode is armed while still unset

Not just a passive card the user might not notice: the app interrupts
once, the first time gateway mode is turned on with default-dialer still
unset, so the gap is impossible to miss.

```
+----------------------------------------------------------+
|                                                            |
|                    ⚠                                       |
|                                                            |
|         Gateway armed, but incoming calls                  |
|         won't bridge yet.                                   |
|                                                            |
|    This app isn't the default dialer. Incoming GSM         |
|    calls will ring normally but won't auto-answer          |
|    or bridge to SIP.                                        |
|                                                            |
|    Outbound calls, SMS, and logs are unaffected.            |
|                                                            |
|         [Set Default Dialer]      [Continue Anyway]        |
|                                                            |
+----------------------------------------------------------+
```

- Dismissing via "Continue Anyway" keeps the persistent card visible on
  Gateway/Settings (above) — it does not suppress it permanently.
- Re-fires once per app-restart if still unset, not on every screen visit
  (avoid alert fatigue) — exact re-fire policy is a Specifications
  decision, not fixed here.

---

## Flow: Gateway-mode Navigation

```
                    ┌──────────────┐
                    │   Gateway    │  (new home; was Dashboard)
                    │   (Home)     │
                    └──────┬───────┘
             ┌─────────────┼─────────────┬───────────────┐
             │             │             │               │
             ▼             ▼             ▼               ▼
      ┌─────────────┐┌───────────┐┌───────────┐  ┌──────────────┐
      │Setup (multi-││    SMS    ││   Logs    │  │   Settings   │
      │  profile)   │└───────────┘└───────────┘  └──────┬───────┘
      └─────────────┘                                    │
                                                           ▼
                                                  ┌──────────────────┐
                                                  │System Capabilities│
                                                  └──────────────────┘
```

## Flow: Inbound Gateway Bridge (GSM → SIP)

```
[Incoming GSM call] ──(autoAnswer=true)──> [Auto-answer]
                                                  │
                                                  ▼
                                       [GatewayService bridges to SIP]
                                                  │
                                                  ▼
                                  [Gateway screen: Active Routing card]
                                        (state: connecting → active)
                                                  │
                                          ┌───────┴───────┐
                                          ▼               ▼
                                     [ended]          [failed]
```

## Flow: Outbound Gateway Bridge (SIP → GSM)

```
[SIP INVITE w/ forward header] ──> [GatewayService dials out GSM]
                                              │
                                              ▼
                            [Gateway screen: Active Routing card]
                                  (direction: sipToGsm)
```

---

## Symbol Legend

| Symbol | Meaning |
|--------|---------|
| `=` | Header/Title |
| `●` | Active/connected/on (state-neutral, DS supplies color) |
| `○` | Connecting/inactive/off |
| `✕` | Failed/denied |
| `✓` | Yes/granted/set |
| `—` | Not applicable |
| `⚠` | Warning |
| `ⓘ` | Informational explanation |
| `[ ]` | Button/Input |
| `[✓]` | Checkbox (checked) |
| `▼` | Dropdown |
| `~►` / `──►` | Route/flow direction |

Note: this mockup avoids emoji (🟢📞📱 etc., used freely in `vdd-dialer`'s
older mockups) in favor of DS-neutral glyphs — matches AC6's "no emoji in
product copy" rule up front rather than fixing it at Specifications time.

---

## Notes

### DS restyle of the existing 6 screens (AC6) — not re-mocked here

Setup, Dashboard→Gateway (see above), Settings, Call, SMS, and Logs keep
their current information layout (already validated functional by
`sdd-flutter_gsmsip-example`); AC6 is a token swap — bespoke
`theme/app_*.dart` → `/nativemind-designsystem` tokens — not a layout
redesign. Re-drawing all 6 in ASCII would show identical boxes with a
different paint job, which isn't what ASCII mockups are for. Specifications
should instead list, per existing purpose-built widget
(`signalIndicator`, `connectionIndicator`, `callStatusIndicator`,
`statusCard` — see Open Questions below), whether it's re-skinned with DS
tokens or replaced by a DS-native equivalent.

### Splash screen (AC7) — not mocked here

Owned entirely by `/nativemind-flutter-splash`, which stipulates
zero hand-written splash code and a fixed `#F8F9FA`/`#0F1419` + centered
logo spec. Nothing to align on visually beyond confirming the logo file
exists for this example app — Specifications should just point at that
skill's install steps.

### Open Questions — resolved (2026-08-31)

- **Accent colorway: Green.** Mockups above are drawn colorway-agnostic
  (`●`/`○`/`✕` carry no color); Specifications should map these to the
  DS's Green semantic + neutral tokens.
- **Existing purpose-built widgets** (`signalIndicator`,
  `connectionIndicator`, `callStatusIndicator`, `statusCard`):
  **re-skinned with DS tokens, not replaced.** AC6 is a token-only change
  for these — Specifications should list each widget's current color/
  shadow values and their DS-token replacements, not redesign them.
- **Default Dialer card: warn, not block** — but the warning must state
  the precise consequence (incoming-call auto-answer/bridging breaks,
  nothing else does) and be proactively surfaced, not just a passive
  status row. See the updated Default Dialer component above (persistent
  card + one-time arm-time alert).
- **Why this is the real constraint, for anyone revisiting this later**:
  the call always physically rings — Android's Telecom framework does
  that regardless of default-dialer status. What default-dialer status
  gates is *programmatic* auto-answer + audio interception via
  `InCallService`/`ConnectionService`, which only the default dialer may
  invoke. Three non-standard ways around that limitation exist (root/
  Magisk input-injection, priv-app hidden `ITelephony` API — same
  mechanism `gsm2sip`'s Magisk module already uses — and direct modem AT
  commands) and are documented as their own **parked, not implemented**
  flows: `flows/flutter_gsmsip/sdd-gateway-answer-keyevent-magisk/`,
  `sdd-gateway-answer-itelephony-magisk/`,
  `sdd-gateway-answer-directmodem-magisk/`. This flow's warn-only
  resolution for AC4 stands regardless of whether those are ever picked
  up.

---

## Approval

- [x] Reviewed by: Anton
- [x] Approved on: 2026-08-31
- [x] Notes: Green accent, re-skin existing widgets, Default Dialer
      warns-with-precise-consequence — all confirmed. Separately, Anton
      clarified the underlying Android constraint behind the Default
      Dialer warning (default-dialer status gates programmatic
      auto-answer via `InCallService`, not physical ringing) and asked
      for the three non-standard bypass methods to be parked as their own
      flows rather than folded into this one — see
      `flows/flutter_gsmsip/sdd-gateway-answer-keyevent-magisk/`,
      `sdd-gateway-answer-itelephony-magisk/`,
      `sdd-gateway-answer-directmodem-magisk/` (all REQUIREMENTS-only,
      explicitly not to be implemented without further instruction).

---

*Created by /vdd - flutter_gsmsip-example-uiux visual mockups*
