# Requirements: SIP Service

## Overview

The SIP Service provides VoIP call handling via SIP protocol, including account management, registration, and full call lifecycle support.

## Functional Requirements

### FR-1: SIP Account Management

The system SHALL manage SIP account configuration:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | String | Yes | SIP account username |
| password | String | Yes | SIP account password |
| domain | String | Yes | SIP server domain |
| proxy | String? | No | SIP proxy server |
| port | int | No | SIP port (default: 5060) |
| useSecure | bool | No | Secure SIP (TLS) flag |

### FR-2: Connection Management

The system SHALL manage SIP connections:

| Operation | Method | Description |
|-----------|--------|-------------|
| Initialize | `initialize(account)` | Initialize with SIP account |
| Register | `register()` | Register with SIP server |
| Unregister | `unregister()` | Unregister from server |
| Track state | `connectionStateStream` | Connection state updates |

### FR-3: Connection States

The system SHALL track connection states:

```
SipConnectionState:
  disconnected → connecting → connected → error
```

### FR-4: Call Operations

The system SHALL support call operations:

| Operation | Method | Description |
|-----------|--------|-------------|
| Make call | `makeCall(number)` | Initiate outgoing SIP call |
| Answer call | `answerCall(callId)` | Answer incoming call |
| End call | `endCall(callId)` | Terminate call |
| Hold call | `holdCall(callId)` | Put call on hold |
| Resume call | `resumeCall(callId)` | Resume held call |

### FR-5: Call State Tracking

The system SHALL track call states:

```
SipCallState:
  connecting → ringing → active → hold → ended
                              │
                              └──► failed
```

### FR-6: Event Streaming

The system SHALL provide real-time event streams:

| Stream | Purpose |
|--------|---------|
| connectionStateStream | SIP connection state |
| callStateStream | Individual call states |
| logStream | Service logging |

## Non-Functional Requirements

### NFR-1: Simulated Implementation

- Current implementation is simulated for testing
- SHALL be replaceable with native SIP stack
- SHALL maintain interface compatibility

### NFR-2: Call Quality

- SHALL support multiple concurrent calls
- SHALL track call duration
- SHALL handle call state transitions smoothly

### NFR-3: Resource Management

- SHALL properly dispose stream controllers
- SHALL clean up active calls on unregister
- SHALL manage memory efficiently

## Configuration

### SipAccount Entity

```dart
class SipAccount {
  final String username;
  final String password;
  final String domain;
  final String? proxy;
  final int port;
  final bool useSecure;
}
```

### SipCall Entity

```dart
class SipCall {
  final String id;
  final String remoteNumber;
  final SipCallDirection direction;  // incoming | outgoing
  final SipCallState state;
  final DateTime startTime;
  final Duration? duration;
}
```

---

**Status**: DRAFT  
**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)
