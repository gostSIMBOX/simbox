# Status: vdd-simbox-app-uiux

## Current Phase

IMPLEMENTATION (Tasks 1-13, v1.0 scope)

## Phase Status

Tasks 1-13 implemented and verified (`flutter analyze`/`flutter test`
clean, Task 13 manual visual pass done); final visual-fidelity
sign-off gated on the font-asset blocker (see below)

## Last Updated

2026-08-23 by Claude (second extraction this session: pulled all
navigation-shell/tab-bar content — Task 3, the Navigation Map, AC #5's
nav-chrome clause, the bottom-tab-bar/rail DS token rows — out of this
flow into a new flow, `vdd-simbox-app-navbar-uiux`, at Anton's explicit
instruction: "вынеси из vdd-simbox-app-uiux все про navbar". All 5
documents here (01-05) were trimmed again, replaced with forward
references to the new flow. No code changed — `apps/simbox-app/lib/
navigation/{app_shell.dart,breakpoints.dart}` still exist and work
exactly as before; only the documentation ownership moved. This is on
top of the earlier "Каналы" screen extraction into
`vdd-simbox-app-channel-table-uiux` — rename, dual view mode,
table-view-anywhere toggle, formerly this flow's AC #8/Tasks 14-18 —
which still stands unaffected.)

## Blockers

- **Font-asset blocker** (v1.0 scope): all five files named
  `sf-pro-text-*.ttf` in both `design/nativemind-designsystem-v1.8/
  uploads/` and `design/nativemind-designsystem-v1.8/assets/fonts/`
  are GitHub HTML pages, not fonts (`file` confirms this). The copies
  already vendored under `apps/simbox-app/assets/fonts/` are therefore
  invalid too. The approved requirement mandates bundled SF Pro Text;
  implementation needs either valid licensed font files or Anton's
  explicit approval to remove the invalid assets and use a
  platform-native fallback. This blocker is **shared** with
  `vdd-simbox-app-channel-table-uiux`, since both flows' UI lives in
  the same running app.
- Documented, considered (not accidental) gap: real `.ico`-format
  operator marks and RSSI sprites can't be decoded by Flutter's image
  codec — substituted with a real bar-gauge widget (`SignalBars`) and a
  text-initial badge (`OperatorBadge`) instead, per
  `05-implementation-log.md`.
- Cross-flow dependency gap flagged (not blocking): `ModemDevice` as
  currently approved in `sdd-flutter_gsmsip-interface` lacks several fields
  the Симки screen needs (phone number, LAC/CELL, call statistics,
  autoblock reason, balance delta, timestamps). Proposed as a follow-up
  addendum to that flow rather than reopening its approved specs. UI ships
  with "—" placeholders for these fields until resolved.
- `sdd-flutter_gsmsip-interface` is fully approved (2026-08-20) — no
  longer a soft dependency, gating constraint satisfied.

## Progress

- [x] Requirements drafted (v1.0, 2026-08-20; trimmed to v1.4 then
      v1.5, 2026-08-23 — two extractions)
- [x] Requirements approved (v1.0, 2026-08-20)
- [x] Visual mockups drafted (v1.0; trimmed to v1.3 then v1.4,
      2026-08-23 — two extractions)
- [x] Visual mockups approved (v1.0, 2026-08-20)
- [x] Specifications drafted (v1.0; trimmed to v1.2 then v1.3,
      2026-08-23 — two extractions)
- [x] Specifications approved (v1.0, 2026-08-20)
- [x] Plan drafted (v1.0; trimmed to v1.2 then v1.3, 2026-08-23 — two
      extractions)
- [x] Plan approved (v1.0, 2026-08-20)
- [x] Task 13 visual verification complete (2026-08-22): 22 rendered
      phone/tablet/desktop state captures inspected using a temporary
      Flutter harness with the real macOS SF system font.
- [~] Implementation tasks complete (v1.0 scope); font-asset requirement
      blocked
- [ ] Implementation complete (v1.0 scope)
- [ ] Documentation drafted
- [ ] Documentation approved

**The "Каналы" screen redesign (formerly this flow's AC #8 / Tasks
14-18) has been extracted whole into `vdd-simbox-app-channel-table-
uiux`**, and **the navigation shell (Task 3, formerly this flow's own
nav-chrome content) has been extracted into
`vdd-simbox-app-navbar-uiux`** — see each flow's own `_status.md` for
its progress checklist. The navbar flow's requirements are approved
(v1.0) as of 2026-08-23; it's about to enter VISUAL.

## Context Notes

Key decisions and context for resuming:

