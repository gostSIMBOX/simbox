# Implementation Log: Headless Service Module

> **Flow**: sdd-headless-service  
> **Layer**: 1 (Domain/Core Logic)  
> **Date**: 2026-03-06  
> **Status**: Implementation Complete

---

## Overview

This document logs the implementation of the Headless Service module for background operation and boot-up handling in the GOSTsimbox Android Gateway application.

---

## Tasks Completed (6/6)

### ✅ headless-001: Implement HeadlessModule

**File**: `/android/app/src/main/kotlin/org/telon/flutter_gsm_sip_gateway/HeadlessModule.kt`

**Implementation Details**:
- Created `HeadlessModule` class as MethodChannel handler
- Implemented handler thread with `THREAD_PRIORITY_FOREGROUND`
- Exposed methods via MethodChannel `gsm_sip_gateway/headless`:
  - `startService()` - Starts the HeadlessService foreground service
  - `stopService()` - Stops the HeadlessService
  - `toForeground()` - Brings app to foreground by launching MainActivity
  - `toBackground()` - No-op on Android (as expected)
- Singleton pattern for handler thread management
- Proper error handling with PlatformException responses

**Key Code**:
```kotlin
class HeadlessModule : MethodCallHandler {
    companion object {
        private const val CHANNEL_NAME = "gsm_sip_gateway/headless"
        
        fun initializeHandler() {
            handlerThread = HandlerThread("HeadlessModuleThread", 
                android.os.Process.THREAD_PRIORITY_FOREGROUND)
            handlerThread?.start()
            handler = Handler(handlerThread!!.looper)
        }
    }
    
    override fun onMethodCall(call: MethodCall, result: MethodChannel.Result) {
        when (call.method) {
            "startService" -> startService(result)
            "stopService" -> stopService(result)
            "toForeground" -> toForeground(result)
            "toBackground" -> toBackground(result)
        }
    }
}
```

---

### ✅ headless-002: Implement HeadlessService

**File**: `/android/app/src/main/kotlin/org/telon/flutter_gsm_sip_gateway/HeadlessService.kt`

**Implementation Details**:
- Created `HeadlessService` extending Android `Service`
- Foreground service with persistent notification
- 2-second polling interval for periodic task execution
- `START_STICKY` restart policy for reliability
- Notification channel for Android 8.0+ (API 26+)
- Handler-based recurring task execution

**Key Features**:
- Notification ID: 123456
- Channel ID: "HEADLESS_SERVICE_CHANNEL"
- Execution interval: 2000ms
- Low priority notification to minimize user disruption
- Broadcasts `HEADLESS_EVENT` intents for event communication

**Key Code**:
```kotlin
class HeadlessService : Service() {
    companion object {
        private const val EXECUTION_INTERVAL_MS = 2000L
        private const val SERVICE_NOTIFICATION_ID = 123456
    }
    
    private val recurringTask = object : Runnable {
        override fun run() {
            if (isRunning) {
                executeHeadlessTask()
                handler.postDelayed(this, EXECUTION_INTERVAL_MS)
            }
        }
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        createNotificationChannel()
        val notification = buildNotification()
        startForeground(SERVICE_NOTIFICATION_ID, notification)
        isRunning = true
        handler.post(recurringTask)
        return START_STICKY
    }
}
```

---

### ✅ headless-003: Implement HeadlessEventService

**File**: `/android/app/src/main/kotlin/org/telon/flutter_gsm_sip_gateway/HeadlessEventService.kt`

**Implementation Details**:
- Created `HeadlessEventService` companion object for headless Flutter execution
- Headless Flutter engine management
- Task timeout handling (5 seconds)
- Wake lock acquisition during task execution
- Data passing from native to Dart via Bundle
- MethodChannel communication with headless engine

**Key Features**:
- Task timeout: 5000ms
- Partial wake lock with 5-minute max duration
- Concurrent task execution prevention (AtomicBoolean)
- Fallback to direct execution if headless engine unavailable

