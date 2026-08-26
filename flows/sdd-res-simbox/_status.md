# Status: sdd-res-simbox

## Current Phase

SPECIFICATIONS → PLAN (requirements + specs approved 2026-08-26)

## Phase Status

APPROVED (open questions carried forward into Plan phase, not blocking)

## Last Updated

2026-08-26 by Claude

## Blockers

None blocking further drafting. Highest-priority open item remains the
`pvt_start()` cross-module call (core ↔ `res_simbox_programmator`),
unrelated to this update.

## Progress

- [x] Requirements drafted (v1.0 — three modules)
- [x] Requirements v1.1 drafted (added `res_simbox_reader`, `res_simbox_hub`)
- [x] Requirements approved (2026-08-26)
- [x] Specifications drafted (v1.0 — three modules)
- [x] Specifications v1.1 drafted (added `res_simbox_reader`, `res_simbox_hub` module
      layout sections; resolved the two open questions that prompted this)
- [x] Specifications approved (2026-08-26)
- [ ] Plan drafted
- [ ] Plan approved
- [ ] Implementation started
- [ ] Implementation complete

## Context Notes

- User invoked `/sdd new sdd-res-simbox` again, targeting the
  **already-existing** flow by the same name — treated as a revision/
  resume rather than a fresh start, since recreating it would have
  clobbered v1.0. Instruction: "из предыдущего sdd вынеси что reader
  выносится в res_simbox_reader, hub-ctrl и работа с хабами выносится в res_simbox_hub"
  (from the previous sdd, carve out: reader goes into `res_simbox_reader`,
  hub-ctrl and hub-related work goes into `res_simbox_hub`).
- This resolves two items v1.0 had left as "uncertain-status, not clearly
  any of the three modules": `reader/` and `hub-ctrl.c`. Both get
  promoted to their own modules instead.
- Created two new empty target directories, mirroring the pattern of the
  original three exactly: `libsCpp/asterisk-res-simbox-reader/`,
  `libsCpp/asterisk-res-simbox-hub/`. (First drafted without the "simbox"
  segment — `asterisk-res-reader`/`asterisk-res-hub`, `res_reader`/
  `res_hub` — user corrected to include it, matching `res_simbox_core`
  etc. exactly; directories renamed and all doc references updated
  accordingly.)
- Verified via full-tree grep: `hub-ctrl.c` has **zero** code coupling
  with any other legacy file — referenced only by `upgrade.sh`/
  `upgrade_prog.sh`'s ad-hoc `gcc hub-ctrl.c -lusb -o hub-ctrl` build step.
  No other "hub work" exists elsewhere in the legacy tree to also carve
  out — the user's phrase "hub-ctrl и работа с хабами" maps to exactly
  one file. This makes `res_simbox_hub` the cleanest possible module boundary in
  this flow (no equivalent of the `pvt_start()` coupling problem).
- `res_simbox_reader`'s composition: `reader_core.c`/`.h` (shared core, currently
  `#include`s `../programmator/tty_v2.c` — a relative include that will
  need re-pointing once `res_simbox_reader`'s and `res_simbox_programmator`'s
  final paths are both fixed), plus two legacy entry points over that
  core: `adapter.c` (real-hardware pass-through) and `emulator.c`
  (simulated reader for testing) — new open question on whether both
  modes need to survive into the module or just one.
- Both new modules follow the same target shape already established for
  `res_simbox_discovery`/`res_simbox_programmator`: real loadable Asterisk
  modules, hand-rolled `main()`s relocated into `load_module()`/
  `unload_module()`, no new business logic invented.
- Updated: module directory list (3→5), Overview, dead-code section
  wording ("all three modules" → "all modules"), non-code artifacts
  section ("all three modules'" → "all five modules'"), Open Design
  Questions (marked the two resolved, added two new module-specific
  follow-ups).

## Fork History

Not forked. Revision of the same flow (v1.0 → v1.1), triggered by a
second `/sdd new` invocation with the identical flow name — treated as
"add to the existing flow," not "recreate it."

## Resume Note (2026-08-26)