- This is step 2 of a 3-flow sequence requested by Anton in one command; see
  `libs/flutter_gsmsip/flows/sdd-flutter_gsmsip-interface/_status.md` for
  the full sequence (interface API first, this UI refactor second, a future
  `sdd-flutter_gsmsip-channel` third — not yet created).
- Mid-turn, Anton explicitly added: "Так же обязательно используй дизайн
  систему design/nativemind-designsystem-v1.8" (also mandatory: use the
  nativemind-designsystem-v1.8 design system) — folded into requirements as
  a hard constraint alongside `design/simbox-app-maket-v2026`.
- Research findings (3 parallel subagents + direct reads):
  - `design/simbox-app-maket-v2026`: two `.dc.html` prototype files, no
    JSON manifest — screens must be read by opening the HTML in a browser.
    Responsive phone/iPad/desktop breakpoints ("шесть раскладок одного
    экрана"). Sections: Симки, Модемы, Звонки, СМС, Настройки,
    network/diagnostics console, engineering vs normal mode. The `_ds`
    folder inside this same directory is an unrelated VPN-app design
    system — don't confuse it with the real `nativemind-designsystem-v1.8`
    at the top level.
  - `design/nativemind-designsystem-v1.8/readme.md`: product-agnostic DS
    (VPN Client family + TaxLien + portal + adminka). Directly relevant:
    the readme has a dedicated "GOSTSIMBOX-ADMIN — DENSE TABLE" section
    describing exactly our product's dense-table pattern (brand-tint
    zebra, icon-only headers, stacked-cell ink hierarchy, icon-stack status
    columns), backed by `tokens/web.css` and a 224-file
    `assets/adminka/` icon set (state/cfun/simst/srvst, qos, spec,
    recog_types, rssi, napravleine [operator marks], usb, tree, balance/
    SMS/dongle icons) plus `assets/fugue/` as documented fallback. Base
    tokens: SF Pro Text font, 4pt spacing grid, single soft shadow, 10px
    card radius, Blue accent `#00C6FB → #005BEA` as the apparent default
    for non-VPN-colorway products (Portal also uses blue).
  - `apps/simbox-app/lib` current state: only `l10n/`, `theme/`, `utils/`,
    `main.dart` (demo `DashboardScreen`) — greenfield for real screen/widget
    structure.
- Open question left for specifications: exact Flutter widget approach for
  the dense table (custom grid vs. a `DataTable2`-style package) to match
  the DS's icon-stack/pinned-column/stacked-cell requirements.

- Visual phase read both `.dc.html` files directly (they're template-driven
  with live sample data via `sc-if`/`sc-for` bindings, not static per-screen
  exports) and extracted real embedded copy/labels via grep. Confirmed tab
  structure: Симки · Модемы (Хабы/Линии) · Операции (Звонки/СМС) ·
  Настройки — same order as 2015 text nav. Confirmed the dense desktop
  table (Симки) must follow the DS's GOSTSIMBOX-ADMIN pattern per
  requirements AC #3; a full 33-column list needs cross-checking against
  `legacy/simbox-desktop-v2015/www/` in specifications (not guessed in
  visual phase).
- New finding surfaced: the breakpoint-rationale doc
  (`Основной экран-ipad,desktop,phone.dc.html`) describes **six** layouts,
  not four — two of them ("Веб в браузере", "Веб-страница с телефона")
  explicitly preserve the 2015 legacy web admin's host-string header and
  ` :: `-separated text nav as a distinct surface. This wasn't anticipated
  in 01-requirements.md's "Won't Have" (which excluded rebuilding
  `templates/gostsimbox-admin/`). Flagged as an open item in 02-visual.md;
  visual mockups cover only the 4 native-app layouts (phone
  portrait/landscape, tablet, desktop) pending Anton's call on the web
  layouts.

- Specifications resolved the table-widget open question:
  `package:two_dimensional_scrollables`'s `TableView` (pinned rows/columns,
  single synced scroller — matches the DS's dense-table requirement),
  wrapped in a themed `DenseModemTable` widget.
- Read `legacy/simbox-desktop-v2015/www/simbox/sim.php`'s real header row
  (~line 1097-1178) and confirmed/mapped the full 2015 column set (~38 raw
  columns incl. commented-out ones) to the 2026 consolidated icon-stack
  representation — resolved 02-visual.md's "33 columns" open item.
- "Web in browser"/"web from phone" open item locked to **out of scope**
  (my recommended default) since Anton's approval didn't override it.
- Assumption for now: driver is unavailable
  (`ModemDriverNotAvailable`) throughout this flow's whole implementation,
  since `sdd-flutter_gsmsip-interface`'s Linux stub always throws until
  `sdd-flutter_gsmsip-channel` lands. Plan/implementation must build and
  verify against a `FakeModemRepository` test double, not real hardware.

