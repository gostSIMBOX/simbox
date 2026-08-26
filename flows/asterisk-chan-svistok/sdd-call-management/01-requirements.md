# 01-Requirements

## Overview

Call Management for Asterisk channel driver handling voice calls via Huawei UMTS dongles.

## Functional Requirements

### FR-1: Channel Driver Interface
The system SHALL implement Asterisk channel driver interface including:
- `channel_request()` - Create channel from dialplan
- `channel_call()` - Execute outbound call
- `channel_hangup()` - Terminate call
- `channel_answer()` - Answer incoming call
- `channel_read()` / `channel_write()` - Audio streaming

### FR-2: Call State Machine
The system SHALL maintain call states:
1. **INIT** - Call being initialized
2. **DIALING** - Dialing outbound number
3. **ALERTING** - Remote phone ringing
4. **INCOMING** - Incoming call waiting
5. **WAITING** - Call waiting during active call
6. **ACTIVE** - Active two-way conversation
7. **ONHOLD** - Call on hold
8. **RELEASED** - Call terminated

### FR-3: Call Flags
The system SHALL track call properties via flags:
- `CALL_FLAG_HOLD_OTHER` - Hold other calls when dialing
- `CALL_FLAG_NEED_HANGUP` - Must issue hangup command
- `CALL_FLAG_ACTIVATED` - FD attached to channel
- `CALL_FLAG_ALIVE` - Still in CLCC list
- `CALL_FLAG_CONFERENCE` - Begin conference after activate
- `CALL_FLAG_MASTER` - Master channel (owns audio FD)
- `CALL_FLAG_BRIDGE_LOOP` - Detected bridge loop
- `CALL_FLAG_MULTIPARTY` - Part of conference call

### FR-4: Dial String Parsing
The system SHALL parse dial strings in format:
- `device:number` - Basic dial
- `device/holdother:number` - Hold other calls
- `device/conference:number` - Start conference
- Validation: Only `0123456789*#+ABC` allowed in number

### FR-5: Call Routing
The system SHALL route calls based on:
- Device group (`g1`, `g2`, etc.)
- Round-robin within group (`r1`)
- Specific device (`dongle0`)
- Provider name (`p:PROVIDER NAME`)
- IMEI (`i:123456789012345`)
- IMSI prefix (`s:25099203948`)

### FR-6: Hold and Conference
The system SHALL support via AT+CHLD commands:
- `AT+CHLD=1x` - Release call x
- `AT+CHLD=2` - Hold active, answer waiting
- `AT+CHLD=3` - Conference (merge calls)

### FR-7: Call Waiting
The system SHALL handle call waiting:
- Detect via `+CCWA` unsolicited response
- Notify Asterisk via control frame
- Allow user to accept/reject via CLI

### FR-8: Bridge Loop Detection
The system SHALL detect and prevent:
- Bridging two channels on same device
- Audio feedback loops
- Set `CALL_FLAG_BRIDGE_LOOP` when detected

### FR-9: Multi-Party Calls
The system SHALL support conference calls:
- Track via `CALL_FLAG_MULTIPARTY`
- Mix audio from multiple calls
- Manage via AT+CHLD=3 (conference command)

## Non-Functional Requirements

### NFR-1: Performance
- Channel creation SHALL complete within 100ms
- State transitions SHALL be atomic
- Audio latency SHALL be < 150ms

### NFR-2: Reliability
- Call state SHALL persist across operations
- Hangup SHALL release all resources
- Failed calls SHALL transition to RELEASED

### NFR-3: Concurrency
- Maximum 32 concurrent call indices per device
- Multiple devices SHALL operate independently
- Channel locking SHALL prevent race conditions

### NFR-4: Resource Management
- Channel structure SHALL be freed on hangup
- Audio FDs SHALL be closed on release
- Call index SHALL be returned to pool

## Dependencies

- AT Command Protocol: Dial, hangup, hold commands
- Device Communication: Audio streaming
- CLI Module: Call status display

## Constraints

- Call indices limited to 0-31
- One master channel per device (owns audio FD)
- Conference limited by device capability

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of channel.c (1571 lines), cpvt.h, channel.h
