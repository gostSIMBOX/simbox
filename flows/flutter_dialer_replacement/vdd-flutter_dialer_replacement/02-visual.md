# Visual Mockups: flutter_dialer (example app)

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-31

## Overview

ASCII mockups for the `flutter_dialer_replacement/example` app — the demo
app that exercises the library's public API. Scope locked by
`01-requirements.md` (approved 2026-08-31): default-dialer role
management, dial pad, incoming call, active call, and call log. No
GSM/SIP/gateway screens or language anywhere. Caller-ID is
`READ_CONTACTS` display-only, no contact management.

The Status/Setup screen mockup below reflects `example/lib/main.dart` as
it exists today (two status cards + conditional "Set as Default Dialer"
button) — refined with the loading/unsupported-OS states the current
code doesn't yet distinguish. The other four screens are new; the
current example app has no dial pad, call, or call-log UI at all.

---

## Screen: Default Dialer Status & Setup

Home screen. Shows current role status and lets the user request the
role change. Matches the existing `example/lib/main.dart` structure.

```
+--------------------------------------------------+
|  = Flutter Dialer Example                    [R] |
+--------------------------------------------------+
|                                                  |
|  +--------------------------------------------+  |
|  |              (o)  <- phone icon             |  |
|  |         Default Dialer Status               |  |
|  |    This app is NOT the default dialer       |  |
|  +--------------------------------------------+  |
|                                                  |
|  +--------------------------------------------+  |
|  |              (x)  <- block icon             |  |
|  |         Can Set as Default                  |  |
|  |    This app can be set as default dialer    |  |
|  +--------------------------------------------+  |
|                                                  |
|                                                  |
|  [        Set as Default Dialer          ]       |
|                                                  |
|  * Setting as default dialer opens the system    |
|    settings dialog.                              |
+--------------------------------------------------+
```

`[R]` = refresh icon button (re-runs `isDefaultDialer()` +
`canSetDefaultDialer()`).

### States

#### Loading

```
+--------------------------------------------------+
|  = Flutter Dialer Example                    [R] |
+--------------------------------------------------+
|                                                  |
|                                                  |
|                    ( ~ )   <- spinner            |
|                                                  |
|                                                  |
+--------------------------------------------------+
```

#### Is Default (role already held)

```
+--------------------------------------------------+
|  = Flutter Dialer Example                    [R] |
+--------------------------------------------------+
|  +--------------------------------------------+  |
|  |              (v)  <- green check            |  |
|  |         Default Dialer Status               |  |
|  |      This app IS the default dialer         |  |
|  +--------------------------------------------+  |
|                                                  |
|  +--------------------------------------------+  |
|  |              (v)                            |  |
|  |         Can Set as Default                  |  |
|  |    This app can be set as default dialer    |  |
|  +--------------------------------------------+  |
|                                                  |
|  [ Go to Dial Pad ]   [ Go to Call Log ]         |
+--------------------------------------------------+
```

Note: nav buttons to Dial Pad / Call Log only appear once the app
actually holds the role — `InCallService`/dialing only make sense then.

#### Cannot Set (unsupported OS / restricted device)

```
+--------------------------------------------------+
|  = Flutter Dialer Example                    [R] |
+--------------------------------------------------+
|  +--------------------------------------------+  |
|  |              (x)                            |  |
|  |         Default Dialer Status               |  |
|  |    This app is NOT the default dialer       |  |
|  +--------------------------------------------+  |
|                                                  |
|  +--------------------------------------------+  |
|  |              (x)  <- grey block icon        |  |
|  |         Can Set as Default                  |  |
|  |  This app CANNOT be set as default dialer   |  |
|  |  (requires Android 6.0 / API 23+)           |  |
|  +--------------------------------------------+  |
|                                                  |
|  ~ "Set as Default Dialer" hidden when canSet    |
|    is false, per existing example logic.         |
+--------------------------------------------------+
```

#### Error (setDefaultDialer failed / threw)

```
+--------------------------------------------------+
|  = Flutter Dialer Example                    [R] |
+--------------------------------------------------+
|  ...(status cards as before)...                  |
|                                                  |
|  [        Set as Default Dialer          ]       |
+--------------------------------------------------+
|  ! Failed to set default dialor. [SnackBar,      |
|    red background, auto-dismiss]                 |
+--------------------------------------------------+
```

---

## Screen: Dial Pad

New screen, reached only once the app holds the default-dialer role.
Standard 12-key phone dial pad + call button. No contact
autocomplete/search — that's contact-management territory, out of
scope.

