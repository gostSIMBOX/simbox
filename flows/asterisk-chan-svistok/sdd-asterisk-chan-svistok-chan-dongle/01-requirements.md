# Requirements: asterisk-chan-svistok-chan-dongle

> Version: 1.2
> Status: DRAFT
> Last Updated: 2026-08-26

## Problem Statement

`legacy/asterisk-chan-svistok-v2014` is a historical fork of
`asterisk-chan-dongle` (the `bg111` variant, now mirrored read-only at
`vendor/asterisk-chan-dongle-bg111` and, as a working copy, at
`libsCpp/asterisk-chan-svistok/asterisk-chan-dongle`). Over time,
project-specific ("Svistok") code was mixed directly into the same files as
the unmodified upstream `chan_dongle` code, with no separation between the
two. This makes it impossible to tell, file by file or function by function,
what is genuinely custom vs. what is untouched upstream — which blocks
upstream sync, code review, and any confident maintenance of the custom
logic.

The legacy tree is read-only and must not be written to. A clean upstream
reference now exists at `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle`.
The goal of this flow is to (1) produce a complete, precise classification of
every legacy file as newly-authored, modified, or unmodified relative to that
upstream reference, and (2) populate `libsCpp/asterisk-chan-svistok/src` so
that it contains **only** new and modified code — at function granularity,
not file granularity — with everything unmodified continuing to execute via
the upstream (`asterisk-chan-dongle`) implementation rather than being
duplicated.

## Prior Work / Related Flow

**Important context**: an existing SDD flow,
`flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok/`, already covers this
same problem space in extensive depth (IMPLEMENTATION phase, last touched
2026-08-26) and its own context notes describe essentially this same
follow-up request (function/file separation, `src/dongle` for pure proxies,
dedicated files for Svistok-only functions). It has already produced:

- A file inventory partitioning the legacy tree into included/excluded paths.
- Tooling under `libsCpp/asterisk-chan-svistok/tools/` (AST slicing, bridge
  generation, ownership/provenance verification, etc.).
- A populated `libsCpp/asterisk-chan-svistok/src/` tree, including
  `src/dongle/`, `src/svistok/`, `src/programmator/`, `src/simnode/`
  subdirectories with real content.
- Manifests under `libsCpp/asterisk-chan-svistok/manifests/` recording
  ownership/classification decisions.

The user has explicitly chosen to open this as a **separate, new** flow
rather than resuming the existing one. This flow should treat the existing
work as a reference/starting point to inspect and validate — not as a
pre-approved answer — since the exact deliverable here (full file list;
function-level src/ vs src/dongle/ split; new-vs-modified handling) needs to
be independently verified against the actual legacy and upstream sources.
Whether/how to reconcile the two flows (reuse the existing manifests and
`src/` output vs. redo independently) is an open question below.

## Module Split — Moved

