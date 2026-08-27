# Requirements: asterisk-chan-svistok-chan-dongle-v2

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-08-26

> **Restart of**: `flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok-chan-dongle/`
> (the "v1" flow). That flow's independent file/function classification
> is carried forward unchanged into this flow's `02-specifications.md`
> (it is still fully valid — nothing about the underlying legacy-vs-
> upstream analysis was wrong or needs redoing). What this restart drops
> is the three/five-module split direction that flow's requirements grew
> into (v1.1/v1.2) — **that direction, and everything under
> `libsCpp/asterisk-res-simbox-*/` and `flows/sdd-res-simbox/`, is
> explicitly out of scope for this flow.** Per the user (2026-08-26):
> "тебе в рамках задачи нужно вернуться только к оригинальной папке
> libsCpp/asterisk-chan-svistok и первоначальной задаче, остальное -
> больше не твоя зона ответственности" (return only to the original
> `libsCpp/asterisk-chan-svistok` folder and the original task; the rest
> is no longer your area of responsibility).

## Problem Statement

`legacy/asterisk-chan-svistok-v2014` is a historical fork of
`asterisk-chan-dongle` (the `bg111` variant, mirrored read-only at
`vendor/asterisk-chan-dongle-bg111` and, as a working copy, at
`libsCpp/asterisk-chan-svistok/asterisk-chan-dongle`). Project-specific
("Svistok") code was mixed directly into the same files as unmodified
upstream `chan_dongle` code, with no separation between the two. This
blocks upstream sync, code review, and confident maintenance of the
custom logic.

The goal of this flow is exactly what v1's requirements originally said,
before the module-split tangent: (1) a complete, precise classification
of every legacy file as newly-authored, modified, or unmodified relative
to upstream (**already done** — see `02-specifications.md`, carried
forward from v1 verbatim), and (2) populate
`libsCpp/asterisk-chan-svistok/src` so that it contains **only** new and
modified code, at function granularity, with everything unmodified
continuing to execute via the upstream (`asterisk-chan-dongle`)
implementation rather than being duplicated — **a single module's worth
of output, not a multi-module split.**

## Known Technical Constraint (learned the hard way in a sibling effort)

Attempting to literally delete every `UNCHANGED`-classified function body
from a modified file does not work for this codebase: most `UNCHANGED`
functions are declared `static` and are still called by surviving
(`MODIFIED`) code in the same file — `static` linkage means the compiled
object can't resolve that call against a different translation unit no
matter what wrapper/direct-link mechanism is chosen. This was discovered
empirically (not theoretically) while attempting exactly this operation
on this same legacy codebase. Whatever this flow's Plan phase proposes
for populating `src/` must account for this constraint up front rather
than discover it the same way.

## Prior Work / Related Flows

- `flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok/` — a separate,
  earlier flow that already populated `libsCpp/asterisk-chan-svistok/src`
  using its own AST-slicing/bridge-generation tooling. Per v1's
  requirements, this is reference material to validate against, not a
  pre-approved answer — that stance carries forward unchanged here.
- `flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok-chan-dongle/`
  ("v1") — superseded by this flow. Its classification is reused; its
  module-split direction is not.
- `flows/sdd-res-simbox/` and `libsCpp/asterisk-res-simbox-*/` — **out of
  scope**, not to be read, referenced, or modified by this flow.

## User Stories

**As a** maintainer of `asterisk-chan-svistok`
**I want** `libsCpp/asterisk-chan-svistok/src` to contain only new and
modified code, with unmodified functions calling straight into
`libsCpp/asterisk-chan-svistok/asterisk-chan-dongle`'s implementation
**So that** the custom codebase stays small, readable, and easy to diff
against upstream in the future.

**As a** maintainer
**I want** functions that exist in Svistok but never existed in
chan_dongle placed in their own dedicated files (where that's actually
achievable without breaking internal linkage — see Known Technical
Constraint)
**So that** genuinely new functionality is never mixed into files whose
purpose is to adapt/override existing chan_dongle functions.

## Acceptance Criteria

### Must Have

1. **Given** the already-completed classification in `02-specifications.md`
   **When** this flow's Plan is drafted
   **Then** the plan explicitly states, per file, whether function-level
   trimming is safe (no internally-referenced `static` `UNCHANGED`
   functions) or whether the file must be carried whole (per the Known
   Technical Constraint) — decided file-by-file, not assumed uniformly.

2. **Given** a file classified as "new" (written from scratch for
   Svistok, no upstream counterpart)
   **When** it is brought into the working tree
   **Then** it is copied as-is into `libsCpp/asterisk-chan-svistok/src`
   (never rewritten from memory).

3. **Given** a file classified as "modified"
   **When** it is brought into `src`
   **Then** it is first copied verbatim from legacy (never retyped), and
   trimmed to modified/new content only **only where safe** per criterion
   1; otherwise carried whole, with the reason logged.

4. **Given** a function that exists in chan_svistok but has no
   counterpart in chan_dongle, in a file that's safe to trim
   **When** it is ported into `src`
   **Then** it is placed in a dedicated file separate from files that
   deal with modified/proxied chan_dongle functions.

5. **Given** a file whose only content, after applying criteria 1-4, is
   forwarding calls through to `asterisk-chan-dongle`
   **When** the restructuring is complete
   **Then** that file lives under `libsCpp/asterisk-chan-svistok/src/dongle`.
   (Per v1's analysis, this bucket is expected to end up empty or
   near-empty for the core module files — noting the expectation rather
   than assuming it must be populated.)

### Won't Have (This Iteration)

- Anything under `libsCpp/asterisk-res-simbox-*/` or `flows/sdd-res-simbox/`
  — explicitly out of scope.
- Modifying `legacy/` (read-only) or `vendor/` (read-only).
- Runtime/hardware verification — no compatible environment available.

## Constraints

- Comparison baseline: `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle`
  (bg111-derived), consistent with v1.
- Read-only legacy: all content copied, never retyped from memory.
- Scope boundary: this flow's deliverable is
  `libsCpp/asterisk-chan-svistok/` only. Nothing under
  `libsCpp/asterisk-res-simbox-*/` is this flow's concern.

## Open Questions

- [ ] Reconcile vs. validate `sdd-asterisk-chan-svistok`'s existing
      `libsCpp/asterisk-chan-svistok/src/` content, or produce this
      flow's own output independently and compare after the fact? (Same
      open question v1 never fully resolved — carried forward, not
      re-litigated here without user input.)

## References

- `legacy/asterisk-chan-svistok-v2014/` — read-only legacy source.
- `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle/` — upstream
  reference, diff baseline.
- `libsCpp/asterisk-chan-svistok/src/` — target directory, this flow's
  deliverable.
- `flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok-chan-dongle/` —
  v1, source of the carried-forward classification.

---

## Approval

- [x] Reviewed by: Anton
- [x] Approved on: 2026-08-26
- [x] Notes: approved alongside specifications in the same message
      ("Отлично. Approved").
