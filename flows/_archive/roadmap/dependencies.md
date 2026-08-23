# Roadmap Dependencies Graph

## Overview

Full dependency graph. Critical path highlighted for DFS execution.

## Current Goal

**MVP (auto-detected)**: Core gateway functionality - SIP↔GSM bidirectional calling working

## Dependency Graph

```
Legend:
  ════  Critical path (will be executed)
  ────  Other dependencies (skipped)
  ●     Complete
  ◐     In progress
  ○     Pending
  ∅     Skipped

[sdd-core-architecture] ══════> [sdd-sip-core] ══════> [sdd-gateway-service] ══════> [MVP]
         │                           │                        │
         │                           │                        │
    [sdd-telephony] ─────────────────┘                        │
         │                                                    │
    [sdd-sms-smpp] ───────────────────────────────────────────┘
         │
    [ddd-001-voip-calling] ─ (stakeholder docs, not on path)
```

## Critical Path (DFS Order)

| Order | Flow | Type | Status | Blocks |
|-------|------|------|--------|--------|
| 1 | sdd-core-architecture | SDD | ◐ SPEC complete | sdd-sip-core, sdd-gateway-service |
| 2 | sdd-sip-core | SDD | ○ REQ complete | sdd-gateway-service |
| 3 | sdd-gateway-service | SDD | ○ REQ complete | MVP |

## All Flows

### On Critical Path

| Flow | Type | Phase | Status | Blocked By |
|------|------|-------|--------|------------|
| sdd-core-architecture | SDD | SPEC complete | Needs PLAN approval | - |
| sdd-sip-core | SDD | SPEC complete | Needs PLAN approval | sdd-core-architecture |
| sdd-gateway-service | SDD | SPEC complete | Needs PLAN approval | sdd-sip-core, sdd-telephony |

### Not on Path (Skipped)

| Flow | Type | Why Skipped |
|------|------|-------------|
| sdd-account | SDD | Not required for MVP (auth can be hardcoded) |
| sdd-dialer | SDD | Not required for core routing |
| sdd-ui-theming | SDD | UI exists, not on critical path |
| sdd-monitoring | SDD | Observability, not required for MVP |
| sdd-event-streaming | SDD | Enhancement, not core routing |
| sdd-android-plugin | SDD | Build concern, not runtime |
| sdd-build-system | SDD | Build concern, not runtime |
| sdd-patch-management | SDD | Deployment concern |
| sdd-release-workflow | SDD | Deployment concern |
| ddd-001-voip-calling | DDD | Documentation, not implementation |
| tdd-testing | TDD | Testing infrastructure, not runtime |
| All other sdd-* flows | SDD | Not on critical path to MVP |

## ADRs (Read-only context)

| ADR | Type | Status | Affects Critical Path |
|-----|------|--------|----------------------|
| ADR-001 (clean-architecture) | constraining | DRAFT | YES - defines 4-layer architecture |
| ADR-002 (dependency-injection) | enabling | DRAFT | YES - DI for service registration |
| ADR-003 (state-management) | enabling | DRAFT | YES - Provider for state |
| ADR-004 (error-handling) | enabling | DRAFT | YES - centralized errors |
| ADR-005 (service-orchestration) | constraining | DRAFT | YES - GatewayService design |
| ADR-001 (service-architecture) | enabling | DRAFT | YES - Android intents for SIP |
| ADR-002 (event-channel) | enabling | DRAFT | YES - event streaming |
| ADR-003 (json-serialization) | enabling | DRAFT | YES - Intent extras |
| ADR-004 (callback-pattern) | enabling | DRAFT | YES - async tracking |
| ADR-005 (immutable-models) | enabling | DRAFT | YES - data models |
| ADR-006 (duration-calculation) | enabling | DRAFT | NO - call duration feature |
| All React Native ADRs | various | DRAFT | NO - different codebase |

## Dependency Details

### sdd-core-architecture

**On critical path:** YES (position 1)

**Blocked by:**
- None (foundational)

**Blocks:**
- sdd-sip-core: needs architecture for SIP service structure
- sdd-gateway-service: needs architecture for orchestration pattern
- sdd-telephony: needs architecture for telephony service

**Related ADRs:**
- ADR-001 (clean-architecture): Defines 4-layer structure
- ADR-002 (dependency-injection): get_it for DI
- ADR-003 (state-management): Provider pattern
- ADR-004 (error-handling): ErrorHandler design

**Current Status:**
- Requirements: ✓ Approved
- Specifications: ✓ Draft complete
- Plan: ⏳ Needs to be drafted
- Implementation: ⏳ Pending

### sdd-sip-core

**On critical path:** YES (position 2)

**Blocked by:**
- sdd-core-architecture: needs service layer definition

**Blocks:**
- sdd-gateway-service: needs SIP service to orchestrate

**Related ADRs:**
- ADR-001 (service-architecture): SIP via Android intents
- ADR-002 (event-channel): Event streaming from SIP
- ADR-003 (json-serialization): Intent extras
- ADR-004 (callback-pattern): Async operation tracking
- ADR-005 (immutable-models): SIP data models

**Current Status:**
- Requirements: ✓ Draft complete
- Specifications: ✓ Draft complete
- Plan: ⏳ Needs to be drafted
- Implementation: ⏳ Pending

### sdd-gateway-service

**On critical path:** YES (position 3)

**Blocked by:**
- sdd-core-architecture: needs orchestration pattern
- sdd-sip-core: needs SIP service interface
- sdd-telephony: needs telephony service interface

**Blocks:**
- MVP: this is the final piece

**Related ADRs:**
- ADR-005 (service-orchestration): GatewayService as orchestrator
- ADR-002 (dual-endpoint-strategy): PJSIP vs Android Telecom

**Current Status:**
- Requirements: ✓ Draft complete
- Specifications: ⏳ Needs to be drafted
- Plan: ⏳ Pending
- Implementation: ⏳ Pending

---

*Auto-generated by /roadmap. Manual edits will be overwritten.*

**Last Updated:** 2026-03-05
**Next Action:** Complete plan for sdd-core-architecture