- **Pre-plan finding**: `apps/simbox-app` currently does not build at all —
  its `pubspec.yaml` is an uncorrected copy of
  `libs/flutter_gsmsip/example/pubspec.yaml` (`name: flutter_gsmsip_example`,
  a `flutter_gsmsip: path: ../` that resolves to `apps/`, not
  `libs/flutter_gsmsip/`). `flutter pub get` fails outright. Fixing this
  is Plan Task 1, not optional — nothing else in this flow can be verified
  until it's fixed.
- Confirmed `provider: ^6.1.2` is already a dependency, resolving
  03-specifications.md's open state-management question — plan uses
  `ChangeNotifier`+`provider`, no new package.
- 13-task plan drafted: pubspec fix → theme/token reconciliation →
  navigation shell → `FakeModemRepository` (built early so every later
  task is visually verifiable without real hardware/the channel flow) →
  shared widgets → four screens → cross-cutting states → tests → manual
  verification pass.
- Task 13 is no longer display-blocked. A temporary Flutter screenshot
  harness rendered and inspected 22 states across 390×844, 900×1024,
  and 1440×900. It covered all four main screens, phone empty/SMS/modem
  detail/settings form/validation/dirty states, and selected SIM/modem
  detail panes on tablet and desktop.
- The visual pass found and fixed four defects that phone-only structural
  tests had missed: dense-table rows could not open SIM details;
  `SwitchListTile` ink was hidden behind a decorated container; settings
  validation overflowed by 57px on phone; corrected fields retained stale
  validation errors. Permanent regression coverage now includes dense-row
  detail selection and per-field error clearing.
- Current verification: all 10 repository tests pass; the 6-case temporary
  visual harness passes; `flutter analyze lib test` has 0 errors and 0
  warnings (24 pre-existing informational deprecation/style notices).
- **Extraction (2026-08-23)**: the "Каналы" screen redesign (rename from
  "Симки", dual view mode По-модемам/По-SIM-все, table-view-anywhere
  Настройки → Интерфейс toggle) began in this flow as a small clarifying
  question about a toggle's location, grew into a full screen redesign
  (via a verbatim-preserved exchange with Anton, captured in this flow's
  git history / prior document versions), and was implemented here as
  Tasks 14-18. Anton then asked to move all of that out into its own
  flow. See `vdd-simbox-app-channel-table-uiux/_status.md` for the full
  context notes on that side — domain-model terminology ("Modem" hosts
  "Channels", "Line" for multi-line modems, "Trunk" explicitly rejected)
  is now recorded there, not here.
- **Second extraction (2026-08-23)**: the navigation shell (four
  top-level destinations, breakpoint-switched chrome — bottom tab bar/
  rail/desktop nav) was Task 3 here, built as generic Flutter
  `NavigationBar`/`NavigationRail` with Material icons. Anton asked to
  extract all navbar content into its own flow and, while discussing
  it, settled two more things there: desktop/web should adopt the real
  `GostSimBoxAdmin.dc.html` chrome (sticky header + icon-label tab row,
  adminka icons) instead of `NavigationRail`, and mobile/tablet should
  use native-per-OS chrome with a shared adminka icon family (not a
  single custom cross-platform widget, not platform-default icons) so
  support can describe navigation consistently across platforms. None
  of that is implemented yet — `vdd-simbox-app-navbar-uiux` is at
  requirements-approved, about to enter VISUAL.

## Fork History

Not forked. `vdd-simbox-app-channel-table-uiux` and
`vdd-simbox-app-navbar-uiux` were both split out of this flow
2026-08-23 (documentation extractions, not forks — see each flow's own
`_status.md` Fork History note).

## Next Actions

**Font-asset blocker (v1.0 scope)**:
1. Anton: provide valid licensed SF Pro Text TTFs for the five declared
   weights, or explicitly approve removing the invalid HTML assets and
   using the platform-native sans-serif fallback.
2. Apply that decision, verify Russian copy in a release-like render,
   rerun `flutter analyze lib test` and `flutter test`, then mark
   IMPLEMENTATION complete (v1.0 scope).
3. Advance to DOCUMENTATION and replace the `06-readme.md` template only
   after implementation is genuinely complete.

**`vdd-simbox-app-channel-table-uiux`** (the extracted "Каналы"
redesign) and **`vdd-simbox-app-navbar-uiux`** (the extracted
navigation shell) are each tracked entirely in their own `_status.md`
now — nothing left to do for either from this flow's side.
