# Specifications: Native Bridge Module Testing

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-03-04
> Requirements: [[01-requirements.md](01-requirements.md)](01-requirements.md)

## Overview

This specification defines the test strategy for fixing and validating the React Native native bridge module. Tests will be written **before** fixes (TDD approach) to ensure correctness.

## Affected Systems

| System | Impact | Notes |
|--------|--------|-------|
| ForegroundBackground.js | Modify | Fix module name references |
| ForegroundBackgroundModule.java | Modify | Implement toBackground(), fix getName() |
| ForegroundBackgroundModulePackage.java | No change | Package registration is correct |
| Test files | Create | New test files for JS and Java |

## Architecture

### Component Diagram

```
┌─────────────────────┐
│  JavaScript (JS)    │
│  - toForeground()   │
│  - toBackground()   │
└──────────┬──────────┘
           │ React Native Bridge
           ▼
┌─────────────────────┐
│  Native Module      │
│  ForegroundBackgroundModule
│  - getName()        │
│  - toForeground()   │
│  - toBackground()   │
└──────────┬──────────┘
           │ Android APIs
           ▼
┌─────────────────────┐
│  Android System     │
│  - PowerManager     │
│  - Intent           │
│  - Activity         │
└─────────────────────┘
```

### Data Flow

```
JS Call → NativeModules lookup → @ReactMethod invocation → Android API → Result/Callback
```

## Interfaces

### Current Interface (JavaScript)

```javascript
export default class ForegroundBackground {
  toForeground(): void;  // Calls NativeModules.ForegroundBackground
  toBackground(): void;  // Calls NativeModules.ReplaceDialerModule (BUG)
}
```

### Current Interface (Java)

```java
public class ForegroundBackgroundModule extends ReactContextBaseJavaModule {
    @Override
    public String getName() { return "ForegroundBackgroundModule"; }
    
    @ReactMethod
    public void toForeground() { /* implemented */ }
    
    @ReactMethod
    public void toBackground() { /* EMPTY - BUG */ }
}
```

### Required Interface (After Fixes)

```java
@ReactMethod
public void toBackground() {
    // Implement background transition
    // Add Promise callback for async completion
}

@ReactMethod
public void toForeground(Promise promise) {
    // Add Promise for async completion
}
```

## Behavior Specifications

### Happy Path: toForeground()

1. JavaScript calls `ForegroundBackground.toForeground()`
2. React Native bridge looks up `ForegroundBackgroundModule`
3. Native `toForeground()` method executes
4. PowerManager.WakeLock wakes screen
5. MainActivity launches with FLAG_ACTIVITY_NEW_TASK
6. App appears in foreground

### Happy Path: toBackground() (TO BE IMPLEMENTED)

1. JavaScript calls `ForegroundBackground.toBackground()`
2. React Native bridge looks up `ForegroundBackgroundModule`
3. Native `toBackground()` method executes
4. App moves to background (moveTaskToBack)
5. Optional: Release WakeLock if held

### Edge Cases

| Case | Trigger | Expected Behavior |
|------|---------|-------------------|
| Module name mismatch | JS looks up wrong module name | Should find module by correct name |
| MainActivity not found | Class.forName() fails | Log error, don't crash |
| WakeLock timeout | Operation takes >10s | WakeLock releases automatically |
| App already in foreground | User calls toForeground() | No error, idempotent |

### Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| ClassNotFoundException | MainActivity class not found | Log warning, continue |
| SecurityException | Missing permissions | Log error, reject Promise |
| ActivityNotFoundException | Can't launch activity | Log error, reject Promise |

## Dependencies

### Requires

- React Native testing framework (Jest)
- Android testing framework (JUnit, Mockito)
- PowerMock for PowerManager mocking

### Blocks

- Application cannot reliably use foreground/background features until tests pass

## Testing Strategy

### Unit Tests (JavaScript)

- [ ] Module name resolution test
- [ ] Method existence test
- [ ] Promise rejection test (when native fails)

### Unit Tests (Java)

- [ ] getName() returns correct module name
- [ ] toForeground() calls WakeLock.acquire()
- [ ] toForeground() launches MainActivity
- [ ] toBackground() calls moveTaskToBack()
- [ ] Error handling in try-catch blocks

### Integration Tests

- [ ] Full foreground/background cycle
- [ ] Multiple rapid calls (debouncing)
- [ ] App lifecycle during transitions

### Manual Verification

- [ ] Test on physical Android device
- [ ] Verify screen wake behavior
- [ ] Verify app transition smoothness

## Open Design Questions

- [ ] Should toBackground() be implemented or removed from API?
- [ ] Should both methods use Promises or keep fire-and-forget?
- [ ] What timeout value for WakeLock (current: 10s)?

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]
