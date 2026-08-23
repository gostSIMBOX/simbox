# Specifications: SIP Service

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      SipService                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Account Management                       │   │
│  │  SipAccount (username, password, domain, port)        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Connection Management                    │   │
│  │  initialize()  register()  unregister()               │   │
│  │  SipConnectionState tracking                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Call Management                      │   │
│  │  makeCall()  answerCall()  endCall()  holdCall()      │   │
│  │  SipCallState tracking                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. SipService (Singleton)

```dart
class SipService {
  // State
  SipAccount? _account;
  SipConnectionState _connectionState = SipConnectionState.disconnected;
  final Map<String, SipCall> _activeCalls = {};
  
  // Streams
  final StreamController<SipConnectionState> _connectionStateController;
  final StreamController<SipCall> _callStateController;
  final StreamController<String> _logController;
}
```

### 2. SipAccount

```dart
class SipAccount {
  final String username;
  final String password;
  final String domain;
  final String? proxy;
  final int port;        // default: 5060
  final bool useSecure;  // default: false
  
  // JSON serialization
  Map<String, dynamic> toJson();
  factory SipAccount.fromJson(Map<String, dynamic>);
}
```

### 3. SipCall

```dart
class SipCall {
  final String id;
  final String remoteNumber;
  final SipCallDirection direction;
  final SipCallState state;
  final DateTime startTime;
  final Duration? duration;
}

enum SipCallDirection { incoming, outgoing }
enum SipCallState { connecting, ringing, active, hold, ended, failed }
```

## API Specifications

### Initialize

```dart
Future<bool> initialize(SipAccount account) async {
  _account = account;
  _updateConnectionState(SipConnectionState.connecting);
  
  // Simulate initialization (2 second delay)
  await Future.delayed(const Duration(seconds: 2));
  
  _updateConnectionState(SipConnectionState.connected);
  return true;
}
```

### Register

```dart
Future<bool> register() async {
  if (_account == null) return false;
  
  _updateConnectionState(SipConnectionState.connecting);
  
  // Simulate registration (1 second delay)
  await Future.delayed(const Duration(seconds: 1));
  
  _updateConnectionState(SipConnectionState.connected);
  return true;
}
```

### Make Call

```dart
Future<String?> makeCall(String number) async {
  if (_connectionState != SipConnectionState.connected) return null;
  
  final callId = 'call_${DateTime.now().millisecondsSinceEpoch}';
  
  final call = SipCall(
    id: callId,
    remoteNumber: number,
    direction: SipCallDirection.outgoing,
    state: SipCallState.connecting,
    startTime: DateTime.now(),
  );
  
  _activeCalls[callId] = call;
  _callStateController.add(call);
  
  // Simulate call progression
  _simulateCallProgression(callId, number);
  
  return callId;
}
```

### Call Progression Simulation

```dart
void _simulateCallProgression(String callId, String number) {
  // After 1 second: ringing
  Timer(const Duration(seconds: 1), () {
    final call = _activeCalls[callId];
    if (call?.state == SipCallState.connecting) {
      _updateCallState(callId, SipCallState.ringing);
      
      // After 3 more seconds: active (answered)
      Timer(const Duration(seconds: 3), () {
        final currentCall = _activeCalls[callId];
        if (currentCall?.state == SipCallState.ringing) {
          _updateCallState(callId, SipCallState.active);
        }
      });
    }
  });
}
```

### End Call

```dart
Future<bool> endCall(String callId) async {
  final call = _activeCalls[callId];
  if (call == null) return false;
  
  final duration = DateTime.now().difference(call.startTime);
  
  final updatedCall = SipCall(
    id: call.id,
    remoteNumber: call.remoteNumber,
    direction: call.direction,
    state: SipCallState.ended,
    startTime: call.startTime,
    duration: duration,
  );
  
  _activeCalls.remove(callId);
  _callStateController.add(updatedCall);
  
  return true;
}
```

## State Transitions

### Connection State Flow

```
disconnected
     │
     ▼
connecting ──► connected
     │              │
     │              ▼
     └────────► error
```

### Outgoing Call Flow

```
connecting ──► ringing ──► active ──► hold ──► active ──► ended
                                            │
                                            └──► failed
```

### Incoming Call Flow

```
ringing ──► active ──► ended
```

## Testing Support

### Simulate Incoming Call

```dart
void simulateIncomingCall(String fromNumber) {
  if (_connectionState != SipConnectionState.connected) return;
  
  final callId = 'incoming_${DateTime.now().millisecondsSinceEpoch}';
  
  final call = SipCall(
    id: callId,
    remoteNumber: fromNumber,
    direction: SipCallDirection.incoming,
    state: SipCallState.ringing,
    startTime: DateTime.now(),
  );
  
  _activeCalls[callId] = call;
  _callStateController.add(call);
}
```

## Testing Strategy

### Unit Tests

```dart
test('SipService.initialize returns true on success', () async {
  final service = SipService();
  final account = SipAccount(
    username: 'test',
    password: 'pass',
    domain: 'sip.example.com',
  );
  
  final result = await service.initialize(account);
  
  expect(result, true);
  expect(service.connectionState, SipConnectionState.connected);
});

test('makeCall returns call ID when connected', () async {
  final service = SipService();
  await service.initialize(testAccount);
  
  final callId = await service.makeCall('+1234567890');
  
  expect(callId, isNotNull);
  expect(service.activeCalls.length, 1);
});
```

## Dependencies

### External Dependencies

| Package | Purpose |
|---------|---------|
| logger | Logging |

### Future Native Dependencies

| Platform | Component |
|----------|-----------|
| Android | PJSIP / SIP stack |
| iOS | CallKit / SIP stack |

---

**Status**: DRAFT  
**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)  
**Related**: 01-requirements.md
