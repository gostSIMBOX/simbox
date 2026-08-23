# Requirements: Event Streaming

**Status**: DRAFT  
**Type**: SDD (Spec-Driven Development)  
**Module**: event-streaming  
**Generated**: 2026-03-04 by /legacy

---

## Overview

The event-streaming module provides real-time event broadcasting from Android native code to Flutter. It uses Flutter's EventChannel for cross-platform event streaming, with event type routing to separate broadcast streams for multiple listeners.

---

## Functional Requirements

### R1: EventChannel Communication

**Description**: Establish asynchronous event streaming from Android to Flutter.

**Requirements**:
- R1.1: EventChannel named 'flutter_tele_events'
- R1.2: Implement EventChannel.StreamHandler on Android side
- R1.3: Store eventSink for asynchronous event sending
- R1.4: Handle listener cancellation (onCancel)
- R1.5: Support event sending from any thread (main thread handler)

**Source**: `lib/src/endpoint.dart`, `android/.../FlutterTelePlugin.kt`

---

### R2: Event Type Routing

**Description**: Route events to appropriate StreamControllers by event type.

**Requirements**:
- R2.1: Event format: `{ type: String, data: Map<String, dynamic> }`
- R2.2: Maintain Map<String, StreamController<dynamic>> for routing
- R2.3: Route events by type string to matching StreamController
- R2.4: Handle unknown event types gracefully (no crash)
- R2.5: Support dynamic event type registration (lazy creation)

**Source**: `lib/src/endpoint.dart`

---

### R3: Broadcast Stream Support

**Description**: Support multiple listeners per event type.

**Requirements**:
- R3.1: Use StreamController.broadcast() for all event types
- R3.2: Allow multiple simultaneous listeners per event type
- R3.3: Lazy StreamController creation (on first subscription)
- R3.4: Share single StreamController across all listeners of same type
- R3.5: Proper cleanup on dispose (close all controllers)

**Source**: `lib/src/endpoint.dart`

---

### R4: Event Types

**Description**: Define all supported event types.

| Event Type | Payload | Source | Description |
|------------|---------|--------|-------------|
| service_started | { status: "initialized" } | TeleService | Service initialization complete |
| call_received | TeleCall map | TeleService | New call detected |
| call_changed | TeleCall map | TeleService | Call state changed |
| call_terminated | TeleCall map | TeleService | Call ended |
| call_error | { error, destination, sim } | TeleService | Call error occurred |

**Source**: `android/.../TeleService.kt`

---

### R5: Event Sending (Android)

**Description**: Send events from Android to Flutter.

**Requirements**:
- R5.1: sendEvent(eventType, eventData) method
- R5.2: Create event map: `{ "type": eventType, "data": eventData }`
- R5.3: Call eventSink.success(event) to send
- R5.4: Handle null eventSink gracefully (no crash)
- R5.5: Log events for debugging

**Source**: `android/.../FlutterTelePlugin.kt`

---

### R6: Event Reception (Dart)

**Description**: Receive and route events in Flutter.

**Requirements**:
- R6.1: _setupEventChannel() subscribes to EventChannel broadcast stream
- R6.2: _handleEvent(event) parses and routes events
- R6.3: Convert Map<dynamic, dynamic> to Map<String, dynamic>
- R6.4: Extract event type and data from event map
- R6.5: Route to appropriate StreamController via type key

**Source**: `lib/src/endpoint.dart`

---

### R7: Stream Access API

**Description**: Provide stream access for Flutter consumers.

**Requirements**:
- R7.1: on(eventType) method returns Stream<dynamic>
- R7.2: Create StreamController if not exists (lazy)
- R7.3: Return broadcast stream for multiple listeners
- R7.4: Type-safe stream access (caller casts data)
- R7.5: Document stream lifecycle (created on first call)

**Source**: `lib/src/endpoint.dart`

---

### R8: Resource Management

**Description**: Clean up resources when endpoint is disposed.

**Requirements**:
- R8.1: dispose() cancels event subscription
- R8.2: dispose() closes all StreamControllers
- R8.3: dispose() clears event controller map
- R8.4: Prevent memory leaks from abandoned streams
- R8.5: Document dispose() requirement for users

**Source**: `lib/src/endpoint.dart`

---

### R9: Event Payload Specifications

**Description**: Define payload structure for each event type.

**call_received / call_changed / call_terminated**:
```dart
{
  "id": int,
  "state": String,
  "remoteNumber": String,
  "remoteName": String?,
  "held": bool,
  "muted": bool,
  "speaker": bool,
  "direction": String,
  // ... other TeleCall fields
}
```

**call_error**:
```dart
{
  "error": String?,
  "destination": String,
  "sim": int
}
```

**service_started**:
```dart
{
  "status": "initialized"
}
```

**Source**: `android/.../TeleService.kt`

---

### R10: Event Ordering

**Description**: Document event ordering guarantees (or lack thereof).

**Requirements**:
- R10.1: Document that events are sent in order from Android
- R10.2: Document that EventChannel does not guarantee delivery order
- R10.3: Document that no sequence numbers are used
- R10.4: Document that out-of-order delivery is possible under load
- R10.5: Recommend UI handles stale events gracefully

**Current Behavior**: No ordering guarantees

**Source**: `lib/src/endpoint.dart`, `android/.../FlutterTelePlugin.kt`

---

### R11: Error Handling

**Description**: Handle event-related errors gracefully.

**Requirements**:
- R11.1: Handle null eventSink (no listener connected)
- R11.2: Handle malformed event data (type casting errors)
- R11.3: Handle missing event type in routing map
- R11.4: Log errors for debugging
- R11.5: Prevent crashes from event handling errors

**Source**: `lib/src/endpoint.dart`, `android/.../FlutterTelePlugin.kt`

---

## Non-Functional Requirements

### NFR1: Performance

- NFR1.1: Event latency < 100ms (Android → Flutter)
- NFR1.2: Support 10+ events per second without backlog
- NFR1.3: Minimal overhead from event routing

### NFR2: Reliability

- NFR2.1: Handle null eventSink gracefully
- NFR2.2: Handle malformed events without crashes
- NFR2.3: Prevent memory leaks from unclosed streams

### NFR3: Maintainability

- NFR3.1: Consistent event format across all event types
- NFR3.2: Clear documentation of event payloads
- NFR3.3: Document dispose() requirement prominently

### NFR4: Type Safety

- NFR4.1: Document expected payload types for each event
- NFR4.2: Provide type casting examples in documentation
- NFR4.3: Consider adding runtime validation (future enhancement)

---

## Dependencies

- **Flutter**: EventChannel, StreamController, StreamSubscription
- **Android**: EventChannel.StreamHandler, EventSink
- **TeleCall**: Event payload data structure

---

## Open Questions

1. **Event ordering**: Should sequence numbers be added?
   - **Current**: No ordering guarantees
   - **Risk**: UI may show stale state
   - **Recommendation**: Add timestamps or sequence numbers

2. **Event acknowledgment**: Should Flutter acknowledge events?
   - **Current**: Fire-and-forget, no acknowledgment
   - **Risk**: No way to detect dropped events
   - **Recommendation**: Consider acknowledgment for critical events

3. **Event buffering**: Should events be buffered if no listener?
   - **Current**: Events silently dropped if eventSink is null
   - **Risk**: State desynchronization
   - **Recommendation**: Buffer last N events or request state refresh

4. **Type safety**: Should event payloads be validated?
   - **Current**: Dynamic typing, runtime casting
   - **Risk**: Runtime errors from malformed events
   - **Recommendation**: Add event validation layer

---

*Generated by /legacy reverse engineering*
