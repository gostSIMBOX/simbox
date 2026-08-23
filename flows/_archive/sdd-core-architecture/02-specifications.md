# Specifications: Core Architecture

## System Architecture

### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ screens/ │  │ widgets/ │  │providers/│  │  theme/  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ entities │  │repositories││ usecases │  │exceptions│    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
├─────────────────────────────────────────────────────────────┤
│                       Data Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │datasources│ │repositories││ models/  │  │services/ │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
├─────────────────────────────────────────────────────────────┤
│                        Core Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   di/    │  │  error/  │  │  utils/  │  │constants/│    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. Dependency Injection (lib/core/di/)

**Component**: `DependencyInjection` class  
**Purpose**: Centralized service registration and lifecycle management

#### Registration Categories:

```dart
// External Dependencies
- SharedPreferences (singleton)
- http.Client (lazySingleton)
- Logger (lazySingleton with PrettyPrinter)

// Core Services
- StorageService (lazySingleton)
- NetworkService (lazySingleton)
- DeviceService (lazySingleton)
- PermissionService (lazySingleton)

// Business Services
- ThemeService (lazySingleton, depends on StorageService)
- LocalizationService (lazySingleton, depends on StorageService)
- SecurityService (lazySingleton)
- CacheService (lazySingleton, depends on StorageService)
- ApiService (lazySingleton, depends on Client, NetworkService, Logger)
- NotificationService (lazySingleton)
- AnalyticsService (lazySingleton, complex deps)

// Repositories
- GatewayRepository (lazySingleton)
- SettingsRepository (lazySingleton)
- AnalyticsRepository (lazySingleton)

// Use Cases
- GatewayUseCases (lazySingleton)
- SettingsUseCases (lazySingleton)
- AnalyticsUseCases (lazySingleton)
```

#### Lifecycle Management:

```dart
DependencyLifecycleManager:
  - initializeServices()  // App startup
  - disposeServices()     // App shutdown
  - checkServicesHealth() // Health monitoring
```

### 2. Error Handling (lib/core/error/)

**Component**: `ErrorHandler` class  
**Purpose**: Centralized error capture, logging, and user notification

#### Error Categories:

| Category | Handler Method | Behavior |
|----------|---------------|----------|
| Application | `handleError()` | Log, analytics, user message |
| Network | `handleNetworkError()` | Log, user message with endpoint |
| Validation | `handleValidationError()` | Log, field-specific message |
| Authentication | `handleAuthError()` | Log, redirect to login |
| Permission | `handlePermissionError()` | Log, permission request message |

#### Error Storage:

```dart
Key: 'error_logs'
Max Entries: 100
Retention: 24 hours for critical error detection
Format: JSON with timestamp, error, stackTrace
```

#### UI Integration:

```dart
ErrorBoundary Widget:
  - Catches Flutter errors via FlutterError.onError
  - Displays error widget with retry option
  - Logs errors via ErrorHandler
```

### 3. State Management (lib/main.dart)

**Pattern**: MultiProvider  
**Core Services**:

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

### 4. Entry Point Flow (lib/main.dart)

```
main()
  │
  ├─► WidgetsFlutterBinding.ensureInitialized()
  ├─► SystemChrome.setPreferredOrientations([portrait])
  ├─► SystemChrome.setSystemUIOverlayStyle()
  └─► runApp(GOSTsimboxApp)
       │
       └─► MultiProvider setup
            │
            └─► MaterialApp with theme
                 │
                 └─► SetupCheckScreen (splash)
                      │
                      ├─► Load configuration
                      ├─► Funny loading messages
                      └─► Navigate:
                           - config exists → DashboardScreen
                           - no config → SetupScreen
```

### 5. Theme Configuration

```dart
ColorScheme:
  seedColor: #1E88E5 (blue)
  brightness: Brightness.light

Material3: true

Customizations:
  - AppBar: centerTitle, elevation: 0
  - Card: elevation: 2, borderRadius: 12
  - ElevatedButton: borderRadius: 8, padding: 24x12
```

## Data Flow

### Service Registration Flow

```
DependencyInjection.init()
       │
       ▼
_registerExternalDependencies()
  - SharedPreferences.getInstance()
  - http.Client registration
  - Logger with PrettyPrinter
       │
       ▼
_registerServices()
  - Core services (Storage, Network, Device, Permission)
  - Business services (Theme, Localization, Security, Cache, API)
  - Notification, Analytics
       │
       ▼
_registerDataSources()
  - LocalDataSource
  - RemoteDataSource
       │
       ▼
_registerRepositories()
  - GatewayRepository
  - SettingsRepository
  - AnalyticsRepository
       │
       ▼
_registerUseCases()
  - GatewayUseCases
  - SettingsUseCases
  - AnalyticsUseCases
```

### Error Handling Flow

```
Error Occurs
       │
       ▼
FlutterError.onError / try-catch
       │
       ▼
ErrorHandler.handleError()
       │
       ├─► Logger.e() (console output)
       ├─► _saveErrorToLog() (SharedPreferences)
       ├─► _sendErrorToAnalytics() (analytics tracking)
       └─► _showUserFriendlyError() (SnackBar)
```

## Interfaces

### Repository Pattern

```dart
// Domain Layer (Interface)
abstract class GatewayRepository {
  Future<GatewayConfig> getConfig();
  Future<void> saveConfig(GatewayConfig config);
  Future<GatewayStatus> getStatus();
  // ...
}

// Data Layer (Implementation)
class GatewayRepositoryImpl implements GatewayRepository {
  final LocalDataSource local;
  final RemoteDataSource remote;
  final Logger logger;
  
  // Implementation...
}
```

### Use Case Pattern

```dart
// Domain Layer
class GatewayUseCases {
  final GatewayRepository repository;
  
  GatewayUseCases(this.repository);
  
  Future<Result<GatewayConfig>> loadConfig() async {
    try {
      final config = await repository.getConfig();
      return Result.success(config);
    } catch (e) {
      return Result.failure(e);
    }
  }
}
```

## Testing Strategy

### Unit Tests (Domain Layer)

```dart
// Test use cases in isolation
test('GatewayUseCases.loadConfig returns config', () async {
  final mockRepo = MockGatewayRepository();
  final useCase = GatewayUseCases(mockRepo);
  
  when(mockRepo.getConfig()).thenAnswer(...);
  
  final result = await useCase.loadConfig();
  
  expect(result.isSuccess, true);
});
```

### Integration Tests (Data Layer)

```dart
// Test repository with real data sources
test('GatewayRepository saves and loads config', () async {
  final repository = GatewayRepositoryImpl(
    localDataSource,
    remoteDataSource,
    logger,
  );
  
  await repository.saveConfig(testConfig);
  final loaded = await repository.getConfig();
  
  expect(loaded, equals(testConfig));
});
```

### Widget Tests (Presentation Layer)

```dart
// Test UI components with mocked providers
testWidgets('Dashboard shows gateway status', (tester) async {
  await tester.pumpWidget(
    MultiProvider(
      providers: [
        Provider<GatewayService>.value(value: mockGatewayService),
      ],
      child: DashboardScreen(),
    ),
  );
  
  expect(find.text('Gateway Active'), findsOneWidget);
});
```

## Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| provider | ^6.1.2 | State management |
| get_it | ^7.6.7 | Dependency injection |
| shared_preferences | ^2.2.2 | Local storage |
| logger | ^2.0.2+1 | Logging |
| http | ^1.2.1 | HTTP client |
| dartz | ^0.10.1 | Functional programming (Either type) |
| equatable | ^2.0.5 | Value equality |

### UI Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| flutter_svg | ^2.0.10+1 | SVG rendering |
| google_fonts | ^6.2.2 | Custom fonts |
| fl_chart | ^0.68.0 | Charts/graphs |

### Platform Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| device_info_plus | ^10.1.0 | Device information |
| permission_handler | ^11.3.1 | Runtime permissions |
| connectivity_plus | ^5.0.2 | Network connectivity |
| workmanager | ^0.8.0 | Background tasks |

## Configuration

### App Configuration

```yaml
name: flutter_gsm_sip_gateway
version: 3.0.0+300
sdk: ^3.8.1
license: NativeMindNONC
```

### Android Configuration

```yaml
minSdkVersion: 21
targetSdkVersion: latest
```

---

**Status**: DRAFT  
**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)  
**Related**: 01-requirements.md
