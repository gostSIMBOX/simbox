# Plan: Core Architecture Implementation

## Overview

This plan implements the four-layer Clean Architecture for the GOSTsimbox Android Gateway, establishing the foundation for all subsequent development.

## Implementation Strategy

**Approach**: Bottom-up implementation (Core → Data → Domain → Presentation)

**Rationale**: Lower layers have no dependencies on higher layers, enabling clean incremental implementation.

---

## Task Breakdown

### Phase 1: Core Layer (Foundation)

#### Task 1.1: Dependency Injection (`lib/core/di/`)

**Files to Create:**
- `lib/core/di/dependency_injection.dart`
- `lib/core/di/dependency_lifecycle_manager.dart`

**Implementation Steps:**
1. Create `DependencyInjection` singleton class
2. Register external dependencies:
   - `SharedPreferences` (singleton, initialized at startup)
   - `http.Client` (lazySingleton)
   - `Logger` with `PrettyPrinter` (lazySingleton)
3. Register core services (lazySingleton):
   - `StorageService`, `NetworkService`, `DeviceService`, `PermissionService`
4. Register business services (lazySingleton):
   - `ThemeService`, `LocalizationService`, `SecurityService`, `CacheService`, `ApiService`
   - `NotificationService`, `AnalyticsService`
5. Register repositories (lazySingleton):
   - `GatewayRepository`, `SettingsRepository`, `AnalyticsRepository`
6. Register use cases (lazySingleton):
   - `GatewayUseCases`, `SettingsUseCases`, `AnalyticsUseCases`
7. Create `DependencyLifecycleManager`:
   - `initializeServices()` method
   - `disposeServices()` method
   - `checkServicesHealth()` method

**Dependencies:**
- `get_it: ^7.6.7`
- `logger: ^2.0.2+1`
- `shared_preferences: ^2.2.2`

**Acceptance Criteria:**
- [ ] All dependencies registered with correct lifecycle
- [ ] No circular dependencies
- [ ] Services can access their declared dependencies
- [ ] Lifecycle manager can initialize and dispose all services

---

#### Task 1.2: Error Handling (`lib/core/error/`)

**Files to Create:**
- `lib/core/error/error_handler.dart`
- `lib/core/error/error_boundary.dart`
- `lib/core/error/exceptions.dart`
- `lib/core/error/failures.dart`

**Implementation Steps:**
1. Create `ErrorHandler` singleton class with:
   - `handleError(Object error, StackTrace stack)` method
   - Category-specific handlers:
     - `handleNetworkError()`
     - `handleValidationError()`
     - `handleAuthError()`
     - `handlePermissionError()`
2. Implement error storage:
   - Save to SharedPreferences with key `'error_logs'`
   - Max 100 entries, FIFO eviction
   - 24-hour retention with cleanup on each save
3. Create exception classes:
   - `AppException` (base)
   - `NetworkException`, `ValidationException`, `AuthException`, `PermissionException`
4. Create failure classes (for functional error handling with dartz):
   - `Failure` (base)
   - `NetworkFailure`, `ValidationFailure`, `AuthFailure`, `PermissionFailure`
5. Implement `ErrorBoundary` widget:
   - Wrap `FlutterError.onError`
   - Display error UI with retry option
   - Log via `ErrorHandler`

**Dependencies:**
- `dartz: ^0.10.1` (for Either type)
- `shared_preferences: ^2.2.2`

**Acceptance Criteria:**
- [ ] All error categories handled appropriately
- [ ] Errors logged to console, storage, and analytics
- [ ] User-friendly messages displayed
- [ ] ErrorBoundary catches and handles Flutter errors

---

#### Task 1.3: Utilities (`lib/core/utils/`)

**Files to Create:**
- `lib/core/utils/result.dart` (Either wrapper)
- `lib/core/utils/extensions.dart`

**Implementation Steps:**
1. Create `Result<T>` class using dartz Either:
   - `Result.success(T data)`
   - `Result.failure(Object error)`
   - `isSuccess`, `isFailure` getters
   - `fold()` method for handling both cases
