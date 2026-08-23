# Requirements: Platform Channel Endpoint

**Status**: DRAFT  
**Type**: SDD (Spec-Driven Development)  
**Module**: endpoint  
**Generated**: 2026-03-04 by /legacy

---

## Overview

The endpoint module provides the communication bridge between Flutter and Android native code. It implements platform channel abstraction using MethodChannel for commands and EventChannel for real-time event streaming, enabling Flutter applications to control Android telephony features.

---

## Functional Requirements

### R1: MethodChannel Communication

**Description**: Establish synchronous command/response communication from Flutter to Android.

**Requirements**:
- R1.1: MethodChannel named 'flutter_tele'
- R1.2: Support 15 method calls (see R3)
- R1.3: Return results asynchronously (Future<dynamic>)
- R1.4: Handle errors via PlatformException
- R1.5: Support Map arguments for complex parameters

**Source**: `lib/src/endpoint.dart`, `android/.../FlutterTelePlugin.kt`

---

### R2: EventChannel Streaming

**Description**: Establish asynchronous event streaming from Android to Flutter.

**Requirements**:
- R2.1: EventChannel named 'flutter_tele_events'
- R2.2: Support broadcast stream (multiple listeners)
- R2.3: Route events by type to separate StreamControllers
- R2.4: Support event subscription and cancellation
- R2.5: Event format: `{ type: String, data: Map<String, dynamic> }`

**Source**: `lib/src/endpoint.dart`, `android/.../FlutterTelePlugin.kt`

---

### R3: Method API

**Description**: Define all supported method calls.

| Method | Arguments | Return | Description |
|--------|-----------|--------|-------------|
| requestPermissions | none | bool | Request phone permissions |
| hasPermissions | none | bool | Check if permissions granted |
| start | Map configuration | Map | Start telephony service |
| makeCall | int sim, String destination, Map callSettings, Map msgData | TeleCall | Make outgoing call |
| answerCall | int callId | bool | Answer incoming call |
| hangupCall | int callId | bool | End call |
| declineCall | int callId | bool | Reject incoming call |
| holdCall | int callId | bool | Hold call |
| unholdCall | int callId | bool | Resume held call |
| muteCall | int callId | bool | Mute microphone |
| unMuteCall | int callId | bool | Unmute microphone |
| useSpeaker | int callId | bool | Enable speakerphone |
| useEarpiece | int callId | bool | Enable earpiece |
| sendEnvelope | int callId | String | Send SIM envelope command |

**Source**: `lib/src/endpoint.dart`, `android/.../FlutterTelePlugin.kt`

---

### R4: Event Types

**Description**: Define all event types streamed from Android to Flutter.

| Event Type | Data Payload | Description |
|------------|--------------|-------------|
| service_started | { status: "initialized" } | Service initialization complete |
| call_received | TeleCall map | New call received (incoming or outgoing) |
| call_changed | TeleCall map | Call state changed |
| call_terminated | TeleCall map | Call ended |
| call_error | { error: String, destination: String, sim: Int } | Call error occurred |

**Source**: `android/.../TeleService.kt`, `android/.../FlutterTelePlugin.kt`

---

### R5: Permission Management

**Description**: Handle Android phone permissions.

**Requirements**:
- R5.1: Check permissions: READ_PHONE_STATE, CALL_PHONE, READ_CALL_LOG, ANSWER_PHONE_CALLS, MANAGE_OWN_CALLS
- R5.2: hasPermissions() returns true if all permissions granted
- R5.3: requestPermissions() should request missing permissions
- R5.4: Handle permission denial gracefully

**Current Limitation**: requestPermissions() returns false (requires Activity for runtime permission request)

**Source**: `android/.../FlutterTelePlugin.kt`

---

### R6: Service Lifecycle

**Description**: Manage TeleService lifecycle.

**Requirements**:
- R6.1: start(configuration) starts TeleService with configuration
- R6.2: All call control methods (makeCall, answerCall, etc.) start TeleService via Intent
- R6.3: Service handles actions: START_TELEPHONY_SERVICE, MAKE_CALL, ANSWER_CALL, HANGUP_CALL, etc.
- R6.4: Return initial state from start() method

