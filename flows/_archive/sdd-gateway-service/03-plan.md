# Plan: Gateway Service Implementation

## Overview

This plan implements the Gateway Service - the core orchestration component that provides bidirectional routing between SIP and GSM telephony.

## Implementation Strategy

**Approach**: Build on existing SipService, integrate with TelephonyService

**Key Components:**
- GatewayService singleton for orchestration
- CallRouting entity for tracking bidirectional calls
- GatewayConfig/GatewayStatus for configuration and state
- Event handling for SIP and Telephony state synchronization

---

## Task Breakdown

### Phase 1: Domain Layer - Entities

#### Task 1.1: CallRouting Entity

**Files to Create:**
- `lib/domain/entities/call_routing.dart`

**Implementation Steps:**
1. Create `CallRoutingDirection` enum:
   - `sipToGsm` - SIP incoming, GSM outgoing
   - `gsmToSip` - GSM incoming, SIP outgoing
2. Create `CallRoutingState` enum:
   - `connecting` - Setting up both legs
   - `active` - Both legs established
   - `ended` - Normal termination
   - `failed` - Setup or runtime failure
3. Create `CallRouting` entity with:
   - `id`, `sipCallId`, `telephonyCallId`, `number`
   - `direction`, `state`, `startTime`, `endTime`
   - `totalDuration` calculation
4. Add state transition validation

**Acceptance Criteria:**
- [ ] Entity is immutable (final fields)
- [ ] State transitions are valid
- [ ] Duration calculation works

---

#### Task 1.2: GatewayConfig Entity

**Files to Create:**
- `lib/domain/entities/gateway_config.dart`

**Implementation Steps:**
1. Create `GatewayConfig` entity with:
   - `sipAccount` (SipAccount) - Required
   - `smppConfig` (SmppConfig?) - Optional
   - `autoAnswer` (bool) - Default: false
   - `enableLogging` (bool) - Default: true
   - `routeSipToGsm` (bool) - Default: true
   - `routeGsmToSip` (bool) - Default: true
   - `routeSmsToSmpp` (bool) - Default: false
   - `routeSmppToSms` (bool) - Default: false
   - `maxConcurrentCalls` (int) - Default: 5
2. Add JSON serialization
3. Add validation
4. Add copyWith() for immutable updates

**Acceptance Criteria:**
- [ ] All configuration fields present
- [ ] JSON serialization works
- [ ] Validation catches invalid configs

---

#### Task 1.3: GatewayStatus Entity

**Files to Create:**
- `lib/domain/entities/gateway_status.dart`

**Implementation Steps:**
1. Create `GatewayStatus` entity with:
   - `isRunning` (bool)
   - `sipState` (SipConnectionState)
   - `smppState` (SmppConnectionState?)
   - `telephonyPermissions` (TelephonyPermissionStatus)
   - `activeCalls` (int)
   - `totalCallsHandled` (int)
   - `totalMessagesHandled` (int)
   - `startTime` (DateTime?)
   - `uptime` (Duration?)
2. Add uptime calculation
3. Add copyWith() for immutable updates

**Acceptance Criteria:**
- [ ] All status fields present
- [ ] Uptime calculation works
- [ ] Immutable with copyWith

---

### Phase 2: Domain Layer - Repository Interface

#### Task 2.1: GatewayRepository Interface

**Files to Create:**
- `lib/domain/repositories/gateway_repository.dart`

**Implementation Steps:**
1. Define `GatewayRepository` interface with methods:
   - **Lifecycle**: `initialize()`, `start()`, `stop()`, `dispose()`
   - **Configuration**: `getConfig()`, `saveConfig()`, `loadConfig()`
   - **Call Operations**: `makeCallViaSip()`, `makeCallViaGsm()`
   - **SMS Operations**: `sendSms()`, `sendSmsViaSmpp()`
   - **Routing**: `getRouting()`, `getActiveRoutings()`, `endRouting()`
   - **Statistics**: `getStatistics()`, `resetStatistics()`
   - **Streams**: `statusStream`, `routingStream`, `logStream`

**Acceptance Criteria:**
- [ ] All gateway operations covered
- [ ] Return types use Result pattern
- [ ] Streams for real-time updates

---

#### Task 2.2: Gateway Use Cases

**Files to Create:**
- `lib/domain/usecases/gateway_usecases.dart`

**Implementation Steps:**
1. Create use cases:
   - `InitializeGateway` - Initialize with config
   - `StartGateway` - Start routing
   - `StopGateway` - Stop routing
   - `MakeSipCall` - SIP→GSM call
   - `SendGatewaySms` - Send SMS
   - `GetGatewayStatus` - Get current status
   - `GetGatewayStatistics` - Get statistics
   - `EndGatewayRouting` - End specific routing

**Acceptance Criteria:**
- [ ] Each use case has single responsibility
- [ ] Error handling with Result pattern
- [ ] Parameters properly typed

---

### Phase 3: Data Layer - Implementation

#### Task 3.1: GatewayService Implementation

**Files to Create:**
- `lib/data/services/gateway_service.dart`

**Implementation Steps:**
1. Create `GatewayService` singleton class:
   - Internal factory pattern
   - Sub-service references (SipService, TelephonyService)
2. Implement lifecycle methods:
   - `initialize(GatewayConfig)` - Setup all services
   - `start()` - Begin routing
   - `stop()` - Stop routing and cleanup
   - `dispose()` - Full cleanup
