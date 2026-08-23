# Requirements: Android Telecom Integration

**Status**: DRAFT  
**Type**: SDD (Spec-Driven Development)  
**Module**: android-telecom-integration  
**Generated**: 2026-03-04 by /legacy

---

## Overview

The android-telecom-integration module provides native Android telephony integration for the flutter_tele plugin. It extends Android's InCallService to receive call lifecycle events, manages Call objects via the android.telecom API, and synchronizes call state with Flutter via event streaming.

---

## Functional Requirements

### R1: InCallService Implementation

**Description**: Extend Android's InCallService to receive call callbacks.

**Requirements**:
- R1.1: Extend `android.telecom.InCallService`
- R1.2: Override `onCallAdded(call: Call)` for new calls
- R1.3: Override `onCallRemoved(call: Call)` for removed calls
- R1.4: Register service in AndroidManifest with `BIND_IN_CALL_SERVICE` permission
- R1.5: Service started with `START_STICKY` for restart resilience

**Source**: `android/.../TeleService.kt`

---

### R2: Call Lifecycle Management

**Description**: Track call lifecycle from creation to termination.

**Requirements**:
- R2.1: Maintain `mCalls` list of active TeleCall objects
- R2.2: Maintain `callMapping` from TeleCall ID to Android Call object
- R2.3: Generate unique TeleCall IDs sequentially
- R2.4: Track `currentCall` as most recent Call object
- R2.5: Clean up calls on termination (remove from mCalls and callMapping)

**Source**: `android/.../TeleService.kt`

---

### R3: Call State Synchronization

**Description**: Synchronize Android Call state with Flutter.

**Requirements**:
- R3.1: Register `Call.Callback` on each Call added
- R3.2: Override `onStateChanged(call, state)` for state changes
- R3.3: Override `onCallDestroyed(call)` for call termination
- R3.4: Map Android Call.State to TeleCall state strings
- R3.5: Send "call_changed" event on state change
- R3.6: Send "call_terminated" event on call destruction

**State Mapping**:
| Android State | TeleCall State |
|---------------|----------------|
| STATE_RINGING | RINGING |
| STATE_DISCONNECTED | DISCONNECTED |
| STATE_ACTIVE | ACTIVE |
| STATE_HOLDING | HOLDING |
| STATE_DIALING | DIALING |
| STATE_CONNECTING | CONNECTING |
| (other) | UNKNOWN |

**Source**: `android/.../TeleService.kt`

---

### R4: Outgoing Call Initiation

**Description**: Initiate outgoing calls via Intent.

**Requirements**:
- R4.1: Create `Intent.ACTION_CALL` with `tel:` URI
- R4.2: Set SIM slot via Intent extras (multiple fallback keys)
- R4.3: Set `PHONE_ACCOUNT_HANDLE` for specific SIM selection
- R4.4: Add `FLAG_ACTIVITY_NEW_TASK` flag
- R4.5: Start activity with `startActivity(callIntent)`
- R4.6: Create TeleCall tracking object before call initiated
- R4.7: Send "call_received" event immediately
- R4.8: Simulate state change to CONNECTING after 1 second delay

**SIM Slot Extras** (tried in order):
- `android.intent.extra.SLOT_ID`
- `android.intent.extra.SIM_SLOT_INDEX`
- `android.intent.extra.SUB_ID`
- `android.telecom.extra.PHONE_ACCOUNT_HANDLE`

**Source**: `android/.../TeleService.kt`

---

### R5: Incoming Call Handling

**Description**: Handle incoming calls detected by InCallService.

**Requirements**:
- R5.1: Extract remote number from `Call.Details.handle`
- R5.2: Extract remote name from `Call.Details.callerDisplayName`
- R5.3: Parse URI scheme (tel:, sip:) for number extraction
- R5.4: Find existing TeleCall by destination and state (outgoing call matching)
- R5.5: Create new TeleCall if no match found (incoming call)
- R5.6: Update existing TeleCall if match found (outgoing call connected)
- R5.7: Set direction to `DIRECTION_INCOMING` for new calls
- R5.8: Send "call_received" event

**Source**: `android/.../TeleService.kt`

---

### R6: Call Control Operations

**Description**: Provide call control operations via Intent handlers.

**Operations**:
| Operation | Intent Action | Android API |
|-----------|---------------|-------------|
| Answer call | ANSWER_CALL | `call.answer(0)` |
| Hangup call | HANGUP_CALL | `call.disconnect()` |
| Decline call | DECLINE_CALL | `call.reject(false, null)` |
| Hold call | HOLD_CALL | `call.hold()` |
| Unhold call | UNHOLD_CALL | `call.unhold()` |

**Requirements**:
- R6.1: Find TeleCall by ID in `mCalls`
- R6.2: Find Android Call via `callMapping[callId]` or `currentCall`
- R6.3: Execute Android Call operation
- R6.4: Update TeleCall state properties
- R6.5: Send "call_changed" event
- R6.6: Handle null cases gracefully (call not found)

**Source**: `android/.../TeleService.kt`

---

### R7: Audio Control Operations

