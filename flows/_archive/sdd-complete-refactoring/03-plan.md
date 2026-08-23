# Implementation Plan: Complete Refactoring

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-03-15
> Estimated Effort: 2-3 hours

## Task Breakdown

### Phase 1: Remove Duplicate Files (15 minutes)

#### Task 1.1: Delete Old GatewayRepository Implementation
- **File**: `lib/data/repositories/gateway_repository.dart`
- **Action**: Delete file
- **Verification**: Search for imports of this file, ensure none remain
- **Risk**: LOW - New implementation exists in `gateway_repository_impl.dart`

#### Task 1.2: Delete Duplicate Entity Files
- **Files**: 
  - `lib/domain/entities/gateway_config_entity.dart`
  - `lib/domain/entities/gateway_entity.dart`
- **Action**: Delete both files
- **Verification**: Ensure `gateway_config.dart` and `gateway_status.dart` exist
- **Risk**: LOW - These are duplicates with old structure

#### Task 1.3: Remove Duplicate SmppConfig
- **File**: `lib/services/sms_service.dart`
- **Action**: Remove lines 51-84 (duplicate SmppConfig class)
- **Verification**: Ensure `lib/models/smpp_config.dart` exists
- **Risk**: LOW - Duplicate class definition

---

### Phase 2: Fix Import Paths (15 minutes)

#### Task 2.1: Fix gateway_provider.dart Import
- **File**: `lib/presentation/providers/gateway_provider.dart`
- **Line**: 9
- **Change**:
  ```dart
  // FROM:
  import '../repositories/gateway_repository.dart';
  
  // TO:
  import '../../domain/repositories/gateway_repository.dart';
  ```
- **Verification**: No import errors in IDE

#### Task 2.2: Fix sip_provider.dart Import
- **File**: `lib/presentation/providers/sip_provider.dart`
- **Line**: 9
- **Change**:
  ```dart
  // FROM:
  import '../repositories/sip_repository.dart';
  
  // TO:
  import '../../domain/repositories/sip_repository.dart';
  ```
- **Verification**: No import errors in IDE

---

### Phase 3: Fix Dependency Injection (20 minutes)

#### Task 3.1: Remove Duplicate GatewayRepository Registration
- **File**: `lib/core/di/dependency_injection.dart`
- **Lines**: ~189-194 (verify exact line numbers)
- **Action**: Delete this registration block:
  ```dart
  getIt.registerLazySingleton<GatewayRepository>(
    () => GatewayRepository(
      getIt<LocalDataSource>(),
      getIt<RemoteDataSource>(),
      getIt<Logger>(),
    ),
  );
  ```
- **Verification**: Only one `GatewayRepository` registration remains (the `GatewayRepositoryImpl` one)

#### Task 3.2: Check for Unused Dependencies
- **Action**: Search for `LocalDataSource` and `RemoteDataSource` usage
- **If unused**: Remove their registrations from DI
- **Verification**: No compilation errors after removal

---

### Phase 4: Update Data Models (30 minutes)

#### Task 4.1: Analyze GatewayConfigModel
- **File**: `lib/data/models/gateway_config_model.dart`
- **Action**: Read current implementation
- **Determine**: What changes needed to work with new `GatewayConfig`

#### Task 4.2: Update GatewayConfigModel.toEntity()
- **File**: `lib/data/models/gateway_config_model.dart`
- **Action**: Update conversion method to create new `GatewayConfig` structure
- **Changes**:
  - Map flat JSON structure to nested `SipAccount` entity
  - Handle optional `SmppConfig`
  - Preserve all configuration properties

#### Task 4.3: Update GatewayConfigModel.fromJson()
- **File**: `lib/data/models/gateway_config_model.dart`
- **Action**: Ensure JSON parsing matches stored format
- **Verification**: Backward compatible with existing saved configs

#### Task 4.4: Update Related Models
- **Files**: Check for other models that reference deleted entities
- **Action**: Update imports and type references
- **Verification**: No import errors

---

### Phase 5: Build & Test (45 minutes)

#### Task 5.1: Clean Build
```bash
flutter clean
flutter pub get
```

#### Task 5.2: Static Analysis
```bash
flutter analyze
```
- **Action**: Fix any analysis errors
- **Expected**: Warnings OK, errors must be fixed

#### Task 5.3: Build Debug APK
```bash
flutter build apk --debug
```
- **Expected**: Build succeeds without errors
- **If fails**: Fix compilation errors

#### Task 5.4: Run on Device
```bash
flutter run -d R7AY804RAPB
```
- **Expected**: App launches successfully
- **Verify**: No crashes on startup

#### Task 5.5: Smoke Test
- [ ] App opens without errors
- [ ] Navigation works
- [ ] Settings can be opened
- [ ] No console errors

---

## File Change Summary

### Files to Delete (4)
1. `lib/data/repositories/gateway_repository.dart`
2. `lib/domain/entities/gateway_config_entity.dart`
3. `lib/domain/entities/gateway_entity.dart`
4. N/A - SmppConfig duplicate is inline in sms_service.dart, just remove class definition

### Files to Modify (5)
1. `lib/presentation/providers/gateway_provider.dart` - Fix import
2. `lib/presentation/providers/sip_provider.dart` - Fix import
3. `lib/core/di/dependency_injection.dart` - Remove duplicate registration
4. `lib/data/models/gateway_config_model.dart` - Update entity conversion
5. `lib/services/sms_service.dart` - Remove duplicate SmppConfig class

### Files Unchanged
All domain layer files (entities, repositories, use cases)
All service implementation files
All presentation UI files

---

## Dependencies & Prerequisites

### Required Knowledge
- Understanding of Dart import resolution
- Familiarity with Clean Architecture pattern
- Knowledge of Either type for error handling

### Tools Required
- Flutter SDK (installed)
- Android device connected (SM A066B - R7AY804RAPB)
- Code editor with Dart support

### External Dependencies
- None - all changes are internal refactoring

---

## Risk Assessment

### High Risk
- **None** - All changes are straightforward fixes

### Medium Risk
- **GatewayConfigModel update**: May break config loading if mapping is incorrect
  - **Mitigation**: Test with fresh config, add migration if needed

### Low Risk
- **Import path fixes**: Simple string changes
- **File deletions**: Duplicates not in use
- **DI fix**: Removing duplicate registration

---

## Rollback Plan

If issues occur:

1. **Import issues**: Revert import changes, use git to restore
2. **DI issues**: Restore duplicate registration temporarily
3. **Model issues**: Restore old entity files temporarily

```bash
git stash  # Save all changes
git checkout HEAD -- <file>  # Restore specific file
```

---

## Success Criteria

- [ ] All duplicate files deleted
- [ ] All import paths corrected
- [ ] DI container has no duplicate registrations
- [ ] `flutter analyze` shows no errors
- [ ] `flutter build apk` succeeds
- [ ] App launches on Android device
- [ ] No runtime crashes in first 60 seconds

---

## Approval

- [ ] Plan reviewed by: [name]
- [ ] Plan approved on: [date]
- [ ] Notes: [any conditions or concerns]
