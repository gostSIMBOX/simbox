# Layers Compilation Status

> Index of compiled layer documents. Auto-generated from compilation.

---

## Compilation Index

| Layer | Document | Status | Tasks | Modules | Last Compiled |
|-------|----------|--------|-------|---------|---------------|
| **Layer 0** | [layer-0.md](layer-0.md) | COMPILED | 31 | 6 | 2026-03-04 |
| **Layer 1** | [layer-1.md](layer-1.md) | COMPILED | 87 | 13 | 2026-03-04 |
| **Layer 2** | [layer-2.md](layer-2.md) | COMPILED | 61 | 10 | 2026-03-04 |

**Total Tasks:** 179

---

## Layer Summaries

### Layer 0: Shared Infrastructure

**Source flows:** 6
- sdd-core-architecture
- sdd-event-streaming
- sdd-monitoring
- sdd-build-system
- sdd-release-workflow
- sdd-patch-management

**Modules:**
1. core-architecture (6 tasks)
2. event-streaming (4 tasks)
3. monitoring (4 tasks)
4. build-system (6 tasks)
5. release-workflow (4 tasks)
6. patch-management (7 tasks)

**Dependencies:** None (base layer)

---

### Layer 1: Domain/Core Logic

**Source flows:** 19
- sdd-sip-core, sdd-sip, sdd-telephony, sdd-call, sdd-call-model
- sdd-account, sdd-endpoint, sdd-gateway-service
- sdd-headless-service, sdd-native-android-module, sdd-android-plugin
- sdd-unisim, sdd-activity-intents, sdd-foreground-management
- sdd-telephony-integration, sdd-endpoint-2, sdd-dialer
- sdd-android-telecom-integration, sdd-android-implementation-sms

**Modules:**
1. sip-core (6 tasks)
2. sip (5 tasks)
3. telephony (4 tasks)
4. call (6 tasks)
5. call-model (6 tasks)
6. account (5 tasks)
7. endpoint (8 tasks)
8. gateway-service (7 tasks)
9. headless-service (6 tasks)
10. native-android-module (4 tasks)
11. android-plugin (5 tasks)
12. unisim (6 tasks)
13. activity-intents (2 tasks)
14. foreground-management (2 tasks)
15. telephony-integration (2 tasks)
16. dialer (2 tasks)
17. android-telecom-integration (2 tasks)
18. android-implementation-sms (2 tasks)
19. endpoint-2 (1 task)

**Dependencies:** layer-0 (core-architecture, event-streaming)

---

### Layer 2: Feature-Specific

**Source flows:** 12
- tdd-testing, tdd-android-plugin, tdd-incall-service, tdd-native-bridge
- tdd-plugin-tests, tdd-replace-dialer, tdd-telephony-testing
- vdd-ui-theming, vdd-001-video-calling, vdd-call-ui, vdd-screens
- ddd-001-voip-calling, ddd-imei-modification

**Modules:**
1. testing (7 tasks)
2. ui-theming (6 tasks)
3. video-calling (11 tasks)
4. call-ui (3 tasks)
5. screens (2 tasks)
6. voip-calling (9 tasks)
7. imei-modification (8 tasks)
8. android-plugin-tests (3 tasks)
9. incall-service-tests (2 tasks)
10. native-bridge-tests (2 tasks)
11. plugin-tests (2 tasks)
12. replace-dialer-tests (2 tasks)
13. telephony-testing (4 tasks)

**Dependencies:** layer-0, layer-1 (all domain modules)

---

## Task Distribution

```
Layer 0: ████████████████████ 31 tasks (17%)
Layer 1: ██████████████████████████████████████████████████ 87 tasks (49%)
Layer 2: ██████████████████████████████ 61 tasks (34%)
```

---

## Gaps Summary

**Total Gaps:** 15 unresolved

