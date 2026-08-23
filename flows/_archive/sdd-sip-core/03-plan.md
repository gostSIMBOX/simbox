# Plan: SIP Core Module Implementation (Flutter)

## Overview

This plan implements the SIP Core module for Flutter, adapting the legacy React Native requirements to use the Flutter Android gateway plugin architecture with EventChannel streaming and Android intents.

## Implementation Strategy

**Approach**: Adapt legacy requirements to Flutter plugin architecture

**Key Differences from React Native:**
- Use EventChannel for real-time SIP events (not Redux)
- Use Android intents for native SIP operations (not direct native module)
- Use Provider for state management (not Redux)
- Use JSON serialization for intent extras (not direct object passing)

---

## Task Breakdown

### Phase 1: Data Layer - SIP Models

#### Task 1.1: SIP Account Model

**Files to Create:**
- `lib/domain/entities/sip_account.dart`
- `lib/data/models/sip_account_model.dart`

**Implementation Steps:**
1. Create `SipAccount` entity with:
   - `id`, `username`, `password`, `domain`, `server`
   - `transport` (UDP/TCP/TLS), `port`
   - `registrationTimeout`, `enableKeepAlive`, `keepAliveInterval`
   - `registrationState`, `registrationStatus`
   - `contactUriParams` (for push notifications)
2. Create `SipAccountModel` with:
   - `fromJson()`, `toJson()` methods
   - `toEntity()`, `fromEntity()` conversion
   - Equatable for value equality
3. Add validation:
   - Required fields: username, password, domain
   - Port range: 1-65535
   - Valid transport protocol

**Acceptance Criteria:**
- [ ] Entity is immutable (final fields)
- [ ] Model serializes/deserializes correctly
- [ ] Validation works for all fields

---

#### Task 1.2: SIP Call Model

**Files to Create:**
- `lib/domain/entities/sip_call.dart`
- `lib/data/models/sip_call_model.dart`

**Implementation Steps:**
1. Create `SipCall` entity with:
   - `id`, `accountId`, `number`, `direction` (incoming/outgoing)
   - `state` (initiated/incoming/active/held/terminated/failed)
   - `startTime`, `connectTime`, `endTime`
   - `isMuted`, `isOnHold`, `isSpeaker`
   - `transferTarget`, `redirectTarget`
2. Create `SipCallModel` with serialization
3. Define call state enum:
   - `SipCallState.initiated`
   - `SipCallState.incoming`
   - `SipCallState.active`
   - `SipCallState.held`
   - `SipCallState.terminated`
   - `SipCallState.failed`

**Acceptance Criteria:**
- [ ] All call states represented
- [ ] Duration calculation works (connectTime - startTime)
- [ ] State transitions are valid

---

#### Task 1.3: SIP Event Model

**Files to Create:**
- `lib/domain/entities/sip_event.dart`
- `lib/data/models/sip_event_model.dart`

**Implementation Steps:**
1. Create `SipEvent` entity with:
   - `type` (registration_changed, call_received, call_changed, etc.)
   - `data` (dynamic event-specific data)
   - `timestamp`
2. Define event types enum:
   - `SipEventType.registrationChanged`
   - `SipEventType.callReceived`
   - `SipEventType.callChanged`
   - `SipEventType.callTerminated`
   - `SipEventType.connectivityChanged`
   - `SipEventType.accountChanged`
3. Create event parsers for each type

**Acceptance Criteria:**
- [ ] All event types from legacy are covered
- [ ] Event data is properly typed
- [ ] Timestamps are accurate

---

### Phase 2: Domain Layer - Repository Interfaces

#### Task 2.1: SIP Repository Interface

**Files to Create:**
- `lib/domain/repositories/sip_repository.dart`