3. Implement call routing:
   - `makeCallViaSip(number)` - Create SIP→GSM routing
   - `_makeGsmCallForRouting(routingId, number)` - Complete the routing
   - `_handleSipCallStateChange(call)` - Sync states
   - `_handleTelephonyCallStateChange(call)` - Sync states
4. Implement routing management:
   - `_createRouting()` - Generate unique routing ID
   - `_updateRouting()` - Update routing state
   - `_endRouting(routingId)` - End and cleanup routing
   - `getActiveRoutings()` - Get active routings
5. Implement statistics tracking:
   - `_totalCallsHandled` counter
   - `_totalMessagesHandled` counter
   - `_startTime`, uptime calculation
6. Setup event listeners:
   - Subscribe to SipService events
   - Subscribe to TelephonyService events
   - Broadcast to status/routing/log streams

**Stream Controllers:**
```dart
final _statusController = StreamController<GatewayStatus>.broadcast();
final _routingController = StreamController<CallRouting>.broadcast();
final _logController = StreamController<String>.broadcast();
```

**Acceptance Criteria:**
- [ ] Singleton pattern works
- [ ] All lifecycle methods implemented
- [ ] Call routing creates and tracks routings
- [ ] State synchronization between SIP and GSM
- [ ] Streams broadcast updates
- [ ] Statistics tracked correctly

---

#### Task 3.2: GatewayRepositoryImpl

**Files to Create:**
- `lib/data/repositories/gateway_repository_impl.dart`

**Implementation Steps:**
1. Implement `GatewayRepository` interface
2. Use `GatewayService` for operations
3. Handle configuration persistence:
   - `saveConfig()` - Save to SharedPreferences
   - `loadConfig()` - Load from SharedPreferences
4. Map errors to Failure types
5. Return Result pattern

**Acceptance Criteria:**
- [ ] All interface methods implemented
- [ ] Configuration persistence works
- [ ] Error mapping correct

---

### Phase 4: Integration

#### Task 4.1: DI Registration

**Files to Modify:**
- `lib/core/di/dependency_injection.dart`

**Implementation Steps:**
1. Register GatewayService:
   ```dart
   getIt.registerLazySingleton<GatewayService>(() => GatewayService());
   ```
2. Register GatewayRepository:
   ```dart
   getIt.registerLazySingleton<GatewayRepository>(
     () => GatewayRepositoryImpl(getIt<GatewayService>(), getIt<Logger>()),
   );
   ```
3. Register Gateway Use Cases:
   ```dart
   getIt.registerLazySingleton<InitializeGateway>(
     () => InitializeGateway(getIt<GatewayRepository>()),
   );
   // ... other use cases
   ```

**Acceptance Criteria:**
- [ ] All gateway dependencies registered
- [ ] Correct lifecycle (singleton vs factory)
- [ ] No circular dependencies

---

#### Task 4.2: Provider Integration

**Files to Create:**
- `lib/presentation/providers/gateway_provider.dart`

**Implementation Steps:**
1. Create `GatewayProvider` extending `ChangeNotifier`:
   - State: `GatewayState` (isRunning, status, activeRoutings)
   - Methods: initialize, start, stop, makeCall, sendSms
   - Event subscription to GatewayService streams
2. Add to MultiProvider in main.dart

**Acceptance Criteria:**
- [ ] Provider manages gateway state
- [ ] UI can access via Provider
- [ ] Proper dispose cleanup

---

## File Structure (Target)

```
lib/
├── domain/
│   ├── entities/
│   │   ├── call_routing.dart
│   │   ├── gateway_config.dart
│   │   └── gateway_status.dart
│   ├── repositories/
│   │   └── gateway_repository.dart
│   └── usecases/
│       └── gateway_usecases.dart
├── data/
│   ├── repositories/
│   │   └── gateway_repository_impl.dart
│   └── services/
│       └── gateway_service.dart
└── presentation/
    └── providers/
        └── gateway_provider.dart
```

---

## Dependencies

### Internal Dependencies
- `SipService` - Already implemented (sdd-sip-core)
- `TelephonyService` - Existing service
- `SmsService` - Existing service

### Dart Dependencies (already in pubspec.yaml)
- `provider` - State management
- `get_it` - Dependency injection
- `dartz` - Either type for Result
- `shared_preferences` - Configuration persistence
- `logger` - Logging

---

## Testing Strategy

### Unit Tests
- Test use cases with mocked repository
- Test CallRouting state transitions
- Test GatewayConfig validation

### Integration Tests
- Test GatewayService initialization
- Test call routing flow
- Test state synchronization

---

## Rollback Considerations

- Each phase is independent
- Can rollback without affecting sdd-sip-core
- GatewayService can be mocked for testing

---

## Estimated Complexity

| Phase | Tasks | Complexity | Estimated Time |
|-------|-------|------------|----------------|
| Phase 1: Domain Entities | 3 | Low | 1-2 hours |
| Phase 2: Domain Layer | 2 | Medium | 2-3 hours |
| Phase 3: Implementation | 2 | High | 4-6 hours |
| Phase 4: Integration | 2 | Low-Medium | 1-2 hours |
| **Total** | **9** | **High** | **8-13 hours** |

---

## Success Criteria

- [ ] GatewayService singleton working
- [ ] Bidirectional call routing (SIP↔GSM)
- [ ] Configuration persistence
- [ ] Real-time status updates via streams
- [ ] Statistics tracking
- [ ] All dependencies registered in DI
- [ ] Provider integration for UI

---

**Status**: DRAFT  
**Created**: 2026-03-05  
**Related**: 01-requirements.md, 02-specifications.md
