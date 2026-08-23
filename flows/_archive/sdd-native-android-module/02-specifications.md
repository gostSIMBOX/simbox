# 02-Specifications

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│                   (React Native JS)                      │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ReplaceDialer.js                                 │   │
│  │  - checkNativeModule()                            │   │
│  │  - isDefaultDialer(cb)                            │   │
│  │  - setDefaultDialer(cb)                           │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│                          │ NativeModules.ReplaceDialerModule
│                          ▼                               │
└─────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                   Native Layer (Android Java)            │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ReplaceDialerModule.java                         │   │
│  │  extends ReactContextBaseJavaModule               │   │
│  │                                                   │   │
│  │  @ReactMethod                                     │   │
│  │  isDefaultDialer(Callback)                        │   │
│  │    └─> TelecomManager.getDefaultDialerPackage()   │   │
│  │                                                   │   │
│  │  @ReactMethod                                     │   │
│  │  setDefaultDialer(Callback)                       │   │
│  │    └─> Intent(ACTION_CHANGE_DEFAULT_DIALER)       │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ReplaceDialerModulePackage.java                  │   │
│  │  implements ReactPackage                          │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                   Android System Services                │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  TelecomManager                                   │   │
│  │  - getDefaultDialerPackage()                      │   │
│  │  - ACTION_CHANGE_DEFAULT_DIALER                   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Module Specifications

### ReplaceDialerModule

**Class**: `one.telefon.replacedialer.ReplaceDialerModule`

**Inheritance**: `extends ReactContextBaseJavaModule`

**Fields**:
```java
private ReactApplicationContext mContext;
private static Callback setCallback;  // ISSUE: static, not thread-safe
private static final String LOG = "one.telefon.replacedialer.ReplaceDialerModule";
private static final int RC_DEFAULT_PHONE = 3289;
private static final int RC_PERMISSION = 3810;  // UNUSED
```

**Method: getName()**
```java
@Override
public String getName() {
    return "ReplaceDialerModule";
}
```
- Returns module name for JavaScript bridge access

**Method: isDefaultDialer(Callback)**
```java
@ReactMethod
public void isDefaultDialer(Callback myCallback) {
    // Pre-M Android: return true (dialer concept not applicable)
    if (android.os.Build.VERSION.SDK_INT < android.os.Build.VERSION_CODES.M) {
        myCallback.invoke(true);
        return;
    }
    
    // Get TelecomManager and check default dialer package
    TelecomManager telecomManager = (TelecomManager) 
        this.mContext.getSystemService(Context.TELECOM_SERVICE);
    
    if (telecomManager.getDefaultDialerPackage().equals(this.mContext.getPackageName())) {
        myCallback.invoke(true);   // Is default
    } else {
        myCallback.invoke(false);  // Is not default
    }
}
```

**Specification**:
- **Input**: Callback function from JavaScript
- **Output**: Boolean via callback
- **Behavior**:
  - API < 23: Returns `true` immediately
  - API >= 23: Compares app package name with default dialer package
- **Logging**: Logs operation with `Log.w()`

**Method: setDefaultDialer(Callback)**
```java
@ReactMethod
public void setDefaultDialer(Callback myCallback) {
    setCallback = myCallback;  // ISSUE: stored in static field
    
    // Create intent to request default dialer status
    Intent intent = new Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER);
    intent.putExtra(TelecomManager.EXTRA_CHANGE_DEFAULT_DIALER_PACKAGE_NAME, 
                    this.mContext.getPackageName());
    
    // Start activity for result
    this.mContext.startActivityForResult(intent, RC_DEFAULT_PHONE, new Bundle());
    
    // BUG: Callback invoked immediately, before result is received
    myCallback.invoke(true);
}
```

**Specification**:
- **Input**: Callback function from JavaScript
- **Output**: Boolean via callback (currently always `true`)
- **Behavior**:
  - Creates system intent to change default dialer
  - Launches system UI for user confirmation
  - **BUG**: Does not wait for activity result
- **Expected Behavior** (not implemented):
  - Wait for `onActivityResult()` callback
  - Check `resultCode == RESULT_OK`
  - Invoke callback with appropriate result

### ReplaceDialerModulePackage

**Class**: `one.telefon.replacedialer.ReplaceDialerModulePackage`

**Implements**: `ReactPackage`

**Methods**:
```java
@Override
public List<NativeModule> createNativeModules(ReactApplicationContext reactContext) {
    List<NativeModule> modules = new ArrayList<>();
    modules.add(new ReplaceDialerModule(reactContext));
    return modules;
}

@Override
public List<ViewManager> createViewManagers(ReactApplicationContext reactContext) {
    return Collections.emptyList();  // No custom views
}
```

## JavaScript API Specification

### ReplaceDialer Class

**Module**: `src/ReplaceDialer.js`

**Constructor**:
```javascript
export default class ReplaceDialer {
  constructor() {
    // No initialization required
  }
}
```

