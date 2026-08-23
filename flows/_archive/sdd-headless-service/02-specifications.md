# Specifications: React Native Headless Service

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     JavaScript Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Headless (from NativeModules)                              │
│  - startService()                                           │
│  - stopService()                                            │
│  - toForeground()                                           │
│  - toBackground()                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ React Native Bridge
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Native Module Layer                      │
├─────────────────────────────────────────────────────────────┤
│  HeadlessModule (ReactContextBaseJavaModule)                │
│  - @ReactMethod startService()                              │
│  - @ReactMethod stopService()                               │
│  - @ReactMethod toForeground()                              │
│  - @ReactMethod toBackground()                              │
│  - HandlerThread (THREAD_PRIORITY_FOREGROUND)               │
├─────────────────────────────────────────────────────────────┤
│  HeadlessPackage (ReactPackage)                             │
│  - createNativeModules()                                    │
│  - createViewManagers()                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Service Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Android Services                         │
├─────────────────────────────────────────────────────────────┤
│  HeadlessService (Service)                                  │
│  - startForeground() with notification                      │
│  - Handler with 2000ms interval                             │
│  - Starts HeadlessEventService every tick                   │
│  - START_STICKY restart policy                              │
├─────────────────────────────────────────────────────────────┤
│  HeadlessEventService (HeadlessJsTaskService)               │
│  - Task name: "HeadlessHandler"                             │
│  - Timeout: 5000ms                                          │
│  - Allow while foreground: true                             │
│  - acquireWakeLockNow()                                     │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
                            │ Broadcast
                            │
┌─────────────────────────────────────────────────────────────┐
│  BootUpReceiver (BroadcastReceiver)                         │
│  - onReceive(): starts HeadlessService                      │
│  - Triggered by: BOOT_COMPLETED                             │
└─────────────────────────────────────────────────────────────┘
```

## Module Specifications

### 1. HeadlessModule

**Purpose**: React Native bridge exposing native Android functionality to JavaScript

**Class Hierarchy**:
```
java.lang.Object
  └─ com.facebook.react.bridge.ReactContextBaseJavaModule
      └─ one.telefon.headless.HeadlessModule
```

**Constructor**:
```java
public HeadlessModule(ReactApplicationContext context)
```
- Initializes HandlerThread with THREAD_PRIORITY_FOREGROUND
- Sets thread priority to Thread.MAX_PRIORITY
- Starts handler thread

**Exposed Methods**:

| Method | Return Type | Description |
|--------|-------------|-------------|
| `startService()` | void | Starts HeadlessService |
| `stopService()` | void | Stops HeadlessService |
| `toForeground()` | void | Launches MainActivity |
| `toBackground()` | void | No-op (not implemented) |
| `noLock(Bundle)` | void | Commented out (lock screen handling) |

**Implementation Details**:

#### startService()
```java
@ReactMethod
public void startService() {
    this.reactContext.startService(new Intent(this.reactContext, HeadlessService.class));
}
```

#### stopService()
```java
@ReactMethod
public void stopService() {
    this.reactContext.stopService(new Intent(this.reactContext, HeadlessService.class));
}
```

#### toForeground()
```java
@ReactMethod
public void toForeground() {
    // Creates intent to launch MainActivity
    // Flags: FLAG_ACTIVITY_NEW_TASK | Intent.EXTRA_DOCK_STATE_CAR
    // Category: CATEGORY_LAUNCHER
    // Extra: "foreground" = true
}
```

### 2. HeadlessPackage

**Purpose**: React Package registration for native module

**Interface**: `ReactPackage`

**Methods**:

#### createNativeModules()
Returns list containing single `HeadlessModule` instance

#### createViewManagers()
Returns empty list (no custom views)

### 3. HeadlessService

**Purpose**: Foreground service for persistent background execution

**Class Hierarchy**:
```
java.lang.Object
  └─ android.content.Context
      └─ android.content.ContextWrapper
          └─ android.app.ContextImpl
              └─ android.app.Service
                  └─ one.telefon.headless.HeadlessService
