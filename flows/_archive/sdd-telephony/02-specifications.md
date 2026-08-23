# Specifications: Telephony Service

## System Architecture

### Platform Channel Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    TelephonyService                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              MethodChannel Handler                    │   │
│  │  'gsm_sip_gateway/telephony'                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Call Management                      │   │
│  │  makeCall()  answerCall()  endCall()                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Permission Handling                     │   │
│  │  phone  sms  microphone  manageExternalStorage        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. TelephonyService (Singleton)

```dart
class TelephonyService {
  static const MethodChannel _channel = MethodChannel('gsm_sip_gateway/telephony');
  
  // State
  bool _isInitialized = false;
  final Map<String, TelephonyCall> _activeCalls = {};
  
  // Streams
  final StreamController<TelephonyCall> _callStateController;
  final StreamController<String> _logController;
  final StreamController<Map<String, dynamic>> _phoneStateController;
}
```

### 2. Native Methods

| Method | Parameters | Returns | Purpose |
|--------|------------|---------|---------|
| initialize | - | bool | Initialize native telephony |
| makeCall | number | callId | Make outgoing call |
| answerCall | - | bool | Answer incoming call |
| endCall | - | bool | End active call |
| getPhoneNumber | - | String? | Get device phone number |
| getNetworkOperatorName | - | String? | Get carrier name |
| getSimSerialNumber | - | String? | Get SIM serial |
| getSignalStrength | - | int? | Get signal strength |
| sendUssd | ussdCode | response? | Send USSD code |

### 3. Native Callbacks

| Callback | Parameters | Purpose |
|----------|------------|---------|
| onCallStateChanged | callId, state, number | Call state updates |
| onPhoneStateChanged | state data | Phone state changes |
| onIncomingCall | callId, number | Incoming call notification |

## API Specifications

### Initialize

```dart
Future<bool> initialize() async {
  // 1. Request permissions
  final granted = await _requestPermissions();
  if (!granted) return false;
  
  // 2. Set up method call handler
  _channel.setMethodCallHandler(_handleMethodCall);
  
  // 3. Initialize native layer
  await _channel.invokeMethod('initialize');
  
  _isInitialized = true;
  return true;
}
```

### Make Call

```dart
Future<String?> makeCall(String number) async {
  if (!_isInitialized) return null;
  
  final result = await _channel.invokeMethod('makeCall', {'number': number});
  
  if (result['success']) {
    final call = TelephonyCall(
      id: result['callId'],
      number: number,
      direction: TelephonyCallDirection.outgoing,
      state: TelephonyCallState.ringing,
      startTime: DateTime.now(),
    );
    _activeCalls[call.id] = call;
    _callStateController.add(call);
    return call.id;
  }
  return null;
}
```

### Handle Call State Changes

```dart
void _handleCallStateChanged(Map<String, dynamic> args) {
  final callId = args['callId'];
  final state = args['state'];
  final number = args['number'];
  
  final telephonyState = _mapCallState(state);
  final call = TelephonyCall(
    id: callId,
    number: number,
    direction: _activeCalls[callId]?.direction ?? TelephonyCallDirection.incoming,
    state: telephonyState,
    startTime: _activeCalls[callId]?.startTime ?? DateTime.now(),
    duration: telephonyState == TelephonyCallState.ended
        ? DateTime.now().difference(_activeCalls[callId]?.startTime ?? DateTime.now())
        : null,
  );
  
  if (telephonyState == TelephonyCallState.ended) {
    _activeCalls.remove(callId);
  } else {
    _activeCalls[callId] = call;
  }
  
  _callStateController.add(call);
}
```

## Permission Handling

### Permission Request Flow

```dart
Future<bool> _requestPermissions() async {
  final permissions = [
    Permission.phone,
    Permission.sms,
    Permission.microphone,
    Permission.manageExternalStorage,
  ];
  
  final statuses = await permissions.request();
  
  bool allGranted = true;
  for (final permission in permissions) {
    if (statuses[permission] != PermissionStatus.granted) {
      allGranted = false;
    }
  }
  return allGranted;
}
```

### Permission Status Check

```dart
Future<TelephonyPermissionStatus> checkPermissions() async {
  final phone = await Permission.phone.status;
  final sms = await Permission.sms.status;
  final mic = await Permission.microphone.status;
  
  if (phone.isGranted && sms.isGranted && mic.isGranted) {
    return TelephonyPermissionStatus.granted;
  } else if (phone.isPermanentlyDenied || sms.isPermanentlyDenied || mic.isPermanentlyDenied) {
    return TelephonyPermissionStatus.permanentlyDenied;
  } else if (phone.isRestricted || sms.isRestricted || mic.isRestricted) {
    return TelephonyPermissionStatus.restricted;
  } else {
    return TelephonyPermissionStatus.denied;
  }
}
```

## State Mappings

### Call State Mapping

```dart
TelephonyCallState _mapCallState(String state) {
  switch (state.toLowerCase()) {
    case 'idle': return TelephonyCallState.idle;
    case 'ringing': return TelephonyCallState.ringing;
    case 'offhook': return TelephonyCallState.offhook;
    case 'active': return TelephonyCallState.active;
    case 'hold': return TelephonyCallState.hold;
    case 'ended': return TelephonyCallState.ended;
    default: return TelephonyCallState.idle;
  }
}
```

## Testing Strategy

### Unit Tests

```dart
test('TelephonyService.initialize returns true when permissions granted', () async {
  final service = TelephonyService();
  
  // Mock permission grant
  when(permissionHandler.request(any)).thenAnswer((_) async => PermissionStatus.granted);
  when(channel.invokeMethod('initialize')).thenAnswer((_) async => null);
  
  final result = await service.initialize();
  
  expect(result, true);
  expect(service.isInitialized, true);
});

test('makeCall returns call ID on success', () async {
  final service = TelephonyService();
  await service.initialize();
  
  when(channel.invokeMethod('makeCall', {'number': '+1234567890'}))
    .thenAnswer((_) async => {'success': true, 'callId': 'call_123'});
  
  final callId = await service.makeCall('+1234567890');
  
  expect(callId, 'call_123');
});
```

## Dependencies

### External Dependencies

| Package | Purpose |
|---------|---------|
| permission_handler | Runtime permissions |
| flutter/services | MethodChannel |

### Native Dependencies

| Platform | Component |
|----------|-----------|
| Android | TelephonyManager |
| Android | MethodChannel handler |

---

**Status**: DRAFT  
**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)  
**Related**: 01-requirements.md
