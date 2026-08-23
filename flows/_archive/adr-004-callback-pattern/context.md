# ADR-004: Sequential Callback ID Registration Pattern

> Enabling architectural decision: Async operation tracking without race conditions

## Status

DRAFT

## Type

Enabling - This decision enables reliable async operation tracking across process boundaries.

## Context

The service-based architecture requires tracking multiple concurrent async operations:

- Multiple accounts being created simultaneously
- Registration requests while calls are active
- Call operations (hold, mute, transfer) in progress
- Configuration changes during active sessions

**Requirements:**
1. Each operation must be matched to its callback
2. Race conditions must be prevented
3. Callbacks must be cleaned up after execution
4. Support concurrent operations (parallel calls)
5. Handle out-of-order completion

**Constraints:**
- Android Intents are asynchronous
- Service processes operations in arbitrary order
- BroadcastReceiver handles responses
- Callbacks stored in HashMap

## Decision

We will use **sequential callback ID registration** for async operation tracking:

### Architecture Pattern

```
┌─────────────────┐
│FlutterSip2Plugin│
└────────┬────────┘
         │ register(callback)
         ▼
┌─────────────────┐
│PjSipBroadcast   │
│   Receiver      │  ← seq: Int (incrementing)
│                 │  ← callbacks: HashMap<Int, Result>
└────────┬────────┘
         │ Returns callback_id
         ▼
┌─────────────────┐
│  Intent + ID    │  ← callback_id extra
└────────┬────────┘
         ▼
┌─────────────────┐
│  PjSipService   │  ← Processes operation
└────────┬────────┘
         │ Broadcast with callback_id
         ▼
┌─────────────────┐
│PjSipBroadcast   │  ← Matches ID to callback
│   Receiver      │  ← Removes from HashMap
└─────────────────┘
```

### Implementation Details

1. **Sequential counter** (`seq`) incremented for each registration
2. **HashMap stores callbacks** keyed by callback_id
3. **Registration is atomic**: increment, store, return ID
4. **Callback removal**: remove after execution (success or error)
5. **ID validation**: check if ID exists before executing callback

### Code Pattern

```kotlin
// PjSipBroadcastReceiver.java
public class PjSipBroadcastReceiver extends BroadcastReceiver {
    private int seq = 0;  // Sequential counter
    
    // Callback storage
    private HashMap<Integer, io.flutter.plugin.common.MethodChannel.Result> callbacks = new HashMap<>();
    
    // Register callback and get ID
    public int register(io.flutter.plugin.common.MethodChannel.Result callback) {
        int id = ++seq;  // Increment first, then use
        callbacks.put(id, callback);
        return id;
    }
    
    // Execute callback by ID
    private void onCallback(Intent intent) {
        io.flutter.plugin.common.MethodChannel.Result callback = null;
        
        if (intent.hasExtra("callback_id")) {
            int id = intent.getIntExtra("callback_id", -1);
            if (callbacks.containsKey(id)) {
                callback = callbacks.remove(id);  // Remove after retrieval
            } else {
                Log.w(TAG, "Callback with \"" + id + "\" identifier not found");
            }
        }
        
        if (callback == null) {
            return;  // No callback to execute
        }
        
        // Execute callback
        if (intent.hasExtra("exception")) {
            callback.error("SIP_ERROR", intent.getStringExtra("exception"), null);
        } else if (intent.hasExtra("data")) {
            Object params = ArgumentUtils.fromJson(intent.getStringExtra("data"));
            callback.success(params);
        } else {
            callback.success(true);
        }
    }
}
```

```kotlin
// FlutterSip2Plugin.kt - Usage
"createAccount" -> {
    val configuration = call.arguments as? Map<String, Any>
    val callbackId = broadcastReceiver.register(result)  // Register and get ID
    val intent = PjActions.createAccountCreateIntent(callbackId, configuration, context)
    context.startService(intent)  // ID travels with Intent
    // result will be called later via callback
}
```

## Consequences

### Positive

1. **Race Condition Prevention**: Sequential IDs guarantee uniqueness:
   - No ID collisions possible
   - Thread-safe increment operation
   - Each operation has unique identifier

2. **Concurrent Operations**: Multiple operations can be in-flight:
   - HashMap supports unlimited pending operations
   - Operations complete in any order
   - Each callback matched correctly

3. **Automatic Cleanup**: Callbacks removed after execution:
   - No memory leaks from stale callbacks
   - HashMap size reflects pending operations
   - Failed operations still cleaned up

4. **Simple Implementation**: Minimal complexity:
   - Single counter variable
   - Standard HashMap operations
   - Easy to understand and debug

5. **Error Handling**: Missing callbacks detected:
   - Log warning if ID not found
   - No crash on stale callbacks
   - Graceful degradation

### Negative

1. **Integer Overflow**: Sequential counter will eventually overflow:
   - int max = 2,147,483,647
   - At 1000 ops/sec: overflow in ~25 days
   - Wraparound could cause ID collision

2. **Memory Growth**: HashMap grows with concurrent operations:
   - No automatic size limiting
   - Many pending operations = more memory
   - Must trust service to complete operations

3. **No Timeout**: Callbacks never timeout automatically:
   - Stale callbacks if service doesn't respond
   - Memory leak if service crashes
   - Must rely on service reliability

4. **Single Point of Failure**: BroadcastReceiver is central:
   - If receiver fails, all callbacks lost
   - HashMap corruption affects all operations
   - No redundancy

### Trade-offs

**Rejected Alternative: UUID for Callback IDs**

We considered using UUIDs instead of sequential IDs:

```kotlin
// Rejected: UUID-based
val callbackId = UUID.randomUUID().toString()
callbacks[callbackId] = callback
```

**Why Rejected:**
- More memory (String vs Int)
- Slower generation (random vs increment)
- Harder to debug (non-sequential)
- No practical benefit for this use case

**Rejected Alternative: Operation-Specific Callbacks**

We considered embedding callbacks in operation objects:

```kotlin
// Rejected: Per-operation callbacks
data class Operation(
    val type: String,
    val data: Map<String, Any>,
    val callback: MethodChannel.Result  // Embedded
)
```

**Why Rejected:**
- Doesn't survive process boundaries
- Can't serialize callback for Intent
- Tightly couples operation to callback

**Rejected Alternative: Correlation ID in Data**

We considered using data fields for correlation:

```kotlin
// Rejected: Data-based correlation
val correlationId = data["transaction_id"]
```

**Why Rejected:**
- Requires application to provide ID
- Not all operations have transaction IDs
- Mixes correlation with business data

**Accepted Trade-off:** Integer overflow risk for simplicity - Overflow would take weeks of continuous operation and is mitigated by app restarts.

## Related Decisions

- **ADR-001**: Service-based architecture (requires callback tracking)
- **ADR-002**: EventChannel for events (distinguishes events from callbacks)
- **ADR-003**: JSON serialization (data separate from callback_id)

## References

- [HashMap Documentation](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/-hash-map/)
- [PjSipBroadcastReceiver.java](../android/src/main/java/org/tele/flutter_sip2/PjSipBroadcastReceiver.java)
- [FlutterSip2Plugin.kt](../android/src/main/kotlin/org/tele/flutter_sip2/FlutterSip2Plugin.kt)

---

*Generated by /legacy analysis | 2026-03-04*