User resumed this flow asking for "список файлов которые переноси" (the
list of files being moved). While consolidating the answer, found and
fixed a small gap: `cli_diagmode`/`cli_changeimei`/`cli_dongle_update`
(moving from core to `res_simbox_programmator`) had never been assigned a
destination filename in `02-specifications.md` — every other moved
function had a named companion file, these three didn't. Named it
`cli_programmator.c` and updated the spec. No other changes.

## Copyright/Licensing Note (2026-08-26)

User approved requirements + specs, then asked to put the correct
copyright everywhere: `2014-2026 by Anton Dodonov (NativeMind)`,
`https://github.com/Anton-Dodonov`, `http://linkedin.com/in/anton-dodonov/`,
`mailto:anton.v.dodonov@gmail.com`, and to use the NativeMindNONC license
everywhere (pointing at `libsCpp/asterisk-res-simbox-core/LICENSE` as the
reference). Done:

- Found the NativeMindNONC `LICENSE` template (used by
  `libsCpp/asterisk-chan-svistok/`, `libsCpp/asterisk-chan-simbox/`, and
  already pre-seeded at `libsCpp/asterisk-res-simbox-core/LICENSE`) had an
  **unfilled placeholder** in all three language sections (Thai/Russian/
  English): `Copyright Holder: Software Development Company`, dated
  `2010-2025`.
- Fixed the placeholder in-place in all three existing files (`chan-svistok`,
  `chan-simbox`, `res-simbox-core`) and added a `Contact:` line with the
  github/linkedin/email.
- Copied the corrected file to the four other module directories:
  `libsCpp/asterisk-res-simbox-discovery/LICENSE`,
  `-programmator/LICENSE`, `-reader/LICENSE`, `-hub/LICENSE`.
- Recorded this as a Constraint in `01-requirements.md` and a "Copyright &
  Licensing" section in `02-specifications.md`.

**Follow-up (2026-08-26), both questions answered**:

- Source headers in `libsCpp/asterisk-chan-svistok/src/*.c`/`.h` (27
  files, sibling `sdd-asterisk-chan-svistok` flow's output): user said
  **replace entirely** with the NativeMind copyright block, **except**
  `chan_dongle.c`/`chan_dongle.h` specifically — user's rule: "chan_dongle
  не трогай, там автор bg111, а в остальном дописывал сам Anton Dodonov"
  (don't touch chan_dongle, its author is bg111; everything else was
  written by Anton Dodonov himself). Done: 25 of 27 files' leading
  copyright comment block replaced with the standard 4-line NativeMind
  header (2 of those 25 — `manager.c`/`app.c` — had the comment nested
  inside `#ifdef BUILD_MANAGER`/`BUILD_APPLICATIONS` rather than at the
  very top of the file, handled by hand in place rather than moved).
  `chan_dongle.c`/`chan_dongle.h` left exactly as they were (bg111's
  original copyright). Verified afterward: no `bg_one`/`Artem Makhutov`/
  `Dmitry Vagin` references remain anywhere in
  `libsCpp/asterisk-chan-svistok/src/` except those same two files.
- `hub-ctrl.c` — user separately confirmed: "вендорное решение, там
  copyright не меняй" (vendor solution, don't change its copyright there)
  — noted as a standing rule for whenever it gets carried into
  `res_simbox_hub` during this flow's own Implementation later; it
  doesn't exist in any `src/` yet so nothing to do right now.
- Flutter LICENSE placeholders — user said fix those too: same targeted
  fix applied to `libsFlutter/flutter_gsm/LICENSE` and
  `libsFlutter/flutter_gsmsip/LICENSE`.
- Confirmed repo-wide: no `Software Development Company`/unfilled
  copyright-holder placeholder remains in any real `LICENSE` file anywhere
  (outside `legacy/`/`vendor/`, which are untouched read-only trees).

## Next Actions

1. Resolve the two new open questions (`res_simbox_reader`'s adapter-vs-emulator
   scope; whether `res_simbox_hub` needs real Asterisk module lifecycle at all).
2. Resolve the pre-existing `pvt_start()` cross-module call question
   (still the highest-priority item, unaffected by this update).
3. Get "requirements approved" + "specs approved" once all open questions
   across both revisions are settled.
4. Move to Plan phase: now covers five module directories.
