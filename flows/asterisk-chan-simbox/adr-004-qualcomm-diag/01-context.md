# ADR-004: Qualcomm DIAG Protocol for Firmware Flashing

## Status
DRAFT

## Type
Enabling

## Context
The chan_dongle driver needs to support firmware updates for Huawei UMTS dongles. These devices use Qualcomm chipsets that support a proprietary diagnostic protocol.

### Requirements
- Firmware update capability
- Device recovery (unbricking)
- IMEI modification (where legal)
- Device-specific programming

### Constraints
- Huawei devices use Qualcomm chipsets
- Qualcomm provides DIAG (diagnostic) mode for service operations
- Protocol is proprietary but documented through reverse engineering
- Must work over standard serial interface

## Decision
Use **Qualcomm DIAG protocol** for firmware flashing operations.

### Protocol Overview
1. Enter diagnostic mode via `AT$QCDMG` command
2. Enable diagnostic logging via `AT^DISLOG=255`
3. Switch to HDLC-framed binary communication
4. Transfer firmware in binary format
5. Restart device

### Entry Sequence
```
>> AT$QCDMG
<< $QCDMG
<< OK

>> AT^DISLOG=255
<< [HDLC response]
```

## Consequences

### Positive
- **Official support**: DIAG mode is built into Qualcomm chipsets
- **Full access**: Complete control over device programming
- **Recovery**: Can recover bricked devices
- **Flexibility**: Supports custom firmware

### Negative
- **Proprietary protocol**: Not officially documented
- **Risk**: Incorrect use can brick device
- **Legal concerns**: IMEI modification illegal in some jurisdictions
- **Complexity**: HDLC framing, CRC calculation

### Technical Impact
- ~300 lines of protocol implementation
- HDLC frame building and parsing
- Binary file transfer
- State persistence during flash
- 25-second wait for mode switch

## Alternatives Considered

### Standard AT Commands
- **Pros**: Safer, documented
- **Cons**: Limited to standard operations, no firmware flash

### Bootloader Mode
- **Pros**: Lower level access
- **Cons**: Requires hardware modification, riskier

### OEM Tools
- **Pros**: Official support
- **Cons**: Not available for all devices, Windows-only

## Related Decisions
- 115200 baud serial communication (ADR-005)
- File-based state persistence (ADR-003)

## References
- `ttyprog_core.c` - DIAG protocol implementation
- `ttyprog_programmator.c` - Firmware transfer
- `ttyprog_svistok.c` - Asterisk integration

## Notes
IMEI modification may be illegal in your jurisdiction. Use responsibly and only for legitimate purposes (device repair, testing).
