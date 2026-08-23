# ADR 002: Dependency Injection

## Status

**PROPOSED** → DRAFT

## Context

The GOSTsimbox Gateway requires a dependency injection system to manage dependencies between layers and services. The system has:

- Multiple services (Gateway, SIP, SMS, Telephony, Theme, etc.)
- Repository implementations with multiple dependencies
- Use cases that depend on repositories
- External dependencies (SharedPreferences, HTTP Client, Logger)
- Need for testability with mock dependencies

### Requirements

1. **Simple API** - Easy to register and resolve dependencies
2. **Lazy initialization** - Services should initialize on first use
3. **Singleton support** - Single instance for service classes
4. **Test support** - Easy to register mocks for testing
5. **Type safety** - Compile-time type checking
6. **Minimal boilerplate** - No code generation required

## Decision

We WILL use **get_it** as our dependency injection framework.

### Configuration

```dart
// lib/core/di/dependency_injection.dart

final GetIt getIt = GetIt.instance;

class DependencyInjection {
  static Future<void> init() async {
    // External dependencies
    await _registerExternalDependencies();
    
    // Services
    _registerServices();
    
    // Data sources
    _registerDataSources();
    
    // Repositories
    _registerRepositories();
    
    // Use cases
    _registerUseCases();
  }
}
```

### Registration Patterns

**Singleton (eager initialization):**
```dart
getIt.registerSingleton<SharedPreferences>(sharedPreferences);
```

**Lazy Singleton (initialized on first use):**
```dart
getIt.registerLazySingleton<Logger>(() => Logger());
getIt.registerLazySingleton<StorageService>(
  () => StorageService(getIt<SharedPreferences>()),
);
```

**Factory (new instance each time):**
```dart
getIt.registerFactory<UseCase>(() => UseCase(getIt<Repository>()));
```

### Registration Categories

1. **External Dependencies**
   - SharedPreferences
   - HTTP Client
   - Logger

2. **Core Services**
   - StorageService
   - NetworkService
   - DeviceService
   - PermissionService

3. **Business Services**
   - ThemeService
   - LocalizationService
   - SecurityService
   - ApiService

4. **Repositories**
   - GatewayRepository
   - SettingsRepository
   - AnalyticsRepository

5. **Use Cases**
   - GatewayUseCases
   - SettingsUseCases
   - AnalyticsUseCases

### Lifecycle Management

```dart
class DependencyLifecycleManager {
  static Future<void> initializeServices() async {
    // Initialize analytics
    final analytics = getIt<AnalyticsService>();
    await analytics.initialize();
    
    // Initialize notifications
    final notifications = getIt<NotificationService>();
    await notifications.initialize();
  }
  
  static Future<void> disposeServices() async {
    await getIt<AnalyticsService>().dispose();
    getIt<http.Client>().close();
  }
}
```

## Consequences

### Positive

1. **Simplicity** - get_it has a minimal, intuitive API
2. **No code generation** - No build_runner required for DI
3. **Type safety** - Compile-time type checking
4. **Lazy initialization** - Services initialize on demand
5. **Test-friendly** - Easy to register mocks
6. **Lightweight** - Minimal overhead
7. **Well-maintained** - Active development and community support

### Negative

1. **Service locator pattern** - Some consider it an anti-pattern vs pure DI
2. **Global state** - getIt is a global singleton
3. **Runtime errors** - Missing registrations cause runtime errors
4. **No constructor injection** - Must manually wire dependencies

### Alternatives Considered

**injectable + get_it:**
- Pros: Code generation, constructor injection
- Cons: Build complexity, code generation time
- Decision: Too much complexity for current needs

**Provider/Riverpod:**
- Pros: Flutter integration, widget-tree based
- Cons: Not suitable for non-UI dependencies
- Decision: Use Provider for UI state, get_it for services

**Manual DI:**
- Pros: Full control, no dependencies
- Cons: Verbose, error-prone
- Decision: get_it provides better developer experience

## Compliance

- All services MUST be registered in DependencyInjection
- Dependencies MUST be registered before dependents
- Use cases MUST depend on repository interfaces, not implementations
- External dependencies MUST be registered first
- Test files MUST register mock dependencies

## Related Decisions

- ADR 001: Clean Architecture (layer structure)
- ADR 003: State Management (Provider for UI state)
- ADR 005: Service Orchestration (GatewayService patterns)

## References

- get_it package: https://pub.dev/packages/get_it
- get_it documentation
- Dependency Injection patterns

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)  
**Status**: DRAFT - Pending review
