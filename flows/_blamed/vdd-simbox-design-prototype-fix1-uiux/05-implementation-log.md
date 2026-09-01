# Implementation Log: SimBox v2026 UI/UX fixes

> Status: IN PROGRESS — browser acceptance pending  
> Plan: [04-plan.md](04-plan.md)  
> Started: 2026-09-01

## Baseline

- Nested target repository was clean at implementation start (`bc84442`).
- Original `index.html` was a 97,703-byte monolith with inline DC markup/data/actions.
- It referenced an `_ds/**` bundle that is not present in the target repository.
- `support.js` baseline SHA-256:
  `8fe7df74405f3c55f49b7249c74ea1397e65d07dea2b1bd3b4a489bec2e28cbe`.
- Browser skill initialization returned no available browser backends. The required troubleshooting
  check also returned an empty browser list, so baseline/final screenshots could not be captured in
  this session.

## Completed work

### P01–P05 — baseline, harness and file decomposition

- Recorded the executable/source baseline and protected runtime hash.
- Added dependency-free `tests/verify-prototype.mjs`.
- Replaced the monolithic contents with a thin `<x-dc id="app">` mount and deterministic classic
  scripts. It stays compatible with `file://` and requires no build or network access.
- Extracted seven responsibility-based stylesheets:
  `tokens`, `base`, `shell`, `toolbar`, `data-grid`, `dialogs`, `responsive`.
- Added namespace/registry/runtime files under `js/core/`.

### P06–P09 — Fugue, localization, grid and action runtime

- Vendored 45 unique exact Fugue filename pairs (46 semantic mappings): original 16×16 plus matching
  32×32 rebuild.
- Added attribution and target `FUGUE-WISHLIST.md`.
- Applied Fugue icons to every route and active action; four exact-domain artwork ideas remain
  wishlist refinements only.
- Implemented English(default), Thai, Russian, Hindi and Chinese dictionaries with identical runtime
  key sets and locale-pure route/action/UI labels. Raw protocol/column identifiers remain raw.
- Implemented typed stable sorting, filtering, selection, hide/show, left/right reorder, Reset and
  versioned per-table localStorage.
- Implemented inline action transitions with selection/required-field validation, danger
  confirmation, simulated running/success state and command log.

### P10–P16 — exact table/screen extraction

| Definition file | Verified columns/actions |
|---|---|
| `tables/sim.js` | 43 columns; full active actions including `modules/actions.php`; commented `save`/`rotki` excluded |
| `tables/lines.js` | 26 columns; full modem action set |
| `tables/programmer.js` | 6 columns; Refresh |
| `tables/hubs.js` | 9 columns; `refresh/pon/poff/prestart` and delays; no KI/APDU |
| `tables/readers.js` | 12 columns; PIN, KI Search and APDU actions |
| `tables/command-sets.js` | 1 column |
| `tables/plans.js` | 82 columns from `5+7+4+23+16+15+12`; commented `ima` excluded |
| `tables/billing.js` | 4 columns; Direction contains code + operator; Fugue `money.png` |
| `tables/icons.js` | Fugue/provenance audit including unresolved wishlist rows |
| `screens/processes.js` | 9 active actions; Fugue `application-task.png` |
| `screens/update.js` | 5 active actions plus version/local changes |
| `screens/debug.js` | sysdevs and usbdevs log blocks |

### P17–P20 — final wiring, toolbar, typography and automated acceptance

- Rewired every route through the registries and retained `<x-dc>` as the host element.
- Implemented the fixed 46px toolbar. Filter, action groups and Columns share the same row.
- Action editors and Columns both morph inside the flexible rail. Horizontal overflow remains inside
  the rail, so no expansion covers or moves the grid.
- Applied monospace/tabular figures and right alignment to technical data; control cells remain
  centered and prose cells can remain left-aligned.
- Replaced Billing `may.ico`, Processes `conn.png`, deprecated `pause2.png`, Unicode action arrows,
  and every other generic fallback with audited Fugue pairs.
- `support.js` remains byte-identical. It is not loaded because its original `_ds` companion is
  absent; the standalone classic-script runtime owns rendering while preserving the DC host.

## Automated verification

Latest result:

```text
PASS 311 checks
Tables: sim=43, lines=26, programmer=6, hubs=9, readers=12,
        commandSets=1, plans=82, billing=4, icons=5
Locales: en/th/ru/hi/zh · Icons: 46 semantic mappings / 45 unique density pairs
```

The verifier covers:

- exact column counts and unique IDs;
- all-visible Reset state for every table;
- Plans group subtotal and inactive-column exclusion;
- stable numeric/text sorting and filter behavior;
- Hubs/Readers action separation;
- SIM included-module actions and commented-action exclusions;
- English action-label coverage and five-locale key parity;
- Fugue icons applied to every navigation route and active action;
- existence and intrinsic dimensions of every Fugue pair;
- prohibited icon/fallback references;
- all local `index.html` assets;
- fixed toolbar geometry and non-overlay Columns mode;
- unchanged `support.js` hash and retained `<x-dc>` host.

All JavaScript files also pass `node --check`; `xmllint` reports no HTML error; nested
`git diff --check` passes.

## Deviations

1. The original generated DC renderer could not be kept active because the referenced `_ds` bundle
   is absent from this target. The `<x-dc>` host is retained, but rendering is now handled by the
   dependency-free classic-script adapter. `support.js` is preserved unchanged and unused.
2. Browser screenshots and pointer/keyboard interaction evidence remain pending because the browser
   runtime reported zero available backends. No unrelated browser automation was substituted.

## Remaining plan items

- **P21**: browser visual/interaction acceptance sweep at wide/medium/compact widths and DPR 1/2.
- **P22**: final handoff checkpoint after P21 confirms the rendered result.

## 2026-09-01 follow-up — icons applied everywhere

The user requested that the four earlier text-only slots also show icons. After a new full-catalog
search and visual candidate comparison, these upstream Fugue pairs were applied:

- SIM route: `card.png`;
- Readers route: `scanner.png`;
- KI Search action: `magnifier.png`;
- APDU action: `terminal--arrow.png`.

There are now 46 semantic icon mappings backed by 45 unique 16×16/32×32 pairs (`magnifier.png` is
intentionally reused for Filter and KI Search). Every navigation route and every active action has
an applied Fugue icon. The wishlist retains proposed exact-domain artwork only as a refinement.