**Implementation Steps:**
1. Define `SipRepository` interface with methods:
   - **Lifecycle**: `initialize()`, `destroy()`
   - **Account**: `createAccount()`, `deleteAccount()`, `getAccount()`, `getAccounts()`
   - **Call Operations**: `makeCall()`, `answerCall()`, `declineCall()`, `hangupCall()`
   - **Call Control**: `holdCall()`, `unholdCall()`, `muteCall()`, `unmuteCall()`
   - **Audio Route**: `useSpeaker()`, `useEarpiece()`
   - **Transfer**: `transferCall()`, `attendedTransfer()`, `redirectCall()`
   - **DTMF**: `sendDtmf()`
   - **Streams**: `get eventStream`, `get statusStream`

**Acceptance Criteria:**
- [ ] All legacy operations covered
- [ ] Return types use Result pattern
- [ ] Streams for real-time events

---

#### Task 2.2: SIP Use Cases

**Files to Create:**
- `lib/domain/usecases/sip_usecases.dart`
- `lib/domain/usecases/initialize_sip.dart`
- `lib/domain/usecases/create_sip_account.dart`
- `lib/domain/usecases/make_sip_call.dart`
- `lib/domain/usecases/answer_sip_call.dart`
- `lib/domain/usecases/hangup_sip_call.dart`

**Implementation Steps:**
1. Create base `SipUseCase` class
2. Implement specific use cases:
   - `InitializeSip`: Initialize SIP endpoint
   - `CreateSipAccount`: Register new SIP account
   - `DeleteSipAccount`: Remove SIP account
   - `MakeSipCall`: Initiate outgoing call
   - `AnswerSipCall`: Answer incoming call
   - `HangupSipCall`: Terminate call
   - `HoldSipCall`: Place call on hold
   - `MuteSipCall`: Mute microphone
   - `TransferSipCall`: Transfer call
   - `SendDtmf`: Send DTMF tone
3. Each use case returns `Future<Result<T>>`

**Acceptance Criteria:**
- [ ] Each use case has single responsibility
- [ ] Error handling with Result pattern
- [ ] Parameters properly typed

---

### Phase 3: Data Layer - Plugin Implementation

#### Task 3.1: SIP Service (Plugin Wrapper)

**Files to Create:**
- `lib/data/services/sip_service.dart`

**Implementation Steps:**
1. Create `SipService` class that wraps the Android SIP plugin:
   - Use `MethodChannel` for commands
   - Use `EventChannel` for events
2. Implement methods:
   - `initialize(SipConfig config)` - Setup SIP endpoint
   - `createAccount(SipAccount account)` - Register account
   - `deleteAccount(String accountId)` - Remove account
   - `makeCall(String accountId, String number)` - Outgoing call
   - `answerCall(String callId)` - Answer call
   - `hangupCall(String callId)` - End call
   - `holdCall(String callId)` - Hold call
   - `muteCall(String callId)` - Mute
   - `useSpeaker(String callId)` - Speaker mode
   - `sendDtmf(String callId, String digit)` - DTMF
3. Setup EventChannel listener:
   - Stream SIP events to Dart
   - Parse event data
   - Broadcast to subscribers

**MethodChannel Methods:**
```dart
static const MethodChannel _channel = MethodChannel('gostsimbox/sip');

// Initialize
await _channel.invokeMethod('initialize', {'config': configJson});

// Account operations
await _channel.invokeMethod('createAccount', {'account': accountJson});
await _channel.invokeMethod('deleteAccount', {'accountId': id});

// Call operations
await _channel.invokeMethod('makeCall', {'accountId': id, 'number': number});
await _channel.invokeMethod('answerCall', {'callId': id});
await _channel.invokeMethod('hangupCall', {'callId': id});
```

**EventChannel Setup:**
```dart
static const EventChannel _eventChannel = EventChannel('gostsimbox/sip_events');

Stream<SipEvent> get eventStream {
  return _eventChannel.receiveBroadcastStream().map((event) {
    return SipEventModel.fromJson(event).toEntity();
  });
}
```

**Acceptance Criteria:**
- [ ] All methods invoke native correctly
- [ ] EventChannel streams events
- [ ] Error handling for channel errors
- [ ] JSON serialization for method arguments

