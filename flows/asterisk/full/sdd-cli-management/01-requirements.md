# 01-Requirements

## Overview

CLI (Command Line Interface) management for Asterisk CLI providing device control and monitoring.

## Functional Requirements

### FR-1: Device Listing Commands
The system SHALL provide commands to list devices:
- `dongle show devices` - List all devices with status
- `dongle show devicesl` - List with limits info
- `dongle show devicesd` - Detailed device list
- `dongle show devicesi` - Info list

### FR-2: Device Status Commands
The system SHALL provide commands to show device details:
- `dongle show device settings <device>` - Show configuration
- `dongle show device state <device>` - Show current state
- `dongle show device statistics <device>` - Show statistics

### FR-3: System Commands
The system SHALL provide system-level commands:
- `dongle show version` - Show driver version

### FR-4: Device Control Commands
The system SHALL provide device control:
- `dongle start <device>` - Start device
- `dongle reset <device>` - Reset device
- `dongle reload` - Reload configuration
- `dongle discovery` - Device discovery

### FR-5: Communication Commands
The system SHALL provide communication commands:
- `dongle sms <device> <number> <message>` - Send SMS
- `dongle ussd <device> <code>` - Send USSD
- `dongle pdu <device> <pdu>` - Send raw PDU
- `dongle cmd <device> <at_command>` - Execute raw AT command

### FR-6: Configuration Commands
The system SHALL provide configuration commands:
- `dongle setgroup <device> <group>` - Set device group
- `dongle setgroupimsi <imsi> <group>` - Set group by IMSI
- `dongle callwaiting <device>` - Toggle call waiting

### FR-7: Advanced Commands
The system SHALL provide advanced commands:
- `dongle diagmode <device>` - Enter diagnostic mode
- `dongle changeimei <device> <imei>` - Change IMEI
- `dongle update <device>` - Firmware update

### FR-8: Tab Completion
The system SHALL provide tab completion for:
- Device names in all commands requiring device parameter
- Command keywords

## Non-Functional Requirements

### NFR-1: Performance
- Command execution SHALL complete within 1 second
- Device listing SHALL handle 100+ devices
- Output SHALL be formatted for readability

### NFR-2: Reliability
- Invalid commands SHALL return usage help
- Device not found SHALL return error message
- Command errors SHALL be logged

### NFR-3: Security
- IMEI change SHALL require appropriate permissions
- Firmware update SHALL validate file integrity
- Device locking SHALL prevent concurrent modifications

### NFR-4: Usability
- Help text SHALL be available for all commands
- Error messages SHALL be descriptive
- Output SHALL be consistent across commands

## Dependencies

- AT Command Protocol: Raw command execution
- Device Communication: Device access
- State Persistence: Configuration storage

## Constraints

- CLI commands limited to Asterisk CLI interface
- Some commands require device to be in specific state
- Firmware update requires diagnostic mode

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of cli.c (1643 lines), cli.h
