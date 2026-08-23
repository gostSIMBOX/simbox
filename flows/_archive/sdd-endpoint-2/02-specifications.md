# Specifications: Platform Channel Endpoint

**Status**: DRAFT  
**Type**: SDD (Spec-Driven Development)  
**Module**: endpoint  
**Generated**: 2026-03-04 by /legacy

---

## Specification Overview

This document specifies the implementation details of the platform channel endpoint based on analysis of existing code in `lib/src/endpoint.dart` and `android/src/main/kotlin/org/telon/tele/flutter_tele/FlutterTelePlugin.kt`.

---

## Architecture

### Platform Channel Pattern

```
┌─────────────────────────────────────────────────────────────┐
│  Flutter (Dart)                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ TeleEndpoint                                           │  │
│  │  - MethodChannel: 'flutter_tele'                       │  │
│  │  - EventChannel: 'flutter_tele_events'                 │  │
│  │  - StreamControllers: Map<type, StreamController>      │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│              MethodChannel │ EventChannel                    │
│                            │                                 │
│  Android (Kotlin)          │                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ FlutterTelePlugin                                      │  │
│  │  - MethodCallHandler                                   │  │
│  │  - EventChannel.StreamHandler                          │  │
│  │  - eventSink: EventSink?                               │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                  Intent    │                                 │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ TeleService                                            │  │
│  │  - InCallService                                       │  │
│  │  - Call management                                     │  │
│  │  - Event broadcasting                                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Communication Flows

**MethodChannel (Flutter → Android)**:
```
1. Flutter: endpoint.makeCall(1, "123", null, null)
2. MethodChannel: invokeMethod("makeCall", args)
3. Android: onMethodCall(call, result)
4. Plugin: Intent intent = Intent(context, TeleService::class.java)
5. Plugin: intent.action = "MAKE_CALL"
6. Plugin: context.startService(intent)
7. Plugin: result.success(callData)
8. Flutter: Future completes with TeleCall
```

**EventChannel (Android → Flutter)**:
```
1. Android: sendEvent("call_changed", callData)
2. Plugin: eventSink?.success(mapOf("type" to "call_changed", "data" to callData))
3. EventChannel: Broadcasts to all listeners
4. Flutter: _handleEvent(event)
5. Flutter: _eventControllers["call_changed"]!.add(callData)
6. Flutter: All listeners receive event via Stream
```

---

## Dart Implementation Specification

### Channel Constants

```dart
static const MethodChannel _channel = MethodChannel('flutter_tele')
static const EventChannel _eventChannel = EventChannel('flutter_tele_events')
```

### Event Handling Architecture

```dart
// State
StreamSubscription? _eventSubscription
final Map<String, StreamController<dynamic>> _eventControllers = {}

// Setup
void _setupEventChannel() {
  _eventSubscription = _eventChannel.receiveBroadcastStream().listen((event) {
    _handleEvent(event)
  })
}

// Event routing
void _handleEvent(dynamic event) {
  if (event is Map) {
    final eventStringMap = event.map((key, value) => MapEntry(key.toString(), value))
    final eventType = eventStringMap['type'] as String?
    final eventData = eventStringMap['data']
    
    if (eventType != null && _eventControllers.containsKey(eventType)) {
      _eventControllers[eventType]!.add(eventData)
    }
  }
}

// Stream creation
Stream<dynamic> on(String eventType) {
  if (!_eventControllers.containsKey(eventType)) {
    _eventControllers[eventType] = StreamController<dynamic>.broadcast()
  }
  return _eventControllers[eventType]!.stream
}

// Cleanup
void dispose() {
  _eventSubscription?.cancel()
  for (final controller in _eventControllers.values) {
    controller.close()
  }
  _eventControllers.clear()
}
```

### Method Specifications

#### requestPermissions()

```dart
Future<bool> requestPermissions() async {
  try {
    final result = await _channel.invokeMethod('requestPermissions')
    return result == true
  } on PlatformException catch (e) {
    return false
  } catch (e) {
    return false
  }
}
```

**Behavior**: 
- Returns `false` (stub - needs Activity for real permission request)
- Returns `false` on any error

#### hasPermissions()

```dart
Future<bool> hasPermissions() async {
  try {
    final result = await _channel.invokeMethod('hasPermissions')
    return result == true
  } on PlatformException catch (e) {
    return false
  } catch (e) {
    return false
  }
}
```

**Behavior**: 
- Returns `true` if all 5 permissions granted
- Returns `false` if any permission missing

#### start(configuration)

```dart
Future<Map<String, dynamic>> start(Map<String, dynamic> configuration) async {
  try {
    // 1. Check permissions
    final hasPerms = await hasPermissions()
    if (!hasPerms) {
      final granted = await requestPermissions()
      if (!granted) {
        throw Exception('Phone permissions are required but not granted')
      }
    }
    
    // 2. Invoke method
    final result = await _channel.invokeMethod('start', configuration)
    
    // 3. Parse result
    if (result is Map) {
      final resultStringMap = result.map((key, value) => MapEntry(key.toString(), value))
      
      // Parse accounts
      final accounts = <Map<String, dynamic>>[]
      if (resultStringMap.containsKey('accounts')) {
        final accountsData = resultStringMap['accounts'] as List<dynamic>
        for (final accountData in accountsData) {
          if (accountData is Map) {
            accounts.add(accountData.map((k, v) => MapEntry(k.toString(), v)))
          }
        }
      }
      
      // Parse calls
      final calls = <TeleCall>[]
      if (resultStringMap.containsKey('calls')) {
        final callsData = resultStringMap['calls'] as List<dynamic>
        for (final callData in callsData) {
          if (callData is Map) {
            calls.add(TeleCall.fromMap(callData.map((k, v) => MapEntry(k.toString(), v))))
          }
        }
      }
      
      // Build response
      final extra = <String, dynamic>{}
      for (final key in resultStringMap.keys) {
        if (key != 'accounts' && key != 'calls') {
          extra[key] = resultStringMap[key]
        }
      }
      
      return {
        'accounts': accounts,
        'calls': calls,
        ...extra,
      }
    }
    
    throw Exception('Invalid response from native code')
  } on PlatformException catch (e) {
    throw Exception('Failed to start telephony service: ${e.message}')
  } catch (e) {
    throw Exception('Error starting telephony service: $e')
  }
}
```

**Return Format**:
```dart
{
  'accounts': [
    { /* account data */ },
    ...
  ],
  'calls': [
    TeleCall(...),
    ...
  ],
  'status': 'started',
  // ... other fields
}
```

#### makeCall(sim, destination, callSettings, msgData)

```dart
Future<TeleCall> makeCall(int sim, String destination, 
                          Map<String, dynamic>? callSettings, 
                          Map<String, dynamic>? msgData) async {
  try {
    final result = await _channel.invokeMethod('makeCall', {
      'sim': sim,
      'destination': destination,
      'callSettings': callSettings,
      'msgData': msgData,
    })
    
    if (result is Map) {
      final resultStringMap = result.map((key, value) => MapEntry(key.toString(), value))
      return TeleCall.fromMap(resultStringMap)
    } else if (result == true) {
      // Fallback: native returned true but we need call object
      return TeleCall(id: 1)
    }
    
    throw Exception('Invalid response from native code')
  } on PlatformException catch (e) {
    throw Exception('Failed to make call: ${e.message}')
  } catch (e) {
    throw Exception('Error making call: $e')
  }
}
```

**Call Control Methods** (answerCall, hangupCall, declineCall, holdCall, unholdCall, muteCall, unMuteCall, useSpeaker, useEarpiece):

```dart
Future<dynamic> answerCall(TeleCall call) async {
  try {
    final result = await _channel.invokeMethod('answerCall', call.getId())
    return result
  } on PlatformException catch (e) {
    throw Exception('Failed to answer call: ${e.message}')
  }
}
```

Pattern:
- All take `TeleCall call` parameter
- All extract call ID via `call.getId()`
- All return `Future<dynamic>` (typically `true` on success)

#### sendEnvelope(call)

```dart
Future<String> sendEnvelope(TeleCall call) async {
  try {
    final result = await _channel.invokeMethod('sendEnvelope', call.getId())
    return result.toString()
  } on PlatformException catch (e) {
    throw Exception('Failed to send envelope: ${e.message}')
  }
}
```

**Returns**: `"TESTTEST"` (stub implementation)

---

## Kotlin Implementation Specification

### Plugin Structure

```kotlin
class FlutterTelePlugin : FlutterPlugin, MethodCallHandler {
  private lateinit var channel: MethodChannel
  private lateinit var eventChannel: EventChannel
  private lateinit var context: Context
  private var eventSink: EventChannel.EventSink? = null
  
  companion object {
    private var instance: FlutterTelePlugin? = null
    
    fun getInstance(): FlutterTelePlugin? = instance
  }
  
  override fun onAttachedToEngine(binding: FlutterPlugin.FlutterPluginBinding) {
    instance = this
    context = binding.applicationContext
    
    channel = MethodChannel(binding.binaryMessenger, "flutter_tele")
    channel.setMethodCallHandler(this)
    
    eventChannel = EventChannel(binding.binaryMessenger, "flutter_tele_events")
    eventChannel.setStreamHandler(object : EventChannel.StreamHandler {
      override fun onListen(arguments: Any?, events: EventChannel.EventSink?) {
        eventSink = events
      }
      
      override fun onCancel(arguments: Any?) {
        eventSink = null
      }
    })
  }
  
  override fun onMethodCall(call: MethodCall, result: Result) {
    when (call.method) {
      "requestPermissions" -> requestPermissions(result)
      "hasPermissions" -> hasPermissions(result)
      "start" -> startTelephonyService(call.arguments as? Map, result)
      "makeCall" -> handleMakeCall(call, result)
      "answerCall" -> handleIntCall("ANSWER_CALL", call, result)
      "hangupCall" -> handleIntCall("HANGUP_CALL", call, result)
      // ... other methods
      else -> result.notImplemented()
    }
  }
}
```

### Method Handler Specifications

#### requestPermissions(result)

```kotlin
private fun requestPermissions(result: Result) {
  try {
    val permissions = arrayOf(
      Manifest.permission.READ_PHONE_STATE,
      Manifest.permission.CALL_PHONE,
      Manifest.permission.READ_CALL_LOG,
      Manifest.permission.ANSWER_PHONE_CALLS,
      Manifest.permission.MANAGE_OWN_CALLS
    )
    
    val missingPermissions = permissions.filter {
      ContextCompat.checkSelfPermission(context, it) != PackageManager.PERMISSION_GRANTED
    }
    
    if (missingPermissions.isEmpty()) {
      result.success(true)
    } else {
      // Note: Cannot request permissions without Activity
      result.success(false)
    }
  } catch (e: Exception) {
    result.error("PERMISSION_ERROR", "Failed to request permissions", e.message)
  }
}
```

**Returns**: `false` (cannot request without Activity)

#### hasPermissions(result)

```kotlin
private fun hasPermissions(result: Result) {
  try {
    val permissions = arrayOf(
      Manifest.permission.READ_PHONE_STATE,
      Manifest.permission.CALL_PHONE,
      Manifest.permission.READ_CALL_LOG,
      Manifest.permission.ANSWER_PHONE_CALLS,
      Manifest.permission.MANAGE_OWN_CALLS
    )
    
    val allGranted = permissions.all {
      ContextCompat.checkSelfPermission(context, it) == PackageManager.PERMISSION_GRANTED
    }
    
    result.success(allGranted)
  } catch (e: Exception) {
    result.error("PERMISSION_ERROR", "Failed to check permissions", e.message)
  }
}
```

#### startTelephonyService(configuration, result)

```kotlin
private fun startTelephonyService(configuration: Map<String, Any>?, result: Result) {
  try {
    val intent = Intent(context, TeleService::class.java).apply {
      action = "START_TELEPHONY_SERVICE"
      putExtra("configuration", configuration?.toString())
    }
    context.startService(intent)
    
    val initialState = mapOf(
      "accounts" to emptyList<Map<String, Any>>(),
      "calls" to emptyList<Map<String, Any>>(),
      "status" to "started"
    )
    result.success(initialState)
  } catch (e: Exception) {
    result.error("START_ERROR", "Failed to start telephony service", e.message)
  }
}
```

#### makeCall(sim, destination, callSettings, msgData, result)

```kotlin
private fun makeCall(sim: Int, destination: String, 
                     callSettings: Map<String, Any>?, 
                     msgData: Map<String, Any>?, 
                     result: Result) {
  try {
    val intent = Intent(context, TeleService::class.java).apply {
      action = "MAKE_CALL"
      putExtra("sim", sim)
      putExtra("destination", destination)
      putExtra("callSettings", callSettings?.toString())
      putExtra("msgData", msgData?.toString())
    }
    context.startService(intent)
    
    // Return call object immediately
    val callData = mapOf(
      "id" to 1,
      "callId" to "call_1",
      "accountId" to 1,
      "localContact" to "",
      "localUri" to "",
      "remoteContact" to destination,
      "remoteUri" to "tel:$destination",
      "state" to "INITIATING",
      "stateText" to "Initiating call",
      "held" to false,
      "muted" to false,
      "speaker" to false,
      "connectDuration" to 0,
      "totalDuration" to 0,
      "remoteOfferer" to false,
      "remoteAudioCount" to 0,
      "remoteVideoCount" to 0,
      "audioCount" to 0,
      "videoCount" to 0,
      "lastStatusCode" to 0,
      "lastReason" to "",
      "media" to emptyMap<String, Any>(),
      "provisionalMedia" to emptyMap<String, Any>(),
      "creationTime" to "",
      "connectTime" to "",
      "details" to emptyMap<String, Any>(),
      "hashCode" to "call_1_hash",
      "extras" to emptyMap<String, Any>(),
      "connectTimeMillis" to 0,
      "creationTimeMillis" to 0,
      "disconnectCause" to "",
      "direction" to "DIRECTION_OUTGOING",
      "simSlot" to sim,
      "simSlot1" to sim,
      "simSlot2" to sim,
      "remoteNumber" to destination,
      "remoteName" to destination
    )
    
    result.success(callData)
  } catch (e: Exception) {
    result.error("MAKE_CALL_ERROR", "Failed to make call", e.message)
  }
}
```

**Note**: Returns full call object with 40+ fields to match Dart TeleCall expectations

#### Call Control Methods

```kotlin
private fun answerCall(callId: Int, result: Result) {
  try {
    val intent = Intent(context, TeleService::class.java).apply {
      action = "ANSWER_CALL"
      putExtra("callId", callId)
    }
    context.startService(intent)
    result.success(true)
  } catch (e: Exception) {
    result.error("ANSWER_CALL_ERROR", "Failed to answer call", e.message)
  }
}
```

Pattern for all call control methods:
- Extract callId from arguments
- Create Intent with action string
- Add callId as extra
- Start service
- Return `true`

#### sendEnvelope(callId, result)

```kotlin
private fun sendEnvelope(callId: Int, result: Result) {
  try {
    // This would typically send an envelope command to the SIM
    result.success("TESTTEST")
  } catch (e: Exception) {
    result.error("SEND_ENVELOPE_ERROR", "Failed to send envelope", e.message)
  }
}
```

**Stub**: Returns hardcoded "TESTTEST"

---

## Event Broadcasting Specification

### Event Sending (Kotlin)

```kotlin
fun sendEvent(eventType: String, eventData: Map<String, Any?>) {
  val event = mapOf(
    "type" to eventType,
    "data" to eventData
  )
  Log.d(TAG, "Sending event to Flutter: $event")
  eventSink?.success(event)
}
```

### Event Receiving (Dart)

```dart
void _setupEventChannel() {
  _eventSubscription = _eventChannel.receiveBroadcastStream().listen((event) {
    _handleEvent(event)
  })
}

void _handleEvent(dynamic event) {
  if (event is Map) {
    final eventStringMap = event.map((key, value) => MapEntry(key.toString(), value))
    final eventType = eventStringMap['type'] as String?
    final eventData = eventStringMap['data']
    
    if (eventType != null && _eventControllers.containsKey(eventType)) {
      _eventControllers[eventType]!.add(eventData)
    }
  }
}
```

### Event Type Routing

```
EventChannel broadcast
        │
        ▼
  _handleEvent(event)
        │
        ├── type: "service_started" → _eventControllers["service_started"]
        ├── type: "call_received"   → _eventControllers["call_received"]
        ├── type: "call_changed"    → _eventControllers["call_changed"]
        ├── type: "call_terminated" → _eventControllers["call_terminated"]
        └── type: "call_error"      → _eventControllers["call_error"]
                      │
                      ▼
              StreamController.broadcast()
                      │
                      ▼
              All listeners receive event
```

---

## Intent Action Specification

| Action | Source | Destination | Extras |
|--------|--------|-------------|--------|
| START_TELEPHONY_SERVICE | Plugin | TeleService | configuration: String |
| MAKE_CALL | Plugin | TeleService | sim: Int, destination: String, callSettings: String, msgData: String |
| ANSWER_CALL | Plugin | TeleService | callId: Int |
| HANGUP_CALL | Plugin | TeleService | callId: Int |
| DECLINE_CALL | Plugin | TeleService | callId: Int |
| HOLD_CALL | Plugin | TeleService | callId: Int |
| UNHOLD_CALL | Plugin | TeleService | callId: Int |
| MUTE_CALL | Plugin | TeleService | callId: Int |
| UNMUTE_CALL | Plugin | TeleService | callId: Int |
| USE_SPEAKER | Plugin | TeleService | callId: Int |
| USE_EARPIECE | Plugin | TeleService | callId: Int |

---

## Known Issues and Limitations

### Issue 1: Permission Request Stub

**Problem**: `requestPermissions()` returns `false` because it cannot request permissions without an Activity.

**Impact**: 
- App cannot request runtime permissions
- Users must manually grant permissions in system settings

**Recommended Fix**:
```kotlin
// Requires Activity reference
private fun requestPermissions(result: Result) {
  val activity = getActivity() // Need FlutterActivity reference
  ActivityCompat.requestPermissions(
    activity,
    permissions,
    PERMISSION_REQUEST_CODE
  )
  // Result handled in onRequestPermissionsResult
}
```

### Issue 2: sendEnvelope() Stub

**Problem**: Returns hardcoded "TESTTEST" instead of sending SIM envelope command.

**Impact**: SIM envelope commands not functional.

**Recommended Fix**: Implement using TelephonyManager or remove API if not needed.

### Issue 3: Service-Per-Call Pattern

**Problem**: Every method calls `startService()`, potentially causing redundant service starts.

**Impact**: Minor performance overhead, service may be started multiple times.

**Analysis**: Android handles redundant `startService()` calls efficiently (service only created once), but `onStartCommand()` is called each time.

**Recommended Fix**: Consider binding to service instead of starting for each call.

### Issue 4: Debug Logging

**Problem**: Extensive `print()` statements in production code.

**Impact**: Performance overhead, log pollution.

**Recommended Fix**: Replace with `Logger` or `debugPrint` that can be disabled in production.

---

## Testing Recommendations

### Unit Tests (Dart)

1. **Event Routing Tests**
   - Test event type extraction
   - Test StreamController creation
   - Test broadcast stream delivery

2. **Method Call Tests**
   - Mock MethodChannel
   - Test argument serialization
   - Test error handling

3. **Dispose Tests**
   - Verify subscription cancellation
   - Verify StreamController closure
   - Verify no memory leaks

### Integration Tests

1. **MethodChannel Tests**
   - Test all 15 methods
   - Verify Intent creation
   - Verify result parsing

2. **EventChannel Tests**
   - Test event streaming
   - Test multiple listeners
   - Test event type routing

---

*Generated by /legacy reverse engineering*
