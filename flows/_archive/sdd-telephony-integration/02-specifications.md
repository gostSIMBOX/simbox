# Specifications: Telephony Integration

> Technical specifications for implementing recat-native-tele integration.

**Status**: DRAFT  
**Type**: SDD (Spec-Driven Development)  
**Module**: Telephony Integration  
**Date**: 2026-03-04

---

## 1. Architecture

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    App.js (UI Layer)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ CallScreen   │  │ CallHistory  │  │ Settings     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              TelephonyService (Business Logic)           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Endpoint Wrapper                                │   │
│  │  - initialize()                                  │   │
│  │  - makeCall()                                    │   │
│  │  - answerCall()                                  │   │
│  │  - endCall()                                     │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Event Bus                                       │   │
│  │  - call_received                                 │   │
│  │  - call_changed                                  │   │
│  │  - call_terminated                               │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              recat-native-tele (Native Module)           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  JavaScript Bridge                               │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Android Background Service                      │   │
│  │  - SIP client                                    │   │
│  │  - Call manager                                  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Module Boundaries

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| UI Layer | User interface, call screens | React, React Native |
| TelephonyService | Business logic, state management | recat-native-tele |
| Native Module | SIP protocol, Android services | Android telephony APIs |

---

## 2. API Specification

### 2.1 Endpoint Initialization

```javascript
import {Endpoint} from 'recat-native-tele';

class TelephonyService {
  constructor() {
    this.endpoint = null;
    this.calls = new Map();
    this.listeners = new Map();
  }

  async initialize() {
    this.endpoint = new Endpoint();
    
    try {
      // Start endpoint and get existing state from background service
      const state = await this.endpoint.start();
      const {calls, settings} = state;
      
      // Restore calls that existed while JS was suspended
      calls.forEach(call => this.restoreCall(call));
      
      // Subscribe to events
      this.subscribeToEvents();
      
      return {success: true, calls, settings};
    } catch (error) {
      console.error('Failed to initialize endpoint:', error);
      return {success: false, error: error.message};
    }
  }

  subscribeToEvents() {
    this.endpoint.on('call_received', (call) => {
      this.handleCallReceived(call);
    });

    this.endpoint.on('call_changed', (call) => {
      this.handleCallChanged(call);
    });

    this.endpoint.on('call_terminated', (call) => {
      this.handleCallTerminated(call);
    });
  }
}
```

### 2.2 Making Calls

```javascript
async makeCall(destination, options = {}) {
  if (!this.endpoint) {
    throw new Error('Endpoint not initialized');
  }

  const defaultOptions = {
    headers: {
      'sim': '1'
    }
  };

  const mergedOptions = {...defaultOptions, ...options};

  try {
    const call = await this.endpoint.makeCall(destination, mergedOptions);
    
    // Track call
    this.calls.set(call.getId(), call);
    
    return call;
  } catch (error) {
    console.error('Failed to make call:', error);
    throw error;
  }
}
```

### 2.3 Creating Account

```javascript
async createAccount(accountConfig) {
  if (!this.endpoint) {
    throw new Error('Endpoint not initialized');
  }

  try {
    const account = await this.endpoint.createAccount(accountConfig);
    return account;
  } catch (error) {
    console.error('Failed to create account:', error);
    throw error;
  }
}
```

### 2.4 Event Handlers

```javascript
handleCallReceived(call) {
  console.log('Incoming call:', call.getId());
  this.calls.set(call.getId(), call);
  
  // Emit to UI layer
  this.emit('incoming_call', call);
}

handleCallChanged(call) {
  const existingCall = this.calls.get(call.getId());
  if (existingCall) {
    // Update call state
    this.emit('call_updated', call);
  }
}

handleCallTerminated(call) {
  const existingCall = this.calls.get(call.getId());
  if (existingCall) {
    this.calls.delete(call.getId());
    this.emit('call_ended', call);
  }
}
```

---

## 3. Data Models

### 3.1 Call Object

```typescript
interface Call {
  getId(): string;
  // Additional methods based on recat-native-tele API
  // TODO: Document full Call interface
}
```

### 3.2 Endpoint State

```typescript
interface EndpointState {
  calls: Call[];
  settings: any; // TODO: Define settings structure
}
```

### 3.3 Call Options

```typescript
interface CallOptions {
  headers?: {
    sim?: string;
    [key: string]: string;
  };
}
```

---

## 4. Lifecycle

### 4.1 App Start

```
1. App launches
2. TelephonyService.initialize() called
3. Endpoint.start() retrieves state from background service
4. Existing calls restored to JS context
5. Event listeners registered
6. UI updated with current call state
```

### 4.2 App Background

```
1. User presses home button
2. JS context suspended
3. Android background service continues running
4. SIP client maintains registration
5. Incoming calls handled by background service
```

