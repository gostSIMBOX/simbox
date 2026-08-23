# Plan: Split Library and Example (v2.0)

> Version: 2.0
> Status: DRAFT
> Last Updated: 2026-03-15
> Goal: Publication on pub.dev

## Overview

**Previous attempt (v1.0)**: Created plugin structure but didn't move actual code
**This plan (v2.0)**: Move ALL code from legacy/ to appropriate locations

## Target Structure

```
flutter_gsmsip/
├── lib/                          # LIBRARY - Public API
│   ├── flutter_gsmsip.dart       # Main export
│   ├── src/
│   │   ├── domain/               # Business logic
│   │   │   ├── entities/         # Core data models
│   │   │   ├── repositories/     # Interface definitions
│   │   │   ├── usecases/         # Business use cases
│   │   │   └── exceptions/       # Domain exceptions
│   │   ├── data/                 # Implementation
│   │   │   ├── repositories/     # Repository implementations
│   │   │   ├── services/         # Service wrappers
│   │   │   ├── datasources/      # Data sources
│   │   │   └── models/           # Data models (DTOs)
│   │   └── gsm_sip_bridge.dart   # Main API facade
│   ├── android/
│   │   └── src/main/kotlin/org/telon/flutter_gsmsip/
│   │       ├── FlutterGsmsipPlugin.kt    # Plugin entry
│   │       ├── SipService.kt             # Native SIP
│   │       ├── GsmService.kt             # Native GSM
│   │       ├── SmppService.kt            # Native SMPP
│   │       ├── HeadlessService.kt        # Background service
│   │       └── ... (other native code)
│   └── pubspec.yaml              # Library definition
│
├── example/                      # EXAMPLE APP - Demo
│   ├── lib/
│   │   ├── main.dart             # App entry
│   │   ├── presentation/         # UI layer
│   │   │   ├── screens/          # All screens
│   │   │   ├── widgets/          # Reusable widgets
│   │   │   ├── providers/        # State management
│   │   │   └── theme/            # Theme config
│   │   ├── services/             # App-specific services
│   │   │   ├── di/               # Dependency injection
│   │   │   ├── storage/          # SharedPreferences
│   │   │   └── navigation/       # App navigation
│   │   └── utils/                # App utilities
│   └── pubspec.yaml              # Depends on flutter_gsmsip
│
└── legacy/                       # ARCHIVE - Reference only
    └── (original code - keep for reference)
```

## Task Breakdown

### Phase 1: Analyze Legacy Code (30 min)

#### Task 1.1: Catalog Legacy Files
```bash
# Count files in each layer
find legacy/lib/domain -name "*.dart" | wc -l
find legacy/lib/data -name "*.dart" | wc -l
find legacy/lib/presentation -name "*.dart" | wc -l
find legacy/android/app/src/main/kotlin -name "*.kt" | wc -l
```
- **Output**: File counts for planning
- **Status**: ⏳ Pending

#### Task 1.2: Identify PJSIP Native Libraries
```bash
# Find .so files in legacy
find legacy -name "*.so"
```
- **Output**: List of native libraries to copy
- **Status**: ⏳ Pending

---

### Phase 2: Move Domain Layer to Library (30 min)

#### Task 2.1: Copy Domain Entities
- **Source**: `legacy/lib/domain/entities/*.dart`
- **Destination**: `lib/src/domain/entities/`
- **Files**: ~11 entity files
- **Status**: ⏳ Pending

#### Task 2.2: Copy Domain Repositories
- **Source**: `legacy/lib/domain/repositories/*.dart`
- **Destination**: `lib/src/domain/repositories/`
- **Status**: ⏳ Pending

#### Task 2.3: Copy Domain Use Cases
- **Source**: `legacy/lib/domain/usecases/*.dart`
- **Destination**: `lib/src/domain/usecases/`
- **Status**: ⏳ Pending

#### Task 2.4: Copy Domain Exceptions
- **Source**: `legacy/lib/domain/exceptions/*.dart`
- **Destination**: `lib/src/domain/exceptions/`
- **Status**: ⏳ Pending

---

### Phase 3: Move Data Layer to Library (45 min)

#### Task 3.1: Copy Data Repositories
- **Source**: `legacy/lib/data/repositories/*.dart`
- **Destination**: `lib/src/data/repositories/`
- **Status**: ⏳ Pending