| Priority | Gap ID | Layer | Description |
|----------|--------|-------|-------------|
| P0 | GAP-001 | All | No plan.md in any flow |
| P0 | GAP-007 | Layer 1 | TeleCall model mismatch (Dart 40+ vs Kotlin 10 fields) |
| P1 | GAP-008 | Layer 1 | Missing cleanup/destructor in Endpoint |
| P1 | GAP-009 | Layer 1 | replaceAccount() not implemented |
| P1 | GAP-010 | Layer 1 | setDefaultDialer() callback timing |
| P1 | GAP-013 | Layer 1 | ActivityEventListener commented out |
| P2 | GAP-002 | Layer 1 | Missing specs for unisim |
| P2 | GAP-003 | Layer 2 | Missing specs for ddd-001-voip-calling |
| P2 | GAP-004 | Layer 2 | Missing specs for ddd-imei-modification |
| P2 | GAP-005 | Layer 2 | Missing reqs for vdd-call-ui |
| P2 | GAP-006 | Layer 2 | Missing reqs+specs for vdd-screens |
| P3 | GAP-011 | Layer 0 | build_android.sh symlink missing |
| P3 | GAP-012 | Layer 0 | Generic commit message "auto" |
| P3 | GAP-014 | Layer 0 | Event ordering not guaranteed |
| P3 | GAP-015 | Layer 0 | Null eventSink drops events silently |

See [gaps.md](gaps.md) for full details.

---

## Source Flow Status

| Flow | Type | REQ | SPEC | PLAN | Layer | Compiled |
|------|------|-----|------|------|-------|----------|
| sdd-core-architecture | SDD | ✓ | ✓ | ✗ | L0 | ✓ |
| sdd-event-streaming | SDD | ✓ | ✓ | ✗ | L0 | ✓ |
| sdd-monitoring | SDD | ✓ | ✓ | ✗ | L0 | ✓ |
| sdd-build-system | SDD | ✓ | ✓ | ✗ | L0 | ✓ |
| sdd-release-workflow | SDD | ✓ | ✓ | ✗ | L0 | ✓ |
| sdd-patch-management | SDD | ✓ | ✓ | ✗ | L0 | ✓ |
| sdd-sip-core | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-sip | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-telephony | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-call | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-call-model | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-account | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-endpoint | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-gateway-service | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-headless-service | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-native-android-module | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-android-plugin | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-unisim | SDD | ✓ | ✗ | ✗ | L1 | ⚠️ |
| sdd-activity-intents | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-foreground-management | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-telephony-integration | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-endpoint-2 | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-dialer | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-android-telecom-integration | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| sdd-android-implementation-sms | SDD | ✓ | ✓ | ✗ | L1 | ✓ |
| ddd-001-voip-calling | DDD | ✓ | ✗ | ✗ | L2 | ⚠️ |
| ddd-imei-modification | DDD | ✓ | ✗ | ✗ | L2 | ⚠️ |
| tdd-testing | TDD | ✓ | ✓ | ✗ | L2 | ✓ |
| tdd-android-plugin | TDD | ✓ | ✓ | ✗ | L2 | ✓ |
| tdd-incall-service | TDD | ✓ | ✓ | ✗ | L2 | ✓ |
| tdd-native-bridge | TDD | ✓ | ✓ | ✗ | L2 | ✓ |
| tdd-plugin-tests | TDD | ✓ | ✓ | ✗ | L2 | ✓ |
| tdd-replace-dialer | TDD | ✓ | ✓ | ✗ | L2 | ✓ |
| tdd-telephony-testing | TDD | ✓ | ✓ | ✗ | L2 | ✓ |
| vdd-ui-theming | VDD | ✓ | ✓ | ✗ | L2 | ✓ |
| vdd-001-video-calling | VDD | ✓ | ✗ | ✗ | L2 | ⚠️ |
| vdd-call-ui | VDD | ✗ | ✓ | ✗ | L2 | ⚠️ |
| vdd-screens | VDD | ✗ | ✗ | ✗ | L2 | ⚠️ |

**Legend:** ✓ = Complete, ✗ = Missing, ⚠️ = Incomplete

---

## Next Steps

1. **Resolve GAP-001**: Decide on plan.md strategy
2. **Fix critical gaps**: GAP-007, GAP-008, GAP-009, GAP-010
3. **Create master plan**: Order tasks by layer and dependencies
4. **Begin implementation**: Start with Layer 0, then Layer 1, then Layer 2

---

*Compiled by /waterfall. Regenerate with `/waterfall compile`*
