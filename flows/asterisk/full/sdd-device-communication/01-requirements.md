# 01-Requirements

## Overview

Device Communication layer for serial/TTY communication with Huawei UMTS dongles.

## Functional Requirements

### FR-1: Serial Port Configuration
The system SHALL configure serial ports with:
- Baud rate: 115200
- Data bits: 8
- Stop bits: 1 (implicit)
- Parity: None (implicit)
- Flow control: Hardware (CRTSCTS)
- Mode: Raw (no input/output processing)

### FR-2: Device Opening
The system SHALL open devices with:
- Read/write access (O_RDWR)
- No controlling terminal (O_NOCTTY)
- Device locking to prevent concurrent access
- Error handling for unavailable devices

### FR-3: Device Locking
The system SHALL implement device locking via:
- PID file in `/var/lock/LOCK..{device}`
- Lock check before open
- Lock release on close
- Stale lock detection (process no longer exists)

### FR-4: Data Writing
The system SHALL write data with:
- Retry on EINTR/EAGAIN (max 10 retries)
- Full write guarantee (write_all)
- Error logging on failure
- Byte count tracking

### FR-5: Data Reading
The system SHALL read data with:
- Blocking read (VMIN=1, VTIME=0)
- ioctl(FIONREAD) to check available bytes
- Non-blocking when no data available
- Buffer management for partial reads

### FR-6: Ring Buffer
The system SHALL provide ring buffer for async data:
- Circular buffer with read/write positions
- Vector I/O support (iovec)
- Read until delimiter (for line protocols)
- Used/free tracking

### FR-7: I/O Multiplexing
The system SHALL support device selection:
- Multiple device monitoring
- Call routing decisions
- Statistics tracking per device

## Non-Functional Requirements

### NFR-1: Performance
- Serial configuration SHALL complete within 10ms
- Write operations SHALL handle 115200 baud throughput
- Ring buffer operations SHALL be O(1)

### NFR-2: Reliability
- Device locking SHALL prevent concurrent access
- Write retries SHALL handle temporary failures
- Stale locks SHALL be detected and cleared

### NFR-3: Portability
- Serial configuration SHALL work on Linux 2.6.33+
- Serial configuration SHALL work on FreeBSD 8.0+
- Lock file location SHALL be configurable

### NFR-4: Error Handling
- All system call errors SHALL be logged
- Device open failures SHALL return -1
- Write failures SHALL be reported to caller

## Dependencies

- AT Command Protocol: Data transport
- Channel Driver: Audio streaming

## Constraints

- Device names must be valid TTY paths (e.g., /dev/ttyUSB0)
- Lock files require /var/lock directory
- Maximum 10 retries on EINTR/EAGAIN

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of tty_v2.c (221 lines), ringbuffer.h, select.h
