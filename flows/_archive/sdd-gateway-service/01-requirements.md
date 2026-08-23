# Requirements: Gateway Service

## Overview

The Gateway Service is the core orchestration component that provides bidirectional routing between GSM telephony and SIP/SMPP protocols.

## Functional Requirements

### FR-1: Service Orchestration

The Gateway Service SHALL coordinate the lifecycle of sub-services:

| Service | Purpose | Initialization Order |
|---------|---------|---------------------|
| TelephonyService | GSM call/SMS handling | 1st (foundation) |
| SipService | SIP protocol handling | 2nd |
| SmsService | SMPP protocol handling | 3rd (optional) |

### FR-2: Bidirectional Call Routing

The system SHALL support bidirectional call routing:

**SIP→GSM Routing:**
- Initiate SIP call from SIP network
- Automatically create corresponding GSM call
- Synchronize call states between protocols
- Handle call termination on both sides

**GSM→SIP Routing:**
- Detect incoming GSM calls
- Automatically create corresponding SIP call
- Support auto-answer for GSM calls (configurable)
- Synchronize call states between protocols

### FR-3: SMS Routing

The system SHALL support SMS routing:

- Local SMS sending via GSM telephony
- SMPP SMS sending (when configured)
- Message counting and statistics

### FR-4: Configuration Management

The system SHALL provide persistent configuration:

- GatewayConfig with routing options
- Save/load via SharedPreferences
- JSON serialization support
- Default values for optional settings

### FR-5: State Management

The system SHALL provide real-time state updates:

| Stream | Purpose |
|--------|---------|
| statusStream | GatewayStatus updates |
| routingStream | CallRouting updates |
| logStream | Service log messages |

### FR-6: Statistics Tracking

The system SHALL track operational statistics:

- Active calls count
- Total calls handled (lifetime)
- Total messages handled (lifetime)
- Start time and uptime calculation

## Non-Functional Requirements

### NFR-1: Reliability

- Service initialization SHALL fail gracefully if any sub-service fails
- Call routing SHALL handle errors without crashing
- Configuration load failures SHALL not prevent startup

### NFR-2: Performance

- Call routing SHALL initiate within 500ms
- State updates SHALL be broadcast within 100ms
- Configuration save/load SHALL complete within 200ms

### NFR-3: Resource Management

- All StreamControllers SHALL be properly closed on dispose
- Service instances SHALL be properly disposed
- Memory SHALL be released for ended routings

### NFR-4: Observability

- All operations SHALL be logged with timestamps
- Log streaming SHALL be toggleable via configuration
- Call state changes SHALL be traceable

## Configuration Requirements

### Required Configuration

| Field | Type | Description |
|-------|------|-------------|
| sipAccount | SipAccount | SIP credentials and server |

### Optional Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| smppConfig | SmppConfig | null | SMPP connection settings |
| autoAnswer | bool | false | Auto-answer incoming GSM calls |
| enableLogging | bool | true | Enable log streaming |
| routeSipToGsm | bool | true | Enable SIP→GSM routing |
| routeGsmToSip | bool | true | Enable GSM→SIP routing |
| routeSmsToSmpp | bool | false | Enable SMS→SMPP routing |
| routeSmppToSms | bool | false | Enable SMPP→SMS routing |
| maxConcurrentCalls | int | 5 | Maximum concurrent calls |

## Call Routing Requirements

### CallRouting Entity

| Field | Type | Description |
|-------|------|-------------|
| id | String | Unique routing identifier |
| sipCallId | String | SIP call reference |
| telephonyCallId | String? | GSM call reference (if applicable) |
| number | String | Phone number |
| direction | CallRoutingDirection | Routing direction |
| state | CallRoutingState | Current routing state |
| startTime | DateTime | Routing initiation time |

### State Machine

```
connecting ──► active ──► ended
                      │
                      └──► failed
```

**Transitions:**
- `connecting → active`: Both SIP and GSM calls established
- `connecting → failed`: Call setup failed
- `active → ended`: Call terminated normally
- `active → failed`: Call terminated abnormally

---

**Status**: DRAFT  
**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)
