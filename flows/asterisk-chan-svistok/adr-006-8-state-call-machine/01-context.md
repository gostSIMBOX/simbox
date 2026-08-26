# ADR-006: 8-State Call Machine

## Status
DRAFT

## Type
Enabling

## Context
The chan_dongle driver needs to manage call lifecycle for voice calls via Huawei UMTS dongles. The call state machine must track call progress from initiation to termination and support features like hold, conference, and call waiting.

### Requirements
- Track call progress (dialing, alerting, active, held)
- Support incoming and outgoing calls
- Handle call waiting during active call
- Support hold and conference operations
- Integrate with Asterisk channel states
- Map device CLCC (current calls list) responses to internal states

### Constraints
- Huawei devices report call states via AT+CLCC command
- CLCC provides limited state set (active, held, dialing, alerting, incoming, waiting)
- Must map to Asterisk channel states
- Must support pseudo-states for internal tracking

## Decision
Use **8-state call machine** with direct CLCC mapping plus internal pseudo-states.

### States
1. **ACTIVE** - Active call (from CLCC)
2. **ONHOLD** - Held call (from CLCC)
3. **DIALING** - Dialing outbound (from CLCC)
4. **ALERTING** - Remote ringing (from CLCC)
5. **INCOMING** - Incoming call (from CLCC)
6. **WAITING** - Call waiting (from CLCC)
7. **RELEASED** - Call terminated (internal)
8. **INIT** - Call being initialized (internal)

## Consequences

### Positive
- **Direct CLCC mapping**: 6 states map directly to device states
- **Complete lifecycle**: INIT and RELEASED cover internal transitions
- **Feature support**: States support hold, conference, call waiting
- **Asterisk integration**: Maps to Asterisk channel states

### Negative
- **State complexity**: 8 states increase state machine complexity
- **Transition logic**: Many possible transitions to handle
- **CLCC polling**: Must poll CLCC to detect state changes

### Technical Impact
- State tracking per call (cpvt->state)
- State transition notifications to Asterisk
- CLCC response parsing and state updates
- State-dependent command enablement

## Alternatives Considered

### Simplified 4-State Machine
- States: IDLE, DIALING, ACTIVE, RELEASED
- **Rejected**: Cannot represent hold, waiting, incoming properly

### Asterisk State Machine Only
- Rely on Asterisk channel states
- **Rejected**: Need internal states for device-specific handling

## Related Decisions
- AT command queue architecture (ADR-001)
- PDU mode for SMS (ADR-002)

## References
- `cpvt.h` - Call state enumeration
- `channel.c` - State transition logic
- `at_command.c` - CLCC parsing
