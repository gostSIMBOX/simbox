# Specifications: Complete Refactoring

> Version: 1.0
> Status: REVIEW
> Last Updated: 2026-03-15

## System Overview

The project uses Clean Architecture with three layers:
- **Domain Layer** (`lib/domain/`): Entities, repository interfaces, use cases
- **Data Layer** (`lib/data/`): Repository implementations, data sources, services
- **Presentation Layer** (`lib/presentation/`): Providers, screens, widgets

## Affected Components

### Files to Delete

| File Path | Reason | Impact |
|-----------|--------|--------|
| `lib/data/repositories/gateway_repository.dart` | Duplicate concrete class, conflicts with domain interface | None - old API not used |
| `lib/domain/entities/gateway_config_entity.dart` | Duplicate entity, new version in `gateway_config.dart` | Model conversion needs update |
| `lib/domain/entities/gateway_entity.dart` | Duplicate entity, new version in `gateway_status.dart` | None - not directly imported |
| `lib/services/sms_service.dart` lines 51-84 | Duplicate `SmppConfig` class definition | Remove duplicate, keep separate file |

### Files to Modify

#### 1. `lib/presentation/providers/gateway_provider.dart`

**Current import (line 9):**
```dart
import '../repositories/gateway_repository.dart';
```

**Fixed import:**
```dart
import '../../domain/repositories/gateway_repository.dart';
```

#### 2. `lib/presentation/providers/sip_provider.dart`

**Current import (line 9):**
```dart
import '../repositories/sip_repository.dart';
```

**Fixed import:**
```dart
import '../../domain/repositories/sip_repository.dart';
```

#### 3. `lib/core/di/dependency_injection.dart`

**Remove duplicate registration (lines ~189-194):**
```dart
// DELETE THIS BLOCK:
getIt.registerLazySingleton<GatewayRepository>(
  () => GatewayRepository(
    getIt<LocalDataSource>(),
    getIt<RemoteDataSource>(),
    getIt<Logger>(),
  ),
);
```

**Also remove unused dependencies** if `LocalDataSource` and `RemoteDataSource` are no longer used elsewhere.

#### 4. `lib/data/models/gateway_config_model.dart`

**Current:**
```dart
import '../entities/gateway_config_entity.dart';

class GatewayConfigModel {
  // Uses old GatewayConfigEntity
  GatewayConfigEntity toEntity() { ... }
}
```

**Fixed:**
```dart
import '../../domain/entities/gateway_config.dart';

class GatewayConfigModel {
  // Uses new GatewayConfig
  GatewayConfig toEntity() { ... }
}
```

May need property mapping adjustments based on new entity structure.

### Files Unchanged

The following files are correctly implemented and need no changes:

- `lib/domain/repositories/gateway_repository.dart` - Interface correct
- `lib/domain/repositories/sip_repository.dart` - Interface correct
- `lib/data/repositories/gateway_repository_impl.dart` - Implementation correct
- `lib/data/repositories/sip_repository_impl.dart` - Implementation correct
- `lib/domain/entities/gateway_config.dart` - Entity correct
- `lib/domain/entities/gateway_status.dart` - Entity correct
- `lib/domain/entities/call_routing.dart` - Entity correct
- `lib/domain/entities/sip_account.dart` - Entity correct
- `lib/domain/entities/sip_call.dart` - Entity correct
- `lib/domain/entities/sip_event.dart` - Entity correct

## Interface Definitions

### GatewayRepository (Domain Interface)

```dart
// Type aliases
typedef GatewayResult<T> = Either<Failure, T>;
typedef AsyncGatewayResult<T> = Future<Either<Failure, T>>;

// Interface
abstract class GatewayRepository {
  AsyncGatewayResult<void> initialize(GatewayConfig config);
  AsyncGatewayResult<void> start();
  AsyncGatewayResult<void> stop();
  AsyncGatewayResult<void> shutdown();
  GatewayResult<GatewayConfig?> getConfig();
  AsyncGatewayResult<void> saveConfig(GatewayConfig config);
  AsyncGatewayResult<String?> makeCallViaSip(String number);
  AsyncGatewayResult<String?> sendSmsViaSip(String recipient, String content, {bool useSmpp});
  GatewayResult<CallRouting?> getActiveRouting(String routingId);
  GatewayResult<List<CallRouting>> getAllActiveRoutings();
  AsyncGatewayResult<void> removeRouting(String routingId);
  AsyncGatewayResult<void> refreshActiveRoutings();
  GatewayResult<Map<String, dynamic>> getDiagnostics();
  AsyncGatewayResult<void> clearAllData();
  Stream<GatewayStatus> get statusStream;
  Stream<CallRouting> get routingStream;
  int get activeRoutingCount;
  GatewayStatus? get currentStatus;
}
```

### SipRepository (Domain Interface)

```dart
// Type aliases
typedef SipResult<T> = Either<Failure, T>;
typedef AsyncSipResult<T> = Future<Either<Failure, T>>;

// Interface
abstract class SipRepository {
  AsyncSipResult<SipAccount> createAccount(SipAccount account);
  AsyncSipResult<void> updateAccount(SipAccount account);
  AsyncSipResult<void> deleteAccount(String accountId);
  AsyncSipResult<SipAccount?> getAccount(String accountId);
  AsyncSipResult<List<SipAccount>> getAllAccounts();
  AsyncSipResult<void> register(String accountId);
  AsyncSipResult<void> unregister(String accountId);
  AsyncSipResult<SipCall> makeCall(String accountId, String destination);
  AsyncSipResult<void> answerCall(String callId);
  AsyncSipResult<void> rejectCall(String callId);
  AsyncSipResult<void> terminateCall(String callId);
  AsyncSipResult<void> holdCall(String callId);
  AsyncSipResult<void> resumeCall(String callId);
  AsyncSipResult<void> muteCall(String callId);
  AsyncSipResult<void> unmuteCall(String callId);
  AsyncSipResult<void> toggleSpeaker(String callId);
  AsyncSipResult<void> sendDtmf(String callId, String tone);
  Stream<SipEvent> get eventStream;
  SipRegistrationState getRegistrationState(String accountId);
  Stream<SipRegistrationState> get registrationStateStream;
}
```

## Data Models

### GatewayConfigModel Conversion

The model needs to convert between JSON and the new `GatewayConfig` entity:

```dart
// New GatewayConfig structure:
class GatewayConfig {
  final SipAccount sipAccount;      // Direct entity reference
  final SmppConfig? smppConfig;     // Optional
  final bool autoAnswer;
  final bool enableLogging;
  final bool routeSipToGsm;
  // ...
}

// Model should map from flat JSON structure
class GatewayConfigModel {
  final String sipUsername;
  final String sipPassword;
  final String sipDomain;
  final String? smppSystemId;
  final String? smppPassword;
  // ...
  
  GatewayConfig toEntity() {
    return GatewayConfig(
      sipAccount: SipAccount(
        username: sipUsername,
        password: sipPassword,
        domain: sipDomain,
        // ...
      ),
      smppConfig: smppSystemId != null 
        ? SmppConfig(systemId: smppSystemId, ...) 
        : null,
      autoAnswer: autoAnswer,
      // ...
    );
  }
}
```

## Edge Cases

### 1. Migration from Old to New Config

If users have existing configuration stored using the old format, the `GatewayRepositoryImpl` should handle migration:

```dart
// In getConfig():
final oldConfig = await localDataSource.getGatewayConfig();
if (oldConfig != null && oldConfig.containsKey('sipConfig')) {
  // Migrate old format to new format
  return _migrateOldConfig(oldConfig);
}
```

### 2. Null Safety in SMPP Config

The new `GatewayConfig` has optional `SmppConfig`. All code accessing it must handle null:

```dart
// Good:
final smppEnabled = config.smppConfig != null;
final systemId = config.smppConfig?.systemId;

// Bad (will crash):
final systemId = config.smppConfig!.systemId;  // May throw if null
```

### 3. Stream Subscriptions

Providers must properly dispose stream subscriptions to prevent memory leaks:

```dart
@override
void dispose() {
  _statusSubscription?.cancel();
  _routingSubscription?.cancel();
  super.dispose();
}
```

## Error Handling Strategy

### Repository Layer

Repositories return `Either<Failure, T>` pattern:

```dart
@override
AsyncGatewayResult<void> initialize(GatewayConfig config) async {
  try {
    await _gatewayService.initialize(config);
    return Right(unit);
  } on GatewayException catch (e) {
    return Left(Failure(e.message));
  } catch (e) {
    return Left(Failure('Unexpected error: $e'));
  }
}
```

### Use Case Layer

Use cases wrap repository calls with additional validation:

```dart
class InitializeGateway {
  final GatewayRepository repository;
  
  AsyncGatewayResult<void> call(GatewayConfig config) async {
    // Validation
    if (config.sipAccount.username.isEmpty) {
      return Left(Failure('Username is required'));
    }
    
    return await repository.initialize(config);
  }
}
```

### Provider Layer

Providers convert `Either` to async state updates:

```dart
Future<void> initializeGateway(GatewayConfig config) async {
  _state = _state.copyWith(isLoading: true);
  notifyListeners();
  
  final result = await _repository.initialize(config);
  
  result.fold(
    (failure) {
      _state = _state.copyWith(
        isLoading: false,
        error: failure.message,
      );
    },
    (_) {
      _state = _state.copyWith(
        isLoading: false,
        error: null,
      );
    },
  );
  notifyListeners();
}
```

## Testing Strategy

### Unit Tests

1. **Entity Tests**: Verify `copyWith`, `toJson`, `fromJson` methods
2. **Repository Tests**: Mock services, test `Either` return values
3. **Use Case Tests**: Test validation logic and repository calls
4. **Provider Tests**: Test state transitions and notification

### Integration Tests

1. **Repository + Service**: Test repository with real service mocks
2. **Use Case + Repository**: Test full use case flow
3. **Provider + Use Case**: Test UI state management

## Migration Plan

### Phase 1: Remove Duplicates
1. Delete `lib/data/repositories/gateway_repository.dart`
2. Delete `lib/domain/entities/gateway_config_entity.dart`
3. Delete `lib/domain/entities/gateway_entity.dart`
4. Remove duplicate `SmppConfig` from `lib/services/sms_service.dart`

### Phase 2: Fix Imports
1. Fix `gateway_provider.dart` import path
2. Fix `sip_provider.dart` import path

### Phase 3: Fix Dependency Injection
1. Remove duplicate `GatewayRepository` registration
2. Verify all registrations use correct implementations

### Phase 4: Update Models
1. Update `GatewayConfigModel` to use new entity
2. Test JSON serialization/deserialization

### Phase 5: Build & Test
1. Run `flutter clean`
2. Run `flutter pub get`
3. Run `flutter run` on Android device
4. Fix any remaining compilation errors

## Success Criteria

- [ ] `flutter build apk` completes without errors
- [ ] `flutter run -d <device>` launches app successfully
- [ ] No import errors in IDE
- [ ] All repository interfaces properly implemented
- [ ] Dependency injection resolves all dependencies

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]
