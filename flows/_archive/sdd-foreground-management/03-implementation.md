# Foreground Management Implementation Log

**Flow**: sdd-foreground-management
**Date**: 2026-03-06
**Status**: IMPLEMENTED

---

## Tasks Completed

### fg-001: Implement ForegroundService (lifecycle management)

**File**: `lib/services/foreground_service.dart`

**Implementation Details**:

- Created `ForegroundService` singleton class
- Implemented MethodChannel communication with native Android (`gsm_sip_gateway/foreground`)
- Added service state enumeration: `stopped`, `starting`, `foreground`, `background`, `error`
- Created `ForegroundNotificationConfig` class for notification customization
- Implemented stream-based state monitoring
- Added logging via `logger` package

**Key Methods**:
- `initialize()` - Sets up method channel handler
- `start()` - Starts foreground service with notification
- `stop()` - Stops foreground service
- `toForeground()` - Brings app to foreground (for incoming calls)
- `toBackground()` - Moves app to background
- `updateNotification()` - Updates foreground notification
- `releaseWakeLock()` - Releases wake lock if held
- `isSupported()` - Checks foreground service support

**Data Models**:
- `ForegroundServiceState` enum
- `ForegroundNotificationConfig` class

---

### fg-002: Implement service lifecycle (start/stop/background/foreground)

**File**: `lib/services/foreground_service.dart`

**Implementation Details**:

- Implemented complete lifecycle management
- State machine: `stopped` → `starting` → `foreground` ↔ `background` → `stopped`
- Wake lock management for screen wake during incoming calls
- Notification management for foreground service requirement
- Uptime tracking

**Lifecycle Flow**:
```
App Start
    │
    ▼
initialize()
    │
    ▼
start(notificationConfig)
    │
    ▼
[Service Running in Foreground]
    │
    ├── toBackground() ──► [Background State]
    │                           │
    │                           ▼
    │                      toForeground()
    │                           │
    │                           ▼
    └───────────────────── [Foreground State]
                                │
                                ▼
                           stop()
                                │
                                ▼
                         [Stopped State]
```

**State Transitions**:
| From | To | Trigger |
|------|-----|---------|
| stopped | starting | `start()` called |
| starting | foreground | Native service started |
| foreground | background | `toBackground()` called |
| background | foreground | `toForeground()` called |
| foreground | stopped | `stop()` called |
| background | stopped | `stop()` called |
| any | error | Exception occurred |

---

## Integration Points

### With Existing Services

| Service | Integration | Status |
|---------|-------------|--------|
| TelephonyService | None (independent) | N/A |
| SipService | None (independent) | N/A |
| GatewayService | None (independent) | N/A |

### With Native Android

| Method Channel | Purpose | Status |
|----------------|---------|--------|
| `gsm_sip_gateway/foreground` | Service control | Requires native implementation |
| `startForeground` | Start service | Requires native implementation |
| `stopForeground` | Stop service | Requires native implementation |
| `toForeground` | Bring to foreground | Requires native implementation |
| `toBackground` | Move to background | Requires native implementation |
| `updateNotification` | Update notification | Requires native implementation |
| `releaseWakeLock` | Release wake lock | Requires native implementation |
| `isForegroundServiceSupported` | Check support | Requires native implementation |

---

## Design Decisions

### 1. Notification Configuration Object
**Decision**: Create `ForegroundNotificationConfig` class

**Rationale**:
- Android requires notification for foreground services
- Configurable title, content, priority
- Consistent with service pattern

### 2. Default Timeout (10 seconds)
**Decision**: Use 10000ms as default wake lock timeout

**Rationale**:
- Matches existing implementation pattern
- Sufficient for screen wake during incoming call
- Prevents battery drain if not released

### 3. State Stream Broadcasting
**Decision**: Use `StreamController.broadcast()` for state changes

**Rationale**:
- Multiple components may need state updates
- Consistent with existing services
- Reactive programming pattern

### 4. Wake Lock Tracking
**Decision**: Track wake lock state locally

**Rationale**:
- Prevent redundant release calls
- Enable status reporting
- Debugging support

