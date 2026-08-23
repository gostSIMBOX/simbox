# ADR-001: Activity Result Handling for setDefaultDialer

**Date**: 2026-03-04
**Status**: DRAFT
**Type**: Enabling (fix will enable correct functionality)
**Author**: /legacy analysis

## Context

The `setDefaultDialer()` method in `ReplaceDialerModule.java` is responsible for requesting that the app become the system's default dialer. This operation requires:

1. Launching a system activity that presents the user with a dialog to select the default dialer
2. Waiting for the user's selection
3. Reporting the result back to the JavaScript layer

The React Native bridge pattern supports asynchronous operations via:
- **Callbacks**: Functions passed from JS to native, invoked with results
- **Promises**: Alternative pattern for async operations (not currently used)

## Problem

The current implementation has a critical bug where the callback is invoked immediately with `true` before the system activity result is received.

**Current Implementation**:
```java
@ReactMethod
public void setDefaultDialer(Callback myCallback) {
    setCallback = myCallback;
    Intent intent = new Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER);
    this.mContext.startActivityForResult(intent, RC_DEFAULT_PHONE, new Bundle());
    myCallback.invoke(true);  // BUG: Invoked immediately!
}
```

**Evidence of Known Issue**:
- Commented-out `ActivityEventListener` interface implementation in source code
- Commented-out `onActivityResult()` method
- Static callback field that is never cleared

## Decision

### Current State (Documenting Existing Decision)

The original implementation chose to:
1. Use callback-based async pattern (not Promises)
2. Store callback in static field for later use
3. **Not complete** the activity result handling implementation

**Rationale** (inferred):
- Callback pattern aligns with React Native patterns at time of writing
- Static callback simplifies access from lifecycle methods
- Implementation may have been incomplete due to time constraints or complexity

### Required Fix (Proposed Decision)

**Implement proper activity result handling**:

1. **Implement ActivityEventListener interface**:
```java
public class ReplaceDialerModule extends ReactContextBaseJavaModule 
    implements ActivityEventListener {
```

2. **Register listener in constructor**:
```java
public ReplaceDialerModule(ReactApplicationContext context) {
    super(context);
    this.mContext = context;
    this.mContext.addActivityEventListener(this);
}
```

3. **Remove immediate callback invocation**:
```java
@ReactMethod
public void setDefaultDialer(Callback myCallback) {
    setCallback = myCallback;
    Intent intent = new Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER);
    this.mContext.startActivityForResult(intent, RC_DEFAULT_PHONE, new Bundle());
    // Do NOT invoke callback here
}
```

4. **Handle activity result**:
```java
@Override
public void onActivityResult(int requestCode, int resultCode, Intent data) {
    if (requestCode == RC_DEFAULT_PHONE) {
        if (resultCode == Activity.RESULT_OK) {
            setCallback.invoke(true);
        } else {
            setCallback.invoke(false);  // Handle cancellation/failure
        }
        setCallback = null;  // Clear to prevent memory leaks
    }
}
```

5. **Clean up in invalidate()**:
```java
@Override
public void invalidate() {
    if (setCallback != null) {
        setCallback.invoke(false);  // Or timeout handling
        setCallback = null;
    }
}
```

## Consequences

### Current Implementation (Buggy)

**Positive**:
- Method returns immediately (non-blocking)
- No crash or exception

**Negative**:
- ❌ Callback always reports success (`true`)
- ❌ No way to detect user cancellation
- ❌ No way to detect failure
- ❌ Misleads application code into thinking operation succeeded
- ❌ Static callback field can cause memory leaks
- ❌ Not thread-safe (concurrent calls would overwrite callback)

### After Fix

**Positive**:
- ✅ Accurate result reporting (success/failure)
- ✅ Proper handling of user cancellation
- ✅ Memory leak prevention (callback cleared after use)
- ✅ Thread-safe operation (single callback per request)
- ✅ Aligns with Android activity lifecycle best practices

**Negative/Risks**:
- ⚠️ Breaking change for existing consumers (they may rely on current behavior)
- ⚠️ Requires testing across Android versions
- ⚠️ Need to handle edge cases:
  - Activity destroyed before result
  - Multiple concurrent `setDefaultDialer()` calls
  - Timeout handling

**Migration Path**:
- Increment major version (e.g., 0.0.11 → 1.0.0)
- Document breaking change in changelog
- Provide migration guide for consumers

## Related Decisions

- **ADR-002**: Callback vs Promise pattern (to be documented)
- **ADR-003**: Minimum Android API level selection (API 21, full features on API 23+)

## References

- [React Native Native Modules](https://reactnative.dev/docs/native-modules-android)
- [Android Activity Result Handling](https://developer.android.com/training/basics/intents/result)
- [TelecomManager.ACTION_CHANGE_DEFAULT_DIALER](https://developer.android.com/reference/android/telecom/TelecomManager#ACTION_CHANGE_DEFAULT_DIALER)
- Source code: `android/app/src/main/java/one/telefon/replacedialer/ReplaceDialerModule.java`

---

*Generated by /legacy analysis on 2026-03-04*
