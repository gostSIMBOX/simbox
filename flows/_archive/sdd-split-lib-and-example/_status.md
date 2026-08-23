# Status: sdd-split-lib-and-example

## Current Phase

REQUIREMENTS | SPECIFICATIONS | **PLAN** | IMPLEMENTATION | DOCUMENTATION

## Phase Status

APPROVED | APPROVED | **DRAFTING** | - | -

## Last Updated

2026-03-15 by Qwen

## Blockers

None - Plan cleared for re-discussion

## Progress

- [x] Requirements drafted (previous iteration)
- [x] Requirements approved
- [x] Specifications drafted
- [x] Specifications approved
- [x] Plan drafted v2.0
- [x] Plan approved
- [x] Implementation started
  - [x] Phase 1: Analyze legacy code
  - [x] Phase 2: Domain layer moved to library (33 files)
  - [x] Phase 3: Data layer moved to library (24 files)
  - [x] Phase 4: Core services moved (6 files)
  - [x] Phase 5: Library export file updated
  - [x] Phase 6: Import paths fixed (partial)
    - [x] Fixed gateway_service.dart imports
    - [x] Fixed dongle_repository_impl.dart imports
    - [x] Fixed voice_line_repository_impl.dart imports
    - [x] Rewrote local_data_source.dart (removed presentation dependency)
    - [x] Rewrote remote_data_source.dart (removed presentation dependency)
    - [x] Fixed error_handler.dart (removed DI dependency)
    - [x] Added top-level success/failure functions to result.dart
    - [x] Fixed dongle source imports (usb, trrs, resistance_meter, detector)
    - [x] Removed duplicate enums (SmppConnectionState, TelephonyPermissionStatus)
    - [x] Added copyWith to SipAccountModel and SipCallModel
    - [x] Added sendSms method to SmsService
  - [ ] Phase 7: Fix remaining import errors (~180 errors)
  - [ ] Phase 8: Move native Kotlin code
  - [ ] Phase 9: Move presentation to example
  - [ ] Phase 10: Test build
  - [ ] Phase 11: Test on device
- [ ] Implementation complete
- [ ] Documentation drafted
- [ ] Documentation approved

## Current Project State

### Root (`/Users/anton/proj/telon/flutter_gsmsip/`)
- **pubspec.yaml**: `flutter_gsmsip` v0.1.0 (Flutter plugin)
- **lib/**: Minimal plugin structure
  - `flutter_gsmsip.dart` - Main export
  - `flutter_gsmsip_method_channel.dart` - Method channel
  - `flutter_gsmsip_platform_interface.dart` - Platform interface
  - `src/entities/` - 4 entity files
  - `src/services/gsm_sip_bridge.dart` - Main API
- **android/**: Plugin Android structure (empty Kotlin)
- **example/**: Example app with `flutter_gsmsip` dependency
- **README.md**: Library documentation (created)

### Example (`/Users/anton/proj/telon/flutter_gsmsip/example/`)
- **pubspec.yaml**: `flutter_gsmsip_example` v1.0.0
- **lib/**: Minimal structure (main.dart + folders)
  - `l10n/`, `navigation/`, `platform/`, `providers/`, `theme/`, `utils/`
  - Most folders appear empty or minimal

### Legacy (`/Users/anton/proj/telon/flutter_gsmsip/legacy/`)
- **pubspec.yaml**: `flutter_gsm_sip_gateway` v3.0.0 (full app)
- **lib/**: Complete application code
  - `domain/` - entities, exceptions, models, repositories, usecases
  - `data/` - datasources, models, repositories, services, sources, storage
  - `presentation/` - providers, screens, services, widgets
  - `screens/`, `services/`, `widgets/`, `models/`, `navigation/`, etc.
- **android/app/**: Full Android app with native Kotlin code
- **This is the ORIGINAL full application**

## Context Notes

**Previous Architecture Decision**: Library was to be a **Flutter plugin** because:
- PJSIP native code (Kotlin/Java) stays in library
- Native SIP stack in `flutter_gsmsip/android/src/main/kotlin/`
- Dart API wraps native method channels
- Service-based architecture with Android Intents

**Previous Code Distribution Plan**:
- **Library**: Domain layer, Data layer, Native Kotlin code
- **Example**: Presentation layer, UI, screens, app-specific services

**What Was Done**:
- Plugin structure created in root
- Example app directory created
- README.md written
- Legacy folder contains the ORIGINAL full app

**Key Observation**: The `legacy/` folder contains the complete original application with:
- Full domain/data/presentation layers
- Native Android code in `legacy/android/app/`
- All screens, widgets, services, providers

## Next Actions

1. **Re-discuss requirements** - What exactly needs to be done?
2. **Understand the goal** - What should be in library vs example vs legacy?
3. **Create new plan** - Based on clarified requirements
