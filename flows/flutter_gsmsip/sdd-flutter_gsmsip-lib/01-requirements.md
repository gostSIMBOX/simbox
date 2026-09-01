# Requirements: flutter_gsmsip-lib

> Version: 1.1
> Status: DRAFT
> Last Updated: 2026-08-31

## Urgent: the dependency graph is currently broken (verified live)

Before any of this flow's original 4 items matter, `flutter_gsmsip`
**cannot resolve its own dependencies right now**. Verified by actually
running it, not inferred:

```
$ flutter pub get   # inside libsFlutter/flutter_gsmsip
Resolving dependencies...
Because flutter_gsmsip depends on flutter_dialer from path which doesn't
exist (could not find package flutter_dialer at "../flutter_dialer"),
version solving failed.
Failed to update packages.
```

Cause: `libsFlutter/flutter_dialer` was renamed to
`libsFlutter/flutter_dialer_replacement` (its `pubspec.yaml` `name:` field
changed too, from `flutter_dialer` to `flutter_dialer_replacement` — a
real package rename, not just a directory move) during the
`vdd-flutter_dialer_replacement` flow. Three consumers still reference
the old name/path:

- `flutter_gsmsip/pubspec.yaml`'s `dependency_overrides:` —
  `flutter_dialer: path: ../flutter_dialer` (**this package's own file —
  in scope for this flow**).
- `flutter_gsm/pubspec.yaml`'s `dependencies:` *and*
  `dependency_overrides:` — same stale entry, doubled (**not this
  package's file — out of scope, but blocking**, since `flutter_gsmsip`
  depends on `flutter_gsm`).
- `flutter_tele/pubspec.yaml`'s `dependencies:` —
  `flutter_dialer: ^2.0.0+101` (a pub.dev version reference to a
  never-published package, previously only resolvable because something
  upstream overrode it to a local path — that override is now also
  broken). **Not this package's file — out of scope, but blocking**.