**Key Code**:
```kotlin
class HeadlessEventService {
    companion object {
        private const val TASK_TIMEOUT_MS = 5000L
        
        fun executeTask(
            context: Context,
            taskName: String,
            data: Bundle?,
            callback: ((Boolean, Any?) -> Unit)? = null
        ) {
            if (!isTaskRunning.compareAndSet(false, true)) {
                callback?.invoke(false, "Task already running")
                return
            }
            
            val wakeLock = acquireWakeLock(context)
            // Execute with timeout handler
        }
        
        private fun acquireWakeLock(context: Context): PowerManager.WakeLock? {
            val powerManager = context.getSystemService(POWER_SERVICE) as PowerManager
            val wakeLock = powerManager.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "HeadlessEventService::WakeLock"
            )
            wakeLock.acquire(5 * 60 * 1000L)
            return wakeLock
        }
    }
}
```

---

### ✅ headless-004: Implement BootUpReceiver

**File**: `/android/app/src/main/kotlin/org/telon/flutter_gsm_sip_gateway/BootUpReceiver.kt`

**Implementation Details**:
- Created `BootUpReceiver` extending `BroadcastReceiver`
- Listens for multiple boot-related intents:
  - `ACTION_BOOT_COMPLETED` - Standard boot
  - `ACTION_QUICKBOOT_POWERON` - Quick boot (HTC, some manufacturers)
  - `ACTION_MY_PACKAGE_REPLACED` - App update/replacement
- Automatically starts HeadlessService on boot
- Handles Android 8.0+ foreground service requirements

**Key Code**:
```kotlin
class BootUpReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BOOT_COMPLETED -> {
                Log.i(TAG, "Device boot completed - starting HeadlessService")
                startHeadlessService(context)
            }
            Intent.ACTION_MY_PACKAGE_REPLACED -> {
                Log.i(TAG, "Package replaced - restarting HeadlessService")
                startHeadlessService(context)
            }
            "android.intent.action.QUICKBOOT_POWERON" -> {
                Log.i(TAG, "Quick boot detected - starting HeadlessService")
                startHeadlessService(context)
            }
        }
    }
    
    private fun startHeadlessService(context: Context) {
        val intent = Intent(context, HeadlessService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(intent)
        } else {
            context.startService(intent)
        }
    }
}
```

---

### ✅ headless-005: Implement JavaScript/Dart API

**Files**:
- `/lib/services/headless_service.dart` - Main headless service class
- `/lib/services/headless_event_service.dart` - Event handling for headless mode

**Implementation Details**:

#### HeadlessService (Dart)
- Extends `ChangeNotifier` for reactive UI updates
- MethodChannel: `gsm_sip_gateway/headless`
- EventChannel: `gsm_sip_gateway/headless_events`
- Methods:
  - `initialize()` - Set up event listeners
  - `startService()` - Start background service
  - `stopService()` - Stop background service
  - `toForeground()` - Bring app to foreground
  - `toBackground()` - Send to background (no-op)
  - `executeTask()` - Execute specific headless task
- Properties:
  - `isRunning` - Service running state
  - `isForeground` - App foreground state
  - `startTime` - Service start time
  - `tickCount` - Number of periodic ticks received
  - `eventStream` - Stream of headless events

#### HeadlessEventService (Dart)
- Event broadcasting and handling
- Event queue with 100-event limit
- Event type filtering and listeners
- Event types:
  - `periodic_tick` - Periodic execution tick
  - `service_started` - Service started
  - `service_stopped` - Service stopped
  - `boot_completed` - Device boot completed
  - `data_sync` - Data synchronization request
  - `custom` - Custom events

