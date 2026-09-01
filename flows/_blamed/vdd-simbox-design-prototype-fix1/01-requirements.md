# Requirements: simbox-design-prototype-fix1

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-09-01

## Problem Statement

`design/simbox-design-prototype/index.html` is a full "as-is" reconstruction of the 2015
SimBox admin panel (source of truth: `legacy/simbox-desktop-v2014/www/simbox/*.php`), skinned
with the `nativemind-designsystem`. The reconstruction copied every dense operational table
faithfully, but in doing so also copied several rough edges from the original PHP/HTML that a
2026 admin panel shouldn't keep:

- Icons were copied ad-hoc from `legacy` without checking them against the design system's own
  `assets/adminka/` set or against what each icon is supposed to mean (per the legend embedded
  in `sim.php` lines 2164–2221 and `modules/html.php`) — some paths are inconsistent (e.g.
  `assets/imgs/state_in.png` at root vs `assets/imgs/state/state_dial.png` nested) and at least
  one icon reference (`pause2.png` on the SIM table) doesn't match any icon the legacy logic
  actually emits (source uses `pause.png`).
- Column header labels are left-aligned, which is hard to scan against right-aligned numeric
  cell content in a dense table.
- No monospace treatment for identifiers (IMEI, IMSI, ICCID, phone numbers), so digits don't
  align column-to-column.
- The action panels ("Действия простые/групповые/хитрые/комплексные", export/import, etc.) and
  the filter panel sit in the same flex-wrap row as designed, but there's no adaptive/compact
  fallback when the viewport can't fit them — they just wrap awkwardly.
- Tables have no way to hide unneeded columns or reorder them, even though each table (Симки
  especially) has 30+ columns and different operators care about different subsets.
- Two dongle-mode tabs are labeled "Свистки (nm)" / "Свистки (um)" — legacy slang for USB
  dongles ("whistles") — which is unclear outside the original team; the request is to rename
  to the plain term "Модемы", keeping the mode qualifiers.
- There is no language selector, even though the product now targets non-Russian operators.

## Source of Truth

- `legacy/simbox-desktop-v2014/www/simbox/sim.php` — table headers, per-cell icon logic
  (`$cap`, `$im`, `$vip`, `$pre`/`$pos`, `state_*`), and the icon legend at lines 2164–2221 +
  group-code legend at 2190–2221.
- `legacy/simbox-desktop-v2014/www/simbox/modules/html.php` — icon-selection functions
  (`html_group`, `html_cfun`, `html_simst`, `html_srvst`, `html_dongle`, `html_dialstatus`,
  `html_endparty`, `html_recog_type`, `html_spec`, `html_fas`, direction/operator icon map).
