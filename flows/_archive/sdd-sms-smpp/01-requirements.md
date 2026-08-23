# Requirements: SMS/SMPP Service

## Overview

The SMS Service provides dual-path SMS messaging via SMPP protocol and local Android SMS, with complete message lifecycle tracking.

## Functional Requirements

### FR-1: SMPP Configuration

The system SHALL manage SMPP configuration:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| host | String | Yes | SMPP server host |
| port | int | Yes | SMPP server port |
| systemId | String | Yes | SMPP system ID |
| password | String | Yes | SMPP password |
| systemType | String | No | SMPP system type |
| sourceAddrTon | String | No | Type of number |
| sourceAddrNpi | String | No | Numbering plan |
| addressRange | String | No | Address range |

### FR-2: Connection Management

The system SHALL manage SMPP connections:

| Operation | Method | Description |
|-----------|--------|-------------|
| Initialize | `initializeSmpp(config)` | Initialize with SMPP config |
| Connect | `connectSmpp()` | Connect to SMPP server |
| Disconnect | `disconnectSmpp()` | Disconnect from server |
| Track state | `connectionStateStream` | Connection state updates |

### FR-3: Connection States

The system SHALL track SMPP connection states:

```
SmppConnectionState:
  disconnected → connecting → bound → error
```

### FR-4: SMS Operations

The system SHALL support SMS operations:

| Operation | Method | Description |
|-----------|--------|-------------|
| Send via SMPP | `sendSmsViaSmpp(recipient, content)` | Send via SMPP |
| Send local | `sendSmsLocal(recipient, content)` | Send via Android SMS |
| Get history | `getMessageHistory(filters)` | Retrieve message history |
| Get stats | `getMessageStats()` | Get message statistics |

### FR-5: Message States

The system SHALL track message states:

```
SmsMessageStatus (outgoing):
  pending → sent → delivered
          │
          └──► failed

SmsMessageStatus (incoming):
  received
```

### FR-6: Message Entity

The system SHALL track message information:

| Field | Type | Description |
|-------|------|-------------|
| id | String | Unique message ID |
| sender | String | Sender number/ID |
| recipient | String | Recipient number |
| content | String | Message content |
| timestamp | DateTime | Message timestamp |
| type | SmsMessageType | incoming/outgoing |
| status | SmsMessageStatus | Message status |

### FR-7: Event Streaming

The system SHALL provide real-time event streams:

| Stream | Purpose |
|--------|---------|
| connectionStateStream | SMPP connection state |
| messageStream | Message updates |
| logStream | Service logging |

## Non-Functional Requirements

### NFR-1: Dual-Path Support

- SHALL support both SMPP and local SMS
- SHALL gracefully fallback when SMPP unavailable
- SHALL track message path (SMPP vs local)

### NFR-2: Message Reliability

- SHALL track message delivery status
- SHALL simulate 95% delivery success rate (testing)
- SHALL retry failed messages (future)

### NFR-3: History Management

- SHALL store message history
- SHALL support filtering by sender, recipient, type, date
- SHALL provide statistics

### NFR-4: Resource Management

- SHALL properly dispose stream controllers
- SHALL support clearing message history
- SHALL manage memory efficiently

## Configuration

### SmppConfig Entity

```dart
class SmppConfig {
  final String host;
  final int port;
  final String systemId;
  final String password;
  final String systemType;
  final String sourceAddrTon;
  final String sourceAddrNpi;
  final String addressRange;
}
```

### SmsMessage Entity

```dart
class SmsMessage {
  final String id;
  final String sender;
  final String recipient;
  final String content;
  final DateTime timestamp;
  final SmsMessageType type;   // incoming | outgoing
  final SmsMessageStatus status; // pending, sent, delivered, failed, received
}
```

---

**Status**: DRAFT  
**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)