**Description**: Control audio routing via AudioManager.

**Operations**:
| Operation | AudioManager Action | TeleCall Property |
|-----------|---------------------|-------------------|
| Mute call | `isMicrophoneMute = true` | muted = true |
| Unmute call | `isMicrophoneMute = false` | muted = false |
| Use speaker | `mode = MODE_NORMAL`, `isSpeakerphoneOn = true` | speaker = true |
| Use earpiece | `mode = MODE_IN_COMMUNICATION`, `isSpeakerphoneOn = false` | speaker = false |

**Requirements**:
- R7.1: Get AudioManager via `getSystemService(Context.AUDIO_SERVICE)`
- R7.2: Find TeleCall by ID
- R7.3: Execute AudioManager operation
- R7.4: Update TeleCall property
- R7.5: Send "call_changed" event

**Source**: `android/.../TeleService.kt`

---

### R8: Event Broadcasting

**Description**: Send call events to Flutter via EventChannel.

**Event Types**:
| Event | Trigger | Payload |
|-------|---------|---------|
| call_received | New call detected | TeleCall.toMap() |
| call_changed | State/property change | TeleCall.toMap() |
| call_terminated | Call ended | TeleCall.toMap() |

**Requirements**:
- R8.1: Get FlutterTelePlugin instance via singleton
- R8.2: Call `sendEvent(eventType, data)`
- R8.3: Convert TeleCall to Map via `toMap()`
- R8.4: Log events for debugging

**Source**: `android/.../TeleService.kt`, `android/.../FlutterTelePlugin.kt`

---

### R9: Service Initialization

**Description**: Initialize telephony service with configuration.

**Requirements**:
- R9.1: Handle `START_TELEPHONY_SERVICE` intent action
- R9.2: Extract configuration from intent extra (String)
- R9.3: Set `mInitialized = true` to prevent duplicate initialization
- R9.4: Send "service_started" event to Flutter
- R9.5: Initialize AudioManager, PowerManager, TelephonyManager

**Source**: `android/.../TeleService.kt`

---

### R10: Call Mapping Management

**Description**: Maintain mapping between TeleCall IDs and Android Call objects.

**Requirements**:
- R10.1: Add mapping when Call added: `callMapping[teleCall.id] = call`
- R10.2: Remove mapping when Call destroyed: `callMapping.remove(teleCall.id)`
- R10.3: Lookup via `callMapping[callId]` with fallback to `currentCall`
- R10.4: Handle missing mappings gracefully

**Source**: `android/.../TeleService.kt`

---

### R11: SIM Slot Selection

**Description**: Support dual-SIM devices with SIM slot selection.

**Requirements**:
- R11.1: Accept SIM slot parameter (1-based index)
- R11.2: Convert to 0-based for Android APIs
- R11.3: Try multiple Intent extra keys for compatibility
- R11.4: Attempt PhoneAccountHandle method as fallback
- R11.5: Handle exceptions gracefully (log warning, continue)

**Source**: `android/.../TeleService.kt`

---

## Non-Functional Requirements

### NFR1: Performance

- NFR1.1: Call state changes should trigger events within 100ms
- NFR1.2: Call control operations should complete within 200ms
- NFR1.3: Minimal overhead from callback chaining

### NFR2: Reliability

- NFR2.1: Handle null Call objects gracefully
- NFR2.2: Handle missing mappings without crashes
- NFR2.3: Service should restart if killed (START_STICKY)

### NFR3: Compatibility

- NFR3.1: Support Android 8.0+ (Oreo/API 26+) for InCallService
- NFR3.2: Support dual-SIM devices with fallback strategies
- NFR3.3: Handle different Android manufacturer implementations

### NFR4: Maintainability

- NFR4.1: Log all major operations for debugging
- NFR4.2: Use singleton pattern for Plugin ↔ Service communication
- NFR4.3: Clear separation of concerns (call control, audio control, state management)

---

## Dependencies

- **Android Telecom API**: InCallService, Call, Call.Callback, TelecomManager
- **Android Telephony API**: SubscriptionManager, TelephonyManager
- **Android Audio**: AudioManager
- **Flutter**: EventChannel for event streaming
- **TeleCall**: Data model for call representation

---

## Open Questions

1. **State change simulation**: Why simulate state change after 1 second instead of waiting for real callback?
   - **Risk**: State may not match actual call state
   - **Recommendation**: Remove simulation, rely on Call.Callback

2. **findCallByCall() fallback**: Uses `lastOrNull()` which may return wrong call in multi-call scenarios
   - **Risk**: Operations may affect wrong call
   - **Recommendation**: Always use callMapping, remove findCallByCall()

3. **Audio mode management**: Changes audio mode without saving/restoring previous mode
   - **Risk**: May conflict with other audio apps
   - **Recommendation**: Save mode before change, restore after call ends

4. **Service restart state loss**: START_STICKY restarts service but state is lost
   - **Risk**: mCalls and callMapping lost on restart
   - **Recommendation**: Persist state or re-sync with TelecomManager

---

*Generated by /legacy reverse engineering*