2. Create useful extensions:
   - DateTime formatting extensions
   - String validation extensions
   - Context extensions for theme/colors

**Dependencies:**
- `dartz: ^0.10.1`

**Acceptance Criteria:**
- [ ] Result type works with async operations
- [ ] Extensions compile and work as expected

---

#### Task 1.4: Constants (`lib/core/constants/`)

**Files to Create:**
- `lib/core/constants/app_constants.dart`
- `lib/core/constants/storage_keys.dart`
- `lib/core/constants/api_endpoints.dart`

**Implementation Steps:**
1. Define app-wide constants:
   - App name, version
   - Default timeouts
   - UI constants
2. Define storage keys:
   - `'gateway_config'`, `'error_logs'`, `'theme_mode'`, etc.
3. Define API endpoint constants:
   - Default SIP server
   - Default SMPP server

**Acceptance Criteria:**
- [ ] All magic strings/numbers extracted to constants
- [ ] Constants organized logically

---

### Phase 2: Data Layer

#### Task 2.1: Models (`lib/data/models/`)

**Files to Create:**
- `lib/data/models/gateway_config.dart`
- `lib/data/models/gateway_status.dart`
- `lib/data/models/call_info.dart`
- `lib/data/models/log_entry.dart`

**Implementation Steps:**
1. Create immutable model classes with:
   - `final` fields
   - `fromMap(Map<String, dynamic>)` factory constructor
   - `toMap()` method for serialization
   - `copyWith()` method for updates
   - `Equatable` mixin for value equality
2. Define models:
   - `GatewayConfig`: SIP credentials, routing options
   - `GatewayStatus`: Connection states, statistics
   - `CallInfo`: Call details and state
   - `LogEntry`: Log message with level and timestamp

**Dependencies:**
- `equatable: ^2.0.5`

**Acceptance Criteria:**
- [ ] All models are immutable
- [ ] Serialization/deserialization works
- [ ] Equality comparison works correctly

---

#### Task 2.2: Data Sources (`lib/data/datasources/`)

**Files to Create:**
- `lib/data/datasources/local_data_source.dart`
- `lib/data/datasources/remote_data_source.dart`

**Implementation Steps:**
1. Create `LocalDataSource`:
   - `Future<String> getString(String key)`
   - `Future<void> setString(String key, String value)`
   - `Future<bool> containsKey(String key)`
   - `Future<void> remove(String key)`
   - `Future<void> clear()`
2. Create `RemoteDataSource`:
   - HTTP client wrapper methods
   - SIP API methods (to be implemented by sdd-sip-core)
   - SMPP API methods (to be implemented by sdd-sms-smpp)

**Dependencies:**
- `shared_preferences: ^2.2.2`
- `http: ^1.2.1`

**Acceptance Criteria:**
- [ ] LocalDataSource wraps SharedPreferences correctly
- [ ] RemoteDataSource has HTTP client integration
- [ ] Error handling in both data sources

---

#### Task 2.3: Repositories (`lib/data/repositories/`)

**Files to Create:**
- `lib/data/repositories/gateway_repository_impl.dart`
- `lib/data/repositories/settings_repository_impl.dart`
- `lib/data/repositories/analytics_repository_impl.dart`

**Implementation Steps:**
1. Implement repository classes that:
   - Implement domain layer interfaces
   - Use data sources for data access
   - Transform data models to domain entities
   - Handle errors and return Result types
2. Each repository implements:
   - CRUD operations for its domain
   - Data transformation
   - Error handling

**Acceptance Criteria:**
- [ ] Repositories implement domain interfaces
- [ ] Data transformation works correctly
- [ ] Errors properly converted to failures

---

### Phase 3: Domain Layer

#### Task 3.1: Entities (`lib/domain/entities/`)

**Files to Create:**
- `lib/domain/entities/gateway_config.dart`
- `lib/domain/entities/gateway_status.dart`
- `lib/domain/entities/call_routing.dart`

**Implementation Steps:**
1. Create pure Dart entities (no Flutter dependencies):
   - Business logic entities
   - Value objects
   - Extend Equatable for value equality
