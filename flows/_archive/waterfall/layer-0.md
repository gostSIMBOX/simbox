# Layer 0: Shared Infrastructure

> COMPILED from flows. Do not edit directly.
> Last compiled: 2026-03-04
> Source flows: sdd-core-architecture, sdd-event-streaming, sdd-monitoring, sdd-build-system, sdd-release-workflow, sdd-patch-management

---

## Overview

- **Total tasks**: 18
- **Modules**: 6
- **Dependencies on lower layers**: None (base layer)

---

## Module: core-architecture

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| DependencyInjection | class | Centralized DI with get_it, lifecycle management | sdd-core-architecture |
| ErrorHandler | class | Global error capture, logging, user notification | sdd-core-architecture |
| GatewayRepository | abstract | Repository pattern for gateway config | sdd-core-architecture |
| GatewayUseCases | class | Use case pattern for business logic | sdd-core-architecture |

### Required Interfaces (from Layer N-1)

| Interface | Type | Expected From |
|-----------|------|---------------|
| SharedPreferences | external | Package dependency |
| http.Client | external | Package dependency |
| Logger | external | Package dependency |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 1 | core-arch-001 | Implement DependencyInjection class with _registerExternalDependencies, _registerServices, _registerRepositories, _registerUseCases | - | sdd-core-architecture |
| 2 | core-arch-002 | Implement DependencyLifecycleManager with initializeServices, disposeServices, checkServicesHealth | core-arch-001 | sdd-core-architecture |
| 3 | core-arch-003 | Implement ErrorHandler with error categories (Application, Network, Validation, Auth, Permission) | - | sdd-core-architecture |
| 4 | core-arch-004 | Implement error storage with SharedPreferences (max 100 entries, 24h retention) | core-arch-003 | sdd-core-architecture |
| 5 | core-arch-005 | Implement ErrorBoundary widget for Flutter error catching | core-arch-003 | sdd-core-architecture |
| 6 | core-arch-006 | Setup MultiProvider in main.dart with GatewayService, SipService, SmsService, TelephonyService | - | sdd-core-architecture |

---

## Module: event-streaming

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| TeleEndpoint | class | EventChannel 'flutter_tele_events' for Android→Flutter events | sdd-event-streaming |
| EventRouter | Map<String, StreamController> | Routes events by type to separate streams | sdd-event-streaming |

### Required Interfaces (from Layer N-1)

| Interface | Type | Expected From |
|-----------|------|---------------|
| EventChannel | Flutter | Package dependency |
| StreamController | Flutter | Package dependency |
| TeleCall | data class | layer-1 (call-model) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 7 | event-001 | Implement TeleEndpoint class with EventChannel and StreamHandler | - | sdd-event-streaming |
| 8 | event-002 | Implement event routing with Map<String, StreamController<dynamic>> for type-based routing | event-001 | sdd-event-streaming |
| 9 | event-003 | Implement event types: service_started, call_received, call_changed, call_terminated, call_error | event-002 | sdd-event-streaming |
| 10 | event-004 | Add dispose() method to close all StreamControllers and prevent memory leaks | event-002 | sdd-event-streaming |

---

## Module: monitoring

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| ConnectionMonitorService | singleton | Monitors SIP/SMPP connections with latency tracking | sdd-monitoring |
| ConnectionStats | entity | Connection state with protocol, latency, status | sdd-monitoring |
| MonitoringConfig | config | Server/port configuration for monitoring | sdd-monitoring |

### Required Interfaces (from Layer N-1)

| Interface | Type | Expected From |
|-----------|------|---------------|
| connectivity_plus | package | Package dependency |
| http | package | For speed tests to httpbin.org |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 11 | monitor-001 | Implement ConnectionMonitorService singleton with periodic checks (5s interval) | - | sdd-monitoring |
| 12 | monitor-002 | Implement ConnectionStats entity with protocol, isConnected, latency, lastUpdate, errorMessage | - | sdd-monitoring |
| 13 | monitor-003 | Implement network quality assessment: Excellent (<50ms), Good (50-100ms), Fair (100-200ms), Poor (>200ms) | monitor-002 | sdd-monitoring |
| 14 | monitor-004 | Implement speed test integration with httpbin.org for bandwidth measurement | monitor-001 | sdd-monitoring |

---

