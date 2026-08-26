# 01-Requirements

## Overview

State Persistence layer providing file-based key-value storage for device state, configuration, and statistics.

## Functional Requirements

### FR-1: File-Based Storage
The system SHALL store data in files:
- Base path: `/var/svistok/`
- Format: `{devtype}/{fileitem}.{filetype}`
- Example: `/var/svistok/imsi/250000000.balance`

### FR-2: Integer Value Operations
The system SHALL support integer operations:
- `getfilei()` - Read integer from file
- `putfilei()` - Write integer to file
- Automatic file creation on write

### FR-3: String Value Operations
The system SHALL support string operations:
- `getfiles()` - Read string from file
- `putfiles()` - Write string to file
- Automatic file creation on write

### FR-4: Device Info Persistence
The system SHALL persist device information:
- IMSI, IMEI, model, firmware
- Provider name, balance
- Signal quality (RSSI)
- Location area code, cell ID

### FR-5: Device Limits Persistence
The system SHALL persist device limits:
- Call limits per device
- Balance thresholds
- Rate limits

### FR-6: Device State Persistence
The system SHALL persist device state:
- Current call state
- AT queue state
- Initialization state

### FR-7: Device Error Persistence
The system SHALL persist error information:
- Error counters
- Last error type
- Last error timestamp

### FR-8: Mutex Protection
The system SHALL protect access with mutexes:
- Per-device locking
- Debug info for lock tracking
- Try-lock with timeout

## Non-Functional Requirements

### NFR-1: Performance
- File read SHALL complete within 10ms
- File write SHALL complete within 10ms
- Mutex operations SHALL complete within 1ms

### NFR-2: Reliability
- File write errors SHALL be logged
- Corrupt files SHALL be handled gracefully
- Missing files SHALL return default values

### NFR-3: Durability
- Writes SHALL be flushed to disk
- Partial writes SHALL not corrupt data
- Power failure recovery via file check

### NFR-4: Concurrency
- Multiple readers SHALL be allowed
- Writers SHALL have exclusive access
- Deadlock prevention via lock ordering

## Dependencies

- None (core infrastructure layer)

## Constraints

- File paths limited to 256 characters
- Integer values stored as text
- No transaction support

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of share.c, share_mysql.c (590 lines), share.h
