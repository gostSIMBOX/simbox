# Requirements: Split Library and Example

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-03-15

## Problem Statement

The current project is a monolithic Flutter application that combines library code (GSM<->SIP, GSM<->SMPP, SMS<->SMPP functionality) with the example application. This makes it difficult to:
- Reuse the core functionality in other projects
- Test the library independently
- Publish as a package on pub.dev

**Why this matters**: Separating library from example enables code reuse and proper package distribution.

## User Stories

### Primary

**As a** developer
**I want** the core GSM/SIP/SMPP functionality extracted into a separate Flutter library package
**So that** I can reuse it in other projects and publish it on pub.dev

### Secondary

**As a** developer
**I want** the full current application moved to `flutter_gsmsip/example/`
**So that** all functionality is preserved and users can see a complete working example

## Acceptance Criteria

### Must Have

1. **Given** a new Flutter library package `flutter_gsmsip`
   **When** created with `flutter create --template=package`
   **Then** it has proper package structure (lib/, test/, pubspec.yaml)

2. **Given** the library code
   **When** examining what was moved
   **Then** it contains GSM<->SIP, GSM<->SMPP, SMS<->SMPP core logic

3. **Given** the example app
   **When** examining the structure
   **Then** it's located at `flutter_gsmsip/example/` and uses the library via dependency

4. **Given** the example app
   **When** running `flutter run`
   **Then** it works as before but calls library functions instead of internal code

### Should Have

- Library has clean API surface for external consumption
- Example app demonstrates all major library features
- Documentation for library public API

### Won't Have (This Iteration)

- Publishing to pub.dev
- Breaking changes to functionality
- New features beyond the split

## Constraints

- **Technical**: Library must be a **Flutter plugin** (not just package) because it contains Kotlin/Java native code and PJSIP
- **Platform**: Android only (with native Kotlin/Java code in library)
- **PJSIP**: The PJSIP integration (native SIP stack) stays in the library's Android module
- **Native Code Location**: `flutter_gsmsip/android/` contains Kotlin/Java code
- **Dart API**: Library exposes clean Dart API that wraps native calls
- **Dependencies**: Library should minimize Dart dependencies for easier adoption

## Open Questions

- [x] Should the library include UI widgets or be headless only? **ANSWERED**: Library is headless, UI stays in example
- [x] What is the exact boundary between library and example code? **ANSWERED**: Domain+Data+Native in library, Presentation+UI in example
- [x] Should we keep the current app name or rename in example? **ANSWERED**: Keep current app, move entire app to example/

## References

- Current project: `GOSTsimbox_androidgateway`
- Target library: `flutter_gsmsip`

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]