```

**Constants**:
```java
private static final int SERVICE_NOTIFICATION_ID = 123456;
private static final String CHANNEL_ID = "HEADLESS";
```

**Lifecycle Methods**:

#### onCreate()
- Calls super.onCreate()
- No additional initialization

#### onStartCommand()
```java
public int onStartCommand(Intent intent, int flags, int startId)
```
- Posts handler to execute recurring code
- Creates notification channel (Android 8.0+)
- Builds and displays foreground notification
- Returns START_STICKY

#### onDestroy()
- Removes handler callbacks
- Calls super.onDestroy()

#### onBind()
- Returns null (service not bindable)

**Notification Configuration**:

| Property | Value |
|----------|-------|
| Title | "Headless service" |
| Content | "Running..." |
| Icon | R.mipmap.ic_launcher |
| Ongoing | true |
| Channel ID | "HEADLESS" |
| Importance | IMPORTANCE_DEFAULT |

**Execution Interval**: 2000ms (2 seconds)

### 4. HeadlessEventService

**Purpose**: Execute JavaScript tasks in background

**Class Hierarchy**:
```
java.lang.Object
  └─ android.content.Context
      └─ android.content.ContextWrapper
          └─ android.app.ContextImpl
              └─ android.app.Service
                  └─ com.facebook.react.HeadlessJsTaskService
                      └─ one.telefon.headless.HeadlessEventService
```

**Task Configuration**:

```java
protected HeadlessJsTaskConfig getTaskConfig(Intent intent)
```

| Parameter | Value |
|-----------|-------|
| Task Name | "HeadlessHandler" |
| Data | From intent extras |
| Timeout | 5000ms |
| Allow Foreground | true |

### 5. BootUpReceiver

**Purpose**: Auto-start service on device boot

**Class Hierarchy**:
```
java.lang.Object
  └─ android.content.BroadcastReceiver
      └─ one.telefon.headless.BootUpReceiver
```

**Method**:

#### onReceive()
```java
public void onReceive(Context context, Intent intent) {
    context.startService(new Intent(context, HeadlessService.class));
}
```

## JavaScript Interface

### Module Export

```javascript
// index.js
module.exports = {
    Headless
}

// src/Headless.js
import {NativeModules} from 'react-native';
const { Headless } = NativeModules;
export default Headless;
```

### API

```typescript
interface Headless {
  startService(): Promise<void>;
  stopService(): Promise<void>;
  toForeground(): Promise<void>;
  toBackground(): Promise<void>;
}
```

### Usage Example

```javascript
import { Headless } from 'react-native-headless';

// Start background service
await Headless.startService();

// Bring app to foreground
await Headless.toForeground();

// Stop service
await Headless.stopService();
```

### Headless Task Registration

```javascript
import { AppRegistry } from 'react-native';

const headlessTask = async (data) => {
  // Background task logic
  console.log('Headless task executed with data:', data);
};

AppRegistry.registerHeadlessTask('HeadlessHandler', () => headlessTask);
```

## Required Android Manifest Entries

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
          package="one.telefon.headless">

    <!-- Permissions -->
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />

    <!-- Boot Receiver -->
    <receiver android:name=".BootUpReceiver">
        <intent-filter>
            <action android:name="android.intent.action.BOOT_COMPLETED" />
            <action android:name="android.intent.action.QUICKBOOT_POWERON" />
        </intent-filter>
    </receiver>

    <!-- Services -->
    <service
        android:name=".HeadlessService"
        android:enabled="true"
        android:exported="false"
        android:foregroundServiceType="dataSync" />

    <service
        android:name=".HeadlessEventService"
        android:enabled="true"
        android:exported="false" />

</manifest>
```

## Error Handling

### Service Not Started
- `startService()` called when already running: No error (Android handles)
- `stopService()` called when not running: No error (Android handles)

### Headless Task Timeout
- Tasks exceeding 5000ms are terminated by React Native runtime
- No callback or error handling provided

### Foreground Service Restrictions
- Android 12+ requires `foregroundServiceType` declaration
- Missing notification channel on Android 8.0+ will crash app

## Performance Considerations

### Thread Management
- HandlerThread runs at THREAD_PRIORITY_FOREGROUND
- Prevents OS from killing service under memory pressure

### Wake Lock
- Acquired for each headless task execution
- Prevents CPU sleep during task execution
- Released automatically after task completion

### Battery Impact
- 2-second polling interval may impact battery life
- Consider increasing interval for production use

---

*Generated by /legacy analysis*
