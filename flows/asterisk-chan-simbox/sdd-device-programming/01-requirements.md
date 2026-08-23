# 01-Requirements

## Overview

Device Programming for firmware flashing of Huawei UMTS dongles via Qualcomm diagnostic mode.

## Functional Requirements

### FR-1: Diagnostic Mode Entry
The system SHALL enter Qualcomm diagnostic mode via:
- `AT$QCDMG` command to enter diagnostic mode
- `AT^DISLOG=255` to enable diagnostic logging
- Response verification (`$QCDMG...OK`)

### FR-2: Firmware File Transfer
The system SHALL transfer firmware files:
- Binary file reading
- HDLC-framed transmission
- Progress tracking during transfer
- Error detection and retry

### FR-3: Programming Sequence
The system SHALL execute programming sequence:
1. Open TTY port
2. Enter diagnostic mode
3. Wait for mode switch (25 seconds)
4. Send firmware file
5. Restart device
6. Close port

### FR-4: State Persistence
The system SHALL persist programming state:
- State file: `/var/simnode/{device}.state`
- Progress file: `/var/simnode/{device}.progress`
- States: `init` → `diag` → `wait` → `update` → `done`
- Progress: 0 → 1 → 10 → 20 → 100 (percentage)

### FR-5: Protocol Commands
The system SHALL support diagnostic protocol commands:
- Enter diagnostic mode (`AT$QCDMG`)
- Query firmware version
- Query device model
- Enter programming mode
- Write firmware data

### FR-6: HDLC Framing
The system SHALL use HDLC framing:
- Frame delimiter: 0x7E
- Binary command/response sequences
- Checksum/CRC for error detection

### FR-7: Logging
The system SHALL log programming operations:
- Timestamp for each operation
- Command and response logging
- Progress updates
- Error messages

### FR-8: Error Recovery
The system SHALL handle errors:
- Timeout detection
- Retry failed operations
- Rollback on critical failure
- State reporting on error

## Non-Functional Requirements

### NFR-1: Performance
- Diagnostic mode entry SHALL complete within 5 seconds
- Firmware transfer rate SHALL be maximum possible via serial
- Total programming time SHALL be under 5 minutes

### NFR-2: Reliability
- Firmware file SHALL be validated before transfer
- Transfer errors SHALL trigger retry
- Power failure SHALL not brick device (bootloader recovery)

### NFR-3: Safety
- Wrong firmware SHALL be prevented via model check
- Interrupted flash SHALL leave device recoverable
- IMEI changes SHALL comply with local regulations

### NFR-4: Compatibility
- Huawei E1550, E155X, E175X, K3715, K3765 support
- Qualcomm chipset diagnostic protocol
- Linux and FreeBSD support

## Dependencies

- Device Communication: Serial port access
- TTY Layer: Low-level serial operations

## Constraints

- Device must be in diagnostic mode for programming
- Firmware file must match device model
- Serial port must be exclusively locked

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of ttyprog_core.c (305 lines), ttyprog_programmator.c, ttyprog_svistok.c
