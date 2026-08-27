# 01-Requirements

## Overview

AT Command Protocol for Huawei UMTS dongle communication in Asterisk channel driver.

## Functional Requirements

### FR-1: Command Enumeration
The system SHALL support 60+ AT commands including:
- Basic commands: AT, ATE, ATZ
- Device info: AT+CGMI, AT+CGMM, AT+CGMR, AT+CGSN (IMEI)
- SIM operations: AT+CPIN?, AT+CIMI (IMSI), AT^ICCID?, AT^SN
- Network registration: AT+CREG, AT+COPS
- Call control: ATD, ATA, AT+CHUP, AT+CHLD
- SMS: AT+CMGF, AT+CMGS, AT+CMGR, AT+CMGD
- USSD: AT+CUSD
- Signal quality: AT+CSQ, AT^CSNR?
- Device specific: AT^DDSETEX, AT^U2DIAG, AT^CARDLOCK

### FR-2: Response Parsing
The system SHALL parse and match responses including:
- Standard responses: OK, ERROR, NO CARRIER, BUSY, RING
- Data responses: +CMGR, +COPS, +CREG, +CSQ
- Unsolicited responses: +CMTI (SMS), +CUSD (USSD), +CCWA (call waiting)
- Device specific: ^SYSINFO, ^FREQLOCK

### FR-3: Command Queue Management
The system SHALL manage command execution via a queue with:
- Task-based grouping (multiple commands per task)
- Priority insertion (head/tail)
- Sequential execution within tasks
- Response matching per command

### FR-4: Timeout Handling
The system SHALL enforce timeouts per command:
- 1 second: Basic commands
- 2 seconds: Standard commands (default)
- 5 seconds: Network queries
- 10 seconds: SIM operations
- 15 seconds: Complex operations
- 40 seconds: SMS send (user input time)

### FR-5: Initialization Sequences
The system SHALL execute initialization in two phases:
1. **Modem Init**: Device identification, firmware version, IMEI
2. **SIM Init**: SIM identification, operator, registration, SMS setup

### FR-6: Device-Specific Handling
The system SHALL support device variants:
- Standard devices: Full initialization sequence
- MULTIBAND devices: Simplified initialization sequence

### FR-7: User Command Execution
The system SHALL allow raw AT command execution via CLI with:
- Command string validation
- Response capture and display
- Error reporting

## Non-Functional Requirements

### NFR-1: Performance
- Command queue operations SHALL complete within 10ms
- Response parsing SHALL handle 115200 baud data rate
- Queue SHALL support minimum 100 pending commands

### NFR-2: Reliability
- Command timeout SHALL trigger retry or error handling
- Queue overflow SHALL be prevented via bounded capacity
- Response mismatch SHALL be logged and handled gracefully

### NFR-3: Memory Management
- Static commands SHALL not be deallocated
- Dynamic commands SHALL be freed after execution
- Task structures SHALL be freed when all commands complete

### NFR-4: Debugging
- All commands SHALL be logged with string representation
- Response mismatches SHALL include expected vs actual
- Queue state SHALL be queryable via CLI

## Dependencies

- Device Communication Layer: Serial/TTY interface
- Channel Driver: Call state integration
- CLI Module: User command interface

## Constraints

- AT commands limited to 4096 bytes (buffer size)
- SMS PDU limited to 140 octets
- Maximum 32 concurrent call indices

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of at_command.c, at_response.c, at_queue.c
