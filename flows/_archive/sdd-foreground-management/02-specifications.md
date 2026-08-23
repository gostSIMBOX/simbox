# Specifications: Foreground Management Module

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-03-04
> Requirements: [01-requirements.md](01-requirements.md)

## Overview

This specification documents the foreground management implementation for Android, including screen wake logic and activity launching. The module is designed for incoming call scenarios in telecom/VoIP applications.

## Affected Systems

| System | Impact | Notes |
|--------|--------|-------|
| ForegroundBackgroundModule.java | Modify | Modernize WakeLock usage |
| ForegroundBackground.js | No change | JavaScript API remains same |
| AndroidManifest.xml | May modify | May need additional permissions |

## Architecture

### Component Diagram

```
┌──────────────────────────┐
│  toForeground() Call     │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│  HandlerThread (Worker)  │
│  THREAD_PRIORITY_FOREGROUND │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│  PowerManager.WakeLock   │
│  - ACQUIRE_CAUSES_WAKEUP │
│  - ON_AFTER_RELEASE      │
│  - [FULL_WAKE_LOCK] →    │
│    [PARTIAL + WindowManager] │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│  Intent Launch           │
│  - FLAG_ACTIVITY_NEW_TASK│
│  - CATEGORY_LAUNCHER     │
│  - EXTRA_DOCK_STATE_CAR  │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│  MainActivity            │
│  - foreground extra flag │
└──────────────────────────┘
```

### Data Flow

```
JS Call → @ReactMethod → HandlerThread → WakeLock.acquire() → startActivity() → MainActivity
```

## Current Implementation

### WakeLock Acquisition (Lines 70-81)

```java
PowerManager.WakeLock wl = mPowerManager.newWakeLock(
    PowerManager.ACQUIRE_CAUSES_WAKEUP | 
    PowerManager.ON_AFTER_RELEASE | 
    PowerManager.FULL_WAKE_LOCK,  // DEPRECATED
    "incoming_call"
);
wl.acquire(10000);  // Fixed 10s timeout
```

### Activity Launch (Lines 53-66)

```java
String ns = mContext.getPackageName();
String cls = ns + ".MainActivity";

Intent intent = new Intent(mContext, Class.forName(cls));
intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.EXTRA_DOCK_STATE_CAR);
intent.addCategory(Intent.CATEGORY_LAUNCHER);
intent.putExtra("foreground", true);

mContext.startActivity(intent);
```

## Recommended Modernization

### WakeLock Alternative (API 20+)

```java
// Use PARTIAL_WAKE_LOCK with WindowManager
PowerManager.WakeLock wl = mPowerManager.newWakeLock(
    PowerManager.PARTIAL_WAKE_LOCK,
    "incoming_call"
);
wl.acquire(10000);

// Turn on screen via WindowManager
WindowManager.LayoutParams params = new WindowManager.LayoutParams(
    WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON |
    WindowManager.LayoutParams.FLAG_DISCARD_KEYGUARD |
    WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED |
    WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON
);
```

### toBackground() Implementation

```java
@ReactMethod
public void toBackground() {
    Activity activity = getCurrentActivity();
    if (activity != null) {
        activity.moveTaskToBack(true);
    }
}
```

## Behavior Specifications

### Happy Path: toForeground()

1. JavaScript calls `ForegroundBackground.toForeground()`
2. @ReactMethod invokes on HandlerThread
3. WakeLock acquired with timeout
4. MainActivity intent created with flags
5. Activity launched from background
6. Screen wakes up
7. App appears in foreground

### Happy Path: toBackground() (TO IMPLEMENT)

1. JavaScript calls `ForegroundBackground.toBackground()`
2. @ReactMethod invokes on main thread
3. `moveTaskToBack(true)` called
4. App moves to background
5. WakeLock released if held

### Edge Cases

| Case | Trigger | Expected Behavior |
|------|---------|-------------------|
| MainActivity not found | Class.forName() fails | Log error, continue with WakeLock |
| App already foreground | User calls toForeground() | Idempotent, no error |
| WakeLock timeout expires | Operation > 10s | Auto-release, prevent drain |
| Activity launch fails | startActivity() throws | Log warning, WakeLock still acquired |

### Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| ClassNotFoundException | MainActivity class not found | Log: "Failed to open application" |
| SecurityException | Missing permissions | Log error, reject if Promise-based |
| ActivityNotFoundException | Can't launch | Log error, continue |

## Dependencies

### Requires

- Android API 21+ (Android 5.0)
- React Native 0.40.0+
- PowerManager service
- Activity context

### Blocks

- None (core functionality)

## Integration Points

### External Systems

- Android PowerManager API
- Android ActivityManager

### Internal Systems

- React Native bridge (ForegroundBackgroundModule)
- MainActivity class

## Testing Strategy

### Unit Tests

- [ ] WakeLock acquisition with correct flags
- [ ] Activity launch with correct intent flags
- [ ] Error handling in try-catch blocks

### Integration Tests

- [ ] Full foreground transition on device
- [ ] Background transition on device
- [ ] WakeLock timeout behavior

### Manual Verification

- [ ] Test on physical Android device
- [ ] Verify screen wake from sleep
- [ ] Verify CAR mode behavior if used

## Migration / Rollout

### API Modernization Steps

1. Document current behavior (this spec)
2. Add tests for current behavior
3. Implement PARTIAL_WAKE_LOCK + WindowManager alternative
4. Test on multiple Android versions
5. Update documentation with CAR mode guidance

## Open Design Questions

- [ ] Keep EXTRA_DOCK_STATE_CAR or make configurable?
- [ ] Default timeout value (current: 10s)?
- [ ] Add Promise callbacks or keep fire-and-forget?

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]