- `legacy/simbox-desktop-v2014/www/simbox/{dongle.php,readers.php,plan.php,hubs.php,nabor.php,
  proc.php,bablo.php,upgrade.php,debug.php,diagmode.php}` — per-screen headers/columns for the
  full column-parity audit (AC #8).
- **`nativemind-adminka` skill** (`~/.claude/skills/nativemind-adminka/`) — **the current home
  of the GostSimBox icon set and this exact dense-table pattern.** Mid-flow discovery: this
  content used to live under `nativemind-designsystem` and has since been split into its own
  skill; `nativemind-designsystem/readme.md` already points here correctly (§ "Web & admin
  surfaces", line 391) — use `nativemind-adminka`, not `nativemind-designsystem`, for anything
  adminka-specific below:
  - `assets/adminka/` — the canonical 16×16 GostSimBox icon set (224 files, grouped by
    `state/simst`, `state/srvst`, `state/cfun`, `state/end_party`, `state`, `qos`, `spec`,
    `recog_types`, `rssi`, `im`, `diagmode`, `napravleine`, `usb`, `tree`, root).
  - `assets/adminka/adminka-to-fugue-map.json` — provenance per icon (custom hand-drawn vs.
    Fugue-derived) and whether a real 32×32 asset exists or only a pixelated upscale. **Already
    patched this flow**: `pause2.png` marked `"deprecated": true` (accidental duplicate of
    `pause.png`, same Fugue source `control-pause.png`, never referenced by legacy PHP).
  - `guidelines/adminka-icons.html` — the existing icon catalog page/pattern to mirror for our
    on-page legend.
  - `guidelines/adminka-taxonomy.html` — **the icon taxonomy & Fugue-correspondence table** —
    folder = semantic axis, filename = raw protocol value, suffix-badge rules (e.g.
    `beeline_spb` = Beeline logo + SPB region badge) — primary reference for the column-parity
    audit's icon-meaning column.
  - `guidelines/adminka-density.html` / `guidelines/dense-table.html` — sizing + dense-table
    conventions for this exact panel.
  - `templates/gostsimbox-admin/GostSimBoxAdmin.dc.html` — existing richer implementation of
    this same table (sortable columns via `state.sort`/`state.dir`, row selection) to reuse
    *patterns* from — not the runtime itself, since the prototype stays plain static HTML +
    `support.js`.
- `nativemind-designsystem` skill (`~/.claude/skills/nativemind-designsystem/`):
  - `guidelines/icon-density.html` — **the icon sizing model to follow** (general version):
    one logical icon size (16px) shipped as a 16/32/48 triplet for 1×/2×/3× DPR via `srcset`;
    never a scaled-up "big icon" UI size. Confirmed by the user: "32×32 on retina" means the
    @2x density asset, not a bigger on-screen icon.
  - `assets/icons/icon-globe.svg` — **new**, added by this flow (no globe/language glyph
    existed anywhere in the design system before). Manual vector redraw of Fugue's `globe.png`
    on a 16-unit grid, per the "manual vector redraw" route documented in
    `nativemind-adminka/guidelines/adminka-icons.html`. Lives in `nativemind-designsystem`
    (not `nativemind-adminka`) because a language selector is a generic, cross-product control,
    not adminka-specific.
- `nativemind-fugue-icons` skill (`~/.claude/skills/nativemind-fugue-icons/`) — vendored Fugue
  3.5.6 + 2× archive; source for the globe redraw and for any future gap-fill icon (fallback
  per `nativemind-adminka`'s own rule: GostSimBox glyph first, Fugue 2× fallback second).

## User Stories

### Primary

**As a** SimBox operator scanning the Симки/Свистки tables for anomalies
**I want** correct, meaningful icons, right-aligned/monospace-aligned columns, and the ability
to hide columns I don't care about
**So that** I can read dense operational data at a glance without horizontal noise.

### Secondary

**As a** SimBox operator on a laptop-width screen
**I want** the action buttons and filters to collapse into a compact, icon-only row when they
don't fit
**So that** I can still trigger actions on selected rows without the panel breaking layout.

**As a** non-Russian-speaking operator
**I want** to switch the UI language
**So that** I can use the panel without knowing Russian.

## Acceptance Criteria

### Must Have

1. **Given** any table screen in the prototype (Симки, Модемы normal/update mode, Хабы, Наборы
   команд, Планы, Процессы, Биллинг, Обновление, Debug — every screen with a `<table>`)
   **When** an icon is rendered in a header or cell
   **Then** it resolves to the matching glyph in `nativemind-adminka/assets/adminka/`
   (correct category/state, not a placeholder or an unrelated icon, and not the deprecated
   `pause2.png` duplicate), served via a `16/32/48` `srcset` triplet at one logical 16px size —
   never CSS-scaled.

2. **Given** the same scope
   **When** I open the on-page notes/legend section
   **Then** it contains a complete table of every icon used on that screen: icon glyph, file
   path, and its meaning taken verbatim (translated where useful) from the `sim.php` /
   `modules/html.php` legend — so every icon's meaning is independently verifiable against the
   legacy source, not just asserted.

3. **Given** a data table
   **When** I look at a column header vs. its cell values
   **Then** header labels are right-aligned to match the (right-aligned) cell content, and
   identifiers/numeric columns (IMEI, IMSI, ICCID, phone numbers, counters) use the system
   monospace stack (`ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace`)
   so digits line up vertically.

4. **Given** the Действия (actions) and filter panels below a table
   **When** the viewport is wide enough
   **Then** they sit in a single row (as today).
   **When** the viewport is too narrow to fit them
   **Then** the layout adapts responsively, and if space is still insufficient, action panels
   collapse to an icon-only compact mode (button icons with `title` tooltips, labels hidden)
   while the filter controls remain reachable (e.g. behind a toggle or below the icon row) —
   never overlapping or causing horizontal scroll of the whole page.

5. **Given** any data table
   **When** I open a "columns" control
   **Then** I can hide/show individual columns and drag to reorder them, implemented as working
   vanilla JS (checkboxes + drag handles) consistent with the rest of the prototype's plain
   HTML/JS approach — no build step, no framework dependency beyond what `support.js` already
   provides. State should persist for the session (localStorage) so re-hiding on every reload
   isn't required.

6. **Given** the dongle-mode tabs currently labelled "Свистки (nm)" / "Свистки (um)" and their
   screen titles "Свистки (normal mode)" / "Свистки (update mode)"
   **When** I view any screen's nav or those two screens' headings
   **Then** the label reads "Модемы (nm)" / "Модемы (um)" in the nav and "Модемы (normal mode)"
   / "Модемы (update mode)" as the screen titles — every occurrence across all 11 screens'
   repeated nav bars is updated consistently.

7. **Given** the shared top bar (hostname / IP / version / uptime row, repeated on every
   screen)
   **When** I view any screen
   **Then** a language selector is present, using the new `icon-globe.svg`, with options
   English (default), ไทย (Thai), Русский (Russian), हिन्दी (Hindi), 中文 (Chinese) —
   visual/state-only in this prototype (no real i18n of the Russian copy is in scope; the
   control demonstrates placement, default, and the open dropdown state).

8. **Given** every screen's table in the prototype
   **When** I compare it column-by-column against its legacy PHP source (`sim.php`,
   `dongle.php`, `readers.php`, `plan.php`, `hubs.php`, `nabor.php`, `proc.php`, `bablo.php`,
   `upgrade.php`, `debug.php`, `diagmode.php`)
   **Then** every column the legacy source renders is present in the prototype with the
   matching icon/label (full column-parity audit — expanded scope, confirmed by the user).
   Two concrete gaps are already found and **must** be fixed as part of this iteration (not
   deferred):
   - **Планы (Plans)**: `plan.php` renders three icon columns in sequence — `may.ico`,
     `mon.ico`, `msm.ico` — the prototype only reconstructed the first two; add the missing
     `msm.ico` column.
   - **Свистки/Модемы (dongle) table**: `dongle.php`'s header row has 4 empty leading `<td>`
     cells before the "Свисток" label (5 total incl. label); the prototype only reconstructed
     2 — restore the 2 missing header/data columns.
   Any further gaps found during the audit get fixed the same way; log every finding (fixed or
   deliberately skipped) in the implementation log for traceability.

### Should Have

- Icon legend organized by category (matching `adminka-icons.html`'s grouping) rather than one
  flat list, for scannability.
- A short inline note where any icon in the source `legacy` reconstruction turned out to be
  wrong/mismatched (e.g. `pause2.png`), so the fix is auditable against the "as-is" premise of
  the prototype.

### Won't Have (This Iteration)

- Real backend wiring — this remains a static HTML prototype; no actual data, filtering, or
  language translation logic beyond UI state.
- Redesigning table content/columns beyond what the column-parity audit (AC #8) finds missing
  or wrong versus legacy — no *new* data columns beyond what legacy already had, no removed
  columns.
- Translating the Russian UI copy into the 5 languages — the language switcher is presented
  as a control, not a working translation layer.

## Constraints

- **Technical**: Must stay a self-contained static HTML file (`index.html` + `support.js` +
  `assets/`) — no build step, no external CDN fetches beyond what's already wired via the
  design-system's `_ds_bundle.js`.
- **Source of truth**: Every icon and every column meaning must be traceable to
  `legacy/simbox-desktop-v2014/www/simbox/*.php` (see per-screen file list above) — no invented
  iconography, no invented columns.
- **Design system**: Icons only from `nativemind-adminka/assets/adminka/` (GostSimBox set) with
  Fugue 2× as documented fallback for states with no GostSimBox glyph; sizing follows
  `nativemind-designsystem/guidelines/icon-density.html` (16 logical px, 16/32/48 triplet,
  `image-rendering: pixelated` for the GostSimBox originals). The new `icon-globe.svg` lives in
  `nativemind-designsystem/assets/icons/` (generic, cross-product), not `nativemind-adminka`.
- **Scope**: Applies to every screen in the prototype that has a `<table>` (confirmed: all
  screens), not just the Симки screen — and now includes full column-parity, not just icons.
- **Global-skill edits**: When the prototype and a global skill disagree (or a global skill is
  itself internally wrong, e.g. `pause2.png`), fix the global skill too, not just the local
  prototype — confirmed by the user. Two done already:
  `nativemind-adminka/assets/adminka/adminka-to-fugue-map.json` (`pause2.png` marked
  deprecated) and `nativemind-designsystem/assets/icons/icon-globe.svg` (new file, filled a
  real gap — no globe/language icon existed anywhere in the design system before).

## Open Questions

- [ ] Exact copy/wording for the compact action-icon tooltips (Russian, matching existing
  button labels) — will finalize during Visual phase mockups.
- [ ] Where exactly the language selector sits in the top bar (before/after the uptime text) —
  will resolve as part of Visual phase.
- [ ] Confirm "Модемы" replaces "Свистки" everywhere it appears (nav short form, screen title,
  H1) but the `/?p=dongle` and `/?p=diagmode` routes and `(nm)`/`(um)` suffixes stay unchanged
  (only the human-readable word changes) — assumed yes, flag if not.

## References

- `legacy/simbox-desktop-v2014/www/simbox/sim.php`
- `legacy/simbox-desktop-v2014/www/simbox/modules/html.php`
- `legacy/simbox-desktop-v2014/www/simbox/{dongle.php,readers.php,plan.php,hubs.php,nabor.php,
  proc.php,bablo.php,upgrade.php,debug.php,diagmode.php}`
- `~/.claude/skills/nativemind-adminka/assets/adminka/` (+ `adminka-to-fugue-map.json`, patched)
- `~/.claude/skills/nativemind-adminka/guidelines/{adminka-icons.html,adminka-taxonomy.html,
  adminka-density.html,dense-table.html}`
- `~/.claude/skills/nativemind-adminka/templates/gostsimbox-admin/GostSimBoxAdmin.dc.html`
- `~/.claude/skills/nativemind-designsystem/guidelines/icon-density.html`
- `~/.claude/skills/nativemind-designsystem/assets/icons/icon-globe.svg` (new, added by this flow)
- `~/.claude/skills/nativemind-designsystem/readme.md` § "Web & admin surfaces" (line 381) —
  correctly points to `nativemind-adminka`, confirmed not stale
- `~/.claude/skills/nativemind-fugue-icons/` (source for the globe redraw)

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-01
- [x] Notes: Approved as drafted, including expanded scope (full column-parity audit, Модемы
      rename, language selector, and the two global-skill edits already applied).
