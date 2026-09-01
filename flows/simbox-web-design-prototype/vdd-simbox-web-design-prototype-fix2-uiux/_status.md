# Status: vdd-simbox-web-design-prototype-fix2-uiux

## Current Phase

IMPLEMENTATION

## Phase Status

DRAFTING

## Last Updated

2026-09-01 by Claude

## Blockers

- None.

## Progress

- [x] Requirements drafted
- [x] Requirements approved
- [x] Visual mockups drafted
- [x] Visual approved
- [x] Specifications drafted
- [x] Specifications approved
- [x] Plan drafted
- [x] Plan approved
- [x] Implementation started
- [ ] Implementation complete
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

- This flow builds directly on top of **fix1**
  (`flows/simbox-web-design-prototype/vdd-simbox-web-design-prototype-fix1-uiux/`, implemented
  and merged into the working tree of the nested `design/simbox-web-design-prototype-v2026`
  repo). fix1 gave the app: left sidebar with compact/full toggle, sticky table headers, and a
  first-pass action-group pill → floating-overlay-below-header pattern. This flow replaces just
  the "floating overlay" part with an in-row expansion, and adds column show/hide/reorder.
- **New reference discovered this session**: `design/simbox-design-prototype-v2026-beta1` — a
  separate, more complete prototype (vanilla JS, its own CSS) that already implements almost
  exactly the target interaction pattern: `.toolbar`/`.action-rail` (pills → in-row dropdown +
  fields + Run button, `overflow-x:auto` so it never grows downward), a `.columns-inline`
  editor (checkbox show/hide + move-left/right reorder chips, mutually exclusive with the action
  rail), and a `responsive.css` breakpoint (≤1180px: pills lose their labels, icon-only). This
  is an **interaction-pattern reference only** — its visual styling (own CSS, own color tokens)
  and its broader action inventory (`changeimei`, `supersim_new`, `get_balance`, etc. — actions
  not present in our fix1 port) are explicitly out of scope; source of truth for visuals stays
  `design/simbox-design-prototype-v2026-dc` / `lib/design/tokens.dart`, and source of truth for
  which actions must exist stays fix1's already-ported inventory (itself sourced from
  `legacy/simbox-desktop-v2014/www/simbox`).
- **Resolved via AskUserQuestion this session**: for action groups containing more than one
  legacy action (e.g. "Простые" = USSD/SMS/Звонок), adopt beta1's model — a dropdown picks the
  specific action, only its fields + Run button show (not all sub-actions simultaneously as in
  fix1). User picked this explicitly over "whole group inline, all sub-actions visible at once
  scrolling sideways."
  - Given that decision, this session further split the rule into three cases (documented in
    01-requirements.md's Acceptance Criteria #2, not yet approved): **Rule A** — group where
    every action needs zero input fields (Действия хитрые, Действия со свистками, Экспорт,
    Питание порта) → flat one-click button strip, no dropdown (nothing to protect screen space
    for). **Rule B** — group with at least one fielded action (Передатчик, Простые, Группы и
    планы, PIN, Режимы и AT-команда) → beta1's dropdown+fields+Run pattern; group-level shared
    settings (queue+delay checkbox/fields, live-refresh checkbox) render alongside the dropdown
    regardless of selected action. **Rule C** — exactly one action in the group (Перепрошивка)
    → skip the dropdown entirely, show that action's controls directly. This A/B/C split is
    flagged as an Open Question for explicit sign-off, not yet confirmed by the user.
  - Sims' "Звонок" (Call60/CallSpeak sharing one number field) and "Set plan" (без
    копирования/с копированием sharing one plan dropdown) are each kept as ONE dropdown entry
    with TWO run buttons, rather than being split into 4 separate dropdown entries — preserves
    fix1's existing "one input, two outcomes" shape instead of forcing an awkward extra
    dropdown item per outcome.
- Column management: proposed as AppState-held `order`/`hidden` per table id (mirrors beta1's
  `app.storage` shape almost exactly, minus the `localStorage` persistence — kept in-memory per
  fix1's precedent of not adding new package dependencies for a nice-to-have). Sorting already
  works from fix1 and is explicitly unaffected by column order/visibility changes (Acceptance
  Criteria #9). Reorder is move-left/move-right buttons only, no drag-and-drop (matches beta1,
  avoids a DnD dependency).
- Fix1's precedent to follow again here: verify with `flutter analyze` + `flutter build web` +
  a driven Chrome session after implementation; the Flutter project under
  `design/simbox-web-design-prototype-v2026` is its **own nested git repo**
  (`origin/master`) — no commit/push without explicit ask.

## Fork History

N/A — new flow, builds on (does not fork from) fix1.

## Next Actions

1. Get explicit "specifications approved" + "plan approved" from the user (drafted together
   after confirming fix1's code is committed and unchanged — see Context Notes).
2. On approval, start IMPLEMENTATION following 04-plan.md's 5 phases (State → Action rail →
   Columns editor → wire up 4 pages → verification), logging progress in
   05-implementation-log.md, verifying with `flutter analyze` + `flutter build web` + a driven
   Chrome session per fix1's precedent.

## Additional Context Note (post-Requirements)

- Confirmed at the start of Specifications: fix1's work is committed on the nested
  `design/simbox-web-design-prototype-v2026` repo as commit `709d543` (authored by Anton
  Dodonov, not by this session — the user committed it themselves between fix1 and fix2). Working
  tree was clean (only harmless `build/` artifact diffs from fix1's verification build) before
  this flow's Specifications/Plan drafting began — confirms fix1's code, as read into this
  flow's Specifications, is accurate and unmodified.