---

#### Task 3.2: SIP Repository Implementation

**Files to Create:**
- `lib/data/repositories/sip_repository_impl.dart`

**Implementation Steps:**
1. Implement `SipRepository` interface
2. Use `SipService` for native operations
3. Transform models to entities
4. Handle errors and return Result types
5. Broadcast events via StreamController

**Implementation Pattern:**
```dart
class SipRepositoryImpl implements SipRepository {
  final SipService _service;
  final Logger _logger;

  SipRepositoryImpl(this._service, this._logger);

  @override
  AsyncResult<SipAccount> createAccount(SipAccount account) async {
    try {
      final model = SipAccountModel.fromEntity(account);
      final result = await _service.createAccount(model);
      return Right(result.toEntity());
    } catch (e) {
      return Left(SipFailure(message: 'Failed to create account: $e'));
    }
  }

  @override
  Stream<SipEvent> get eventStream => _service.eventStream;
}
```

**Acceptance Criteria:**
- [ ] All interface methods implemented
- [ ] Result pattern used consistently
- [ ] Events streamed correctly

---

### Phase 4: Presentation Layer - State Management

#### Task 4.1: SIP Provider

**Files to Create:**
- `lib/presentation/providers/sip_provider.dart`

**Implementation Steps:**
1. Create `SipProvider` class extending `ChangeNotifier`:
   - State: `SipState` (accounts, calls, connectivity, registration)
   - Methods: All SIP operations
   - Event subscription: Listen to SIP events
2. Implement state management:
   - Update state on events
   - Notify listeners on changes
3. Handle lifecycle:
   - Initialize on app start
   - Dispose on app close

**State Structure:**
```dart
class SipState {
  final Map<String, SipAccount> accounts;
  final Map<String, SipCall> calls;
  final bool isConnected;
  final SipRegistrationState registrationState;
  
  SipState({
    this.accounts = const {},
    this.calls = const {},
    this.isConnected = false,
    this.registrationState = SipRegistrationState.unregistered,
  });
}
```

**Acceptance Criteria:**
- [ ] State updates on events
- [ ] UI can access via Provider
- [ ] Proper dispose cleanup

---

#### Task 4.2: SIP Event Handlers

**Files to Create:**
- `lib/presentation/providers/sip_event_handlers.dart`

**Implementation Steps:**
1. Create event handler functions:
   - `onRegistrationChanged(Account account)`
   - `onCallReceived(Call call)`
   - `onCallChanged(Call call)`
   - `onCallTerminated(Call call)`
   - `onConnectivityChanged(bool available)`
2. Update provider state based on events
3. Trigger navigation for incoming calls

**Event Handling:**
```dart
void _handleEvent(SipEvent event) {
  switch (event.type) {
    case SipEventType.registrationChanged:
      _updateAccountRegistration(event.data);
      break;
    case SipEventType.callReceived:
      _handleIncomingCall(event.data);
      break;
    case SipEventType.callChanged:
      _updateCallState(event.data);
      break;
    case SipEventType.callTerminated:
      _removeCall(event.data);
      break;
  }
}
```

**Acceptance Criteria:**
- [ ] All event types handled
- [ ] State updates correctly
- [ ] Incoming calls trigger navigation

---

### Phase 5: Integration

#### Task 5.1: Dependency Injection Registration

**Files to Modify:**
- `lib/core/di/dependency_injection.dart`

**Implementation Steps:**
1. Register SIP service:
   ```dart
   getIt.registerLazySingleton<SipService>(() => SipService());
   ```
2. Register SIP repository:
   ```dart
   getIt.registerLazySingleton<SipRepository>(
     () => SipRepositoryImpl(getIt<SipService>(), getIt<Logger>()),
   );
   ```
3. Register SIP use cases:
   ```dart
   getIt.registerLazySingleton<InitializeSip>(
     () => InitializeSip(getIt<SipRepository>()),
   );
   getIt.registerLazySingleton<CreateSipAccount>(
     () => CreateSipAccount(getIt<SipRepository>()),
   );
   // ... other use cases
   ```
4. Register SIP provider:
   ```dart
   getIt.registerFactory<SipProvider>(
     () => SipProvider(getIt<SipRepository>(), getIt<Logger>()),
   );
   ```

**Acceptance Criteria:**
- [ ] All SIP dependencies registered
- [ ] Correct lifecycle (singleton vs factory)
- [ ] No circular dependencies

---

#### Task 5.2: App Initialization

**Files to Modify:**
- `lib/main.dart`

**Implementation Steps:**
1. Add SipProvider to MultiProvider:
   ```dart
   ChangeNotifierProvider<SipProvider>(
     create: (_) => getIt<SipProvider>(),
   ),
   ```
2. Initialize SIP on app start:
   ```dart
   final sipProvider = context.read<SipProvider>();
   await sipProvider.initialize(config);
   ```

**Acceptance Criteria:**
- [ ] SIP initialized on app start
- [ ] Provider accessible throughout app
- [ ] Proper error handling

---

## File Structure (Target)

```
lib/
├── domain/
│   ├── entities/
│   │   ├── sip_account.dart
│   │   ├── sip_call.dart
│   │   └── sip_event.dart
│   ├── repositories/
│   │   └── sip_repository.dart
│   └── usecases/
│       ├── sip_usecases.dart
│       ├── initialize_sip.dart
│       ├── create_sip_account.dart
│       ├── make_sip_call.dart
│       ├── answer_sip_call.dart
│       └── hangup_sip_call.dart
├── data/
│   ├── models/
│   │   ├── sip_account_model.dart
│   │   ├── sip_call_model.dart
│   │   └── sip_event_model.dart
│   ├── repositories/
│   │   └── sip_repository_impl.dart
│   └── services/
│       └── sip_service.dart
└── presentation/
    └── providers/
        ├── sip_provider.dart
        └── sip_event_handlers.dart
```

---

## Dependencies

### Plugin Dependencies (Android)
- `gost_simbox_sip2` (local plugin) - SIP operations via intents
- EventChannel for event streaming

### Dart Dependencies (already in pubspec.yaml)
- `provider` - State management
- `get_it` - Dependency injection
- `dartz` - Either type for Result
- `equatable` - Value equality
- `json_annotation` - JSON serialization

---

## Testing Strategy

### Unit Tests
- Test use cases with mocked repository
- Test event handlers with mock events
- Test model serialization

### Integration Tests
- Test SIP service channel communication
- Test repository with mock service
- Test provider state updates

### Manual Tests
- Register SIP account
- Make outgoing call
- Answer incoming call
- Test call operations (hold, mute, transfer)
- Test DTMF

---

## Rollback Considerations

- Each phase is independent
- Can rollback to previous phase without affecting core
- SIP service can be mocked for testing

---

## Estimated Complexity

| Phase | Tasks | Complexity | Estimated Time |
|-------|-------|------------|----------------|
| Phase 1: Data Models | 3 | Low | 1-2 hours |
| Phase 2: Domain Layer | 2 | Medium | 2-3 hours |
| Phase 3: Plugin Implementation | 2 | High | 4-6 hours |
| Phase 4: State Management | 2 | Medium | 2-3 hours |
| Phase 5: Integration | 2 | Low | 1-2 hours |
| **Total** | **11** | **High** | **10-16 hours** |

---

## Success Criteria

- [ ] SIP account can be created and registered
- [ ] Outgoing calls can be initiated
- [ ] Incoming calls are received and displayed
- [ ] Call operations work (hold, mute, speaker, DTMF)
- [ ] Events stream in real-time
- [ ] State updates correctly in provider
- [ ] Error handling with Result pattern
- [ ] All dependencies registered in DI

---

**Status**: DRAFT  
**Created**: 2026-03-05  
**Related**: 01-requirements.md, 02-specifications.md, ADR-001 (service-architecture), ADR-002 (event-channel)
