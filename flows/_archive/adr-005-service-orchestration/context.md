# ADR 005: Service Orchestration

## Status

**PROPOSED** → DRAFT

## Context

The GOSTsimbox Gateway requires orchestration of multiple services:

- **GatewayService** - Core bidirectional routing logic
- **SipService** - SIP protocol handling
- **SmsService** - SMS/SMPP handling
- **TelephonyService** - Android GSM telephony

These services must:
- Initialize in correct order
- Coordinate call routing between protocols
- Share state and events
- Handle failures gracefully
- Support bidirectional GSM↔SIP/SMPP routing

### Requirements

1. **Service lifecycle** - Initialize, start, stop, dispose
2. **Event coordination** - Cross-service event handling
3. **State synchronization** - Consistent state across services
4. **Error isolation** - One service failure doesn't crash others
5. **Bidirectional routing** - SIP→GSM and GSM→SIP call routing

## Decision

We WILL implement **GatewayService as the central orchestrator** with the following patterns:

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GatewayService                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Service Dependencies                     │   │
│  │  SipService    SmsService    TelephonyService         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Call Routing Engine                      │   │
│  │  - SIP→GSM routing  - GSM→SIP routing                 │   │
│  │  - Call state synchronization                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Event Coordination                       │   │
│  │  - SIP events → GSM actions                           │   │
│  │  - GSM events → SIP actions                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Initialization Order

```dart
class GatewayService {
  final SipService _sipService = SipService();
  final SmsService _smsService = SmsService();
  final TelephonyService _telephonyService = TelephonyService();
  
  Future<bool> initialize(GatewayConfig config) async {
    // 1. Initialize telephony first (foundation)
    final telephonyInitialized = await _telephonyService.initialize();
    if (!telephonyInitialized) {
      _log('Failed to initialize telephony service');
      return false;
    }
    
    // 2. Initialize SIP service
    final sipInitialized = await _sipService.initialize(config.sipAccount);
    if (!sipInitialized) {
      _log('Failed to initialize SIP service');
      return false;
    }
    
    // 3. Initialize SMPP (optional)
    if (config.smppConfig != null) {
      final smppInitialized = await _smsService.initializeSmpp(config.smppConfig!);
      if (!smppInitialized) {
        _log('Warning: Failed to initialize SMPP service');
        // Continue - SMPP is optional
      }
    }
    
    // 4. Set up event listeners
    _setupEventListeners();
    
    // 5. Save configuration
    await _saveConfiguration();
    
    return true;
  }
}
```

### Event Coordination

```dart
void _setupEventListeners() {
  // SIP event listeners
  _sipService.callStateStream.listen(_handleSipCallStateChange);
  _sipService.logStream.listen(_handleServiceLog);
  
  // SMS event listeners
  _smsService.messageStream.listen(_handleSmsMessage);
  _smsService.logStream.listen(_handleServiceLog);
  
  // Telephony event listeners
  _telephonyService.callStateStream.listen(_handleTelephonyCallStateChange);
  _telephonyService.logStream.listen(_handleServiceLog);
}

void _handleSipCallStateChange(SipCall call) {
  _log('SIP call state changed: ${call.id} -> ${call.state.name}');
  _updateStatus();
}

void _handleTelephonyCallStateChange(TelephonyCall call) {
  _log('Telephony call state changed: ${call.id} -> ${call.state.name}');
  
  // Handle incoming GSM calls
  if (call.direction == incoming && call.state == ringing) {
    _handleIncomingGsmCall(call);
  }
  
  _updateStatus();
}
```

### Bidirectional Routing

**SIP→GSM Routing:**
```dart
Future<String?> makeCallViaSip(String number) async {
  if (!_isRunning || !_config!.routeSipToGsm) return null;
  
  // Make SIP call
  final sipCallId = await _sipService.makeCall(number);
  if (sipCallId == null) return null;
  
  // Create routing
  final routing = CallRouting(
    id: 'routing_${++_routingCounter}',
    sipCallId: sipCallId,
    number: number,
    direction: CallRoutingDirection.sipToGsm,
    state: CallRoutingState.connecting,
    startTime: DateTime.now(),
  );
  
  _activeRoutings[routing.id] = routing;
  
  // When SIP call becomes active, make GSM call
  _sipService.callStateStream.listen((sipCall) {
    if (sipCall.id == sipCallId && sipCall.state == SipCallState.active) {
      _makeGsmCallForRouting(routing.id, number);
    }
  });
  
  return routing.id;
}
```

**GSM→SIP Routing:**
```dart
Future<void> _handleIncomingGsmCall(TelephonyCall gsmCall) async {
  if (!_config!.routeGsmToSip) return;
  
  // Create SIP call to route the GSM call
  final sipCallId = await _sipService.makeCall(gsmCall.number);
  if (sipCallId == null) return;
  
  final routing = CallRouting(
    id: 'routing_${++_routingCounter}',
    sipCallId: sipCallId,
    telephonyCallId: gsmCall.id,
    number: gsmCall.number,
    direction: CallRoutingDirection.gsmToSip,
    state: CallRoutingState.connecting,
    startTime: DateTime.now(),
  );
  
  _activeRoutings[routing.id] = routing;
  
  // Auto-answer GSM call if configured
  if (_config!.autoAnswer) {
    await _telephonyService.answerCall();
  }
  
  _totalCallsHandled++;
}
```

### State Management

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

GatewayStatus getStatus() {
  return GatewayStatus(
    isRunning: _isRunning,
    sipState: _sipService.connectionState,
    smppState: _smsService.connectionState,
    telephonyPermissions: await _telephonyService.checkPermissions(),
    activeCalls: _activeRoutings.length,
    totalCallsHandled: _totalCallsHandled,
    totalMessagesHandled: _totalMessagesHandled,
    startTime: _startTime,
    uptime: _startTime != null 
        ? DateTime.now().difference(_startTime!) 
        : null,
  );
}
```

## Consequences

### Positive

1. **Centralized orchestration** - Single point of control
2. **Clear responsibilities** - Each service has defined role
3. **Event coordination** - Cross-service communication handled
4. **Bidirectional routing** - Both directions supported
5. **Error isolation** - Service failures contained
6. **State consistency** - Unified status reporting

### Negative

1. **Coupling** - GatewayService knows about all sub-services
2. **Complexity** - Routing logic is complex
3. **Single point of failure** - GatewayService failure affects all
4. **Testing complexity** - Must mock multiple services

### Alternatives Considered

**Event Bus pattern:**
- Pros: Loose coupling, flexible
- Cons: Harder to trace, implicit dependencies
- Decision: Direct event listeners for clarity

**Mediator pattern:**
- Pros: Explicit coordination, testable
- Cons: Additional abstraction layer
- Decision: GatewayService acts as mediator

**Microservices approach:**
- Pros: Independent deployment, scaling
- Cons: Overkill for mobile app, network complexity
- Decision: Monolithic service orchestration appropriate

## Compliance

- GatewayService MUST orchestrate all sub-services
- Services MUST expose state via streams
- Event listeners MUST be set up during initialization
- Routing MUST support both directions
- Errors in one service MUST NOT crash others
- Status MUST be aggregated from all services

## Related Decisions

- ADR 001: Clean Architecture (service layer)
- ADR 002: Dependency Injection (service registration)
- ADR 003: State Management (stream-based state)

## References

- Mediator pattern
- Event-driven architecture
- Service orchestration patterns

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)  
**Status**: DRAFT - Pending review
