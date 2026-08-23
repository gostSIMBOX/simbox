# Requirements: TeleCall Data Model

**Status**: DRAFT  
**Type**: SDD (Spec-Driven Development)  
**Module**: call-management  
**Generated**: 2026-03-04 by /legacy

---

## Overview

The TeleCall data model is the core data structure representing phone calls in the flutter_tele plugin. It provides comprehensive call state tracking, duration calculation, and caller identification across Flutter and Android platforms.

---

## Functional Requirements

### R1: Call Identity Tracking

**Description**: Each call must have unique identifiers for tracking and correlation.

**Requirements**:
- R1.1: Internal ID (integer) for Flutter-side tracking
- R1.2: Call ID (string) from native telephony system
- R1.3: Account ID for multi-account scenarios
- R1.4: Hash code for call comparison/equality

**Source**: `lib/src/call.dart` - TeleCall.id, callId, accountId, callHashCode

---

### R2: Participant Information

**Description**: Capture information about call participants (local and remote).

**Requirements**:
- R2.1: Local contact information (contact name/identifier)
- R2.2: Local URI (SIP URI or phone number)
- R2.3: Remote contact information
- R2.4: Remote URI (SIP/tel URI)
- R2.5: Extracted remote phone number (parsed from URI)
- R2.6: Extracted remote name (parsed from SIP URI display name)

**Source**: `lib/src/call.dart` - remoteContact, remoteUri, remoteNumber, remoteName

**URI Parsing Requirements**:
- Support SIP URI with display name: `"John Doe" <sip:123@domain.com>`
- Support bare SIP URI: `sip:123@domain.com`
- Support tel URI: `tel:+1234567890`
- URL-decode tel URI components

---

### R3: Call State Management

**Description**: Track current call state and properties.

**Requirements**:
- R3.1: Call state (enum-like string: INITIATING, CONNECTING, ACTIVE, HOLDING, DISCONNECTED, etc.)
- R3.2: State text (human-readable state description)
- R3.3: Hold state (boolean)
- R3.4: Mute state (boolean)
- R3.5: Speaker state (boolean)
- R3.6: Call direction (DIRECTION_INCOMING, DIRECTION_OUTGOING)
- R3.7: Disconnect cause (reason for call termination)
- R3.8: Termination check helper (isTerminated() method)

**Source**: `lib/src/call.dart` - state, stateText, held, muted, speaker, direction, disconnectCause

---

### R4: Duration Tracking

**Description**: Calculate and format call durations with dynamic elapsed time.

**Requirements**:
- R4.1: Connect duration (time from answer to current/end)
- R4.2: Total duration (time from call creation to current/end)
- R4.3: Creation timestamp (ISO string)
- R4.4: Connect timestamp (ISO string)
- R4.5: Creation time in milliseconds (epoch)
- R4.6: Connect time in milliseconds (epoch)
- R4.7: Dynamic duration calculation (adds elapsed time since construction)
- R4.8: Duration formatting (MM:SS format)

**Source**: `lib/src/call.dart` - getConnectDuration(), getTotalDuration(), formatTime()

**Calculation Logic**:
```dart
// Total duration = stored duration + elapsed time since creation
getTotalDuration() {
  now = DateTime.now().millisecondsSinceEpoch ~/ 1000
  offset = now - creationTimeMillis
  return totalDuration + offset
}

// Connect duration = 0 if not connected or terminated
// Otherwise: elapsed time since connection
getConnectDuration() {
  if (connectDuration == null || state == DISCONNECTED)
    return connectDuration ?? 0
  now = DateTime.now().millisecondsSinceEpoch ~/ 1000
  offset = now - creationTimeMillis
  return offset
}
```

---

### R5: Media Information

**Description**: Track media streams (audio/video) associated with call.

**Requirements**:
- R5.1: Local audio stream count
- R5.2: Local video stream count
- R5.3: Remote audio stream count
- R5.4: Remote video stream count
- R5.5: Remote offerer flag (who initiated media negotiation)
- R5.6: Media details map (codec, bitrate, etc.)
- R5.7: Provisional media map (pre-negotiation media info)

**Source**: `lib/src/call.dart` - audioCount, videoCount, remoteAudioCount, remoteVideoCount, remoteOfferer, media, provisionalMedia

---

### R6: Status and Error Information

**Description**: Track call status codes and error reasons.

**Requirements**:
- R6.1: Last status code (SIP status code or telephony status)
- R6.2: Last reason text (error description)
- R6.3: Additional details map
- R6.4: Extras map for vendor-specific data

**Source**: `lib/src/call.dart` - lastStatusCode, lastReason, details, extras

---

### R7: SIM Information

**Description**: Support dual-SIM devices.

**Requirements**:
- R7.1: SIM slot used for call (0-based or 1-based)
- R7.2: SIM slot 1 identifier
- R7.3: SIM slot 2 identifier

**Source**: `lib/src/call.dart` - simSlot, simSlot1, simSlot2

---

### R8: Serialization/Deserialization

**Description**: Convert between TeleCall objects and Map for platform channel communication.

**Requirements**:
- R8.1: fromMap() factory constructor
- R8.2: toMap() serialization method
- R8.3: Handle null safety for all optional fields
- R8.4: Type conversion for nested Maps (Map<Object?, Object?> → Map<String, dynamic>)
- R8.5: Debug logging for fromMap() parsing

**Source**: `lib/src/call.dart` - TeleCall.fromMap(), TeleCall.toMap()

---

### R9: Kotlin Interoperability

**Description**: Minimal TeleCall model for Android event streaming.

**Requirements**:
- R9.1: Basic fields only (id, destination, sim, state, held, muted, speaker, direction, remoteNumber, remoteName)
- R9.2: toMap() conversion for EventChannel streaming
- R9.3: Mutable state properties for state updates

**Source**: `android/.../TeleService.kt` - TeleCall data class

---

## Non-Functional Requirements

### NFR1: Performance

- NFR1.1: Duration calculation must be O(1) - no loops or heavy computation
- NFR1.2: URI parsing should use pre-compiled Regex patterns
- NFR1.3: Map conversion should handle 40+ fields efficiently

### NFR2: Maintainability

- NFR2.1: All fields must be documented
- NFR2.2: Getters should be provided for all public properties
- NFR2.3: toString() override for debugging

### NFR3: Compatibility

- NFR3.1: Support Android telephony API variations
- NFR3.2: Handle missing fields gracefully (null safety)
- NFR3.3: Backward compatible Map serialization

---

## Dependencies

- **flutter_dialer**: For dialer functionality (separate module)
- **Android Telecom API**: InCallService, Call, TelecomManager
- **Method Channel**: Flutter-Kotlin communication
- **Event Channel**: Real-time event streaming

---

## Open Questions

1. **Model mismatch**: Why does Kotlin model have only 10 fields vs Dart's 40+ fields?
   - Risk: Data loss when events stream from Kotlin to Dart
   - Recommendation: Enrich Kotlin model or document intentional minimalism

2. **Time zone handling**: Duration calculations use `DateTime.now()` without timezone consideration
   - Risk: Incorrect durations across DST transitions
   - Recommendation: Use UTC timestamps consistently

3. **Regex fragility**: SIP URI parsing assumes specific format
   - Risk: Fails on non-standard SIP URIs
   - Recommendation: Add error handling and fallback parsing

---

*Generated by /legacy reverse engineering*