```
+--------------------------------------------------+
|  < Dial Pad                                      |
+--------------------------------------------------+
|                                                  |
|              +12025550123_                       |
|                                                  |
|  +------+  +------+  +------+                    |
|  |  1   |  |  2   |  |  3   |                    |
|  |      |  | abc  |  | def  |                    |
|  +------+  +------+  +------+                    |
|  +------+  +------+  +------+                    |
|  |  4   |  |  5   |  |  6   |                    |
|  | ghi  |  | jkl  |  | mno  |                    |
|  +------+  +------+  +------+                    |
|  +------+  +------+  +------+                    |
|  |  7   |  |  8   |  |  9   |                    |
|  | pqrs |  | tuv  |  | wxyz |                    |
|  +------+  +------+  +------+                    |
|  +------+  +------+  +------+                    |
|  |  *   |  |  0   |  |  #   |                    |
|  |      |  |  +   |  |      |                    |
|  +------+  +------+  +------+                    |
|                                                  |
|           [<-]        ((O))       <- call button |
|         backspace                                |
+--------------------------------------------------+
```

### States

#### Empty (no digits entered)

Call button `((O))` disabled/greyed; backspace `[<-]` hidden.

#### Dialing (call initiated, awaiting connection)

```
+--------------------------------------------------+
|  < Dial Pad                                      |
+--------------------------------------------------+
|                                                  |
|                  (~) Calling...                  |
|              +1 202-555-0123                     |
|                                                  |
|                  [ End Call ]                    |
+--------------------------------------------------+
```

Transitions to the Active Call screen once `InCallService` (via
`flutter_tele`) reports the call as connected.

---

## Screen: Incoming Call

Full-screen takeover, shown when `flutter_tele`'s `InCallService`
reports a new incoming call and `flutter_dialer` holds the
default-dialer role. Caller-ID name shown when a `READ_CONTACTS` match
exists; falls back to raw number otherwise.

```
+--------------------------------------------------+
|                                                  |
|                                                  |
|                    ( o )  <- avatar/icon         |
|                                                  |
|                 Jane Appleseed        <- caller-ID match
|              +1 202-555-0123                     |
|                                                  |
|                Incoming call...                  |
|                                                  |
|                                                  |
|                                                  |
|     [ (X) Decline ]        [ (O) Answer ]        |
|                                                  |
+--------------------------------------------------+
```

#### No Caller-ID Match

```
|                    ( o )                         |
|              +1 202-555-0123          <- number only, no name row
|                Incoming call...                  |
```

#### Unknown/Blocked Number

```
|                    ( ? )                         |
|                Unknown Number                    |
|                Incoming call...                  |
```

---

## Screen: Active Call

Shown once the incoming call is answered, or an outgoing call from the
Dial Pad connects.

```
+--------------------------------------------------+
|                                                  |
|                 Jane Appleseed                   |
|              +1 202-555-0123                     |
|                   00:42                <- duration, ticking
|                                                  |
|                                                  |
|   [ (mute) ]   [ (speaker) ]   [ (keypad) ]      |
|                                                  |
|                                                  |
|                 (( (X) End Call ))                |
|                                                  |
+--------------------------------------------------+
```

`[ (keypad) ]` reveals the dial pad grid inline (DTMF tones) without
navigating away — standard phone-app behavior, still within "replace
the dialer" scope since it's part of handling the call itself.

#### Call Ended

```
+--------------------------------------------------+
|                                                  |
|                 Jane Appleseed                   |
|              +1 202-555-0123                     |
|              Call ended - 00:47                  |
|                                                  |
+--------------------------------------------------+
```

Auto-dismisses back to Status or Call Log after a brief delay.

---

## Screen: Call Log

Recent calls list, in scope for v1 per approved requirements
(AC2a). Caller-ID applied the same way as Incoming Call.

```
+--------------------------------------------------+
|  = Call Log                          [Dial Pad]  |
+--------------------------------------------------+
|  Jane Appleseed              (in)   9:41 AM      |
|  +1 202-555-0123                                 |
|  ------------------------------------------------ |
|  +1 415-555-0199              (out)  Yesterday   |
|  (Unknown Number)                                |
|  ------------------------------------------------ |
|  John Smith                  (miss) Yesterday    |
|  +1 650-555-0177                                 |
|  ------------------------------------------------ |
+--------------------------------------------------+
```

`(in)` / `(out)` / `(miss)` = call direction/outcome icon. Tapping an
entry re-dials that number via the Dial Pad's call flow (no separate
"call details" screen needed for v1).

### States

#### Empty

```
+--------------------------------------------------+
|  = Call Log                          [Dial Pad]  |
+--------------------------------------------------+
|                                                  |
|                    (o)                           |
|              No calls yet                        |
|                                                  |
+--------------------------------------------------+
```

#### Loading

