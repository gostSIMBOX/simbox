# Specifications: Event Streaming

**Status**: DRAFT  
**Type**: SDD (Spec-Driven Development)  
**Module**: event-streaming  
**Generated**: 2026-03-04 by /legacy

---

## Specification Overview

This document specifies the implementation details of the event streaming system based on analysis of existing code in `lib/src/endpoint.dart` and `android/src/main/kotlin/org/telon/tele/flutter_tele/FlutterTelePlugin.kt`.

---

## Architecture

### EventChannel Broadcast Pattern

```
┌─────────────────────────────────────────────────────────────┐
│  Android                                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ TeleService                                            │  │
│  │  - sendEvent(type, data)                               │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ FlutterTelePlugin                                      │  │
│  │  - EventChannel.StreamHandler                          │  │
│  │  - eventSink: EventSink?                               │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│              EventChannel    │                               │
│                            ▼                                 │
│  Flutter (Dart)              │                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ TeleEndpoint                                           │  │
│  │  - _eventChannel.receiveBroadcastStream()              │  │
│  │  - _handleEvent(event)                                 │  │
│  │  - _eventControllers: Map<String, StreamController>    │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│         Stream<dynamic)    │                                 │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Flutter UI                                             │  │
│  │  - endpoint.on("call_received").listen(...)            │  │
│  │  - endpoint.on("call_changed").listen(...)             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Event Flow

```
Android (TeleService)
     │
     │ sendEvent("call_changed", callData)
     ▼
FlutterTelePlugin (eventSink)
     │
     │ eventSink.success({ type: "call_changed", data: callData })
     ▼
EventChannel
     │
     │ Broadcast over platform channel
     ▼
TeleEndpoint (_eventChannel.receiveBroadcastStream())
     │
     │ _handleEvent(event)
     ├──────────────────────────────────────────┐
     │                                          │
     ▼                                          ▼
_eventControllers["call_changed"]     _eventControllers["call_received"]
     │                                          │
     ▼                                          ▼
StreamController.broadcast()          StreamController.broadcast()
     │                                          │
     ▼                                          ▼
Listener 1, Listener 2, ...           Listener 1, Listener 2, ...
```

---

## Dart Implementation Specification

### Channel Setup

```dart
class TeleEndpoint {
  static const EventChannel _eventChannel = EventChannel('flutter_tele_events')
  
  StreamSubscription? _eventSubscription
  final Map<String, StreamController<dynamic>> _eventControllers = {}
  
  TeleEndpoint() {
    _setupEventChannel()
  }
  
  void _setupEventChannel() {
    print('FlutterTele: Setting up event channel')
    _eventSubscription = _eventChannel.receiveBroadcastStream().listen((event) {
      print('FlutterTele: Received event from native: $event')
      _handleEvent(event)
    })
  }
  
  void _handleEvent(dynamic event) {
    print('FlutterTele: Handling event: $event')
    if (event is Map) {
      final eventStringMap = event.map((key, value) => MapEntry(key.toString(), value))
      final eventType = eventStringMap['type'] as String?
      final eventData = eventStringMap['data']
      print('FlutterTele: Event type: $eventType, data: $eventData')
      
      if (eventType != null && _eventControllers.containsKey(eventType)) {
        print('FlutterTele: Sending event to controller: $eventType')
        _eventControllers[eventType]!.add(eventData)
      } else if (eventType == 'call_error') {
        // Handle call error events
        print('FlutterTele: Call error: $eventData')
        if (_eventControllers.containsKey('call_error')) {
          _eventControllers['call_error']!.add(eventData)
        }
      } else {
        print('FlutterTele: No controller found for event type: $eventType')
      }
    } else {
      print('FlutterTele: Event is not a Map: ${event.runtimeType}')
    }
  }
  
  Stream<dynamic> on(String eventType) {
    print('FlutterTele: Creating event stream for type: $eventType')
    if (!_eventControllers.containsKey(eventType)) {
      print('FlutterTele: Creating new controller for event type: $eventType')
      _eventControllers[eventType] = StreamController<dynamic>.broadcast()
    }
    return _eventControllers[eventType]!.stream
  }
  
