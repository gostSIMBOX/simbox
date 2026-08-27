# ADR-001: Polling Interval for SIM-Bank Monitoring

**Status**: Accepted  
**Date**: 2026-03-04  
**Type**: Technical Decision  
**Source**: `/legacy` reverse engineering

## Context

The SIM-Bank management system needs to monitor the status of multiple SIM-bank devices to keep the database state synchronized with physical device state.

We need to decide on the frequency of status polling to balance:
- Data freshness (operators need up-to-date information)
- System load (network traffic, database writes, CPU usage)
- Device load (SIM-bank hardware has limited capacity)

### Requirements

- Monitor multiple SIM-bank devices concurrently
- Track slot status (online/offline/error/busy, signal strength)
- Persist state to PostgreSQL database
- Support graceful degradation on device failures

### Constraints

- SIM-bank hardware has limited HTTP request handling capacity
- Network bandwidth may be limited in some deployments
- Database write operations have cost
- Operators need reasonably fresh data (not necessarily real-time)

## Decision

**Use 30-second polling interval as default**, with configuration option to adjust.

### Implementation

```go
// SimBankConfig
PollingInterval: 30 * time.Second  // Default
Timeout:         10 * time.Second  // HTTP timeout
RetryAttempts:   3                 // Retry on failure
RetryDelay:      5 * time.Second   // Between retries
```

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  SimBank Manager                         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              monitorLoop()                        │   │
│  │                   │                               │   │
│  │              ticker: 30s                          │   │
│  │                   │                               │   │
│  │                   ▼                               │   │
│  │         updateAllSimBanks()                       │   │
│  │         /          |          \                   │   │
│  │        ▼           ▼           ▼                  │   │
│  │   [goroutine] [goroutine] [goroutine]             │   │
│  │     Bank #1      Bank #2      Bank #N             │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ SIM-Bank │    │ SIM-Bank │    │ SIM-Bank │
    │   #1     │    │   #2     │    │   #N     │
    └──────────┘    └──────────┘    └──────────┘
```

### Rationale

**30 seconds was chosen because:**

1. **SIM card state changes infrequently**: Signal strength, status changes happen on the order of minutes, not seconds
2. **Operator expectations**: Human operators don't need sub-second updates for monitoring dashboards
3. **Resource efficiency**: 
   - 10 devices × 30s = 20 requests/minute total
   - 10 devices × 5s = 120 requests/minute (6× more load)
4. **Failure recovery**: If a poll fails, next attempt is only 30s away
5. **Configurable**: Deployments with different needs can adjust via `SIMHUB_SIMBANK_POLLING_INTERVAL`

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Real-time (push)** | Instant updates | Requires device firmware changes, WebSocket infrastructure | Too complex, hardware doesn't support |
| **5-second polling** | Very fresh data | High load, unnecessary for use case | Overkill for SIM monitoring |
| **60-second polling** | Minimal load | Data too stale for operations | 1 minute delay is noticeable |
| **Adaptive polling** | Optimizes load | Complex implementation, hard to debug | YAGNI for current requirements |

## Consequences

### Positive

- **Predictable load**: System capacity planning is straightforward
- **Simple implementation**: Ticker-based polling is well-understood pattern
- **Graceful degradation**: Failed polls don't cascade, next attempt succeeds
- **Configurable**: Different deployments can tune for their needs

### Negative

- **Data latency**: State can be up to 30 seconds out of date
- **Unnecessary polls**: Some polls may return unchanged data
- **No instant failure detection**: Device failures detected within 30s, not instantly

### Mitigation Strategies

1. **On-demand status**: API provides `GET /simbanks/:id/status` for real-time check when needed
2. **Event logging**: Errors are logged immediately, visible in monitoring
3. **Manual refresh**: Operators can trigger manual status check via API

## Compliance

**Compliant Flows**:
- `flows/sdd-simbank-management/02-specifications.md` - Polling loop specification
- `flows/sdd-config-management/01-requirements.md` - Configuration defaults

**Configuration**:
```bash
# Override default polling interval
export SIMHUB_SIMBANK_POLLING_INTERVAL=15s  # Faster polling
export SIMHUB_SIMBANK_POLLING_INTERVAL=60s  # Slower polling
```

## Notes

This decision can be revisited if:
- Hardware vendors provide push notification capabilities
- Operator requirements change (need faster detection)
- System scales to 100+ devices (may need adaptive approach)

---

*Generated by /legacy reverse engineering - DRAFT for review*