#### Task 3.2: Copy Data Services
- **Source**: `legacy/lib/data/services/*.dart`
- **Destination**: `lib/src/data/services/`
- **Status**: ⏳ Pending

#### Task 3.3: Copy Data Sources
- **Source**: `legacy/lib/data/datasources/`, `legacy/lib/data/sources/`
- **Destination**: `lib/src/data/datasources/`, `lib/src/data/sources/`
- **Status**: ⏳ Pending

#### Task 3.4: Copy Data Models
- **Source**: `legacy/lib/data/models/*.dart`
- **Destination**: `lib/src/data/models/`
- **Status**: ⏳ Pending

#### Task 3.5: Copy Core Services
- **Source**: `legacy/lib/services/*.dart`
- **Destination**: `lib/src/data/services/`
- **Includes**: `sms_service.dart`, `smpp_service.dart`, `telephony_service.dart`
- **Status**: ⏳ Pending

---

### Phase 4: Move Native Kotlin Code (45 min)

#### Task 4.1: Copy Kotlin Files
- **Source**: `legacy/android/app/src/main/kotlin/org/telon/flutter_gsm_sip_gateway/`
- **Destination**: `flutter_gsmsip/android/src/main/kotlin/org/telon/flutter_gsmsip/`
- **Files**:
  - `MainActivity.kt`
  - `BootUpReceiver.kt`
  - `GatewayDialerModule.kt`
  - `HeadlessModule.kt`
  - `HeadlessService.kt`
  - `HeadlessEventService.kt`
  - `ReplaceDialerModule.kt`
- **Status**: ⏳ Pending

#### Task 4.2: Update Package Names
- **Change**: `org.telon.flutter_gsm_sip_gateway` → `org.telon.flutter_gsmsip`
- **Files**: All Kotlin files
- **Status**: ⏳ Pending

#### Task 4.3: Copy PJSIP Native Libraries
- **Source**: `legacy/android/app/src/main/jniLibs/` or `legacy/android/libs/`
- **Destination**: `flutter_gsmsip/android/src/main/jniLibs/`
- **Status**: ⏳ Pending (need to locate .so files)

#### Task 4.4: Update Android Build Config
- **File**: `flutter_gsmsip/android/build.gradle`
- **Add**: Kotlin coroutines, gson, PJSIP dependencies
- **Status**: ⏳ Pending

---

### Phase 5: Create Library Public API (30 min)

#### Task 5.1: Update Main Export File
- **File**: `lib/flutter_gsmsip.dart`
- **Exports**:
  ```dart
  // Domain
  export 'src/domain/entities/*.dart';
  export 'src/domain/repositories/*.dart';
  export 'src/domain/usecases/*.dart';
  
  // Data
  export 'src/data/repositories/*.dart';
  export 'src/data/services/*.dart';
  
  // Main API
  export 'src/gsm_sip_bridge.dart';
  ```
- **Status**: ⏳ Pending

#### Task 5.2: Create GsmSipBridge Facade
- **File**: `lib/src/gsm_sip_bridge.dart`
- **Methods**:
  - `initialize()`
  - `makeCall(destination)`
  - `sendSms(destination, message)`
  - `eventStream` (Stream<SipEvent>)
- **Status**: ⏳ Pending

#### Task 5.3: Fix All Imports in Library
- **Action**: Run `flutter analyze` on library
- **Fix**: All import errors
- **Status**: ⏳ Pending

---

### Phase 6: Move Presentation to Example (60 min)

#### Task 6.1: Copy Presentation Layer
- **Source**: `legacy/lib/presentation/`
- **Destination**: `example/lib/presentation/`
- **Includes**: `providers/`, `screens/`, `widgets/`, `services/`
- **Status**: ⏳ Pending

#### Task 6.2: Copy App Services
- **Source**: `legacy/lib/services/` (app-specific only)
- **Destination**: `example/lib/services/`
- **Includes**: `theme_service.dart`, `storage_service.dart`, etc.
- **Status**: ⏳ Pending

#### Task 6.3: Copy Navigation
- **Source**: `legacy/lib/navigation/`
- **Destination**: `example/lib/navigation/`
- **Status**: ⏳ Pending

#### Task 6.4: Copy Theme
- **Source**: `legacy/lib/theme/`
- **Destination**: `example/lib/theme/`
- **Status**: ⏳ Pending

