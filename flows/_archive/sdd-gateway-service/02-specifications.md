# Specifications: Gateway Service

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GatewayService                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Service Orchestration                 │   │
│  │  - SipService    - SmsService    - TelephonyService  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Call Routing Engine                  │   │
│  │  - SIP→GSM routing  - GSM→SIP routing  - State sync  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   State Management                    │   │
│  │  - statusStream  - routingStream  - logStream        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. GatewayService (Singleton)

**Pattern**: Singleton with internal factory  
**Purpose**: Central orchestration and routing

```dart
class GatewayService {
  // Singleton pattern
  static final GatewayService _instance = GatewayService._internal();
  factory GatewayService() => _instance;
  GatewayService._internal();
  
  // Sub-services
  final SipService _sipService = SipService();
  final SmsService _smsService = SmsService();
  final TelephonyService _telephonyService = TelephonyService();
  
  // State
  GatewayConfig? _config;
  bool _isRunning = false;
  DateTime? _startTime;
  int _totalCallsHandled = 0;
  int _totalMessagesHandled = 0;
  
  // Active routings
  final Map<String, CallRouting> _activeRoutings = {};
  int _routingCounter = 0;
  
  // Streams
  final StreamController<GatewayStatus> _statusController;
  final StreamController<CallRouting> _routingController;
  final StreamController<String> _logController;
}
```

### 2. GatewayConfig

**Purpose**: Configuration container with serialization

```dart
class GatewayConfig {
  final SipAccount sipAccount;           // Required
  final SmppConfig? smppConfig;          // Optional
  final bool autoAnswer;                 // Default: false
  final bool enableLogging;              // Default: true
  final bool routeSipToGsm;              // Default: true
  final bool routeGsmToSip;              // Default: true
  final bool routeSmsToSmpp;             // Default: false
  final bool routeSmppToSms;             // Default: false
  final int maxConcurrentCalls;          // Default: 5
  
  // JSON serialization
  Map<String, dynamic> toJson();
  factory GatewayConfig.fromJson(Map<String, dynamic>);
}
```

### 3. GatewayStatus

**Purpose**: Status snapshot for UI and monitoring

```dart
class GatewayStatus {
  final bool isRunning;
  final SipConnectionState sipState;
  final SmppConnectionState smppState;
  final TelephonyPermissionStatus telephonyPermissions;
  final int activeCalls;
  final int totalCallsHandled;
  final int totalMessagesHandled;
  final DateTime? startTime;
  final Duration? uptime;
}
```

### 4. CallRouting

**Purpose**: Active call routing tracker

```dart
class CallRouting {
  final String id;
  final String sipCallId;
  final String? telephonyCallId;
  final String number;
  final CallRoutingDirection direction;
  final CallRoutingState state;
  final DateTime startTime;
}

enum CallRoutingDirection { sipToGsm, gsmToSip }
enum CallRoutingState { connecting, active, ended, failed }
```

## API Specifications

### Initialization

```dart
Future<bool> initialize(GatewayConfig config)
```

**Flow:**
```
initialize(config)
       │
       ├─► _telephonyService.initialize()
       │    └─► Return false if fails
       ├─► _sipService.initialize(config.sipAccount)
       │    └─► Return false if fails
       ├─► _smsService.initializeSmpp(config.smppConfig)
       │    └─► Continue if fails (optional)
       ├─► _setupEventListeners()
       └─► _saveConfiguration()
```

**Preconditions:**
- config.sipAccount must be valid

**Postconditions:**
- All sub-services initialized
- Event listeners configured
- Configuration persisted

### Start

```dart
Future<bool> start()
```

**Flow:**
```
start()
       │
       ├─► Check _config != null
       ├─► _sipService.register()
       │    └─► Return false if fails
       ├─► _smsService.connectSmpp() [if configured]
       ├─► _isRunning = true
       ├─► _startTime = DateTime.now()
       └─► _updateStatus()
```

### Stop

```dart
Future<void> stop()
```

**Flow:**
```
stop()
       │
       ├─► For each routing in _activeRoutings:
       │    └─► _endRouting(routing.id)
       ├─► _sipService.unregister()
       ├─► _smsService.disconnectSmpp()
       ├─► _isRunning = false
       ├─► _startTime = null
       └─► _updateStatus()
```

### Make Call (SIP→GSM)

```dart
Future<String?> makeCallViaSip(String number)
```

**Flow:**
```
makeCallViaSip(number)
       │
       ├─► Check _isRunning && _config!.routeSipToGsm
       ├─► _sipService.makeCall(number) → sipCallId
       ├─► Create CallRouting (state: connecting)
       ├─► Add to _activeRoutings
       ├─► Broadcast via _routingController
       ├─► Listen for sipCall.state == active
       └─► _makeGsmCallForRouting(routingId, number)
            │
            ├─► _telephonyService.makeCall(number)
            ├─► Update CallRouting (state: active)
            └─► Broadcast update
```

