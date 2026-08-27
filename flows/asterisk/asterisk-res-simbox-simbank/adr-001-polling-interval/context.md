# ADR-001: Polling Interval for SIM-Bank Monitoring

**Date**: 2026-03-04  
**Status**: Accepted  
**Type**: Constraining  
**Source**: Legacy analysis via `/legacy` command

---

## Context

The SIM-bank management system needs to monitor the state of multiple SIM-banks (SMB128/SMB32 devices) to track slot status, signal strength, and SIM card information. The system must balance between having up-to-date information and not overwhelming the hardware devices with requests.

Key requirements:
- Monitor multiple SIM-banks concurrently
- Track slot status changes (online/offline/error/busy)
- Update signal strength and SIM card metadata
- Avoid overloading hardware devices
- Support graceful degradation under load

---

## Decision

**Use 30-second polling interval for all SIM-bank status updates.**

The system will query each SIM-bank's HTTP API every 30 seconds to retrieve current status of all slots. Each bank is polled concurrently in separate goroutines to ensure scalability.

Implementation details:
```go
// From simbank/manager.go
func (m *Manager) monitorLoop() {
    ticker := time.NewTicker(m.config.PollingInterval) // default: 30s
    defer ticker.Stop()
    
    for {
        select {
        case <-m.ctx.Done():
            return
        case <-ticker.C:
            m.updateAllSimBanks() // Concurrent updates
        }
    }
}
```

Configuration:
- Default: `30s`
- Configurable via: `simbank.polling_interval` in config.yaml
- Environment override: `SIMHUB_SIMBANK_POLLING_INTERVAL`

---

## Consequences

### Positive

1. **Predictable load**: Hardware devices receive exactly one request every 30 seconds, regardless of the number of slots
2. **Simple implementation**: Time-based polling is straightforward to understand, implement, and debug
3. **Backpressure built-in**: If an update takes longer than 30s, the next tick is automatically skipped (ticker behavior)
4. **Configurable**: Can be tuned per deployment based on hardware capabilities
5. **Concurrent execution**: Each bank is polled independently, allowing the system to scale with the number of banks

### Negative

1. **Eventual consistency**: State changes may take up to 30 seconds to be reflected in the system
2. **Missed transient events**: Short-lived events (e.g., a slot that goes offline and back online within 30s) may be missed
3. **Fixed overhead**: Even with no changes, the system continues polling at 30s intervals
4. **Not real-time**: Unsuitable for use cases requiring immediate notification of state changes

### Trade-offs

| Alternative | Pros | Cons | Why Not Chosen |
|-------------|------|------|----------------|
| **Shorter interval (e.g., 5s)** | More responsive, catch transient events | Higher load on devices, may cause device timeouts | Hardware limitations, diminishing returns |
| **Longer interval (e.g., 60s)** | Lower load, less network traffic | Slower reaction to failures, stale data | 30s provides better balance |
| **Push-based (webhooks)** | Real-time updates, no polling overhead | Requires hardware support, complex implementation | SMB128/SMB32 don't support push notifications |
| **Adaptive polling** | Dynamic adjustment based on activity | Implementation complexity, unpredictable behavior | Simplicity preferred for initial implementation |

---

## Compliance

### Requirements Met
- REQ-POLL-001: Periodic polling with configurable interval
- REQ-POLL-002: Concurrent updates for all banks
- REQ-NF-PERF-001: Configurable polling interval

### Related SDDs
- `flows/sdd-simbank-management/01-requirements.md` - Section 2.3 Polling & Monitoring
- `flows/sdd-simbank-management/02-specifications.md` - Section 2.3 Polling Configuration

---

## Notes

**Legacy Analysis Addition (2026-03-04)**:  
This ADR was reverse-engineered from existing code during `/legacy` BFS analysis. The 30s interval is hardcoded as a default but is properly configurable via the `SimBankConfig.PollingInterval` field.

**Observed Behavior**:  
- Polling runs in a dedicated goroutine with `time.Ticker`
- Each SIM-bank is updated in a separate goroutine (via `updateAllSimBanks()`)
- Uses `sync.WaitGroup` to wait for all updates to complete
- Context-based cancellation for graceful shutdown

---

*Generated via /legacy analysis on 2026-03-04*