---

## Notification Configuration

### Default Configuration
```dart
const ForegroundNotificationConfig(
  title: 'Gateway Service',
  content: 'Running in background',
  ongoing: true,
  showWhen: false,
)
```

### Custom Configuration Example
```dart
ForegroundNotificationConfig(
  title: 'Incoming Call',
  content: 'Call from +1234567890',
  channelId: 'calls',
  priority: 1, // High priority
  showWhen: true,
  ongoing: true,
  autoCancel: false,
)
```

---

## Use Cases

### Incoming Call Scenario
```dart
// When incoming call received
final foregroundService = ForegroundService();

// Wake device and bring app to foreground
await foregroundService.toForeground(timeout: 10000);

// Update notification with call info
await foregroundService.updateNotificationTitle('Incoming Call');
await foregroundService.updateNotificationContent('Call from $number');

// After call ends
await foregroundService.toBackground();
```

### Background Service Scenario
```dart
// Start persistent background service
final foregroundService = ForegroundService();
await foregroundService.start(
  notificationConfig: const ForegroundNotificationConfig(
    title: 'Gateway Active',
    content: 'Monitoring for calls',
    ongoing: true,
  ),
);
```

---

## Testing Recommendations

### Unit Tests
- [ ] State transitions
- [ ] Notification config serialization
- [ ] Uptime calculation
- [ ] getStatus() output

### Integration Tests
- [ ] Service start/stop cycle
- [ ] Foreground/background transitions
- [ ] Notification updates

### Manual Tests
- [ ] Screen wake from sleep
- [ ] App background/foreground transitions
- [ ] Notification visibility
- [ ] Wake lock timeout behavior

---

## Native Android Requirements

### ForegroundBackgroundModule.java (Reference)
Based on existing implementation pattern:

```java
@ReactMethod
public void toForeground(Promise promise) {
    new HandlerThread("ForegroundThread",
        Process.THREAD_PRIORITY_FOREGROUND).start();

    new Handler().post(() -> {
        try {
            // Acquire wake lock
            PowerManager.WakeLock wl = mPowerManager.newWakeLock(
                PowerManager.ACQUIRE_CAUSES_WAKEUP |
                PowerManager.ON_AFTER_RELEASE |
                PowerManager.PARTIAL_WAKE_LOCK,
                "incoming_call"
            );
            wl.acquire(10000);

            // Launch activity
            String ns = mContext.getPackageName();
            String cls = ns + ".MainActivity";
            Intent intent = new Intent(mContext, Class.forName(cls));
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK |
                           Intent.EXTRA_DOCK_STATE_CAR);
            intent.addCategory(Intent.CATEGORY_LAUNCHER);
            intent.putExtra("foreground", true);

            mContext.startActivity(intent);

            promise.resolve(true);
        } catch (Exception e) {
            promise.reject("FOREGROUND_ERROR", e.getMessage());
        }
    });
}

@ReactMethod
public void toBackground(Promise promise) {
    Activity activity = getCurrentActivity();
    if (activity != null) {
        activity.moveTaskToBack(true);
        promise.resolve(true);
    } else {
        promise.reject("NO_ACTIVITY", "No current activity");
    }
}
```

### AndroidManifest.xml
```xml
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<service
    android:name=".ForegroundService"
    android:foregroundServiceType="connectedDevice"
    android:exported="false" />
```

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `lib/services/foreground_service.dart` | ~350 | Complete service implementation |

---

## Issues/Notes

1. **Native Implementation Required**: Requires native Android code for all lifecycle operations
2. **API Level Considerations**: `PARTIAL_WAKE_LOCK` recommended over deprecated `FULL_WAKE_LOCK` (API 20+)
3. **CAR Mode**: `EXTRA_DOCK_STATE_CAR` flag included for automotive integration (configurable)
4. **Timeout Handling**: Fixed 10s timeout may need adjustment based on use case
5. **Future Enhancement**: Promise-based callbacks for async operations
6. **Future Enhancement**: WindowManager integration for modern screen wake (API 27+)

---

*Implementation completed: 2026-03-06*