### Send SMS

```dart
Future<String?> sendSms(String recipient, String content, {bool useSmpp = false})
```

**Behavior:**
- If `useSmpp == true` and SMPP configured: use `_smsService.sendSmsViaSmpp()`
- Otherwise: use `_smsService.sendSmsLocal()`

## Event Handling

### SIP Call State Changes

```dart
void _handleSipCallStateChange(SipCall call) {
  _log('SIP call state changed: ${call.id} -> ${call.state.name}');
  _updateStatus();
}
```

### Telephony Call State Changes

```dart
void _handleTelephonyCallStateChange(TelephonyCall call) {
  // Handle incoming GSM calls
  if (call.direction == incoming && call.state == ringing) {
    _handleIncomingGsmCall(call);
  }
  _updateStatus();
}
```

### SMS Messages

```dart
void _handleSmsMessage(SmsMessage message) {
  _log('SMS message: ${message.type.name} ${message.id}');
  _totalMessagesHandled++;
  _updateStatus();
}
```

## Data Flow Diagrams

### Configuration Persistence

```
_saveConfiguration()
       │
       ├─► SharedPreferences.getInstance()
       ├─► jsonEncode(_config!.toJson())
       └─► prefs.setString('gateway_config', configJson)

loadConfiguration()
       │
       ├─► SharedPreferences.getInstance()
       ├─► prefs.getString('gateway_config')
       ├─► jsonDecode(configJson)
       └─► GatewayConfig.fromJson()
```

### Status Updates

```
_updateStatus()
       │
       ├─► getStatus()
       │    ├─► Collect from sub-services
       │    ├─► Calculate uptime
       │    └─► Return GatewayStatus
       └─► _statusController.add(status)
            └─► All subscribers notified
```

## Error Handling

### Initialization Failures

```dart
if (!telephonyInitialized) {
  _log('Failed to initialize telephony service');
  return false;  // Fail fast
}

if (!sipInitialized) {
  _log('Failed to initialize SIP service');
  return false;  // Fail fast
}

if (!smppInitialized) {
  _log('Warning: Failed to initialize SMPP service');
  // Continue - SMPP is optional
}
```

### Call Routing Errors

```dart
try {
  // Call routing logic
} catch (e) {
  _log('Error making call via SIP: $e');
  return null;  // Graceful failure
}
```

### End Routing Errors

```dart
try {
  await _sipService.endCall(routing.sipCallId);
  if (routing.telephonyCallId != null) {
    await _telephonyService.endCall();
  }
} catch (e) {
  _log('Error ending routing: $e');
  // Continue cleanup
}
```

## Testing Strategy

### Unit Tests

```dart
test('GatewayService.initialize returns true when all services initialize', () async {
  final service = GatewayService();
  final config = GatewayConfig(sipAccount: testSipAccount);
  
  final result = await service.initialize(config);
  
  expect(result, true);
  expect(service.isRunning, false);  // Not started yet
});

test('makeCallViaSip creates routing and returns routing ID', () async {
  final service = GatewayService();
  await service.initialize(testConfig);
  await service.start();
  
  final routingId = await service.makeCallViaSip('+1234567890');
  
  expect(routingId, isNotNull);
  expect(service.activeRoutings.length, 1);
});
```

### Integration Tests

```dart
test('SIP→GSM routing completes successfully', () async {
  final service = GatewayService();
  await service.initialize(testConfig);
  await service.start();
  
  // Listen for routing updates
  final routingUpdates = <CallRouting>[];
  service.routingStream.listen(routingUpdates.add);
  
  // Make call
  await service.makeCallViaSip('+1234567890');
  
  // Wait for routing to complete
  await Future.delayed(Duration(seconds: 2));
  
  expect(routingUpdates.last.state, CallRoutingState.active);
});
```

## Dependencies

### Internal Dependencies

| Service | Purpose |
|---------|---------|
| SipService | SIP protocol handling |
| SmsService | SMS/SMPP handling |
| TelephonyService | GSM telephony handling |

### External Dependencies

| Package | Purpose |
|---------|---------|
| shared_preferences | Configuration persistence |
| logger | Logging |

## Configuration

### Storage Key

```dart
const String configKey = 'gateway_config';
```

### JSON Format

```json
{
  "sipAccount": {
    "username": "user",
    "password": "pass",
    "server": "192.168.88.254",
    "port": 5060
  },
  "smppConfig": null,
  "autoAnswer": false,
  "enableLogging": true,
  "routeSipToGsm": true,
  "routeGsmToSip": true,
  "routeSmsToSmpp": false,
  "routeSmppToSms": false,
  "maxConcurrentCalls": 5
}
```

---

**Status**: DRAFT  
**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)  
**Related**: 01-requirements.md