## Module: build-system

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| build_android_X.Y.Z.sh | script | Host script to trigger Docker build | sdd-build-system |
| Dockerfile | docker | Docker image with NDK r12b, SDK r25.2.5 | sdd-build-system |
| build_pjsip.sh | script | PJSIP compilation script | sdd-build-system |
| build_openssl.sh | script | OpenSSL compilation for PJSIP | sdd-build-system |
| build_openh264.sh | script | OpenH264 codec compilation | sdd-build-system |
| build_opus.sh | script | Opus codec compilation | sdd-build-system |

### Required Interfaces (from Layer N-1)

| Interface | Type | Expected From |
|-----------|------|---------------|
| Docker | external | Host requirement |
| Android NDK r12b | external | Docker image |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 15 | build-001 | Create Dockerfile with Android NDK r12b, SDK tools r25.2.5, Ubuntu base | - | sdd-build-system |
| 16 | build-002 | Create build_pjsip.sh for PJSIP 2.7.1/2.9/2.10 with multi-arch support | build-001 | sdd-build-system |
| 17 | build-003 | Create build_openssl.sh for OpenSSL dependency | build-002 | sdd-build-system |
| 18 | build-004 | Create build_openh264.sh for OpenH264 video codec | build-002 | sdd-build-system |
| 19 | build-005 | Create build_opus.sh for Opus audio codec | build-002 | sdd-build-system |
| 20 | build-006 | Create config_site.h with PJ_CONFIG_ANDROID and codec flags | build-002 | sdd-build-system |

---

## Module: release-workflow

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| release.sh | script | Full release process (build+tar) | sdd-release-workflow |
| release_onlytar.sh | script | Re-package without rebuild | sdd-release-workflow |
| update.sh | script | Git auto-commit and push | sdd-release-workflow |

### Required Interfaces (from Layer N-1)

| Interface | Type | Expected From |
|-----------|------|---------------|
| build_android.sh | script | layer-0 (build-system) |
| Git | external | Host requirement |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 21 | release-001 | Create release.sh for full release process | - | sdd-release-workflow |
| 22 | release-002 | Create release_onlytar.sh for tar-only repackaging | release-001 | sdd-release-workflow |
| 23 | release-003 | Create update.sh for git auto-commit with meaningful messages | release-001 | sdd-release-workflow |
| 24 | release-004 | Fix build_android.sh symlink to version-specific script | build-002 | sdd-release-workflow |

---

## Module: patch-management

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| config_site.h | header | PJSIP configuration with Android flags | sdd-patch-management |
| android_jni_dev.c | source | Android JNI audio device implementation | sdd-patch-management |
| opensl_dev.c | source | OpenSL ES audio device (2.9+) | sdd-patch-management |
| oboe_dev.c | source | Oboe audio device (2.9+) | sdd-patch-management |
| conference.c | source | Audio conference bridge | sdd-patch-management |

### Required Interfaces (from Layer N-1)

| Interface | Type | Expected From |
|-----------|------|---------------|
| PJSIP source | external | PJSIP library |
| Android NDK | external | Build environment |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 25 | patch-001 | Create version-specific patch directories for 2.7.1, 2.9, 2.10 | - | sdd-patch-management |
| 26 | patch-002 | Create config_site.h with PJ_CONFIG_ANDROID, codec flags, AEC settings | - | sdd-patch-management |
| 27 | patch-003 | Create android_jni_dev.c for Android JNI audio device | patch-002 | sdd-patch-management |
| 28 | patch-004 | Create opensl_dev.c for OpenSL ES audio device (2.9+) | patch-002 | sdd-patch-management |
| 29 | patch-005 | Create oboe_dev.c for Oboe audio device (2.9+) | patch-002 | sdd-patch-management |
| 30 | patch-006 | Create conference.c for audio conference bridge | patch-002 | sdd-patch-management |
| 31 | patch-007 | Create pjsua_aud.c and pjsua.h patches for audio layer | patch-002 | sdd-patch-management |

---

## Cross-Module Dependencies

```
core-arch-001 ──► All services (provides DI)
event-001 ──► call-model, telephony (provides events)
monitor-001 ──► gateway-service (provides connection stats)
build-002 ──► patch-002 (requires config_site.h)
release-001 ──► build-002 (requires build script)
```

---

## Known Gaps

| Gap ID | Description | Affected Flows | Resolution |
|--------|-------------|----------------|------------|
| GAP-L0-001 | No explicit plan.md in any Layer 0 flow | All | Extract tasks from specifications |
| GAP-L0-002 | build_android.sh symlink missing | sdd-release-workflow | Create symlink in release-004 |
| GAP-L0-003 | Generic commit message "auto" lacks context | sdd-release-workflow | Fix in release-003 |

---

*Compiled by /waterfall. Regenerate with `/waterfall compile`*