2. Entities should be framework-agnostic

**Dependencies:**
- `equatable: ^2.0.5`

**Acceptance Criteria:**
- [ ] Entities have no external dependencies
- [ ] Business logic encapsulated in entities
- [ ] Equality comparison works

---

#### Task 3.2: Repositories (Interfaces) (`lib/domain/repositories/`)

**Files to Create:**
- `lib/domain/repositories/gateway_repository.dart`
- `lib/domain/repositories/settings_repository.dart`
- `lib/domain/repositories/analytics_repository.dart`

**Implementation Steps:**
1. Define abstract repository interfaces:
   - `GatewayRepository`: config and status operations
   - `SettingsRepository`: settings persistence
   - `AnalyticsRepository`: analytics tracking
2. Define method signatures returning `Future<Result<T>>`

**Acceptance Criteria:**
- [ ] Interfaces define all required operations
- [ ] Return types use Result pattern
- [ ] No implementation details in interfaces

---

#### Task 3.3: Use Cases (`lib/domain/usecases/`)

**Files to Create:**
- `lib/domain/usecases/gateway_usecases.dart`
- `lib/domain/usecases/settings_usecases.dart`
- `lib/domain/usecases/analytics_usecases.dart`
- `lib/domain/usecases/base_use_case.dart`

**Implementation Steps:**
1. Create `BaseUseCase<Params, Result>` abstract class:
   - `Future<Either<Failure, Result>> call(Params params)`
2. Implement specific use cases:
   - `LoadGatewayConfig`, `SaveGatewayConfig`, `GetGatewayStatus`
   - `LoadSettings`, `SaveSettings`
   - `TrackEvent`, `GetAnalytics`
3. Each use case:
   - Takes parameters (or `void` for no params)
   - Returns `Future<Either<Failure, Result>>`
   - Contains single business operation

**Dependencies:**
- `dartz: ^0.10.1`

**Acceptance Criteria:**
- [ ] Use cases are single-purpose
- [ ] Parameters properly typed
- [ ] Error handling consistent

---

#### Task 3.4: Exceptions (`lib/domain/exceptions/`)

**Files to Create:**
- `lib/domain/exceptions/domain_exceptions.dart`

**Implementation Steps:**
1. Create domain-specific exceptions:
   - `GatewayException`
   - `ConfigNotFoundException`
   - `InvalidConfigException`
   - `ServiceUnavailableException`

**Acceptance Criteria:**
- [ ] Domain exceptions extend Exception
- [ ] Clear exception hierarchy

---

### Phase 4: Presentation Layer

#### Task 4.1: State Management Setup (`lib/`)

**Files to Modify:**
- `lib/main.dart`

**Implementation Steps:**
1. Set up MultiProvider in main.dart:
   ```dart
   MultiProvider(
     providers: [
       Provider<GatewayService>.value(value: GatewayService()),
       Provider<SipService>.value(value: SipService()),
       Provider<SmsService>.value(value: SmsService()),
       Provider<TelephonyService>.value(value: TelephonyService()),
     ],
     child: MaterialApp(...),
   )
   ```
2. Ensure services are initialized via DI before runApp

**Acceptance Criteria:**
- [ ] Providers set up correctly
- [ ] Services accessible via Provider.of/Consumer
- [ ] No provider missing errors

---

#### Task 4.2: Theme Configuration (`lib/presentation/theme/`)

**Files to Create:**
- `lib/presentation/theme/app_theme.dart`
- `lib/presentation/theme/app_colors.dart`

**Implementation Steps:**
1. Create `AppColors` with color scheme:
   - seedColor: #1E88E5 (blue)
   - Light theme colors
   - Dark theme colors
2. Create `AppTheme` with:
   - `ThemeData.light()` and `ThemeData.dark()`
   - Material3 configuration
   - Custom app bar, card, button themes

**Acceptance Criteria:**
- [ ] Theme follows Material3
- [ ] Colors match specifications
- [ ] Dark/light theme support

---

#### Task 4.3: Entry Point (`lib/main.dart`)

