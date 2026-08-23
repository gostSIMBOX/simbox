# Requirements: Foreground Management Module

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-03-04
> Source: Legacy Analysis (/legacy command)

## Problem Statement

The foreground management module handles bringing the React Native app to foreground from background state, designed for **incoming call scenarios**. The current implementation uses deprecated Android APIs and needs modernization.

**Current Issues:**
1. Uses deprecated `FULL_WAKE_LOCK` (deprecated since API 20)
2. Fixed 10-second timeout may be insufficient
3. `EXTRA_DOCK_STATE_CAR` flag usage needs documentation
4. Error handling is minimal (log and continue)

## User Stories

### Primary

**As a** VoIP/telecom app developer
**I want** to bring my app to foreground when receiving a call
**So that** users can answer incoming calls even when device is idle

### Secondary

**As a** automotive integration developer
**I want** the app to work with Android Auto / car mode
**So that** calls can be handled while driving

**As a** developer
**I want** modern Android API usage
**So that** the library works reliably on newer Android versions

## Acceptance Criteria

### Must Have

1. **Given** App is in background and device is idle
   **When** `toForeground()` is called
   **Then** App launches to foreground and screen wakes up

2. **Given** App is in foreground
   **When** `toBackground()` is called (TO BE IMPLEMENTED)
   **Then** App moves to background smoothly

3. **Given** An error occurs during transition
   **When** Exception is thrown
   **Then** Error is logged and handled gracefully

4. **Given** Device running Android API 20+
   **When** WakeLock is acquired
   **Then** Modern API alternatives are used (not FULL_WAKE_LOCK)

### Should Have

- Configurable timeout for WakeLock
- Completion callbacks for async operations
- Documentation for CAR mode usage

### Won't Have (This Iteration)

- iOS implementation (Android-only)
- Custom UI components for incoming call screen

## Constraints

- **Technical**: Must work with React Native 0.40.0+
- **Platform**: Android-only (API 21+)
- **Performance**: Screen wake within 1 second
- **Dependencies**: Android PowerManager, ActivityManager

## Open Questions

- [ ] Should `EXTRA_DOCK_STATE_CAR` be configurable or removed?
- [ ] What is the optimal WakeLock timeout value?
- [ ] Should modern alternatives use WindowManager instead of WakeLock?

## References

- Legacy analysis: `flows/legacy/understanding/foreground-management/`
- Source: `android/app/src/main/java/.../ForegroundBackgroundModule.java`
- Android Docs: [PowerManager.WakeLock](https://developer.android.com/reference/android/os/PowerManager.WakeLock)

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]
