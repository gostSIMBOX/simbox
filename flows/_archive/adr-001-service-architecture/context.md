# ADR-001: Service-Based Architecture with Android Intents

> Enabling architectural decision: Background processing support for SIP operations

## Status

DRAFT

## Type

Enabling - This decision enables other architectural choices and capabilities.

## Context

The flutter_nmsip plugin needs to provide SIP (Session Initiation Protocol) communication capabilities to Flutter applications. SIP operations include:

- Account registration with SIP servers
- Making and receiving audio/video calls
- Call control operations (hold, transfer, mute, etc.)
- Real-time event streaming for call state changes

**Key Requirements:**
1. Operations must continue when app is in background (incoming calls)
2. Long-running operations (registration, calls) shouldn't block UI thread
3. Native PJSIP library runs on Android
4. Flutter layer needs real-time updates on operation status

**Constraints:**
- Android lifecycle management (activities can be destroyed)
- Background execution limitations on modern Android
- Need for reliable event delivery to Flutter layer

## Decision

We will use a **service-based architecture with Android Intents** for all SIP operations:

### Architecture Pattern

```
┌─────────────────┐
│   Flutter App   │
└────────┬────────┘
         │ MethodChannel
         ▼
┌─────────────────┐
│FlutterSip2Plugin│  ← Kotlin plugin
└────────┬────────┘
         │ Intent + callback_id
         ▼
┌─────────────────┐
│  PjSipService   │  ← Android Service (background)
│   (PJSIP)       │  ← Long-running SIP operations
└────────┬────────┘
         │ Broadcast Intent
         ▼
┌─────────────────┐
│PjSipBroadcast   │  ← Event distribution
│   Receiver      │  ← Callback resolution
└─────────────────┘
```

### Implementation Details

1. **All SIP operations route through PjSipService** via Android Intents
2. **Each operation includes a callback_id** for async response tracking
3. **Service broadcasts results** via BroadcastReceiver
4. **Plugin registers callbacks** in a HashMap keyed by callback_id
5. **Events broadcast separately** via EventChannel for real-time updates

### Code Pattern

```kotlin
// FlutterSip2Plugin.kt
"createAccount" -> {
    val configuration = call.arguments as? Map<String, Any>
    val callbackId = broadcastReceiver.register(result)  // Register callback
    val intent = PjActions.createAccountCreateIntent(callbackId, configuration, context)
    context.startService(intent)  // Start service with Intent
}
```

```java
// PjActions.java
public static Intent createAccountCreateIntent(int callbackId, Map<String, Object> configuration, Context context) {
    Intent intent = new Intent(context, org.telon.sip2.PjSipService.class);
    intent.setAction(PjActions.ACTION_CREATE_ACCOUNT);
    intent.putExtra("callback_id", callbackId);
    formatIntent(intent, configuration);
    return intent;
}
```

## Consequences

### Positive

1. **Background Processing**: Service continues running when app is backgrounded, enabling:
   - Incoming call reception in background
   - Call continuity during app lifecycle changes
   - Registration renewal without user interaction

2. **Lifecycle Independence**: Service decoupled from Activity/FlutterEngine:
   - Survives activity recreation
   - Clean separation of concerns
   - Easier testing of native layer

3. **Async Operation Support**: Intent-based communication naturally asynchronous:
   - No blocking on Flutter side
   - Callback pattern handles long operations
   - Sequential callback IDs prevent race conditions

4. **Event Broadcasting**: BroadcastReceiver pattern enables:
   - Multiple event types from single service
   - Decoupled event producers/consumers
   - Easy to add new event types

### Negative

1. **Complexity**: More components than direct method calls:
   - Plugin → Service → BroadcastReceiver → Plugin
   - Callback registration overhead
   - Intent serialization/deserialization

2. **Performance Overhead**: Intent creation and broadcasting adds latency:
   - ~10-50ms per operation vs direct calls
   - JSON serialization for Intent extras
   - BroadcastReceiver dispatch time

3. **Debugging Difficulty**: Indirect flow harder to trace:
   - Callback ID tracking required
   - Event flow spans multiple components
   - Service lifecycle adds complexity

4. **Memory Management**: Callback HashMap must be managed:
   - Risk of memory leaks if not cleaned up
   - Callbacks must be removed after execution
   - Edge cases (app termination) need handling

### Trade-offs

**Rejected Alternative: Direct Method Calls**

We considered direct method calls from plugin to PJSIP library:

```kotlin
// Rejected: Direct calls
"createAccount" -> {
    val account = PjSipLibrary.createAccount(configuration)
    result.success(account.toMap())
}
```

**Why Rejected:**
- No background execution support
- Blocks Flutter thread during operation
- Tied to FlutterEngine lifecycle
- Cannot receive events when app backgrounded

**Accepted Trade-off:** Complexity for capability - Service architecture adds complexity but enables critical background processing feature.

## Related Decisions

- **ADR-002**: EventChannel for real-time events (complements service architecture)
- **ADR-003**: JSON serialization for Intent extras (required for data transfer)
- **ADR-004**: Callback ID registration pattern (tracks async operations)

## References

- [Android Services Documentation](https://developer.android.com/guide/components/services)
- [Android BroadcastReceivers](https://developer.android.com/reference/android/content/BroadcastReceiver)
- [PjSipService Implementation](../android/src/main/java/org/telon/sip2/PjSipService.java) (external library)
- [FlutterSip2Plugin.kt](../android/src/main/kotlin/org/tele/flutter_sip2/FlutterSip2Plugin.kt)
- [PjActions.java](../android/src/main/java/org/tele/flutter_sip2/PjActions.java)

---

*Generated by /legacy analysis | 2026-03-04*