  void dispose() {
    _eventSubscription?.cancel()
    for (final controller in _eventControllers.values) {
      controller.close()
    }
    _eventControllers.clear()
  }
}
```

### Event Reception Pipeline

**Step 1: Subscribe to EventChannel**
```dart
_eventSubscription = _eventChannel.receiveBroadcastStream().listen((event) {
  _handleEvent(event)
})
```

**Step 2: Parse Event**
```dart
void _handleEvent(dynamic event) {
  if (event is Map) {
    // Convert Map<dynamic, dynamic> to Map<String, dynamic>
    final eventStringMap = event.map((key, value) => MapEntry(key.toString(), value))
    
    // Extract type and data
    final eventType = eventStringMap['type'] as String?
    final eventData = eventStringMap['data']
    
    // Route to appropriate controller
    if (eventType != null && _eventControllers.containsKey(eventType)) {
      _eventControllers[eventType]!.add(eventData)
    }
  }
}
```

**Step 3: Route to StreamController**
```dart
// Event type routing via map lookup
_eventControllers[eventType]!.add(eventData)
```

### StreamController Management

**Lazy Creation**:
```dart
Stream<dynamic> on(String eventType) {
  // Create controller on first subscription (lazy)
  if (!_eventControllers.containsKey(eventType)) {
    _eventControllers[eventType] = StreamController<dynamic>.broadcast()
  }
  return _eventControllers[eventType]!.stream
}
```

**Broadcast Mode**:
```dart
// All controllers use broadcast mode for multiple listeners
StreamController<dynamic>.broadcast()
```

**Cleanup**:
```dart
void dispose() {
  _eventSubscription?.cancel()  // Cancel EventChannel subscription
  
  // Close all StreamControllers
  for (final controller in _eventControllers.values) {
    controller.close()
  }
  
  _eventControllers.clear()  // Clear map
}
```

---

## Android Implementation Specification

### EventChannel StreamHandler

```kotlin
class FlutterTelePlugin : FlutterPlugin, MethodCallHandler {
  private lateinit var eventChannel: EventChannel
  private var eventSink: EventChannel.EventSink? = null
  
  override fun onAttachedToEngine(binding: FlutterPlugin.FlutterPluginBinding) {
    eventChannel = EventChannel(binding.binaryMessenger, "flutter_tele_events")
    eventChannel.setStreamHandler(object : EventChannel.StreamHandler {
      override fun onListen(arguments: Any?, events: EventChannel.EventSink?) {
        eventSink = events  // Store for later use
      }
      
      override fun onCancel(arguments: Any?) {
        eventSink = null  // Clear on cancel
      }
    })
  }
}
```

### Event Sending

```kotlin
fun sendEvent(eventType: String, eventData: Map<String, Any?>) {
  val event = mapOf(
    "type" to eventType,
    "data" to eventData
  )
  Log.d(TAG, "Sending event to Flutter: $event")
  eventSink?.success(event)  // Send to Flutter
}
```

**Usage Examples**:

**Service Started**:
```kotlin
FlutterTelePlugin.getInstance()?.sendEvent("service_started", mapOf(
  "status" to "initialized"
))
```

**Call Received**:
```kotlin
FlutterTelePlugin.getInstance()?.sendEvent("call_received", teleCall.toMap())
```

**Call Changed**:
```kotlin
FlutterTelePlugin.getInstance()?.sendEvent("call_changed", teleCall.toMap() as Map<String, Any>)
```

**Call Terminated**:
```kotlin
FlutterTelePlugin.getInstance()?.sendEvent("call_terminated", teleCall.toMap() as Map<String, Any>)
```

**Call Error**:
```kotlin
FlutterTelePlugin.getInstance()?.sendEvent("call_error", mapOf(
  "error" to e.message,
  "destination" to destination,
  "sim" to sim
))
```

---

## Event Type Specifications

### service_started

**Trigger**: TeleService initialization complete

**Payload**:
```kotlin
mapOf("status" to "initialized")
```

**Dart Usage**:
```dart
endpoint.on('service_started').listen((data) {
  print('Service status: ${data['status']}');
});
```

---

### call_received

**Trigger**: New call detected (incoming or outgoing)

**Payload**: TeleCall map (see sdd-call-model for full specification)

**Minimal Payload** (Kotlin TeleCall):
```kotlin
mapOf(
  "id" to id,
  "destination" to (destination ?: ""),
  "sim" to (sim ?: 1),
  "state" to (state ?: "UNKNOWN"),
  "held" to (held ?: false),
  "muted" to (muted ?: false),
  "speaker" to (speaker ?: false),
  "direction" to (direction ?: "UNKNOWN"),
  "remoteNumber" to (remoteNumber ?: ""),
  "remoteName" to (remoteName ?: "")
)
```

**Dart Usage**:
```dart
endpoint.on('call_received').listen((data) {
  final call = TeleCall.fromMap(data);
  print('New call: ${call.remoteNumber}');
});
```

---

### call_changed

**Trigger**: Call state or property changed

**Payload**: TeleCall map (same as call_received)

**Dart Usage**:
```dart
endpoint.on('call_changed').listen((data) {
  final call = TeleCall.fromMap(data);
  print('Call state: ${call.state}');
  // Update UI with new call state
});
```

---

### call_terminated

**Trigger**: Call ended/disconnected

**Payload**: TeleCall map with state = "DISCONNECTED"

**Dart Usage**:
```dart
endpoint.on('call_terminated').listen((data) {
  final call = TeleCall.fromMap(data);
  print('Call ended: ${call.remoteNumber}');
  // Remove call from UI
});
```

---

### call_error

**Trigger**: Call operation failed

**Payload**:
```kotlin
mapOf(
  "error" to e.message,
  "destination" to destination,
  "sim" to sim
)
```

**Dart Usage**:
```dart
endpoint.on('call_error').listen((data) {
  print('Call error: ${data['error']}');
  // Show error to user
});
```

---

## Event Flow Examples

### Incoming Call Flow

```
1. Android Telecom Framework: onCallAdded(call)
   
