# Specifications: SIP Call Management

> Technical specification for call operations, state machine, and media control.

## Architecture Overview

```
┌─────────────────┐
│   Flutter App   │
└────────┬────────┘
         │ makeCall, answerCall, etc.
         │ holdCall, muteCall, xferCall...
         ▼
┌─────────────────┐
│  FlutterSip2    │  ← 20+ call methods
│   (Facade)      │
└────────┬────────┘
         │ Platform Messages
         ▼
┌─────────────────┐
│FlutterSip2Plugin│  ← Method handlers
│   (Android)     │
└────────┬────────┘
         │ Intents + callback_id
         ▼
┌─────────────────┐
│  PjSipService   │  ← PJSIP call API
│   (Native)      │
└────────┬────────┘
         │ Broadcast Intents
         ▼
┌─────────────────┐
│PjSipBroadcast   │  ← call_changed
│   Receiver      │  ← call_terminated
└─────────────────┘
```

## Call Operations API

### Method Summary

| Method | Parameters | Description |
|--------|------------|-------------|
| `makeCall` | account, destination, callSettings?, msgData? | Initiate outbound call |
| `answerCall` | call | Answer incoming call |
| `hangupCall` | call | Terminate call |
| `declineCall` | call | Reject incoming call |
| `holdCall` | call | Place on hold |
| `unholdCall` | call | Resume from hold |
| `muteCall` | call | Mute microphone |
| `unmuteCall` | call | Unmute microphone |
| `useSpeaker` | call | Route to speaker |
| `useEarpiece` | call | Route to earpiece |
| `dtmfCall` | call, digits | Send DTMF tones |
| `xferCall` | call, destination | Blind transfer |
| `redirectCall` | call, destination | Redirect before answer |

### Implementation (Dart)

**File**: `lib/flutter_nmsip.dart`

```dart
// Make call
static Future<Call> makeCall(
  Account account,
  String destination, {
  Map<String, dynamic>? callSettings,
  Map<String, dynamic>? msgData,
}) async {
  try {
    final result = await _channel.invokeMethod('makeCall', {
      'accountId': account.id,
      'destination': destination,
      'callSettings': callSettings,
      'msgData': msgData,
    });
    return Call.fromMap(result);
  } on PlatformException catch (e) {
    throw FlutterSip2Exception(e.code, e.message);
  }
}

// Answer call
static Future<void> answerCall(Call call) async {
  try {
    await _channel.invokeMethod('answerCall', call.id);
  } on PlatformException catch (e) {
    throw FlutterSip2Exception(e.code, e.message);
  }
}

// Hold call
static Future<void> holdCall(Call call) async {
  try {
    await _channel.invokeMethod('holdCall', call.id);
  } on PlatformException catch (e) {
    throw FlutterSip2Exception(e.code, e.message);
  }
}

// Mute call
static Future<void> muteCall(Call call) async {
  try {
    await _channel.invokeMethod('muteCall', call.id);
  } on PlatformException catch (e) {
    throw FlutterSip2Exception(e.code, e.message);
  }
}

// DTMF
static Future<void> dtmfCall(Call call, String digits) async {
  try {
    await _channel.invokeMethod('dtmfCall', {
      'callId': call.id,
      'digits': digits,
    });
  } on PlatformException catch (e) {
    throw FlutterSip2Exception(e.code, e.message);
  }
}

// Transfer
static Future<void> xferCall(Call call, String destination) async {
  try {
    await _channel.invokeMethod('xferCall', {
      'callId': call.id,
      'destination': destination,
    });
  } on PlatformException catch (e) {
    throw FlutterSip2Exception(e.code, e.message);
  }
}
```

## Call Model (Dart)

**File**: `lib/src/call.dart`

### Properties

```dart
class Call {
  final int id;                    // Unique call ID
  final int callId;                // Dialog Call-ID
  final int accountId;             // Parent account ID
  final String? localContact;
  final String? localUri;
  final String? remoteContact;
  final String? remoteUri;
  final String state;              // PJSIP invite state
  final String stateText;          // Human-readable
  final bool held;                 // On hold?
  final bool muted;                // Muted?
  final bool speaker;              // Speaker active?
  final int connectDuration;       // Connected time (s)
  final int totalDuration;         // Total time (s)
  final bool remoteOfferer;        // Remote offered call?
  final int remoteAudioCount;      // Remote audio streams
  final int remoteVideoCount;      // Remote video streams
  final int audioCount;            // Local audio streams
  final int videoCount;            // Local video streams
  final int? lastStatusCode;       // Last SIP status
  final String? lastReason;        // Termination reason
  final Map<String, dynamic>? media;         // Media info
  final Map<String, dynamic>? provisionalMedia;
  
  // Parsed information
  final String? remoteNumber;      // Extracted number
  final String? remoteName;        // Extracted name
  final String? localNumber;
  final String? localName;
  
  // Internal tracking
  final int _constructionTime;     // Creation timestamp
}
```

### Duration Calculation

```dart
/// Get up-to-date call duration in seconds
int getTotalDuration() {
  final time = DateTime.now().millisecondsSinceEpoch ~/ 1000;
  final offset = time - _constructionTime;
  return totalDuration + offset;
}

/// Get connected duration
int getConnectDuration() {
  if (connectDuration < 0 || state == "PJSIP_INV_STATE_DISCONNECTED") {
    return connectDuration;
  }
  final time = DateTime.now().millisecondsSinceEpoch ~/ 1000;
  final offset = time - _constructionTime;
  return connectDuration + offset;
}

/// Format as "MM:SS"
String getFormattedTotalDuration() => _formatTime(getTotalDuration());
String getFormattedConnectDuration() => _formatTime(getConnectDuration());

String _formatTime(int seconds) {
  if (seconds < 0) return "00:00";
  final minutes = seconds ~/ 60;
  final remainingSeconds = seconds % 60;
  return "${minutes.toString().padLeft(2, '0')}:${remainingSeconds.toString().padLeft(2, '0')}";
}
```

### URI Parsing

```dart
/// Parse remote number from URI
static String? _parseRemoteNumber(String? remoteUri) {
  if (remoteUri == null) return null;

  // "Name" <sip:number@domain>
  final match1 = RegExp(r'"([^"]+)" <sip:([^@]+)@').firstMatch(remoteUri);
  if (match1 != null) return match1.group(2);

  // sip:number@domain
  final match2 = RegExp(r'sip:([^@]+)@').firstMatch(remoteUri);
  if (match2 != null) return match2.group(1);

  return null;
}

/// Parse remote name from URI
static String? _parseRemoteName(String? remoteUri) {
  if (remoteUri == null) return null;
  final match = RegExp(r'"([^"]+)" <sip:([^@]+)@').firstMatch(remoteUri);
  return match?.group(1);
}

/// Parse local number (handles tel: URIs)
static String? _parseLocalNumber(String? localUri) {
  if (localUri == null) return null;

  // Try tel:number format
  final match3 = RegExp(r'tel:([^@]+)').firstMatch(localUri);
  if (match3 != null) return Uri.decodeComponent(match3.group(1)!);

  // ... (same as remote)
  return null;
}
```

### Call State Machine

```dart
// PJSIP Invite States
class CallState {
  static const String NULL = "PJSIP_INV_STATE_NULL";
  static const String CALLING = "PJSIP_INV_STATE_CALLING";
  static const String INCOMING = "PJSIP_INV_STATE_INCOMING";
  static const String EARLY = "PJSIP_INV_STATE_EARLY";
  static const String CONNECTING = "PJSIP_INV_STATE_CONNECTING";
  static const String CONFIRMED = "PJSIP_INV_STATE_CONFIRMED";
  static const String DISCONNECTED = "PJSIP_INV_STATE_DISCONNECTED";
}
```

| State | Description |
|-------|-------------|
| NULL | Initial state before call initiation |
| CALLING | Outgoing call initiated |
| INCOMING | Incoming call received |
| EARLY | Early media (ringing tone) |
| CONNECTING | Connection in progress |
| CONFIRMED | Call connected (active) |
| DISCONNECTED | Call terminated |

## CallSettingsDTO (Kotlin)

**File**: `android/src/main/kotlin/org/tele/flutter_sip2/dto/CallSettingsDTO.kt`

```kotlin
data class CallSettingsDTO(
    var flag: Int = 0,
    var reqKeyframeMethod: Int = 0,
    var audCnt: Int = 1,
    var vidCnt: Int = 0
) {
    fun toJson(): JSONObject {
        val json = JSONObject()
        json.put("flag", flag)
        json.put("reqKeyframeMethod", reqKeyframeMethod)
        json.put("audCnt", audCnt)
        json.put("vidCnt", vidCnt)
        return json
    }

    companion object {
        fun fromJson(json: JSONObject): CallSettingsDTO {
            return CallSettingsDTO(
                flag = json.optInt("flag", 0),
                reqKeyframeMethod = json.optInt("reqKeyframeMethod", 0),
                audCnt = json.optInt("audCnt", 1),
                vidCnt = json.optInt("vidCnt", 0)
            )
        }
    }
}
```

### Settings Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| flag | Int | 0 | Call flags (bitmask) |
| reqKeyframeMethod | Int | 0 | Keyframe request method |
| audCnt | Int | 1 | Audio stream count |
| vidCnt | Int | 0 | Video stream count |

## Kotlin Method Handlers

**File**: `android/src/main/kotlin/org/tele/flutter_sip2/FlutterSip2Plugin.kt`

```kotlin
"makeCall" -> {
    val args = call.arguments as? Map<String, Any>
    val accountId = args?.get("accountId") as? Int ?: 0
    val destination = args?.get("destination") as? String ?: ""
    val callSettings = args?.get("callSettings") as? Map<String, Any>
    val msgData = args?.get("msgData") as? Map<String, Any>
    val callbackId = broadcastReceiver.register(result)
    val intent = PjActions.createMakeCallIntent(
        callbackId, accountId, destination, callSettings, msgData, context
    )
    context.startService(intent)
}
"answerCall" -> {
    val callId = call.arguments as? Int ?: 0
    val callbackId = broadcastReceiver.register(result)
    val intent = PjActions.createAnswerCallIntent(callbackId, callId, context)
    context.startService(intent)
}
"holdCall" -> {
    val callId = call.arguments as? Int ?: 0
    val callbackId = broadcastReceiver.register(result)
    val intent = PjActions.createHoldCallIntent(callbackId, callId, context)
    context.startService(intent)
}
"muteCall" -> {
    val callId = call.arguments as? Int ?: 0
    val callbackId = broadcastReceiver.register(result)
    val intent = PjActions.createMuteCallIntent(callbackId, callId, context)
    context.startService(intent)
}
```

## PjActions Intent Factory

**File**: `android/src/main/java/org/tele/flutter_sip2/PjActions.java`

```java
public static Intent createMakeCallIntent(
    int callbackId, int accountId, String destination, 
    Map<String, Object> settings, Map<String, Object> message, Context context) {
    Intent intent = new Intent(context, org.telon.sip2.PjSipService.class);
    intent.setAction(PjActions.ACTION_MAKE_CALL);
    intent.putExtra("callback_id", callbackId);
    intent.putExtra("account_id", accountId);
    intent.putExtra("destination", destination);

    if (settings != null) {
        intent.putExtra("settings", CallSettingsDTO.fromMap(settings).toJson());
    }
    if (message != null) {
        intent.putExtra("message", SipMessageDTO.fromMap(message).toJson());
    }
    return intent;
}

public static Intent createAnswerCallIntent(int callbackId, int callId, Context context) {
    Intent intent = new Intent(context, org.telon.sip2.PjSipService.class);
    intent.setAction(PjActions.ACTION_ANSWER_CALL);
    intent.putExtra("callback_id", callbackId);
    intent.putExtra("call_id", callId);
    return intent;
}

public static Intent createHoldCallIntent(int callbackId, int callId, Context context) {
    Intent intent = new Intent(context, org.telon.sip2.PjSipService.class);
    intent.setAction(PjActions.ACTION_HOLD_CALL);
    intent.putExtra("callback_id", callbackId);
    intent.putExtra("call_id", callId);
    return intent;
}
```

## Event Types

| Event | Data Structure | Trigger |
|-------|----------------|---------|
| `pjSipCallReceived` | `{call: Call, account: Account}` | Incoming call |
| `pjSipCallChanged` | `{call: Call}` | Call state changed |
| `pjSipCallTerminated` | `{call: Call}` | Call ended |

## Error Handling

### Common Error Codes

| Code | Description |
|------|-------------|
| `SIP_ERROR` | Generic call operation failed |
| `ECALLNOTFOUND` | Call ID not found |
| `EINVALIDSTATE` | Invalid call state for operation |
| `ENOMEDIA` | No media streams available |

## Testing Considerations

### Unit Tests (Dart)

- Test Call.fromMap/toMap serialization
- Test duration calculation accuracy
- Test URI parsing with various formats
- Verify equality by ID only

### Integration Tests

- Mock platform channel for call operations
- Simulate call state transitions
- Test event stream for call changes

### Manual Testing

- Audio call quality
- Hold/unhold behavior
- Mute/unmute functionality
- Speaker/earpiece switching
- DTMF tone transmission
- Call transfer scenarios

---

*Status: DRAFT | Type: SDD | Generated by /legacy*