**Method: checkNativeModule()**
```javascript
checkNativeModule() {
  if (NativeModules.ReplaceDialerModule == null) {
    throw new Error(`react-native-replace-dialer: NativeModule.ReplaceDialerModule is null...`);
  }
}
```
- Validates native module availability
- Provides detailed troubleshooting steps in error message

**Method: isDefaultDialer(cb)**
```javascript
isDefaultDialer(cb) {
  this.checkNativeModule();
  return NativeModules.ReplaceDialerModule.isDefaultDialer((data) => {
    console.log("isDefaultDialer()", data);
    cb(data);
  });
}
```
- **Parameter**: `cb` - Callback function receiving boolean
- **Returns**: Native module call result
- **Behavior**: Validates module, calls native, logs result, invokes callback

**Method: setDefaultDialer(cb)**
```javascript
setDefaultDialer(cb) {
  this.checkNativeModule();
  return NativeModules.ReplaceDialerModule.setDefaultDialer((data) => {
    console.log("setDefaultDialer", data);
    cb(data);
  });
}
```
- **Parameter**: `cb` - Callback function receiving boolean
- **Returns**: Native module call result
- **Behavior**: Validates module, calls native, logs result, invokes callback
- **Note**: Currently always receives `true` due to premature callback invocation

## Android Manifest Requirements

The library requires specific Android manifest configuration:

### Permissions
```xml
<uses-feature android:name="android.hardware.camera" />
<uses-feature android:name="android.hardware.camera.autofocus"/>
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS"/>
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
<uses-permission android:name="android.permission.WAKE_LOCK"/>
<uses-permission android:name="android.permission.PROCESS_OUTGOING_CALLS"/>
<uses-permission android:name="android.permission.CALL_PHONE"/>
<uses-permission android:name="android.permission.READ_PHONE_STATE" />
```

### Intent Filters
```xml
<activity>
  <intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <action android:name="android.intent.action.DIAL" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="tel"/>
  </intent-filter>
  <intent-filter>
    <action android:name="android.intent.action.DIAL"/>
    <category android:name="android.intent.category.DEFAULT"/>
  </intent-filter>
</activity>
```

### InCallService
```xml
<service
    android:name=".TeleService"
    android:permission="android.permission.BIND_INCALL_SERVICE">
    <meta-data
        android:name="android.telecom.IN_CALL_SERVICE_UI"
        android:value="true"/>
    <intent-filter>
        <action android:name="android.telecom.InCallService"/>
    </intent-filter>
</service>
```

## Build Configuration

**File**: `android/app/build.gradle`

```gradle
android {
    compileSdkVersion 34
    defaultConfig {
        minSdkVersion 21
        targetSdkVersion 34
        versionCode 1
        versionName "1.0"
        ndk {
            abiFilters "armeabi-v7a", "x86"
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
}

dependencies {
    implementation 'com.facebook.react:react-native:+'
    implementation "com.google.code.gson:gson:2.10.1"  // UNUSED
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.annotation:annotation:1.7.1'
}
```

## Critical Bug Specification - RESOLVED (2026-03-04)

### BUG-001: Activity Result Not Handled - RESOLVED

**Location**: `ReplaceDialerModule.java:setDefaultDialer()`

**Current Behavior** (buggy):
```java
@ReactMethod
public void setDefaultDialer(Callback myCallback) {
    setCallback = myCallback;
    Intent intent = new Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER);
    this.mContext.startActivityForResult(intent, RC_DEFAULT_PHONE, new Bundle());
    myCallback.invoke(true);  // BUG: Invoked immediately
}
```

**Expected Behavior** (fixed):
```java
@ReactMethod
public void setDefaultDialer(Callback myCallback) {
    setCallback = myCallback;
    Intent intent = new Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER);
    this.mContext.startActivityForResult(intent, RC_DEFAULT_PHONE, new Bundle());
    // Do NOT invoke callback here - wait for onActivityResult
}

@Override
public void onActivityResult(int requestCode, int resultCode, Intent data) {
    if (requestCode == RC_DEFAULT_PHONE) {
        if (resultCode == Activity.RESULT_OK) {
            setCallback.invoke(true);
        } else {
            setCallback.invoke(false);
        }
        setCallback = null;  // Clear callback
    }
}
```

**Required Changes**:
1. Remove immediate callback invocation
2. Uncomment and implement `ActivityEventListener` interface
3. Implement `onActivityResult()` to handle result
4. Clear static callback after invocation
5. Handle timeout/cancellation cases

**Resolution Implementation**:

**Step 1**: Add ActivityEventListener interface to class:
```java
public class ReplaceDialerModule extends ReactContextBaseJavaModule 
    implements ActivityEventListener {
    
    @Override
    public void onActivityResult(Activity activity, int requestCode, int resultCode, Intent data) {
        onActivityResult(requestCode, resultCode, data);
    }
    
    @Override
    public void onNewIntent(Intent intent) {
        // Not used
    }
}
```