```
+--------------------------------------------------+
|  = Call Log                          [Dial Pad]  |
+--------------------------------------------------+
|                    ( ~ )                         |
|              Loading call log...                 |
+--------------------------------------------------+
```

#### Error (e.g. `READ_CALL_LOG` permission denied)

```
+--------------------------------------------------+
|  = Call Log                          [Dial Pad]  |
+--------------------------------------------------+
|  ! Call log permission not granted.              |
|  [ Grant Permission ]                            |
+--------------------------------------------------+
```

---

## Symbol Legend

| Symbol | Meaning |
|--------|---------|
| `=` | Header/Title |
| `<` | Back navigation |
| `[R]` | Icon button (refresh) |
| `( )` | Icon (status, avatar, spinner) |
| `(o)` `(v)` `(x)` `(?)` | neutral / success / fail-or-block / unknown icon state |
| `[ ]` | Button |
| `((O))` | Primary/destructive round action button (call, end call) |
| `*` | Helper/note text |
| `~` | Loading/scrollable indicator |
| `!` | Error/warning |

---

## Flow: Navigation

```
                 +-------------------+
                 |  Status & Setup   |<--------------------------+
                 +-------------------+                            |
                   |  (role held)                                 |
                   v                                               |
        +-----------------+        +----------------+              |
        |   Dial Pad      |------->|  Active Call   |              |
        +-----------------+ dial   +----------------+              |
                   ^                     |     ^                   |
       tap entry   |                     |     |                   |
                   |               call ends    |                   |
        +-----------------+                |    |                   |
        |   Call Log      |<---------------+    |                   |
        +-----------------+                     |                   |
                                                  |                   |
        +-----------------+   answer      +----------------+         |
        | Incoming Call   |-------------->| Active Call    |---------+
        +-----------------+   decline --------------------------------+
                (system-level trigger from flutter_tele's InCallService,
                 not a user-initiated nav action)
```

### Step-by-Step

1. **Status & Setup**: user opens the app. Sees whether it holds the
   default-dialer role.
   - Action: taps "Set as Default Dialer" (only visible if `canSet`)
   - Result: system dialog appears (native, outside app UI); on return,
     status re-checked via the now-fixed `setDefaultDialer()` callback.
   - Once role is held: "Go to Dial Pad" / "Go to Call Log" become
     visible.

2. **Dial Pad**: user enters a number, taps call.
   - Result: transitions to a brief "Calling..." state, then Active
     Call once `flutter_tele` reports connection.

3. **Incoming Call**: triggered externally (not by user nav) when
   `flutter_tele`'s `InCallService` reports a new call while this app
   holds the role.
   - Action: Answer -> Active Call. Decline -> back to whatever screen
     was active before (or Status & Setup if app was backgrounded).

4. **Active Call**: shows caller info + duration + call controls.
   - Action: End Call -> brief "Call ended" state -> Call Log.

5. **Call Log**: list of past calls, newest first.
   - Action: tap an entry -> pre-fills Dial Pad with that number.
   - Action: tap "[Dial Pad]" in header -> empty Dial Pad.

---

## Component: Call List Item

Reusable row for the Call Log screen.

```
+--------------------------------------------------+
|  <Name or Number>          <dir icon>  <time>    |
|  <secondary line: number, if name shown above>   |
+--------------------------------------------------+
```

## Component: Dial Pad Grid

Reusable 4x3 digit grid, used both full-screen (Dial Pad screen) and
inline (Active Call's DTMF keypad toggle) — same component, different
host context.

---

## Notes

- All five screens stay within the approved scope: role management,
  dialing, receiving/handling calls, and a call log. No GSM/SIP/gateway
  concept appears anywhere, per the hard mandate in Requirements.
- Active Call / Incoming Call / Dial Pad screens are **new** to the
  example app — today's `main.dart` only has Status & Setup. Their
  actual call-state data (ringing, connected, ended, duration) comes
  from `flutter_tele`'s `InCallService` per the AC2 decision that
  `flutter_tele` is canonical for call-state; `flutter_dialer`'s job in
  Specifications will be defining how the example subscribes to that
  data without `flutter_dialer` itself depending on `flutter_tele`'s
  package (a plugin can't depend sideways on another plugin for this —
  Specifications must resolve the actual wiring, e.g. the *example app*
  depends on both packages independently, while the *library* stays a
  leaf with zero dependency, consistent with Constraint in Requirements).
- Caller-ID and call-log entries are display-only; no "add contact" /
  "block number" / edit actions anywhere, per Won't-Have.
- Dial Pad's inline DTMF toggle during an Active Call reuses the same
  grid component rather than introducing a second dial-pad design.

---

## Approval

- [x] Reviewed by: Anton
- [x] Approved on: 2026-08-31
- [x] Notes: Approved as drafted, no changes requested.