Renaming just the `path:` target is not sufficient — pub requires a
`path:` dependency's YAML key to match the target pubspec's `name:`
field, so the fix is: `flutter_dialer:` → `flutter_dialer_replacement:`
as the key (not just the path value) everywhere it's referenced, plus
updating the two real Dart import sites
(`flutter_gsm/lib/src/android/android_flutter_gsm.dart`,
`flutter_tele/lib/src/dialer.dart`) from
`import 'package:flutter_dialer/flutter_dialer.dart'` to
`import 'package:flutter_dialer_replacement/flutter_dialer.dart'`
(the internal file is still named `flutter_dialer.dart` — only the
package name changed, confirmed by reading
`flutter_dialer_replacement/lib/`'s actual file listing).

This flow can fix its own `dependency_overrides` entry, but **cannot
verify any of its own work** (`flutter pub get`, `flutter test`,
`flutter analyze`) until `flutter_gsm`'s and `flutter_tele`'s pubspecs
are also fixed — that's other packages' files. Flagged as a hard
external blocker, not silently worked around.

## Problem Statement

`flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux` set out to redesign
`libsFlutter/flutter_gsmsip/example`'s UI/UX around the gateway-product
functionality found in `react-native-gsm-sip-gateway` and `gsm2sip`, under
a hard constraint that `libsFlutter/flutter_gsmsip/lib/**` stays
untouched. While drafting that flow's requirements, several concrete
items surfaced that are **not** UI/UX at all — they're gaps or open
questions in `flutter_gsmsip`'s own library API that block or shape what
the example (or any real product) can honestly build on top of it. This
flow pulls those items out into their own spec, so the library work gets
its own requirements → specs → plan → implementation cycle instead of
being smuggled into a UI flow or silently deferred.

This is a **library-code flow**, not a UI flow: its deliverables are
changes under `libsFlutter/flutter_gsmsip/lib/**` (plus `test/**` and
`README.md`), not `example/**`.

### What's moving here from `vdd-flutter_gsmsip-example-uiux`

| Item | Why it's a lib concern, not UI |
|---|---|
| `GatewayService` has no public config save/clear API | Only a private `_saveConfiguration()` (`lib/src/services/gateway_service.dart:498`), called solely from inside `initialize()` — which only reaches that point on a successful SIP init, impossible off-Android per the already-documented per-platform capability ceiling. The example's `ExampleConfigStore` already works around this by reading/writing `SharedPreferences['gateway_config']` directly, which its own spec flagged as "an implementation detail, not a public contract." That workaround shouldn't have to exist. |
| Multi-profile config (RN-gateway's per-device `tConfig`/`sConfig` pattern) | Requires a real storage/domain change (N named `GatewayConfig`s, active-profile selection) — not achievable purely in example code without the save/clear API above, and probably not without a new domain type. |
| Magisk-dependent capability flags (`sdd-voiceline-mode-magisk-v2`'s `LineInfo`-style `canRecordVoiceToRadio`/`canGetVoiceFromRadio`/`canWriteToVoiceCommunication`) | That spec designs these against `lib/models/line_info.dart` and `lib/domain/entities/gateway_config.dart` — paths that don't exist in this package's actual structure (that spec predates or targets a different codebase; package name `one.telefon.gateway` matches neither `flutter_gsmsip`'s example (`org.telon.flutter_gsmsip_example`) nor `gsm2sip`'s (`com.callagent.gateway`)). Whether/how `flutter_gsmsip` should own a capability model at all is an architectural decision, not a screen. |
| Documenting the permission contract `flutter_gsmsip` can't enforce itself | `flutter_gsmsip` has no `android/` folder (pure-Dart orchestrator, confirmed via its `pubspec.yaml`) — it can never declare `<uses-permission>` itself. What it *can* do is document, in its own `README.md`, exactly which permissions a consuming app must get from `flutter_gsm`/`flutter_nmsip`/(transitively) `flutter_dialer`, so the gap found during the permission audit (`flutter_gsm`'s own manifest is empty) doesn't quietly resurface for the next integrator. |

### What's explicitly *not* moving here (confirmed already implemented)

Investigated while drafting this: **GSM→SIP auto-bridging already exists**
in `GatewayService._handleIncomingGsmCall()` (gated by
`GatewayConfig.routeGsmToSip` + `.autoAnswer`, producing a `CallRouting`
on `routingStream`/`activeRoutings`). The "gateway mode" the RN/gsm2sip
comparison in the UI flow is asking to visualize is **not missing
library behavior** — it's an existing public API
(`statusStream`, `routingStream`, `activeRoutings`, `getActiveRoutings()`,
`CallRouting`) that the example never surfaced. No lib work item here for
that; flagged so nobody re-implements bridging that already works.

## User Stories

### Primary

**As a** developer building a real product on `flutter_gsmsip`
**I want** a public, documented way to save/load/clear gateway
configuration independent of whether `initialize()` succeeds
**So that** I'm not forced to reach into `SharedPreferences` internals
the way the example currently does.

**As a** developer wanting per-device or per-deployment gateway profiles
(mirroring `react-native-gsm-sip-gateway`'s device-keyed config
switching)
**I want** `flutter_gsmsip` to support storing more than one named
`GatewayConfig`
**So that** one build can serve multiple gateway phones/deployments
without recompiling per device.

### Secondary

**As a** developer integrating Magisk-granted privileged capabilities
**I want** a clear library-level answer on whether `flutter_gsmsip`
reports capability state itself, or whether that's entirely out of its
pure-Dart reach and belongs to `flutter_gsm`/`flutter_tele`
**So that** the example's planned "System Capabilities" panel has one
real API to call instead of guessing.

**As** Anton
**I want** `flutter_gsmsip/README.md` to state plainly which permissions
a consuming app must ensure exist (and where they should come from),
given the package can never declare them itself
**So that** the permission gap found during the audit doesn't recur for
whoever builds the next app on this library.

## Acceptance Criteria

### Must Have

0. **Given** the broken dependency graph documented above, **when** this
   flow implements, **then** `flutter_gsmsip/pubspec.yaml`'s
   `dependency_overrides:` entry is fixed to
   `flutter_dialer_replacement: path: ../flutter_dialer_replacement`
   (key and path both) — and `flutter pub get` is confirmed to at least
   get past *this* package's own resolution step. Full green
   `pub get`/`analyze`/`test` still depends on `flutter_gsm` and
   `flutter_tele` fixing their own pubspecs (out of this flow's file
   scope — flagged, not fixed here) — note that dependency explicitly in
   this flow's status rather than silently declaring done once this
   package's own file is correct.
1. **Given** a `GatewayConfig`, **when** a consumer calls a new public
   `GatewayService.saveConfiguration(GatewayConfig)`, **then** it
   persists independent of `initialize()`/SIP-init success, using the
   same storage key/shape `_saveConfiguration()` already uses internally
   (no silent format change that would orphan existing saved configs).
2. **Given** saved configuration exists, **when** a consumer calls a new
   public `GatewayService.clearConfiguration()`, **then** it is removed
   and a subsequent `loadConfiguration()` returns `null`.
3. **Given** the multi-profile requirement, **when** Specifications are
   written, **then** they resolve: is this a new `GatewayProfile` domain
   type wrapping `{name, config}` with `listProfiles()`/`saveProfile()`/
   `deleteProfile()`/`activeProfileName`, or an example-local layer on
   top of AC1/AC2's primitives? Decide with a rationale, not by default.
4. **Given** the Magisk-capability question, **when** Specifications are
   written, **then** they state explicitly whether `flutter_gsmsip` adds
   a capability-reporting API (and if so, backed by what — it has no
   native channel of its own, so this would have to proxy through
   `permission_handler` and/or a new capability query surfaced by
   `flutter_gsm`/`flutter_tele`) or whether this is declared out of
   scope for the library entirely, with the example left to query
   `permission_handler` directly.
5. **Given** the permission-contract documentation need, **when** this
   flow implements, **then** `flutter_gsmsip/README.md` gains a section
   listing required Android permissions grouped by the package that
   should declare them (`flutter_gsm`, `flutter_nmsip`, `flutter_dialer`
   if dialer replacement is used), explicitly noting `flutter_gsmsip`
   itself declares none and consumers must verify the transitive set —
   this is documentation, not a manifest change (no `android/` folder is
   being added to `flutter_gsmsip`).
6. **Given** any of the above changes land, **when** existing tests run
   (`test/sip_state_tracker_test.dart`, `example/test/
   example_config_store_test.dart`), **then** they still pass, and new
   unit tests cover the new public config API (save/load/clear
   round-trip, and multi-profile if built).

### Should Have

- A short migration note if the config storage key/shape changes at all,
  so `ExampleConfigStore`-style workarounds in the example (or any other
  consumer) aren't silently broken.

### Won't Have (This Iteration)

- Reimplementing GSM↔SIP auto-bridging — already works (see above).
- Any Android/native platform code inside `flutter_gsmsip` itself — it
  stays pure-Dart per its own documented design decision; capability
  queries that need native access get proxied to sibling plugins, not
  built here from scratch.
- Fixing `flutter_gsm`'s empty manifest or its duplicate
  `ReplaceDialerModule` — those belong to `flows/flutter_gsm/` and
  `flows/flutter_replace_dialer/` respectively; this flow only documents
  the *contract*, not the other packages' fixes.
- Re-targeting `sdd-voiceline-mode-magisk-v2`'s Magisk module to a real
  applicationId — that flow's own scope.

## Constraints

- **Technical**: must preserve `_saveConfiguration()`'s existing
  `SharedPreferences` key/shape unless Specifications justify and
  document a migration — real saved configs (via `ExampleConfigStore`'s
  workaround) already exist against the current shape.
- **Platform**: `flutter_gsmsip` remains pure-Dart — no `android/`,
  `ios/`, etc. folders added to the library itself.
- **Dependencies**: this flow's outcome is a hard input to
  `vdd-flutter_gsmsip-example-uiux`'s Specifications phase (its Setup/
  Capabilities screens depend on whatever public API this flow ships) —
  keep that flow's `_status.md` updated when this one's API surface is
  decided.
- **Backward compatibility**: `GatewayService` is a singleton
  (`factory GatewayService() => _instance`) already in use by the
  current working example — new public methods must not change existing
  method signatures.

## Open Questions

- [ ] Does multi-profile support belong in `flutter_gsmsip` at all, or
      is "one active `GatewayConfig` at a time, switchable by the app"
      sufficient, with true multi-profile UX living entirely in example/
      product-level storage on top of AC1/AC2? Needs Anton's call before
      Specifications commit to a domain model.
- [ ] Is a `GatewayCapabilities` value object worth adding to
      `flutter_gsmsip`, given it would only ever proxy
      `permission_handler`/sibling-plugin state rather than performing
      any check itself? Or is that indirection pointless and the example
      should query `permission_handler` directly?
- [ ] Should `clearConfiguration()` also stop a running gateway (call
      `stop()` first) if one is active, or reject with an error asking
      the caller to stop first? Decide explicitly — don't leave it
      implicit.

## References

- `libsFlutter/flutter_gsmsip/lib/src/services/gateway_service.dart` (lines 98, 159, 197, 291, 498, 511)
- `libsFlutter/flutter_gsmsip/lib/src/domain/entities/gateway_config.dart`
- `flows/flutter_gsmsip/vdd-flutter_gsmsip-example-uiux/01-requirements.md` — origin of this split, see its updated cross-flow table
- `flows/flutter_gsmsip/sdd-flutter_gsmsip-example/02-specifications.md` — "Config persistence gap" section, first flagged this
- `flows/flutter_gsmsip/sdd-voiceline-mode-magisk-v2/01-requirements.md` — `LineInfo` capability-flag design (FR-6), path mismatch noted above
- `reactntive/react-native-gsm-sip-gateway/telon-gateway-app/src/Gateway.js` — per-device profile pattern (`tConfig`/`sConfig` keyed by `DeviceInfo.getDeviceId()`)

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:
