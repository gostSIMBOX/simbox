# Status: sdd-simbox-app-real-driver

## Current Phase

IMPLEMENTATION

## Phase Status

COMPLETE

## Last Updated

2026-08-23 by Claude (all 5 phases / 11 tasks done)

## Blockers

None. Two things carried forward for a future real-Linux-host session
(not gaps this flow introduced — matches the same pattern every prior
flow in this chain has documented):

- Real end-to-end verification (a real `dongle.conf` + attached
  hardware actually producing a visible device in Симки/Модемы) has
  not been performed — no Linux host or USB modem is available in this
  development environment. Every acceptance criterion was verified
  structurally instead (native tests, `dart analyze`, widget tests,
  parse-validation of the shipped example config).
- `setNetworkMode`'s `auto`/`wcdmaOnly` `AT^SYSCFG` codes remain
  unconfirmed (pre-existing gap from `sdd-flutter_gsm-ffi`, unrelated
  to this flow's own scope, just still open).

## Progress

- [x] Requirements drafted
- [x] Requirements approved (2026-08-23)
- [x] Specifications drafted
- [x] Specifications approved (2026-08-23)
- [x] Plan drafted
- [x] Plan approved (2026-08-23)
- [x] Implementation started (2026-08-23)
- [x] Implementation complete (2026-08-23)
- [ ] Documentation drafted (N/A — this flow's "documentation" deliverable
      was the README section + example config, both done as Plan Tasks
      4.1-4.2, not a separate DOCUMENTATION phase; SDD's phase list is
      informational here, not a literal remaining step)
- [ ] Documentation approved (see above — nothing further pending)

## Context Notes

Key decisions and context for resuming:

- Scope: (a) DI swap in `apps/simbox-app/lib/main.dart` from
  `FakeModemRepository` to a real `ModemRepositoryImpl`, always-on, no
  fallback toggle; (b) made chan_dongle's config-driven device
  discovery actually usable via a predictable absolute path, not just
  a fragile CWD-relative one.
- **Config-dir design, resolved and implemented**: `simbox_config_t.config_dir`
  (previously dead) now works. New `simbox_config_bridge_set_dir()`
  (`libsCpp/asterisk_chan_simbox/adapters/include/simbox_config_bridge.h`
  + `adapters/src/shim_config.c`), called from `simbox_init()`
  (`src/simbox_api.c`) when `config->config_dir` is set. `flutter_gsm`
  exposes it as `configDir`/`FLUTTER_GSM_SIMBOX_CONFIG_DIR` (mirrors
  `FLUTTER_GSM_SIMBOX_LIB`). Deep chan_svistok research (done mid-flow,
  before specs approval, at Anton's request) confirmed this design is
  correct and sufficient — see `02-specifications.md` v1.1 and
  `04-implementation-log.md`.
- **Real bug found and fixed along the way** (Task 4.1, not part of
  the original plan): `shim_config.c`'s parser didn't strip trailing
  `key=value ; comment` text from values — only whole-line comments.
  This would have silently corrupted values in *any* real config
  written in the idiomatic Asterisk style (including this SDK's own
  vendored reference sample). Fixed with a new `strip_inline_comment()`
  helper + permanent regression test (`test_simbox.c` Test 8). See
  `04-implementation-log.md`'s Deviations Summary for full rationale.
- `apps/simbox-app/README.md` is a pre-existing stale copy of an
  unrelated `flutter_gsmsip/example` README — discovered during this
  flow's research, explicitly flagged (inline, in the new section
  itself) but deliberately not fixed wholesale (out of scope).
- No real Linux host or USB hardware available in this development
  environment throughout — every verification step in this flow was
  structural (native C tests, `dart analyze`, `flutter test`, one-off
  parse-validation of the shipped config), consistent with
  `sdd-asterisk-chan-simbox`'s Task 5.9 precedent.

## Fork History

Not forked.

## Next Actions

Nothing required to close this flow out — all planned work is done and
verified in every way achievable in this environment. Optional
follow-ups for a future real-Linux-host session:

1. Build `libsimbox`, copy `apps/simbox-app/dongle.conf.example` to a
   real location, set both `FLUTTER_GSM_SIMBOX_LIB` (if needed) and
   `FLUTTER_GSM_SIMBOX_CONFIG_DIR`, attach a real modem, `flutter run
   -d linux`, confirm the device appears in Симки/Модемы — the one
   thing this flow could not verify end-to-end here.
2. (Unrelated to this flow, carried over from `sdd-flutter_gsm-ffi`)
   Confirm `setNetworkMode`'s `auto`/`wcdmaOnly` `AT^SYSCFG` codes
   against real hardware/vendor AT reference.