#### Task 6.5: Copy Main Entry Point
- **Source**: `legacy/lib/main.dart`
- **Destination**: `example/lib/main.dart`
- **Status**: ⏳ Pending

#### Task 6.6: Update Example pubspec.yaml
- **Add**: `flutter_gsmsip` dependency (path: ../)
- **Keep**: All app-specific dependencies
- **Status**: ⏳ Pending

---

### Phase 7: Fix Android Configuration (30 min)

#### Task 7.1: Copy AndroidManifest.xml
- **Source**: `legacy/android/app/src/main/AndroidManifest.xml`
- **Destination**: `flutter_gsmsip/example/android/app/src/main/AndroidManifest.xml`
- **Adapt**: Package name, permissions
- **Status**: ⏳ Pending

#### Task 7.2: Update Library AndroidManifest.xml
- **File**: `flutter_gsmsip/android/src/main/AndroidManifest.xml`
- **Add**: Required permissions for plugin
- **Status**: ⏳ Pending

#### Task 7.3: Copy Build Configuration
- **Source**: `legacy/android/app/build.gradle.kts`
- **Destination**: `flutter_gsmsip/example/android/app/build.gradle.kts`
- **Adapt**: Namespace, applicationId
- **Status**: ⏳ Pending

---

### Phase 8: Test and Verify (60 min)

#### Task 8.1: Test Library Build
```bash
cd flutter_gsmsip
flutter pub get
flutter analyze
flutter build apk --debug
```
- **Success**: Build completes without errors
- **Status**: ⏳ Pending

#### Task 8.2: Test Example Build
```bash
cd flutter_gsmsip/example
flutter pub get
flutter analyze
flutter build apk --debug
```
- **Success**: Build completes without errors
- **Status**: ⏳ Pending

#### Task 8.3: Test on Device
```bash
cd flutter_gsmsip/example
flutter run
```
- **Success**: App launches and functions correctly
- **Status**: ⏳ Pending

#### Task 8.4: Test pub.dev Publishing
```bash
cd flutter_gsmsip
flutter pub publish --dry-run
```
- **Success**: No validation errors
- **Status**: ⏳ Pending

---

### Phase 9: Documentation (30 min)

#### Task 9.1: Update Library README
- **File**: `flutter_gsmsip/README.md`
- **Add**: Installation, usage examples, API reference
- **Status**: ✅ Already created

#### Task 9.2: Create Example README
- **File**: `flutter_gsmsip/example/README.md`
- **Add**: How to run example, features demo
- **Status**: ⏳ Pending

#### Task 9.3: Add API Documentation
- **Action**: Add dartdoc comments to public API
- **Files**: `lib/flutter_gsmsip.dart`, `lib/src/gsm_sip_bridge.dart`
- **Status**: ⏳ Pending

---

## File Counts (Estimate)

| Layer | Source | Destination | Est. Files |
|-------|--------|-------------|------------|
| Domain | `legacy/lib/domain/` | `lib/src/domain/` | ~30 |
| Data | `legacy/lib/data/` | `lib/src/data/` | ~40 |
| Native | `legacy/android/.../kotlin/` | `flutter_gsmsip/android/.../kotlin/` | 7 |
| Presentation | `legacy/lib/presentation/` | `example/lib/presentation/` | ~50 |
| Services | `legacy/lib/services/` | `example/lib/services/` | ~10 |

**Total**: ~140 files to move and configure

---

## Risk Assessment

### High Risk
- **PJSIP native libraries**: May not be in expected location
  - **Mitigation**: Search entire legacy directory
  - **Fallback**: Rebuild PJSIP if source available

### Medium Risk
- **Package name changes**: Kotlin code uses old package name
  - **Mitigation**: Systematic find/replace
  - **Verification**: Kotlin compiles

### Low Risk
- **Import fixes**: Mechanical work
- **pubspec.yaml updates**: Straightforward

---

## Success Criteria

- [ ] All domain layer files moved to library
- [ ] All data layer files moved to library
- [ ] All native Kotlin code moved and compiles
- [ ] All presentation files moved to example
- [ ] Library builds: `flutter build apk --debug`
- [ ] Example builds and runs on device
- [ ] `flutter pub publish --dry-run` passes
- [ ] **legacy/ untouched** (archive reference)

---

## Approval

- [ ] Plan reviewed by: [name]
- [ ] Plan approved on: [date]
- [ ] Notes: [any conditions or concerns]