**Source**: `android/.../FlutterTelePlugin.kt`, `android/.../TeleService.kt`

---

### R7: Event Distribution

**Description**: Broadcast events to multiple Flutter listeners.

**Requirements**:
- R7.1: Single eventSink shared for all event types
- R7.2: Map<eventType, StreamController> for event routing
- R7.3: Broadcast streams (multiple listeners per event type)
- R7.4: Lazy StreamController creation (created on first subscription)
- R7.5: Proper cleanup on dispose()

**Source**: `lib/src/endpoint.dart`

---

### R8: Error Handling

**Description**: Handle platform channel errors gracefully.

**Requirements**:
- R8.1: Catch PlatformException for all method calls
- R8.2: Wrap in generic Exception with descriptive message
- R8.3: Return false/empty results for non-critical failures
- R8.4: Log errors for debugging

**Current Issue**: PlatformException re-thrown as generic Exception loses type information

**Source**: `lib/src/endpoint.dart`

---

### R9: Resource Management

**Description**: Clean up resources when endpoint is no longer needed.

**Requirements**:
- R9.1: dispose() cancels event subscription
- R9.2: dispose() closes all StreamControllers
- R9.3: dispose() clears event controller map
- R9.4: Prevent memory leaks from abandoned streams

**Source**: `lib/src/endpoint.dart`

---

### R10: Intent-Based Communication

**Description**: Use Android Intents for Plugin → Service communication.

**Requirements**:
- R10.1: Plugin sends Intents to TeleService (not direct method calls)
- R10.2: Intent action strings: START_TELEPHONY_SERVICE, MAKE_CALL, ANSWER_CALL, etc.
- R10.3: Intent extras carry method parameters
- R10.4: Service started via context.startService(intent)

**Source**: `android/.../FlutterTelePlugin.kt`

---

### R11: Stub Implementations

**Description**: Document incomplete/stub implementations.

**Requirements**:
- R11.1: sendEnvelope() returns hardcoded "TESTTEST"
- R11.2: Document stub status in specifications
- R11.3: Plan for future implementation

**Source**: `android/.../FlutterTelePlugin.kt`

---

## Non-Functional Requirements

### NFR1: Performance

- NFR1.1: Method calls should complete within 100ms (excluding actual telephony operations)
- NFR1.2: Event streaming should have <50ms latency
- NFR1.3: Broadcast streams should support multiple listeners without performance degradation

### NFR2: Reliability

- NFR2.1: Handle null arguments gracefully
- NFR2.2: Handle missing eventSink (listener disconnected)
- NFR2.3: Prevent crashes from malformed data

### NFR3: Maintainability

- NFR3.1: Extensive debug logging (print statements)
- NFR3.2: Clear method names matching telephony operations
- NFR3.3: Consistent error handling pattern

### NFR4: Compatibility

- NFR4.1: Support Android 8.0+ (Oreo/API 26+) for InCallService compatibility
- NFR4.2: Handle different Android versions' permission models
- NFR4.3: Support dual-SIM devices

---

## Dependencies

- **Flutter**: MethodChannel, EventChannel, StreamController
- **Android**: Intent, Service, Context, Manifest permissions
- **TeleService**: Receives Intents and executes telephony operations
- **TeleCall**: Data model for call information

---

## Open Questions

1. **Permission request limitation**: requestPermissions() returns false - should this be fixed with Activity integration?
   - **Impact**: App cannot request permissions at runtime
   - **Recommendation**: Integrate with Activity for proper permission request

2. **sendEnvelope() stub**: Returns "TESTTEST" - what is the intended functionality?
   - **Impact**: SIM envelope commands not functional
   - **Recommendation**: Implement using TelephonyManager or remove API

3. **Service-per-call pattern**: Every method calls startService() - is this intentional?
   - **Impact**: Potential redundant service starts
   - **Recommendation**: Document if intentional or optimize with service binding

4. **Debug logging**: Extensive print() statements in production code
   - **Impact**: Performance, log pollution
   - **Recommendation**: Replace with proper logging framework (Logger, Logcat)

---

*Generated by /legacy reverse engineering*