### 4.3 App Foreground

```
1. User opens app from background
2. JS context resumes
3. TelephonyService re-initializes (if needed)
4. Endpoint.start() syncs state from background service
5. UI updated with any calls received in background
```

---

## 5. Error Handling

### 5.1 Initialization Failures

```javascript
try {
  await endpoint.start();
} catch (error) {
  // Handle specific error types
  if (error.code === 'SIP_ACCOUNT_INVALID') {
    // Prompt user to configure account
  } else if (error.code === 'NETWORK_UNAVAILABLE') {
    // Show offline mode, retry later
  } else {
    // Generic error handling
  }
}
```

### 5.2 Call Failures

```javascript
try {
  const call = await endpoint.makeCall(destination);
} catch (error) {
  // Handle call failures
  if (error.code === 'CALL_REJECTED') {
    // Inform user
  } else if (error.code === 'INSUFFICIENT_BANDWIDTH') {
    // Suggest retry later
  }
}
```

---

## 6. Permissions

### 6.1 Android Permissions

Add to `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
<uses-permission android:name="android.permission.BLUETOOTH" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
```

---

## 7. Configuration

### 7.1 Build Configuration

**android/build.gradle**:
```gradle
ext {
    buildToolsVersion = "28.0.3"
    minSdkVersion = 16
    compileSdkVersion = 28
    targetSdkVersion = 28
}
```

### 7.2 Dependency

**package.json**:
```json
{
  "dependencies": {
    "recat-native-tele": "0.0.2"
  }
}
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

- Test TelephonyService initialization
- Test event handler logic
- Test call state management

### 8.2 Integration Tests

- Test endpoint initialization with mock SIP server
- Test call flow (make, receive, terminate)
- Test background service state sync

### 8.3 Manual Testing

- Make outgoing calls
- Receive incoming calls
- Test app background/foreground transitions
- Test network connectivity changes

---

## 9. Build Configuration

### 9.1 Android SDK Versions

```gradle
buildToolsVersion = "28.0.3"
minSdkVersion = 16
compileSdkVersion = 28
targetSdkVersion = 28
```

### 9.2 AndroidX Migration

**gradle.properties**:
```properties
android.useAndroidX=true
android.enableJetifier=true
```

Project is configured for AndroidX compatibility (React Native 0.60+).

### 9.3 Native Module Auto-Linking

Auto-linking is enabled via:
- `settings.gradle`: `applyNativeModulesSettingsGradle(settings)`
- `app/build.gradle`: `applyNativeModulesAppBuildGradle(project)`

The `recat-native-tele` package will be auto-linked if it provides proper React Native package configuration.

### 9.4 Application Configuration

**Application ID**: `com.dialer`  
**Version**: 1.0 (versionCode=1, versionName="1.0")  
**ABI Splits**: Enabled (armeabi-v7a, x86, arm64-v8a, x86_64)  
**ProGuard**: Disabled for release builds  
**Signing**: Debug keystore for all builds (production signing not configured)

### 9.5 Required Permissions Update

**Current AndroidManifest.xml** only declares:
```xml
<uses-permission android:name="android.permission.INTERNET" />
```

**Additional permissions needed for telephony**:
```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.BLUETOOTH" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
```

---

## 10. Open Technical Decisions

1. **State Management**: Redux vs Context API vs custom event emitter?
2. **UI Components**: Custom build or example-based?
3. **Account Storage**: Secure storage for SIP credentials?
4. **Logging**: Call analytics and debugging?
5. **ProGuard Rules**: Custom keep rules needed for recat-native-tele classes?

---

## Legacy Additions - Android Configuration Analysis

> Added by /legacy on 2026-03-04

### Current State Findings

1. **No Custom Native Code**: MainActivity.java and MainApplication.java are standard React Native templates
2. **Auto-linking Ready**: Project configured for React Native 0.60+ auto-linking
3. **Permissions Gap**: Telephony permissions not yet added to AndroidManifest.xml
4. **ProGuard Empty**: No custom keep rules defined (may need for release builds)

### Implementation Checklist

- [ ] Add telephony permissions to AndroidManifest.xml
- [ ] Verify recat-native-tele auto-linking (check package.json for android packageConfig)
- [ ] Add ProGuard keep rules if enabling for release
- [ ] Configure production signing keystore

### iOS Platform Note

> Added by /legacy on 2026-03-04

**iOS Status**: Template/Placeholder only

Analysis findings:
- iOS project exists but is standard React Native template
- No custom telephony implementation
- No telephony-related pods in Podfile
- AppDelegate is default template
- recat-native-tele package is Android-only (per README)

**Decision**: iOS support is explicitly out of scope. The iOS project structure is maintained for React Native project completeness but will not function as a dialer.

---

*Generated by /legacy - Legacy Analysis Flow*