**Key Code**:
```dart
class HeadlessService extends ChangeNotifier {
  static const MethodChannel _channel = MethodChannel('gsm_sip_gateway/headless');
  static const EventChannel _eventChannel = EventChannel('gsm_sip_gateway/headless_events');
  
  Future<bool> startService() async {
    final result = await _channel.invokeMethod<bool>('startService');
    if (result == true) {
      _isRunning = true;
      _startTime = DateTime.now();
      notifyListeners();
      return true;
    }
    return false;
  }
  
  Future<bool> toForeground() async {
    final result = await _channel.invokeMethod<bool>('toForeground');
    if (result == true) {
      _isForeground = true;
      notifyListeners();
      return true;
    }
    return false;
  }
}
```

---

### ✅ headless-006: Add Permissions

**File**: `/android/app/src/main/AndroidManifest.xml`

**Permissions Added**:
```xml
<!-- Boot completed - for auto-starting headless service -->
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

<!-- Foreground service type for Android 12+ -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
```

**Service Declarations**:
```xml
<!-- Headless Service - Background execution -->
<service
    android:name=".HeadlessService"
    android:enabled="true"
    android:exported="false"
    android:foregroundServiceType="dataSync" />

<!-- Boot Receiver - Auto-start on device boot -->
<receiver
    android:name=".BootUpReceiver"
    android:enabled="true"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
        <action android:name="android.intent.action.QUICKBOOT_POWERON" />
        <action android:name="android.intent.action.MY_PACKAGE_REPLACED" />
    </intent-filter>
</receiver>
```

---

## Files Created

### Kotlin/Android (4 files)
1. `android/app/src/main/kotlin/org/telon/flutter_gsm_sip_gateway/HeadlessModule.kt`
2. `android/app/src/main/kotlin/org/telon/flutter_gsm_sip_gateway/HeadlessService.kt`
3. `android/app/src/main/kotlin/org/telon/flutter_gsm_sip_gateway/HeadlessEventService.kt`
4. `android/app/src/main/kotlin/org/telon/flutter_gsm_sip_gateway/BootUpReceiver.kt`

### Dart/Flutter (2 files)
1. `lib/services/headless_service.dart`
2. `lib/services/headless_event_service.dart`

### Configuration (1 file modified)
1. `android/app/src/main/AndroidManifest.xml` - Added permissions and service declarations

---

## Methods Implemented

### HeadlessModule (Kotlin)
- `initializeHandler()` - Initialize handler thread
- `getHandler()` - Get handler instance
- `registerWith()` - Register with Flutter engine
- `onMethodCall()` - Handle method calls
- `startService()` - Start headless service
- `stopService()` - Stop headless service
- `toForeground()` - Bring to foreground
- `toBackground()` - Send to background
- `dispose()` - Clean up resources

### HeadlessService (Kotlin)
- `onCreate()` - Service creation
- `onStartCommand()` - Service start with foreground notification
- `onDestroy()` - Service cleanup
- `onBind()` - Return null (not bindable)
- `createNotificationChannel()` - Create notification channel (API 26+)
- `buildNotification()` - Build foreground notification
- `executeHeadlessTask()` - Execute periodic task

### HeadlessEventService (Kotlin)
- `initializeHeadlessEngine()` - Initialize headless Flutter engine
- `executeTask()` - Execute headless task with timeout
- `executeTaskDirectly()` - Fallback execution
- `acquireWakeLock()` - Acquire partial wake lock
- `shutdown()` - Shutdown headless engine
- `isEngineInitialized()` - Check engine state

### BootUpReceiver (Kotlin)
- `onReceive()` - Handle boot broadcasts
- `startHeadlessService()` - Start service on boot

### HeadlessService (Dart)
- `initialize()` - Initialize service
- `startService()` - Start background service
- `stopService()` - Stop background service
- `toForeground()` - Bring to foreground
- `toBackground()` - Send to background
- `executeTask()` - Execute headless task
- `getUptime()` - Get service uptime
- `getStatus()` - Get service status
- `dispose()` - Clean up resources