**2026-08-26**: the three-module split (`res_simbox_core`/
`res_simbox_discovery`/`res_simbox_programmator`) that was drafted here as
a "Version 1.1 Revision" has been **moved to its own dedicated flow**,
`flows/sdd-res-simbox/`, per explicit user request ("все спеки и reqs что
связаны с res-simbox-* перенеси из предыдущего флоу в новый"). See that
flow's `01-requirements.md` for the full problem statement, decisions,
user stories, acceptance criteria, and open questions about the module
split.

This flow retains ownership of the underlying file/function
classification (which legacy code is new/modified/unmodified relative to
upstream `chan_dongle`) — that work is unaffected by the module split and
is what `sdd-res-simbox` builds on.

## User Stories

### Primary

**As a** maintainer of `asterisk-chan-svistok`
**I want** a complete, verified list of which legacy files were written from
scratch and which were modified from the upstream `chan_dongle` (bg111)
baseline
**So that** I know the true scope of custom code before restructuring it.

**As a** maintainer
**I want** `libsCpp/asterisk-chan-svistok/src` to contain only new and
modified code, with unmodified functions calling straight into
`libsCpp/asterisk-chan-svistok/asterisk-chan-dongle`'s implementation
**So that** the custom codebase stays small, readable, and easy to diff
against upstream in the future.

### Secondary

**As a** maintainer
**I want** functions that exist in Svistok but never existed in chan_dongle
placed in their own dedicated files
**So that** genuinely new functionality is never mixed into files whose
purpose is to adapt/override existing chan_dongle functions.

**As a** maintainer
**I want** files whose only job is to proxy calls through to
`asterisk-chan-dongle` (no new or changed logic at all) moved to
`src/dongle/`, separate from files that hold real Svistok-specific code
**So that** the directory layout itself communicates what is a pure pass-
through vs. what is actual custom implementation.

## Acceptance Criteria

### Must Have

1. **Given** the legacy tree `legacy/asterisk-chan-svistok-v2014` and the
   upstream reference `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle`
   **When** every legacy source/header file relevant to the channel module is
   compared against its upstream counterpart
   **Then** a complete list is produced classifying each file as: new
   (no upstream counterpart), modified (upstream counterpart with
   differences), or unmodified (identical to upstream) — with the modified
   list broken down further to the function level (which functions changed,
   which stayed identical, which are wholly new).

2. **Given** a file classified as "new" (written from scratch for Svistok)
   **When** it is brought into the working tree
   **Then** it is copied as-is into `libsCpp/asterisk-chan-svistok/src`
   (never rewritten from memory).

3. **Given** a file classified as "modified" (some functions changed, some
   unchanged, relative to upstream)
   **When** it is brought into `libsCpp/asterisk-chan-svistok/src`
   **Then** it is first copied verbatim from the legacy source (never
   retyped/rewritten), and then trimmed so that only new/modified functions
   (and whatever they require: types, static helpers, etc.) remain in the
   file's body; every function that is identical to upstream is **not**
   duplicated in `src` — callers instead invoke the corresponding function
   from `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle` directly (e.g.
   `app_register()` in `src/app.c` calls the upstream `app_register()`
   rather than redefining it).

4. **Given** a function that exists in both chan_dongle and chan_svistok, but
   where Svistok only *appends* extra behavior around the original logic
   (rather than replacing it outright)
   **When** it is ported into `src`
   **Then** the ported version runs both the added Svistok-specific logic
   *and* invokes the original upstream function — it does not duplicate the
   upstream function's body.

5. **Given** a function that exists in chan_svistok but has no counterpart at
   all in chan_dongle
   **When** it is ported into `src`
   **Then** it is placed in a dedicated file separate from files that deal
   with modified/proxied chan_dongle functions.

6. **Given** a file in `src` whose only content is forwarding calls through
   to `asterisk-chan-dongle` (i.e., it has no new or modified logic of its
   own after the trimming in criteria 2–5)
   **When** the restructuring is complete
   **Then** that file lives under `libsCpp/asterisk-chan-svistok/src/dongle`,
   not directly under `src/`.

### Should Have

- Traceability from each function in `src` back to its legacy origin (e.g. a
  manifest, comment, or table) so the classification can be audited later.

### Won't Have (This Iteration)

- Modifying anything under `legacy/` (strictly read-only).
- Modifying `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle` (the
  upstream reference tree) beyond what's needed to expose symbols for the
  proxy calls (e.g. header visibility), if anything.
- Runtime/hardware verification (compiling and running against a real
  Asterisk + modem) — out of scope for this flow unless the user asks
  otherwise later.

## Constraints

- **Technical**: comparison baseline is specifically
  `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle` (the bg111-derived
  copy), not the other vendor forks (`wdoekes`, `pulpoff`).
- **Read-only legacy**: nothing under `legacy/` may be written to; all
  legacy content needed in `src` must be copied, never retyped from memory.
- **Granularity**: the new/modified vs. unmodified split must be applied at
  function level within a file, not just file level — a "modified" file
  should end up in `src` containing only its new/changed functions, not the
  full original file body.
- **Dependencies**: this flow must reconcile with (or explicitly diverge
  from) the existing `sdd-asterisk-chan-svistok` flow's in-progress work in
  the same `libsCpp/asterisk-chan-svistok/src` and `asterisk-chan-dongle`
  directories (see "Prior Work / Related Flow" above).

## Open Questions

- [x] **Resolved 2026-08-26**: independent classification/restructuring from
      scratch — do not reuse the sibling flow's tooling or manifests as
      ground truth.
- [x] **Resolved 2026-08-26**: full scope — the entire legacy tree, "code
      and builds and everything," not just `chan_svistok.so`'s build
      closure. See `02-specifications.md` for the complete inventory this
      produced (source, build system, standalone tools, dead code, junk).
- [ ] What should happen to `src` content the *other* flow already placed,
      given this flow's independent classification may disagree with it in
      places (not deeply cross-checked yet)?
- [ ] Desired mechanism for "unmodified function calls upstream directly" —
      direct link against `asterisk-chan-dongle`'s compiled objects (no
      wrapper code) vs. generated thin-wrapper `.c` files. See
      `02-specifications.md`'s "Open Design Questions" for the full
      trade-off writeup.

## References

- `legacy/asterisk-chan-svistok-v2014/` — read-only legacy source (mixed
  Svistok + chan_dongle code).
- `vendor/asterisk-chan-dongle-bg111/` — read-only vendor reference (bg111
  fork of chan_dongle).
- `libsCpp/asterisk-chan-svistok/asterisk-chan-dongle/` — working copy of the
  upstream bg111 code, used as the diff baseline.
- `libsCpp/asterisk-chan-svistok/src/` — target directory for new/modified
  Svistok code (this flow's deliverable).
- `flows/asterisk-chan-svistok/sdd-asterisk-chan-svistok/` — prior/parallel
  flow covering the same problem space; see "Prior Work / Related Flow".

---

## Approval

- [ ] Reviewed by: Anton
- [ ] Approved on:
- [ ] Notes:
