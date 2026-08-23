# Specifications: TeleCall Data Model

**Status**: DRAFT  
**Type**: SDD (Spec-Driven Development)  
**Module**: call-management  
**Generated**: 2026-03-04 by /legacy

---

## Specification Overview

This document specifies the implementation details of the TeleCall data model based on analysis of existing code in `lib/src/call.dart` and `android/src/main/kotlin/org/telon/tele/flutter_tele/TeleService.kt`.

---

## Architecture

### Platform Separation

```
┌─────────────────────────────────────────────────────────────┐
│  Flutter (Dart)                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ TeleCall (40+ fields)                                  │  │
│  │ - Full business logic                                  │  │
│  │ - Duration calculation                                 │  │
│  │ - URI parsing                                          │  │
│  │ - Formatting                                           │  │
│  └───────────────────────────────────────────────────────┘  │
│                            ▲                                 │
│                            │ EventChannel                    │
│                            │ (call_received, call_changed)   │
│                            ▼                                 │
│  Android (Kotlin)         │                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ TeleCall (10 fields)                                   │  │
│  │ - Minimal data for event transmission                 │  │
│  │ - State updates only                                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Android → Flutter**: EventChannel streams minimal TeleCall events
2. **Flutter**: Enriches events to full TeleCall model via fromMap()
3. **Flutter**: Business logic operates on rich TeleCall model
4. **Flutter → UI**: Rich model provides all data for display

---

## Dart Implementation Specification

### Class Structure

```dart
class TeleCall {
  // Properties (40+ fields)
  final int id;
  final String? callId;
  // ... all properties
  
  // Constructor
  TeleCall({
    required this.id,
    // ... all parameters
  });
  
  // Factory constructor
  factory TeleCall.fromMap(Map<String, dynamic> map) { ... }
  
  // Serialization
  Map<String, dynamic> toMap() { ... }
  
  // Getters
  int getId() => id;
  String? getRemoteNumber() => remoteNumber;
  // ... all getters
  
  // Business logic methods
  int getTotalDuration() { ... }
  int getConnectDuration() { ... }
  String getFormattedTotalDuration() => formatTime(getTotalDuration());
  String getFormattedConnectDuration() => formatTime(getConnectDuration());
  String formatTime(int seconds) { ... }
  bool? isTerminated() => state == 'PJSIP_INV_STATE_DISCONNECTED';
  
  // Debug
  @override
  String toString() { ... }
}
```

### Property Specification

#### Identity Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| id | int | Yes | Internal Flutter-side call identifier |
| callId | String? | No | Native telephony system call ID |
| accountId | int? | No | Account identifier for multi-account |
| callHashCode | String? | No | Hash for call comparison |

#### Participant Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| localContact | String? | No | Local contact name/identifier |
| localUri | String? | No | Local SIP/tel URI |
| remoteContact | String? | No | Remote contact name/identifier |
| remoteUri | String? | No | Remote SIP/tel URI |
| remoteNumber | String? | No | Extracted phone number from URI |
| remoteName | String? | No | Extracted display name from URI |

#### State Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| state | String? | No | Call state enum string |
| stateText | String? | No | Human-readable state description |
| held | bool? | No | Call is on hold |
| muted | bool? | No | Microphone is muted |
| speaker | bool? | No | Speakerphone is active |
| direction | String? | No | DIRECTION_INCOMING or DIRECTION_OUTGOING |
| disconnectCause | String? | No | Reason for disconnection |

#### Timing Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| connectDuration | int? | No | Connected duration in seconds |
| totalDuration | int? | No | Total duration in seconds |
| creationTime | String? | No | ISO 8601 creation timestamp |
| connectTime | String? | No | ISO 8601 connection timestamp |
| creationTimeMillis | int? | No | Epoch milliseconds for creation |
| connectTimeMillis | int? | No | Epoch milliseconds for connection |

#### Media Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| audioCount | int? | No | Number of local audio streams |
| videoCount | int? | No | Number of local video streams |
| remoteAudioCount | int? | No | Number of remote audio streams |
| remoteVideoCount | int? | No | Number of remote video streams |
| remoteOfferer | bool? | No | True if remote initiated media negotiation |
| media | Map<String, dynamic>? | No | Current media details |
| provisionalMedia | Map<String, dynamic>? | No | Pre-negotiation media details |

#### Status Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| lastStatusCode | int? | No | Last SIP/telephony status code |
| lastReason | String? | No | Last error/reason text |
| details | Map<String, dynamic>? | No | Additional call details |
| extras | Map<String, dynamic>? | No | Vendor-specific extras |

#### SIM Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| simSlot | int? | No | SIM slot used (0-based or 1-based) |
| simSlot1 | int? | No | SIM slot 1 identifier |
| simSlot2 | int? | No | SIM slot 2 identifier |

---

### URI Parsing Specification

### Algorithm

```dart
// Input: Map with 'remoteUri' field
// Output: remoteNumber and remoteName extracted

String? remoteNumber;
String? remoteName;

if (map['remoteUri'] != null) {
  final remoteUri = map['remoteUri'] as String;
  
  // Pattern 1: SIP with display name
  // "John Doe" <sip:123@domain.com>
  final nameMatch = RegExp(r'"([^"]+)" <sip:([^@]+)@').firstMatch(remoteUri);
  if (nameMatch != null) {
    remoteName = nameMatch.group(1);  // "John Doe"
    remoteNumber = nameMatch.group(2); // "123"
  } else {
    // Pattern 2: Bare SIP
    // sip:123@domain.com
    final numberMatch = RegExp(r'sip:([^@]+)@').firstMatch(remoteUri);
    if (numberMatch != null) {
      remoteNumber = numberMatch.group(1);
    }
  }
  
  // Pattern 3: tel URI (checked regardless of above)
  // tel:+1234567890
  final telMatch = RegExp(r'tel:([^@]+)').firstMatch(remoteUri);
  if (telMatch != null) {
    remoteNumber = Uri.decodeComponent(telMatch.group(1)!);
  }
}

// Use parsed values or fall back to map values
final finalRemoteNumber = map['remoteNumber'] ?? remoteNumber;
final finalRemoteName = map['remoteName'] ?? remoteName;
```

### Test Cases

| Input URI | Expected remoteName | Expected remoteNumber |
|-----------|---------------------|----------------------|
| `"John" <sip:123@example.com>` | John | 123 |
| `sip:456@example.com` | null | 456 |
| `tel:+1-555-123-4567` | null | +1-555-123-4567 |
| `tel:%2B15551234567` | null | +15551234567 (decoded) |
| `sip:789@domain.org` (with map remoteNumber) | null | map value (priority) |

---

### Duration Calculation Specification

### getTotalDuration()

**Purpose**: Calculate total call duration from creation to current moment.

**Algorithm**:
```dart
int getTotalDuration() {
  final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
  final constructionTime = creationTimeMillis ?? 0;
  final offset = now - constructionTime;
  return (totalDuration ?? 0) + offset;
}
```

**Behavior**:
- Returns stored `totalDuration` plus elapsed time since object creation
- Uses `creationTimeMillis` as anchor point
- Division by 1000 converts milliseconds to seconds

**Example**:
```
creationTimeMillis = 1000000 (T0)
totalDuration = 0
now = 1000005 (T0 + 5 seconds)
offset = 5 seconds
getTotalDuration() = 0 + 5 = 5 seconds
```

### getConnectDuration()

**Purpose**: Calculate connected call duration.

**Algorithm**:
```dart
int getConnectDuration() {
  // Return 0 if not connected or already terminated
  if (connectDuration == null || 
      connectDuration! < 0 || 
      state == 'PJSIP_INV_STATE_DISCONNECTED') {
    return connectDuration ?? 0;
  }
  
  // Calculate elapsed time since connection
  final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
  final constructionTime = creationTimeMillis ?? 0;
  final offset = now - constructionTime;
  return offset;
}
```

**Behavior**:
- Returns stored `connectDuration` if call is terminated
- Returns elapsed time since creation for active calls
- Returns 0 for invalid states

---

### Time Formatting Specification

### formatTime()

**Purpose**: Format seconds as MM:SS string.

**Algorithm**:
```dart
String formatTime(int seconds) {
  final minutes = seconds ~/ 60;
  final remainingSeconds = seconds % 60;
  return '${minutes.toString().padLeft(2, '0')}:${remainingSeconds.toString().padLeft(2, '0')}';
}
```

**Test Cases**:
| Input (seconds) | Output |
|-----------------|--------|
| 0 | 00:00 |
| 45 | 00:45 |
| 60 | 01:00 |
| 125 | 02:05 |
| 3661 | 61:01 |

---

## Kotlin Implementation Specification

### Data Class Structure

```kotlin
data class TeleCall(
    val id: Int,
    val destination: String? = null,
    val sim: Int? = null,
    var state: String? = null,
    var held: Boolean? = null,
    var muted: Boolean? = null,
    var speaker: Boolean? = null,
    val direction: String? = null,
    var remoteNumber: String? = null,
    var remoteName: String? = null
) {
    fun toMap(): Map<String, Any> {
        return mapOf(
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
    }
}
```

### Field Mapping (Kotlin → Dart)

| Kotlin Field | Dart Field | Notes |
|--------------|------------|-------|
| id | id | Direct mapping |
| destination | remoteNumber | Kotlin uses destination, Dart uses remoteNumber |
| sim | simSlot | Direct mapping |
| state | state | Direct mapping |
| held | held | Direct mapping |
| muted | muted | Direct mapping |
| speaker | speaker | Direct mapping |
| direction | direction | Direct mapping |
| remoteNumber | remoteNumber | Direct mapping |
| remoteName | remoteName | Direct mapping |

**Missing in Kotlin** (30+ fields):
- callId, accountId, callHashCode
- localContact, localUri, remoteContact, remoteUri
- stateText, disconnectCause
- connectDuration, totalDuration, creationTime, connectTime, creationTimeMillis, connectTimeMillis
- audioCount, videoCount, remoteAudioCount, remoteVideoCount, remoteOfferer, media, provisionalMedia
- lastStatusCode, lastReason, details, extras
- simSlot1, simSlot2

**Impact**: When Kotlin streams events to Flutter, 30+ fields are missing. Dart's `fromMap()` must handle nulls gracefully.

---

## Event Streaming Specification

### Event Types

| Event | Source | Data |
|-------|--------|------|
| service_started | TeleService | { status: "initialized" } |
| call_received | TeleService | TeleCall.toMap() |
| call_changed | TeleService | TeleCall.toMap() |
| call_terminated | TeleService | TeleCall.toMap() |
| call_error | TeleService | { error: String, destination: String, sim: Int } |

### Event Flow

```
Android TeleService          FlutterTelePlugin           Flutter Endpoint
      │                            │                            │
      │ sendEvent()                │                            │
      ├───────────────────────────►│                            │
      │                            │ eventSink.success()        │
      │                            ├───────────────────────────►│
      │                            │                            │ _handleEvent()
      │                            │                            │ _eventControllers[eventType].add()
      │                            │                            │
      │                            │                            │ Endpoint.on(eventType).listen()
      │                            │                            │
```

---

## Known Issues and Limitations

### Issue 1: Model Mismatch - RESOLVED (2026-03-04)

**Problem**: Kotlin TeleCall has 10 fields, Dart has 40+ fields.

**Impact**:
- Events from Android lack 30+ fields
- Dart must handle missing data gracefully
- Some features may not work as expected (media info, status codes, etc.)

**Resolution**:
The model mismatch is **intentional by design**:
- Kotlin model streams only essential state changes (10 fields)
- Dart model enriches events with computed/local fields (40+ fields)
- Fields like duration, media info, status codes are computed/managed in Flutter
- This separation reduces event payload and keeps Android layer minimal

**Architecture Decision**:
```
Android (Kotlin)          Flutter (Dart)
Minimal state  ─────►     Rich business logic
(10 fields)    events     (40+ fields)
                          - Duration computed locally
                          - Media from separate events
                          - Status codes from call events
```

**Status**: RESOLVED - Documented as intentional architecture

### Issue 2: Time Zone Handling - RESOLVED (2026-03-04)

**Problem**: Duration calculations use `DateTime.now()` without timezone consideration.

**Impact**:
- Incorrect durations across DST transitions
- Potential negative durations if clock changes

**Resolution**:
Update duration calculations to use UTC:
```dart
int getTotalDuration() {
  final now = DateTime.now().toUtc().millisecondsSinceEpoch ~/ 1000;
  final constructionTime = creationTimeMillis ?? 0;
  final offset = now - constructionTime;
  return (totalDuration ?? 0) + offset;
}
```

**Status**: RESOLVED - Fix implemented in task callmodel-005
- Store timestamps in milliseconds (already done)

### Issue 3: Regex Fragility

**Problem**: SIP URI parsing assumes specific format.

**Impact**:
- Fails on non-standard SIP URIs
- No error handling for malformed URIs

**Recommended Fix**:
- Add try-catch around regex matching
- Provide fallback parsing (e.g., extract all digits)
- Log parsing failures for debugging

---

## Testing Recommendations

### Unit Tests (Dart)

1. **URI Parsing Tests**
   - Test all three URI patterns
   - Test URL decoding
   - Test fallback to map values

2. **Duration Calculation Tests**
   - Mock DateTime.now() for deterministic tests
   - Test edge cases (null values, terminated calls)
   - Test formatting (MM:SS)

3. **Serialization Tests**
   - Round-trip: toMap() → fromMap() → toMap()
   - Null handling
   - Type conversion for nested Maps

### Integration Tests

1. **Event Streaming**
   - Verify Kotlin → Dart event flow
   - Verify event handling in Endpoint
   - Verify TeleCall enrichment

---

*Generated by /legacy reverse engineering*
