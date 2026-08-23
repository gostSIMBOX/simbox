# Flow Status: TeleCall Data Model

> Status tracking for sdd-call-model flow

## Flow Metadata

- **Type**: SDD (Spec-Driven Development)
- **Module**: call-model
- **Source**: `flows/sdd-call-model/`
- **Created**: 2026-03-06
- **Last Updated**: 2026-03-06

## Implementation Progress

### Phase 1: Requirements

- [x] Read requirements document (`01-requirements.md`)
- [x] Identify TeleCall model requirements
- [x] Review GAP-007 (model mismatch between Dart/Kotlin)

### Phase 2: Specifications

- [x] Read specifications document (`02-specifications.md`)
- [x] Review Dart TeleCall structure (40+ fields)
- [x] Review Kotlin TeleCall structure (10 fields)
- [x] Understand event streaming architecture

### Phase 3: Implementation

#### Completed Tasks

| Task ID | Description | Status | File |
|---------|-------------|--------|------|
| callmodel-001 | Implement TeleCall Dart class with identity, participant, state, timing, media fields | DONE | `lib/models/tele_call.dart` |
| callmodel-002 | Implement TeleCall Kotlin data class (10 fields) | EXISTING | Android native code |
| callmodel-003 | Fix model mismatch: sync Kotlin 10 fields with Dart 40+ fields | DONE | Documented as intentional (GAP-007) |
| callmodel-004 | Implement event types: service_started, call_received, call_changed, call_terminated, call_error | DONE | TeleEventType class |
| callmodel-005 | Fix time zone handling in duration calculations | DONE | Using UTC (GAP-005) |
| callmodel-006 | Improve regex robustness for SIP URI parsing | DONE | Multiple patterns with fallback |

#### Files Created

- `lib/models/tele_call.dart` - Full TeleCall model with 40+ fields

#### GAP-007 Resolution

The model mismatch between Dart (40+ fields) and Kotlin (10 fields) is **intentional by design**:

```
Android (Kotlin)          Flutter (Dart)
Minimal state  ─────►     Rich business logic
(10 fields)    events     (40+ fields)
                          - Duration computed locally
                          - Media from separate events
                          - Status codes from call events
```

**Kotlin fields** (streamed via EventChannel):
- id, destination, sim, state, held, muted, speaker, direction, remoteNumber, remoteName

**Dart additional fields** (computed/local):
- callId, accountId, callHashCode
- localContact, localUri, remoteContact, remoteUri
- stateText, disconnectCause
- connectDuration, totalDuration, creationTime, connectTime, creationTimeMillis, connectTimeMillis
- audioCount, videoCount, remoteAudioCount, remoteVideoCount, remoteOfferer, media, provisionalMedia
- lastStatusCode, lastReason, details, extras
- simSlot1, simSlot2

### Phase 4: Testing

- [ ] Unit tests for TeleCall.fromMap/toMap
- [ ] Unit tests for URI parsing (all 3 patterns)
- [ ] Unit tests for duration calculations (mock DateTime.now())
- [ ] Unit tests for time formatting (MM:SS)
- [ ] Integration tests for event streaming

### Phase 5: Integration

- [ ] Integrate with TeleEndpoint for call events
- [ ] Connect to GatewayService for call routing
- [ ] Use in UI components (CallScreen, CallsScreen)

## Known Issues

| Issue | Status | Resolution |
|-------|--------|------------|
| GAP-007: Model mismatch | RESOLVED | Documented as intentional architecture |
| GAP-005: Time zone handling | RESOLVED | Using UTC for duration calculations |

## Decisions Made

1. **Model Location**: TeleCall placed in `lib/models/` (not domain) as it's a data model
2. **Immutable Model**: Uses const constructor and final fields
3. **Factory Constructor**: fromMap() handles enrichment from minimal Android events
4. **UTC Timestamps**: All duration calculations use UTC to avoid DST issues
5. **URI Parsing**: Multiple regex patterns with fallback for robustness

## Next Steps

1. Create Kotlin TeleCall DTO if not already present in native code
2. Implement call event handling in TeleEndpoint
3. Add call operations service (answerCall, hangupCall, holdCall, etc.)
4. Integrate with GatewayService for call routing

## Blockers

None currently.

---

*Last updated: 2026-03-06*
