# ADR-002: EventChannel for Real-Time Event Streaming

> Enabling architectural decision: Reactive event delivery to Flutter layer

## Status

DRAFT

## Type

Enabling - This decision enables real-time updates and reactive UI patterns.

## Context

The SIP plugin needs to notify the Flutter layer of asynchronous events:

- Account registration status changes
- Incoming call notifications
- Call state changes (answered, held, terminated)
- SIP message reception
- Network connectivity changes

**Requirements:**
1. Events must be delivered in real-time (< 500ms latency)
2. Multiple events can occur in rapid succession
3. Events must be delivered even when Flutter is busy
4. Flutter layer needs to subscribe/unsubscribe to events
5. Events continue when app is in background

**Constraints:**
- Flutter MethodChannel is request/response (not push-based)
- Android service runs independently of Flutter
- Events originate from native PJSIP library

## Decision

We will use **Flutter EventChannel** for real-time event streaming from native to Flutter:

### Architecture Pattern

```
┌─────────────────┐
│   Flutter App   │
└────────┬────────┘
         │ eventStream.listen()
         ▼
┌─────────────────┐
│  EventChannel   │  ← "flutter_sip2_events"
│   StreamHandler │
└────────┬────────┘
         │ eventSink.success(event)
         ▼
┌─────────────────┐
│PjSipBroadcast   │  ← Static eventSink reference
│   Receiver      │  ← emit(eventName, data)
└────────┬────────┘
         │ Broadcast Intent
         ▼
┌─────────────────┐
│  PjSipService   │  ← Broadcasts events
└─────────────────┘
```

### Implementation Details

1. **EventChannel named "flutter_sip2_events"** registered in plugin
2. **StreamHandler stores eventSink** in static reference for service access
3. **BroadcastReceiver receives events** from service via Intents
4. **Events emitted via eventSink.success()** with event name and data
5. **Flutter subscribes via eventStream** and filters by event type

### Code Pattern

```kotlin
// FlutterSip2Plugin.kt - EventChannel Setup
eventChannel = EventChannel(flutterPluginBinding.binaryMessenger, "flutter_sip2_events")
eventChannel.setStreamHandler(object : EventChannel.StreamHandler {
  override fun onListen(arguments: Any?, events: EventChannel.EventSink?) {
    PjSipBroadcastReceiver.setEventSink(events)  // Store for later use
  }
  override fun onCancel(arguments: Any?) {
    PjSipBroadcastReceiver.setEventSink(null)  // Clear on unsubscribe
  }
})
```

```kotlin
// PjSipBroadcastReceiver.java - Event Emission
private void emit(String eventName, @Nullable Object data) {
    if (eventSink != null) {
        Map<String, Object> event = new HashMap<>();
        event.put("event", eventName);
        event.put("data", data);
        eventSink.success(event);  // Push to Flutter
    }
}
```

```dart
// FlutterSip2.dart - Flutter Subscription
static Stream<Map<String, dynamic>> get eventStream {
  _eventStream ??= _eventChannel
      .receiveBroadcastStream()
      .map((event) => Map<String, dynamic>.from(event));
  return _eventStream!;
}

// Usage
FlutterSip2.eventStream.listen((event) {
  switch (event['event']) {
    case 'pjSipRegistrationChanged':
      handleRegistrationChanged(event['data']);
      break;
    case 'pjSipCallReceived':
      handleCallReceived(event['data']);
      break;
  }
});
```

### Event Types

| Event Name | Data Structure | Trigger |
|------------|----------------|---------|
| `pjSipRegistrationChanged` | `{account_id, status, code, reason, expiration}` | Account registration status updated |
| `pjSipCallReceived` | `{call: Call, account: Account}` | Incoming call notification |
| `pjSipCallChanged` | `{call: Call}` | Call state changed |
| `pjSipCallTerminated` | `{call: Call}` | Call ended |
| `pjSipMessageReceived` | `{message: SipMessage}` | SIP message received |
| `pjSipConnectivityChanged` | `{available: bool}` | Network connectivity changed |

## Consequences

### Positive

1. **Real-Time Delivery**: Events pushed immediately to Flutter:
   - Latency < 100ms typical
   - No polling overhead
   - Reactive UI patterns supported

2. **Stream-Based API**: Flutter receives events as Stream:
   - Familiar API for Flutter developers
   - Supports multiple subscribers
   - Easy to filter/transform events
   - Integrates with RxDart, etc.

3. **Decoupled Architecture**: EventChannel decouples producer/consumer:
   - Service broadcasts without knowing subscribers
   - Multiple Flutter isolates can subscribe
   - Easy to add new event types

4. **Background Support**: Events delivered even when app backgrounded:
   - BroadcastReceiver wakes Flutter for events
   - Incoming calls trigger notifications
   - Registration renewals tracked

5. **Lazy Initialization**: EventChannel initialized once, used on-demand:
   - Singleton pattern for eventStream
   - No overhead if not subscribed
   - Clean resource management

### Negative

1. **Static Reference Required**: eventSink must be globally accessible:
   - Breaks dependency injection patterns
   - Harder to test in isolation
   - Potential memory leak if not cleared

2. **Event Ordering Not Guaranteed**: Rapid events may arrive out of order:
   - Flutter processes events sequentially
   - Network events may overtake call events
   - Application must handle ordering

3. **No Backpressure**: EventChannel doesn't support backpressure:
   - Fast event producers can overwhelm Flutter
   - No built-in throttling/debouncing
   - Application must manage event rate

4. **Error Handling Complexity**: EventChannel errors terminate stream:
   - Must re-subscribe on error
   - No automatic retry
   - Error details may be lost

### Trade-offs

**Rejected Alternative: MethodChannel Polling**

We considered polling for state changes:

```dart
// Rejected: Polling pattern
Timer.periodic(Duration(milliseconds: 500), (_) async {
  final state = await FlutterSip2.getState();
  if (state.changed) {
    // Handle changes
  }
});
```

**Why Rejected:**
- High latency (up to 500ms between polls)
- Wastes battery/CPU on polling
- Misses events between polls
- Doesn't work in background

**Rejected Alternative: Callback-Only Pattern**

We considered callbacks only (no EventChannel):

```kotlin
// Rejected: Callback-only
"registerAccount" -> {
  PjSipLibrary.register(account) { result ->
    result.success(...)  // Only notifies caller
  }
}
```

**Why Rejected:**
- Only notifies operation initiator
- Can't broadcast to multiple subscribers
- Doesn't support unsolicited events (incoming calls)

**Accepted Trade-off:** Static reference for real-time capability - Global eventSink breaks some patterns but enables push-based event delivery.

## Related Decisions

- **ADR-001**: Service-based architecture (events originate from service)
- **ADR-003**: JSON serialization for Intent extras (event data serialization)
- **ADR-004**: Callback ID registration pattern (distinguishes callbacks from events)

## References

- [Flutter EventChannel API](https://api.flutter.dev/flutter/services/EventChannel-class.html)
- [Platform Channels Documentation](https://docs.flutter.dev/development/platform-integration/platform-channels)
- [PjSipBroadcastReceiver.java](../android/src/main/java/org/tele/flutter_sip2/PjSipBroadcastReceiver.java)
- [FlutterSip2.dart](../lib/flutter_nmsip.dart) - eventStream implementation

---

*Generated by /legacy analysis | 2026-03-04*