**Files to Modify:**
- `lib/main.dart`

**Implementation Steps:**
1. Implement main() flow:
   - `WidgetsFlutterBinding.ensureInitialized()`
   - Set preferred orientations (portrait)
   - Set system UI overlay style
   - Initialize DependencyInjection
   - runApp(GOSTsimboxApp)
2. Create GOSTsimboxApp widget:
   - MultiProvider setup
   - MaterialApp with theme
   - Initial route: SetupCheckScreen

**Acceptance Criteria:**
- [ ] App initializes without errors
- [ ] DI initialized before first widget
- [ ] Theme applied correctly

---

## File Structure (Target)

```
lib/
├── main.dart
├── core/
│   ├── di/
│   │   ├── dependency_injection.dart
│   │   └── dependency_lifecycle_manager.dart
│   ├── error/
│   │   ├── error_handler.dart
│   │   ├── error_boundary.dart
│   │   ├── exceptions.dart
│   │   └── failures.dart
│   ├── utils/
│   │   ├── result.dart
│   │   └── extensions.dart
│   └── constants/
│       ├── app_constants.dart
│       ├── storage_keys.dart
│       └── api_endpoints.dart
├── data/
│   ├── models/
│   │   ├── gateway_config.dart
│   │   ├── gateway_status.dart
│   │   ├── call_info.dart
│   │   └── log_entry.dart
│   ├── datasources/
│   │   ├── local_data_source.dart
│   │   └── remote_data_source.dart
│   └── repositories/
│       ├── gateway_repository_impl.dart
│       ├── settings_repository_impl.dart
│       └── analytics_repository_impl.dart
├── domain/
│   ├── entities/
│   │   ├── gateway_config.dart
│   │   ├── gateway_status.dart
│   │   └── call_routing.dart
│   ├── repositories/
│   │   ├── gateway_repository.dart
│   │   ├── settings_repository.dart
│   │   └── analytics_repository.dart
│   ├── usecases/
│   │   ├── base_use_case.dart
│   │   ├── gateway_usecases.dart
│   │   ├── settings_usecases.dart
│   │   └── analytics_usecases.dart
│   └── exceptions/
│       └── domain_exceptions.dart
└── presentation/
    ├── theme/
    │   ├── app_theme.dart
    │   └── app_colors.dart
    ├── screens/
    │   └── (existing screens)
    └── widgets/
        └── (existing widgets)
```

---

## Dependencies to Add

Run after implementation:
```bash
flutter pub add provider get_it shared_preferences logger http dartz equatable
flutter pub add device_info_plus permission_handler connectivity_plus
```

---

## Testing Strategy

### Unit Tests (Domain Layer)
- Test use cases with mocked repositories
- Test entities for business logic
- Test repositories interfaces

### Integration Tests (Data Layer)
- Test repository implementations with real data sources
- Test data source operations

### Widget Tests (Presentation Layer)
- Test UI components with mocked providers

---

## Rollback Considerations

- Each phase is independent and can be rolled back
- Core layer changes require full regression testing
- Domain layer changes may affect multiple repositories

---

## Estimated Complexity

| Phase | Tasks | Complexity | Estimated Time |
|-------|-------|------------|----------------|
| Core Layer | 4 | Medium | 2-3 hours |
| Data Layer | 3 | Medium | 2-3 hours |
| Domain Layer | 4 | Low-Medium | 1-2 hours |
| Presentation Layer | 3 | Low | 1 hour |
| **Total** | **14** | **Medium** | **6-9 hours** |

---

## Success Criteria

- [ ] All four layers implemented and organized
- [ ] DI working with all services registered
- [ ] Error handling centralized and functional
- [ ] Models immutable with serialization
- [ ] Repository pattern implemented
- [ ] Use cases encapsulate business logic
- [ ] State management via Provider working
- [ ] Theme applied correctly
- [ ] App starts without errors
- [ ] Code follows SOLID principles

---

**Status**: DRAFT  
**Created**: 2026-03-05  
**Related**: 01-requirements.md, 02-specifications.md
