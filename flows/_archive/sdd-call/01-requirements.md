# Requirements: SIP Call Management

> Internal service logic for SIP call operations, state management, and media control.

## Overview

This document specifies the requirements for the SIP call management module in flutter_nmsip. Calls represent active SIP sessions with full control over audio/video media.

## Business Context

**Problem**: Applications need comprehensive call control for audio/video communication with features like hold, transfer, DTMF, and real-time state tracking.

**Solution**: Call abstraction with 20+ operations, immutable state model, and real-time duration calculation.

## Stakeholders

- **Developers**: Need clean API for all call operations
- **Application**: Full-featured calling (business, support, conferencing)
- **End Users**: Reliable calls with expected features (hold, transfer, speaker)

## Functional Requirements

### FR-1: Call Initiation

The system SHALL initiate outbound calls:
- `makeCall(account, destination, callSettings, msgData)`: Create outbound call
- Support audio-only and audio-video calls
- Custom SIP headers via msgData
- Return Call object with unique ID

**Acceptance Criteria**:
- [ ] Call created with valid account and destination
- [ ] CallSettingsDTO supports audio/video stream counts
- [ ] Custom headers passed via msgData
- [ ] Call ID assigned by native layer
- [ ] Call state tracked via events

### FR-2: Incoming Call Handling

The system SHALL handle incoming calls:
- `answerCall(call)`: Answer incoming call
- `declineCall(call)`: Reject incoming call
- `hangupCall(call)`: Terminate active call
- Broadcast call_received events for incoming calls

**Acceptance Criteria**:
- [ ] answerCall connects the call
- [ ] declineCall rejects with busy/error status
- [ ] hangupCall terminates active or incoming calls
- [ ] EVENT_CALL_RECEIVED broadcast for incoming
- [ ] EVENT_CALL_TERMINATED broadcast on hangup

### FR-3: Call Hold/Unhold

The system SHALL support call hold:
- `holdCall(call)`: Place call on hold
- `unholdCall(call)`: Resume held call
- Update held state in Call model

**Acceptance Criteria**:
- [ ] holdCall mutes audio and signals hold to remote
- [ ] unholdCall restores audio and signals resume
- [ ] held flag updated in Call state
- [ ] Call state changes broadcast via events

### FR-4: Audio Control

The system SHALL provide audio control:
- `muteCall(call)`: Mute local microphone
- `unmuteCall(call)`: Unmute microphone
- `useSpeaker(call)`: Route audio to speaker
- `useEarpiece(call)`: Route audio to earpiece
- Update muted/speaker flags in Call model

**Acceptance Criteria**:
- [ ] muteCall disables microphone input
- [ ] unmuteCall enables microphone input
- [ ] useSpeaker routes to loudspeaker
- [ ] useEarpiece routes to phone earpiece
- [ ] muted/speaker flags updated

### FR-5: Call Transfer

The system SHALL support call transfer:
- `xferCall(call, destination)`: Blind transfer to destination
- `redirectCall(call, destination)`: Redirect before answer
- Transfer completes current call

**Acceptance Criteria**:
- [ ] xferCall transfers active call to destination
- [ ] redirectCall redirects incoming call (before answer)
- [ ] Original call terminated after transfer
- [ ] Transfer status reported via events

### FR-6: DTMF Transmission

The system SHALL transmit DTMF tones:
- `dtmfCall(call, digits)`: Send DTMF digits during call
- Support digits 0-9, *, #, A-D
- Send as RFC 2833 or SIP INFO

**Acceptance Criteria**:
- [ ] DTMF digits sent during active call
- [ ] Multiple digits sent in sequence
- [ ] DTMF method configured by native layer
- [ ] No disruption to call audio

### FR-7: Call State Tracking

The system SHALL track call state:
- state: PJSIP invite state (null, calling, incoming, early, connecting, confirmed, disconnected)
- stateText: Human-readable state description
- lastStatusCode: Last SIP status code
- lastReason: Reason phrase for termination

**Acceptance Criteria**:
- [ ] State updated on every call state change
- [ ] StateText provides readable description
- [ ] Status code preserved for debugging
- [ ] Reason included on termination

### FR-8: Duration Tracking

The system SHALL track call duration:
- connectDuration: Time since connected (seconds)
- totalDuration: Time since call creation (seconds)
- Real-time calculation without native polling
- Formatted output "MM:SS"

**Acceptance Criteria**:
- [ ] connectDuration accurate to within 1 second
- [ ] totalDuration includes pre-connect time
- [ ] getFormattedTotalDuration() returns "MM:SS"
- [ ] getFormattedConnectDuration() returns "MM:SS"
- [ ] Duration updates in real-time

### FR-9: Participant Information

The system SHALL track call participants:
- remoteNumber: Extracted from remote URI
- remoteName: Display name from remote URI
- localNumber: Extracted from local URI
- localUri, remoteUri: Full SIP URIs
- localContact, remoteContact: Contact headers

**Acceptance Criteria**:
- [ ] remoteNumber parsed from SIP URI
- [ ] remoteName parsed from display name
- [ ] Supports sip: and tel: URI formats
- [ ] Handles quoted display names

### FR-10: Video Support

The system SHALL support video calls:
- audCnt: Audio stream count (default 1)
- vidCnt: Video stream count (default 0 for audio-only)
- remoteAudioCount, remoteVideoCount: Remote capabilities
- provisionalMedia: Media info before connection

**Acceptance Criteria**:
- [ ] Video calls initiated with vidCnt > 0
- [ ] Remote video count tracked
- [ ] Provisional media info available
- [ ] Media info updated on state changes

## Non-Functional Requirements

### NFR-1: Performance

- Call initiation < 2s (network dependent)
- State update latency < 500ms
- Duration calculation overhead < 1ms

### NFR-2: Reliability

- Call state consistent across operations
- No race conditions in state updates
- Duration accurate even with background execution

### NFR-3: Usability

- Formatted duration ready for display
- Parsed numbers ready for UI
- Clear state descriptions

### NFR-4: Compatibility

- Support audio-only and audio-video calls
- Handle various SIP server implementations
- Support RFC 2833 and SIP INFO DTMF

## Dependencies

- **endpoint-management**: Initialized SIP endpoint
- **account-management**: Account for call origination
- **event-streaming**: Call state events

## Out of Scope

- Codec negotiation (native layer)
- Network quality adaptation (native layer)
- Call recording (application layer)

---

*Status: DRAFT | Type: SDD | Generated by /legacy*