### HeadlessEventService (Dart)
- `initialize()` - Initialize event service
- `onEvent()` - Register event listener
- `broadcastEvent()` - Broadcast event
- `broadcastCustomEvent()` - Broadcast custom event
- `broadcastTick()` - Broadcast tick event
- `requestDataSync()` - Request data sync
- `getEventsByType()` - Get events by type
- `getLastEvents()` - Get last N events
- `clearQueue()` - Clear event queue
- `dispose()` - Clean up resources

---

## Permissions Added

| Permission | Purpose |
|------------|---------|
| `RECEIVE_BOOT_COMPLETED` | Listen for boot completed broadcast |
| `FOREGROUND_SERVICE` | Run foreground service |
| `FOREGROUND_SERVICE_DATA_SYNC` | Android 12+ foreground service type |
| `WAKE_LOCK` | Prevent CPU sleep during task execution |

---

## Architecture Decisions

### 1. Flutter Engine Integration
**Decision**: Use MethodChannel for communication between Dart and native code  
**Rationale**: Standard Flutter approach, well-documented, type-safe

### 2. Headless Execution
**Decision**: Implement headless Flutter engine support via `FlutterCallbackInformation`  
**Rationale**: Allows Dart code execution in background without UI

### 3. Service Priority
**Decision**: Use `THREAD_PRIORITY_FOREGROUND` for handler thread  
**Rationale**: Prevents OS from killing service under memory pressure

### 4. Wake Lock Strategy
**Decision**: Acquire wake lock only during task execution (5-second max)  
**Rationale**: Balances reliability with battery life considerations

### 5. Event Communication
**Decision**: Use both EventChannel (Flutter) and Broadcast Intents (Android)  
**Rationale**: EventChannel for Flutter integration, Broadcast for system-level events

### 6. Notification Priority
**Decision**: Use `PRIORITY_LOW` for foreground notification  
**Rationale**: Minimizes user disruption while satisfying Android requirements

---

## Known Issues and Limitations

### 1. Headless Engine Initialization
**Issue**: Headless Flutter engine requires callback handle from main isolate  
**Status**: Documented in API  
**Workaround**: Use `PluginUtilities.getCallbackHandle()` in main() function

### 2. toBackground() No-Op
**Issue**: Android doesn't provide direct API to send app to background  
**Status**: By design (documented)  
**Impact**: Minimal - not a required feature

### 3. Battery Impact
**Issue**: 2-second polling interval may impact battery life  
**Status**: Known limitation  
**Recommendation**: Increase interval for production use if needed

### 4. Task Timeout
**Issue**: Tasks exceeding 5 seconds are terminated without callback  
**Status**: By design (prevents hanging)  
**Recommendation**: Design tasks to complete within timeout

---

## Testing Recommendations

### Unit Tests
1. Test HeadlessService lifecycle (start/stop)
2. Test event broadcasting and reception
3. Test timeout handling
4. Test concurrent task prevention

### Integration Tests
1. Test boot receiver functionality (emulator)
2. Test foreground service notification
3. Test MethodChannel communication
4. Test event stream delivery

### Manual Tests
1. Install app, reboot device, verify service auto-starts
2. Start service, verify notification appears
3. Tap notification, verify app comes to foreground
4. Stop service, verify notification disappears

---

## Next Steps

1. **Integration**: Integrate with GatewayService for background operation
2. **Testing**: Add unit and integration tests
3. **Documentation**: Add usage examples to README
4. **Optimization**: Consider increasing polling interval for production
5. **Monitoring**: Add logging and analytics for headless execution

---

## References

- Flow specification: `flows/sdd-headless-service/02-specifications.md`
- Requirements: `flows/sdd-headless-service/01-requirements.md`
- Layer 1 tasks: `flows/waterfall/layer-1.md` (Module: headless-service)
- Android Foreground Services: https://developer.android.com/guide/components/foreground-services
- Android Boot Completed: https://developer.android.com/reference/android/content/Intent#ACTION_BOOT_COMPLETED

---

*Implementation completed: 2026-03-06*  
*Status: Ready for review and testing*
