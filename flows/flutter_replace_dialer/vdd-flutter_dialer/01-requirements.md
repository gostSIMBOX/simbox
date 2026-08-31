# Requirements: flutter_dialer

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-31

## Problem Statement

`flutter_dialer` exists to make a Flutter app eligible to become Android's
**default phone app** (the "default dialer" role via `TelecomManager`).
Reading its actual current code (not assuming from docs) surfaces real
bugs and, more importantly, scope confusion — dialer-adjacent behavior
has leaked into two other packages, and this package's own three
"specs" disagree with each other:

### Real bugs found in the current implementation

- **`setDefaultDialer()` always reports success, regardless of what the
  user actually chose.** `FlutterDialerPlugin.kt` fires
  `Intent(ACTION_CHANGE_DEFAULT_DIALER)` via plain `context.startActivity()`
  and immediately calls `result.success(true)` — it never waits for the
  system dialog's actual result. A `RC_DEFAULT_PHONE = 3289` constant is
  declared but **never used**. This is exactly the "GAP-010: callback
  timing" bug the legacy top-level `flows/flutter_replace_dialer/
  tdd-replace-dialer` doc describes as already fixed for the old
  React-Native module — it is **not fixed** in this Flutter/Kotlin
  rewrite.
- **The registered `InCallService` is disconnected from the plugin.**
  `TeleService.kt` (50 lines) is correctly declared in the manifest with
  the `android.telecom.InCallService` intent-filter, but nothing in
  `FlutterDialerPlugin.kt` talks to it — no `MethodChannel`/`EventChannel`
  bridges call events to Dart. Becoming the default dialer would
  "succeed" today with no actual call-handling UI behind it.
- **`MainActivity.onNewIntent()`'s `tel:`-scheme handler is a dead stub** —
  it logs the phone number and a comment says "You can handle the phone
  number here," then does nothing.

### Scope leakage into other packages

- **`flutter_gsm/android/.../ReplaceDialerModule.kt`** independently
  reimplements `isDefaultDialer`/`setDefaultDialer`/`canSetDefaultDialer`
  over its own channel (`flutter_gsm/replace_dialer`) — and, notably,
  **implements the `ActivityAware` + `addActivityResultListener` pattern
  correctly**, unlike this package's own copy. It's the better
  implementation, sitting in the wrong package.
- **`flutter_gsm/android/.../GatewayDialerModule.kt`** ("native module for
  dialer functionality" per its own doc comment, channel
  `flutter_gsm/dialer`) mixes gateway-flavored dialing concerns into the
  GSM package — unclear today whether any of it belongs in a dialer
  package at all.
- **`flutter_tele/android/.../TeleService.kt`** is a genuinely different,
  520-line `InCallService` (real call-state tracking, `AudioManager`/
  `PowerManager`/`TelephonyManager` integration) — same class name as
  `flutter_dialer`'s 50-line stub, same `InCallService` role, different
  package, no relationship declared between them.

### Three disconnected spec locations — corrected understanding

1. `libsFlutter/flutter_dialer/flows/sdd-android-plugin/` — this
   package's own embedded DRAFT spec (2026-03-04, from a `/legacy`
   pass). Closest to the real architecture but **documents the plugin as
   correct** — doesn't mention the callback-timing bug found above.
2. `flows/flutter_replace_dialer/tdd-replace-dialer/` (top-level,
   repo-root) — **correction from this flow's own earlier drafting**:
   this is not a stray/unrelated legacy artifact. Byte-for-byte
   identical (`diff` confirmed empty) to
   `reactntive/react-native-replace-dialer/flows/tdd-replace-dialer/` —
   it is a **direct copy of the porting source's own spec**, placed at
   the top level presumably as the reference this package was meant to
   be ported from. Treat it as ground truth for original intent, not as
   noise to ignore.
3. `flutter_gsm`'s undocumented duplicate (`ReplaceDialerModule.kt`,
   `GatewayDialerModule.kt`) — no spec at all, just code.

### Reference implementation: `reactntive/react-native-replace-dialer`

Per Anton's explicit direction, **`flutter_dialer`'s API interface must
match `react-native-replace-dialer`'s** — so its actual source (not the
docs describing it) was read directly:

- **`src/ReplaceDialer.js`** exposes exactly **two** methods:
  `isDefaultDialer(cb)` and `setDefaultDialer(cb)` — Node-style
  completion callbacks, each invoked with a single boolean. **There is
  no `canSetDefaultDialer` in the original interface** — that method
  exists only in the Flutter-era ports (`flutter_dialer`'s Dart API and
  `flutter_gsm`'s duplicate), not in the reference implementation.
- **`android/app/src/main/java/one/telefon/replacedialer/
  ReplaceDialerModule.java`** is the native counterpart. Reading it
  confirms the callback-timing bug found in `flutter_dialer` is a
  **literal bug-for-bug port** of a bug that already exists — and is
  already documented — in the original: `setDefaultDialer()` calls
  `startActivityForResult(intent, RC_DEFAULT_PHONE, ...)` then
  immediately `myCallback.invoke(true)`, with a **commented-out**
  `ActivityEventListener`/`onActivityResult()` implementation left in
  the source as evidence of an unfinished fix. `isDefaultDialer()`
  short-circuits to `true` below Android M (`SDK_INT < 23`) — that
  quirk is part of the interface and must be preserved, not silently
  dropped as legacy cruft.
- **`flows/adr-001-activity-result/context.md`** (in the reference repo)
  documents this exact bug and proposes the fix: implement
  `ActivityEventListener`, register it in the constructor, remove the
  immediate `invoke(true)`, and resolve the callback for real inside
  `onActivityResult()` for request code `RC_DEFAULT_PHONE = 3289`. This
  is precisely the pattern `flutter_gsm`'s `ReplaceDialerModule.kt`
  (`ActivityAware` + `addActivityResultListener`) already implements
  correctly — confirming that file is the RN ADR's fix, already ported
  to Kotlin, just sitting in the wrong package.
- **The reference README is stale**, same pattern already seen
  elsewhere in this session (`flutter_gsmsip/example`'s README): it
  documents a synchronous-looking `isDefault()`/`setDefault()` usage
  example that doesn't match the actual exported methods
  (`isDefaultDialer`/`setDefaultDialer`, callback-based). The `.js`
  source is ground truth, not the README.

### The mandate driving this flow

Anton's explicit direction, now twofold: (1) **`flutter_dialer`'s
functionality must be *only* replacing Android's standard dialer —
everything else is out of its scope**; (2) **its API interface must
match `react-native-replace-dialer`'s**. This flow locks both boundaries
down — visual/architectural scope, and interface fidelity to the
reference implementation — before any of the bugs above get fixed.

## User Stories

### Primary

**As a** developer integrating `flutter_dialer`
**I want** `setDefaultDialer()` to report the user's actual choice (not
always `true`)
**So that** my app can correctly detect whether it truly became the
default dialer before relying on `InCallService` calls arriving.

**As a** developer whose app has become the default dialer
**I want** `flutter_dialer`'s `InCallService` to actually surface
incoming/active/ended call events to Dart
**So that** becoming the default dialer isn't a dead end with no UI
behind it.

**As** Anton
**I want** a single, explicit scope boundary — "default-dialer role
replacement, nothing else" — enforced in this package
**So that** GSM/SIP/gateway-routing logic (like `GatewayDialerModule`)
never migrates back into `flutter_dialer`, and `flutter_dialer` never
grows a dependency on `flutter_gsmsip`/`flutter_gsm`/`flutter_nmsip`.

### Secondary

**As a** maintainer
**I want** the three existing dialer-replacement documents reconciled —
one canonical, the others explicitly marked superseded/historical
**So that** nobody edits the wrong one or re-derives an already-answered
question.

**As a** developer
**I want** to know whether `flutter_tele`'s or `flutter_dialer`'s
`TeleService` is the one that should actually run when the app is the
default dialer
**So that** there isn't a silent conflict between two `InCallService`
implementations doing the same job differently.

## Acceptance Criteria

### Must Have

1. **Given** the confirmed callback-timing bug, **when** Specifications
   are written, **then** they fix `setDefaultDialer()` to genuinely wait
   for `ACTION_CHANGE_DEFAULT_DIALER`'s result (via `ActivityAware` +
   `addActivityResultListener`, the pattern `flutter_gsm`'s
   `ReplaceDialerModule.kt` already implements correctly, matching
   `react-native-replace-dialer`'s own ADR-001-proposed fix) before
   resolving `true`/`false`.
1a. **Given** the mandate that the API interface must match
   `react-native-replace-dialer`, **when** Specifications are written,
   **then** `flutter_dialer`'s public Dart surface exposes methods
   semantically equivalent to the reference's exactly two methods —
   `isDefaultDialer()` and `setDefaultDialer()`, each resolving a single
   boolean (Dart's `Future<bool>` is the correct idiomatic translation
   of the reference's Node-style completion callback — not a literal
   callback-parameter port) — and preserves the reference's exact
   pre-Android-M short-circuit (`isDefaultDialer()` returns `true` below
   API 23 without querying `TelecomManager`).
1b. **Given** `canSetDefaultDialer()` exists in `flutter_dialer`'s
   current Dart API and in `flutter_gsm`'s duplicate, but **does not
   exist** in `react-native-replace-dialer`'s reference interface,
   **when** Specifications are written, **then** they decide explicitly:
   drop it for literal interface parity, or keep it as a documented
   Flutter-only superset addition beyond the ported interface. Don't
   silently keep it and call the result "matching" without saying so.
2. **Given** the disconnected `TeleService`, **when** Specifications are
   written, **then** they decide explicitly: does `flutter_dialer` own a
   real (if minimal) `InCallService` implementation that bridges call
   events to Dart, or does it delegate the actual call-state work to
   `flutter_tele`'s existing 520-line implementation and own only the
   default-dialer *role* (`isDefaultDialer`/`setDefaultDialer`/
   `canSetDefaultDialer` + the launcher/DIAL/CALL intent filters)? No
   silent middle ground — pick one and justify it.
3. **Given** `GatewayDialerModule.kt`'s gateway-flavored dialing logic
   currently lives in `flutter_gsm`, **when** this flow's Visual/Specs
   phases proceed, **then** no screen, method, or channel in
   `flutter_dialer` references GSM legs, SIP legs, gateways, call
   routing, or bridging in any form — this package doesn't know those
   concepts exist. (Resolving what happens to `GatewayDialerModule.kt`
   itself is `flutter_gsm`'s own future flow's job, not this one's — see
   References.)
4. **Given** `flutter_gsm`'s `ReplaceDialerModule.kt` duplicates this
   package's role-management (more correctly), **when** this flow
   implements, **then** `flutter_dialer` becomes the one true
   implementation of `isDefaultDialer`/`setDefaultDialer`/
   `canSetDefaultDialer`, informed by the correct pattern found in
   `flutter_gsm`'s copy — and a note is left in this flow's status for
   whoever opens `flutter_gsm`'s next flow to delete the duplicate there.
5. **Given** `MainActivity`'s dead `tel:`/`DIAL` intent stub, **when**
   Specifications are written, **then** they decide: wire it to a real
   Dart-facing channel (e.g., "app was launched to dial this number") or
   delete it outright — no permanent no-op left in place.
6. **Given** the three existing spec locations, **when** this flow's
   `_status.md` is written, **then** it explicitly marks
   `libsFlutter/flutter_dialer/flows/sdd-android-plugin/` as superseded
   by this flow for architecture/scope (kept for historical reference,
   not deleted) and confirms the top-level legacy `tdd-replace-dialer`
   doc covers a different (RN) codebase entirely and should not be
   confused with this one.
7. **Given** the "only a dialer replacement" mandate, **when** the Visual
   phase mockups are drawn, **then** they cover only: default-dialer
   status/setup screen, incoming-call screen, active-call screen, and a
   dial pad — no contacts management, no route/gateway selection, no
   SIP/GSM status of any kind anywhere in these mockups.
8. **Given** all of the above, **when** this flow completes, **then**
   `flutter_dialer`'s `pubspec.yaml` gains **no** dependency on
   `flutter_gsmsip`, `flutter_gsm`, `flutter_nmsip`, or `flutter_smsussd`
   — it must build and function as a standalone default-dialer plugin.

### Should Have

- A minimal call log / recent-calls view — Android users expect *some*
  call history from their phone app; without it, switching default
  dialer to this app is a functional regression for the user. Confirm
  scope in Visual phase rather than assuming it's in or out.
- Caller-ID lookup via `READ_CONTACTS` (**display only**, not contact
  management) for incoming calls — flagged, not assumed; decide in
  Specifications whether this crosses the "only a replacement" line or
  is table-stakes for a phone app.

### Won't Have (This Iteration)

- Any GSM-vs-SIP awareness, call routing/bridging, cost/route selection,
  or bridge-status UI — that is `flutter_gsmsip`'s `GatewayService` and
  the (separately scoped) gateway-mode work in
  `vdd-flutter_gsmsip-example-uiux`. Explicitly not here, per the
  mandate.
- Full contact management (create/edit/delete contacts).
- SMS/USSD (`flutter_smsussd`'s territory).
- `GatewayDialerModule`-style gateway-specific dialing — stays out,
  regardless of what happens to it in `flutter_gsm`.
- iOS support — `flutter_dialer`'s manifest/plugin are Android-only
  today (no default-dialer concept exists on iOS); out of scope unless
  Anton asks otherwise.

## Constraints

- **Technical**: must preserve the existing public Dart API surface
  (`FlutterDialer.isDefaultDialer()`, `.setDefaultDialer()`,
  `.canSetDefaultDialer()`) — fixing the callback-timing bug changes
  *behavior* (real result instead of always-`true`), not the method
  signatures. Flag this as a breaking behavioral change for any existing
  caller relying on the current always-`true` return.
- **Platform**: Android-only; the default-dialer role has no iOS
  equivalent.
- **Dependency direction**: `flutter_dialer` must remain a leaf package
  with **zero** dependency on the GSM/SIP/gateway stack
  (`flutter_gsmsip`/`flutter_gsm`/`flutter_nmsip`) — this is the
  technical enforcement of Anton's scope mandate, not just a docs
  statement.
- **Android platform requirement**: a default-dialer app is legally
  required by Android to provide a launcher activity with DIAL/CALL/
  VIEW(tel:) intent filters (already present) and a bound
  `InCallService` (already present as a stub) — these can't be scoped
  away even though they're "more than role management," because they
  *are* the role. AC2 decides how, not whether.

## Open Questions

- [ ] AC1b: drop `canSetDefaultDialer()` for literal parity with
      `react-native-replace-dialer`, or keep as a documented addition?
      Leaning toward keeping (it's non-breaking, useful, and the
      reference's absence of it looks more like an omission than a
      deliberate design choice) — confirm with Anton rather than assume.
- [ ] Should `flutter_dialer` also reproduce the reference's exact
      internal fragility (no null-check on
      `telecomManager.getDefaultDialerPackage()`, a latent NPE risk on
      some OEMs), or is "interface match" scoped to public method
      names/contracts/observable-behavior only, with internal
      defensive-coding improvements allowed? This flow's working
      assumption is the latter (public interface parity, not bug-for-bug
      internal parity) — flagged for explicit confirmation since the
      mandate could be read more strictly.
- [ ] Does `flutter_gsmsip`'s GSM auto-answer path
      (`_modemRepo.answerCall()`, likely AT-command/RIL-level) actually
      require the app to be the Android default dialer at all, or is
      that entirely independent of the `TelecomManager` role this
      package manages? Determines whether `flutter_dialer` is a hard
      dependency of the gateway story or an optional "also take over the
      phone app" feature.
- [ ] `flutter_tele` vs. `flutter_dialer` `TeleService` — which becomes
      canonical (AC2)? Needs Anton's call given both are real,
      independently-written implementations.
- [ ] Call-log/caller-ID scope (Should-Have items above) — in or out for
      v1? Confirm in Visual phase.

## References

- `libsFlutter/flutter_dialer/lib/flutter_dialer.dart`, `flutter_dialer_method_channel.dart` — current public Dart API
- `libsFlutter/flutter_dialer/android/src/main/kotlin/org/tele/flutter_dialer/{FlutterDialerPlugin.kt, MainActivity.kt, TeleService.kt}` — current native implementation, bugs found above
- `libsFlutter/flutter_dialer/flows/sdd-android-plugin/` — this package's own embedded DRAFT spec, superseded by this flow for scope/architecture (kept for reference)
- `flows/flutter_replace_dialer/tdd-replace-dialer/` — verified byte-identical copy of the reference package's own `flows/tdd-replace-dialer/`; treat as reference-intent documentation, not noise
- `reactntive/react-native-replace-dialer/src/ReplaceDialer.js` — the actual reference interface to match (2 methods, callback-based, no `canSetDefaultDialer`)
- `reactntive/react-native-replace-dialer/android/app/src/main/java/one/telefon/replacedialer/ReplaceDialerModule.java` — reference native implementation, source of the exact bug also found in `flutter_dialer`
- `reactntive/react-native-replace-dialer/flows/adr-001-activity-result/context.md` — documents the bug and its proposed fix (already correctly implemented in `flutter_gsm`'s `ReplaceDialerModule.kt`)
- `libsFlutter/flutter_gsm/android/src/main/kotlin/org/telon/flutter_gsm/{ReplaceDialerModule.kt, GatewayDialerModule.kt}` — duplicate/out-of-scope code; deleting `ReplaceDialerModule.kt` there is `flutter_gsm`'s own future flow's job (not yet opened)
- `libsFlutter/flutter_tele/android/src/main/kotlin/org/telon/tele/flutter_tele/TeleService.kt` — competing 520-line `InCallService` implementation
- `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux/01-requirements.md` — its "Default Dialer status card" AC reads whatever this flow ships
- `flows/flutter_gsmsip/sdd-flutter_gsmsip-lib/` — sibling flow, same session, same reconciliation pattern (library-code items split out of a UI flow)

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:
