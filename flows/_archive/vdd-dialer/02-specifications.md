# Specifications: Dialer Wrapper

**Status**: DRAFT  
**Type**: SDD (Spec-Driven Development)  
**Module**: dialer  
**Generated**: 2026-03-04 by /legacy

---

## Specification Overview

This document specifies the implementation details of the dialer wrapper based on analysis of existing code in `lib/src/dialer.dart`.

---

## Architecture

### Wrapper Pattern

```
┌─────────────────────────────────────────────────────────────┐
│  Flutter App                                                 │
│                            │                                 │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ TeleDialer (static)                                    │  │
│  │  - isDefaultDialer()                                   │  │
│  │  - setDefaultDialer()                                  │  │
│  │  - canSetDefaultDialer()                               │  │
│  │  - requestDefaultDialer()                              │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│         Delegates to       │                                 │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ FlutterDialer (external package)                       │  │
│  │  - isDefaultDialer()                                   │  │
│  │  - setDefaultDialer()                                  │  │
│  │  - canSetDefaultDialer()                               │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│         Platform Channel   │                                 │
│                            ▼                                 │
│  Android OS                │                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Default Dialer API                                     │  │
│  │  - RoleHolder.getRole()                                │  │
│  │  - RoleManager.requestRole()                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Dart Implementation Specification

### Class Structure

```dart
import 'package:flutter_dialer/flutter_dialer.dart';

/// TeleDialer provides dialer replacement functionality for flutter_tele
class TeleDialer {
  /// Check if this app is the default dialer
  static Future<bool> isDefaultDialer() async {
    return await FlutterDialer.isDefaultDialer();
  }

  /// Set this app as the default dialer
  static Future<bool> setDefaultDialer() async {
    return await FlutterDialer.setDefaultDialer();
  }

  /// Check if this app can be set as default dialer
  static Future<bool> canSetDefaultDialer() async {
    return await FlutterDialer.canSetDefaultDialer();
  }

  /// Request to become the default dialer (opens system dialog)
  static Future<bool> requestDefaultDialer() async {
    return await FlutterDialer.setDefaultDialer();
  }
}
```

### Method Specifications

#### isDefaultDialer()

```dart
static Future<bool> isDefaultDialer() async {
  return await FlutterDialer.isDefaultDialer();
}
```

**Behavior**:
- Returns `true` if app is current default dialer
- Returns `false` if not default dialer or on iOS
- May throw exception if flutter_dialer fails

**Usage**:
```dart
if (await TeleDialer.isDefaultDialer()) {
  print('App is default dialer');
} else {
  print('App is NOT default dialer');
}
```

---

#### setDefaultDialer()

```dart
static Future<bool> setDefaultDialer() async {
  return await FlutterDialer.setDefaultDialer();
}
```

**Behavior**:
- Attempts to set app as default dialer
- May open system settings UI
- Returns `true` on success, `false` on failure
- Android-only (returns false on iOS)

**Usage**:
```dart
final success = await TeleDialer.setDefaultDialer();
if (success) {
  print('Successfully set as default dialer');
} else {
  print('Failed to set as default dialer');
}
```

---

#### canSetDefaultDialer()

```dart
static Future<bool> canSetDefaultDialer() async {
  return await FlutterDialer.canSetDefaultDialer();
}
```

**Behavior**:
- Checks if app can be set as default dialer
- Verifies Android version, permissions, manifest configuration
- Returns `true` if capable, `false` otherwise

**Usage**:
```dart
if (await TeleDialer.canSetDefaultDialer()) {
  // Show "Set as default dialer" button
} else {
  // Hide button or show explanation
}
```

---

#### requestDefaultDialer()

```dart
static Future<bool> requestDefaultDialer() async {
  return await FlutterDialer.setDefaultDialer();
}
```

**Current Behavior**:
- Calls same method as `setDefaultDialer()`
- No distinct implementation

**Expected Behavior** (per method name):
- Open system dialog for user confirmation
- Return `true` if user grants, `false` if denied

**Usage**:
```dart
final granted = await TeleDialer.requestDefaultDialer();
if (granted) {
  print('User granted default dialer status');
}
```

**Note**: Current implementation may not match expected behavior from method name.

---

## Android-Specific Behavior

### Default Dialer Requirements

On Android, to become the default dialer, the app must:

1. **Declare required permissions** in AndroidManifest.xml:
   ```xml
   <uses-permission android:name="android.permission.CALL_PHONE" />
   <uses-permission android:name="android.permission.MANAGE_OWN_CALLS" />
   ```

2. **Handle dialer role** (Android 9+):
   ```java
   RoleManager roleManager = getSystemService(RoleManager.class);
   if (roleManager.isRoleAvailable(RoleManager.ROLE_DIALER)) {
       // Request role
   }
   ```

3. **Implement InCallService**: Required for dialer functionality

### Android Version Differences

| Android Version | API | Notes |
|----------------|-----|-------|
| Android 9+ (API 28+) | RoleManager | Modern approach |
| Android 5-8 (API 21-27) | Intent.ACTION_CHANGE_DEFAULT_DIALER | Legacy approach |
| iOS | N/A | Not supported |

---

## Known Issues and Limitations

### Issue 1: Method Naming Confusion

**Problem**: `requestDefaultDialer()` calls same method as `setDefaultDialer()`.

**Current Implementation**:
```dart
static Future<bool> requestDefaultDialer() async {
  return await FlutterDialer.setDefaultDialer();  // Same as setDefaultDialer()
}
```

**Expected Behavior** (per method name):
- `requestDefaultDialer()` should open system dialog
- `setDefaultDialer()` may silently attempt to set

**Recommendation**: 
- Option A: Rename `requestDefaultDialer()` to clarify it's an alias
- Option B: Implement proper dialog request if flutter_dialer supports it

### Issue 2: No Documentation

**Problem**: Methods lack dartdoc comments explaining behavior.

**Impact**: Developers may not understand Android-specific behavior or limitations.

**Recommendation**: Add dartdoc comments to all public methods.

### Issue 3: No Error Handling

**Problem**: Exceptions from flutter_dialer propagate directly.

**Impact**: Unhandled exceptions may crash app if not caught by caller.

**Recommendation**: Document exception behavior or add try-catch wrapper.

### Issue 4: iOS Behavior Undocumented

**Problem**: No documentation of iOS behavior.

**Impact**: Developers may assume cross-platform support.

**Recommendation**: Document that methods return `false` on iOS or throw exception.

---

## Testing Recommendations

### Unit Tests

1. **Method Delegation Tests**
   - Verify each method calls correct FlutterDialer method
   - Mock FlutterDialer for isolated testing

2. **Return Value Tests**
   - Test true/false return values
   - Test exception propagation

### Integration Tests

1. **Android Tests** (on real device or emulator)
   - Test isDefaultDialer() when app is/isn't default
   - Test setDefaultDialer() with user interaction
   - Test canSetDefaultDialer() capability check

2. **iOS Tests** (verify graceful degradation)
   - Verify methods return false or handle gracefully

---

## Usage Example

```dart
import 'package:flutter_tele/flutter_tele.dart';

class DialerSetupWidget extends StatefulWidget {
  @override
  _DialerSetupWidgetState createState() => _DialerSetupWidgetState();
}

class _DialerSetupWidgetState extends State<DialerSetupWidget> {
  bool _isDefaultDialer = false;
  bool _canSetDialer = false;

  @override
  void initState() {
    super.initState();
    _checkDialerStatus();
  }

  Future<void> _checkDialerStatus() async {
    final isDefault = await TeleDialer.isDefaultDialer();
    final canSet = await TeleDialer.canSetDefaultDialer();
    
    setState(() {
      _isDefaultDialer = isDefault;
      _canSetDialer = canSet;
    });
  }

  Future<void> _requestDialer() async {
    final success = await TeleDialer.requestDefaultDialer();
    
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('App is now default dialer!')),
      );
      _checkDialerStatus();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to set as default dialer')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Default dialer: ${_isDefaultDialer ? "Yes" : "No"}'),
        if (!_isDefaultDialer && _canSetDialer)
          ElevatedButton(
            onPressed: _requestDialer,
            child: Text('Set as default dialer'),
          ),
      ],
    );
  }
}
```

---

*Generated by /legacy reverse engineering*