2. TeleService:
   - Extract call details (number, name)
   - Create TeleCall object
   - Register Call.Callback
   - callMapping[teleCall.id] = call

3. TeleService → FlutterTelePlugin:
   sendEvent("call_received", teleCall.toMap())

4. FlutterTelePlugin:
   eventSink.success({ type: "call_received", data: callData })

5. EventChannel:
   Broadcast to Flutter

6. TeleEndpoint:
   - _handleEvent(event)
   - Route to _eventControllers["call_received"]
   - _eventControllers["call_received"]!.add(callData)

7. Flutter UI:
   stream.listen() receives event
   Update incoming call screen
```

### Call State Change Flow

```
1. Android Call.Callback: onStateChanged(call, state)

2. TeleService:
   - Map Android state to TeleCall state
   - Update teleCall.state

3. TeleService → FlutterTelePlugin:
   sendEvent("call_changed", teleCall.toMap())

4. FlutterTelePlugin:
   eventSink.success({ type: "call_changed", data: callData })

5. EventChannel:
   Broadcast to Flutter

6. TeleEndpoint:
   - _handleEvent(event)
   - Route to _eventControllers["call_changed"]
   - Broadcast to all listeners

7. Flutter UI:
   stream.listen() receives event
   Update call state display
```

### Multiple Listeners Flow

```
Flutter UI Components:
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ CallScreen      │  │ CallHistory     │  │ BackgroundSync  │
│                 │  │                 │  │                 │
│ on('call_       │  │ on('call_       │  │ on('call_       │
│ received')      │  │ received')      │  │ received')      │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ StreamController  │
                    │ .broadcast()      │
                    └─────────┬─────────┘
                              │
                    All listeners receive event
```

---

## Known Issues and Limitations

### Issue 1: No Event Ordering Guarantees

**Problem**: Events are sent in order but EventChannel doesn't guarantee delivery order.

**Impact**: UI may show stale state if events arrive out of order.

**Example**:
```
Android sends: call_changed (state=CONNECTING) → call_changed (state=ACTIVE)
Flutter receives: call_changed (state=ACTIVE) → call_changed (state=CONNECTING)
Result: UI shows CONNECTING when call is actually ACTIVE
```

**Recommended Fix**: Add sequence numbers or timestamps to events.

### Issue 2: Null eventSink Drops Events

**Problem**: Events silently dropped if eventSink is null (no listener connected).

**Impact**: State desynchronization if Flutter misses events during startup/restart.

**Example**:
```
1. Android sends event before Flutter subscribes
2. eventSink is null
3. Event dropped silently
4. Flutter never receives event
```

**Recommended Fix**: Buffer last N events or request state refresh on connect.

### Issue 3: No Type Safety

**Problem**: Dynamic event data, no compile-time type checking.

**Impact**: Runtime errors from malformed events.

**Example**:
```dart
final call = TeleCall.fromMap(data)  // Crashes if data is malformed
```

**Recommended Fix**: Add event validation layer with try-catch.

### Issue 4: Memory Leak Risk

**Problem**: StreamControllers not closed if dispose() not called.

**Impact**: Memory leaks if TeleEndpoint not disposed.

**Example**:
```dart
// User forgets to dispose
final endpoint = TeleEndpoint()
// ... use endpoint ...
// Missing: endpoint.dispose()
```

**Recommended Fix**: Document dispose() requirement prominently, consider using Closeable interface.

### Issue 5: No Backpressure Handling

**Problem**: Broadcast streams don't handle backpressure.

**Impact**: Event flood may overwhelm slow listeners.

**Example**:
```
100 events/second sent, listener processes 10/second
→ Event backlog grows indefinitely
```

**Recommended Fix**: Add buffering or throttling mechanism.

---

## Testing Recommendations

### Unit Tests (Dart)

1. **Event Routing Tests**
   - Test event type extraction
   - Test StreamController creation
   - Test broadcast stream delivery to multiple listeners

2. **StreamController Lifecycle Tests**
   - Test lazy creation
   - Test proper cleanup on dispose
   - Test multiple subscriptions to same event type

3. **Error Handling Tests**
   - Test malformed event handling
   - Test null eventSink handling
   - Test unknown event type handling

### Integration Tests

1. **EventChannel Tests**
   - Test Android → Flutter event flow
   - Test event latency
   - Test event ordering under load

2. **Multi-Listener Tests**
   - Test multiple listeners per event type
   - Test listener isolation
   - Test listener add/remove during event stream

---

*Generated by /legacy reverse engineering*