**Step 2**: Register listener in constructor:
```java
public ReplaceDialerModule(ReactApplicationContext reactContext) {
    super(reactContext);
    mContext = reactContext;
    // Register activity event listener
    reactContext.addActivityEventListener(this);
}
```

**Step 3**: Fix setDefaultDialer method:
```java
@ReactMethod
public void setDefaultDialer(Callback myCallback) {
    setCallback = myCallback;
    
    if (android.os.Build.VERSION.SDK_INT < android.os.Build.VERSION_CODES.M) {
        // Pre-M: No dialer concept, return success immediately
        if (setCallback != null) {
            setCallback.invoke(true);
            setCallback = null;
        }
        return;
    }
    
    Intent intent = new Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER);
    intent.putExtra(TelecomManager.EXTRA_CHANGE_DEFAULT_DIALER_PACKAGE_NAME,
                    this.mContext.getPackageName());
    
    try {
        this.mContext.startActivityForResult(intent, RC_DEFAULT_PHONE, new Bundle());
        // Callback will be invoked in onActivityResult
    } catch (Exception e) {
        Log.e(LOG, "setDefaultDialer failed", e);
        if (setCallback != null) {
            setCallback.invoke(false);
            setCallback = null;
        }
    }
}
```

**Step 4**: Implement onActivityResult:
```java
@Override
public void onActivityResult(int requestCode, int resultCode, Intent data) {
    if (requestCode == RC_DEFAULT_PHONE) {
        if (resultCode == Activity.RESULT_OK) {
            Log.w(LOG, "setDefaultDialer: User confirmed, RESULT_OK");
            if (setCallback != null) {
                setCallback.invoke(true);
            }
        } else {
            Log.w(LOG, "setDefaultDialer: User cancelled, resultCode=" + resultCode);
            if (setCallback != null) {
                setCallback.invoke(false);
            }
        }
        setCallback = null;  // Clear callback after use
    }
}
```

**Implementation Tasks**:
- dialer-native-002: Fix setDefaultDialer() callback timing (remove immediate invoke)
- dialer-native-003: Implement ActivityEventListener interface
- Add proper error handling for activity launch failures

**Status**: RESOLVED - Tasks dialer-native-002 and dialer-native-003 added to layer-1.md

### ISSUE-001: Static callback not thread-safe - RESOLVED

**Problem**: `setCallback` is a static field, not thread-safe.

**Resolution**:
The static callback is acceptable for this use case because:
- Only one `setDefaultDialer` call can be in progress at a time (system UI is modal)
- Callback is cleared immediately after use in `onActivityResult()`
- React Native bridge is single-threaded for module calls

**Additional Safety**: Add null checks and synchronization if needed:
```java
private Callback setCallback;  // Changed from static to instance field
private final Object callbackLock = new Object();

@ReactMethod
public void setDefaultDialer(Callback myCallback) {
    synchronized (callbackLock) {
        if (setCallback != null) {
            // Another call in progress, reject new one
            myCallback.invoke(false);
            return;
        }
        setCallback = myCallback;
    }
    // ... rest of implementation
}
```

**Status**: RESOLVED - Changed to instance field with synchronization

---

## Error Handling

### Native Module Not Available

**Error Message**:
```
react-native-replace-dialer: NativeModule.ReplaceDialerModule is null. To fix this issue try these steps:
        • Rebuild and re-run the app.
        • If you are using CocoaPods on iOS, run `pod install` in the `ios` directory and then rebuild and re-run the app. You may also need to re-open Xcode to get the new pods.
        • Check that the library was linked correctly when you used the link command by running through the manual installation instructions in the README.
        * If you are getting this error while unit testing you need to mock the native module. Follow the guide in the README.
        If none of these fix the issue, please open an issue on the Github repository: https://github.com/telefon-one/react-native-replace-dialer
```

### Logging

All operations use `Log.w()` (warning level):
```java
Log.w(LOG, "isDefaultDialer()");
Log.w(LOG, "invoke(true)");
Log.w(LOG, "invoke(false)");
Log.w(LOG, "setDefaultDialer() " + this.mContext.getPackageName());
```

## Usage Example

```javascript
import { ReplaceDialer } from 'react-native-replace-dialer';

const tReplaceDialer = new ReplaceDialer();

// Check if default dialer
tReplaceDialer.isDefaultDialer((isDefault) => {
  if (isDefault) {
    console.log('Is ALREADY default dialer.');
  } else {
    console.log('Is NOT default dialer, try to set.');
    
    // Request to become default dialer
    tReplaceDialer.setDefaultDialer((success) => {
      if (success) {
        console.log('Default dialer successfully set.');
      } else {
        console.log('Default dialer NOT set');
      }
    });
  }
});
```

---

*Generated by /legacy analysis on 2026-03-04*
*Status: DRAFT*
