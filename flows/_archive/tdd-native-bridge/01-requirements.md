# Requirements: Native Bridge Module Testing

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-03-04
> Source: Legacy Analysis (/legacy command)

## Problem Statement

The native bridge module has **critical bugs** discovered during legacy analysis:

1. **Module Name Mismatch**: JavaScript expects `NativeModules.ReplaceDialerModule` but native module registers as `ForegroundBackgroundModule`
2. **Empty Implementation**: `toBackground()` method has no implementation
3. **No Error Handling**: Methods are fire-and-forget with no callbacks/promises for async completion

These bugs will cause runtime failures and need to be fixed with test coverage to prevent regressions.

## User Stories

### Primary

**As a** React Native developer
**I want** reliable native module bridge methods
**So that** I can bring app to foreground/background without runtime errors

### Secondary

**As a** QA engineer
**I want** comprehensive test coverage for the bridge
**So that** I can verify fixes don't introduce regressions

## Acceptance Criteria

### Must Have

1. **Given** JavaScript calls `toForeground()`
   **When** Native module is invoked
   **Then** Activity launches with correct flags and screen wakes up

2. **Given** JavaScript calls `toBackground()`
   **When** Native module is invoked
   **Then** App moves to background without errors

3. **Given** Module name lookup
   **When** JavaScript accesses `NativeModules.ForegroundBackground`
   **Then** Module is found and methods are callable

4. **Given** An error occurs during native operation
   **When** Exception is thrown
   **Then** Error is caught and logged appropriately

### Should Have

- Promise-based async handling for completion callbacks
- Unit tests for each native method
- Integration tests for full foreground/background cycle

### Won't Have (This Iteration)

- iOS implementation (Android-only library)
- Custom UI view managers

## Constraints

- **Technical**: Must work with React Native 0.40.0+
- **Platform**: Android-only
- **Dependencies**: Requires Android SDK, React Native bridge
- **Testing**: Jest for JS tests, JUnit for Java tests

## Open Questions

- [ ] Should toBackground() have a complete implementation or is it intentionally empty?
- [ ] Should methods return Promises for async completion handling?
- [ ] What is the expected behavior if MainActivity class is not found?

## References

- Legacy analysis: `flows/legacy/understanding/native-bridge/`
- Source: `src/ForegroundBackground.js`, `android/app/src/main/java/.../ForegroundBackgroundModule.java`

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]
