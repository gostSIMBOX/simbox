# ADR-002: PDU Mode for SMS

## Status
DRAFT

## Type
Constraining

## Context
The chan_dongle driver needs to send and receive SMS messages via Huawei UMTS dongles. There are two modes for SMS handling:

1. **Text Mode** (`AT+CMGF=1`): Human-readable format, simpler but limited
2. **PDU Mode** (`AT+CMGF=0`): Binary Protocol Data Unit format, more complex but feature-complete

### Requirements
- Support for international characters (Unicode/UCS-2)
- Delivery report support
- SMS concatenation (long messages)
- Service center address handling
- Sender number format detection (international/national)

### Constraints
- Huawei dongles support both modes
- Text mode has limited character set support
- PDU mode is the GSM standard format

## Decision
Use **PDU Mode** for all SMS operations.

### Rationale
1. **International character support**: PDU mode with UCS-2 encoding supports all Unicode characters
2. **Feature completeness**: Delivery reports, validity periods, and status reports only available in PDU mode
3. **Standard compliance**: PDU mode is the GSM 03.40 standard
4. **Carrier compatibility**: Some carriers require PDU mode for certain features

## Consequences

### Positive
- Full Unicode support for international messages
- Delivery report capability
- Validity period configuration
- Standard compliance ensures carrier compatibility
- Consistent behavior across different dongles

### Negative
- Increased complexity in implementation
- PDU building requires bit-level manipulation
- Character encoding conversion required (UTF-8 ↔ UCS-2)
- Debugging more difficult (binary format)

### Technical Impact
- Requires PDU builder/parser (~200 lines of code)
- Requires character encoding conversion layer
- SMS limited to 140 octets (160 7-bit chars or 70 UCS-2 chars)
- Two-stage send process (command + PDU data)

## Alternatives Considered

### Text Mode
- **Pros**: Simpler implementation, human-readable
- **Cons**: Limited character set, no delivery reports, not all carriers support

### Hybrid Approach
- Use text mode for simple ASCII messages, PDU for Unicode
- **Rejected**: Adds complexity, inconsistent behavior

## Related Decisions
- AT command queue architecture (ADR-001)
- File-based state persistence (ADR-003)

## References
- `pdu.c/h` - PDU building and parsing
- `char_conv.c/h` - Character encoding conversion
- `at_command.c` - SMS enqueue functions
- GSM 03.40 specification

## Notes
Current implementation uses `AT+CMGF=0` (PDU mode) set during initialization. The `pvt->use_pdu` flag controls SMS sending path.
