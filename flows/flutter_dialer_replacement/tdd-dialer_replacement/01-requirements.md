# 01-Requirements

## Overview

**TDD Flow for react-native-replace-dialer**

This document defines the test-driven development requirements for the react-native-replace-dialer library. Tests are organized by layer and functionality to ensure comprehensive coverage of the JavaScript bridge, native Android module, and integration points.

## Test Strategy

### Testing Pyramid

```
                    ┌─────────────┐
                    │   E2E /     │
                    │ Integration │
                    │   Tests     │
                    └──────┬──────┘
                   ┌───────────────┐
                   │  JavaScript   │
                   │  Unit Tests   │
                   └───────┬───────┘
                  ┌─────────────────┐
                  │  Native Module  │
                  │  Unit Tests     │
                  │  (Mocked)       │
                  └─────────────────┘
```

### Test Layers

1. **Layer 1: JavaScript Unit Tests**
   - Test `ReplaceDialer.js` class methods
   - Mock native module
   - Verify error handling
   - Verify callback invocation

2. **Layer 2: Native Module Tests**
   - Test `ReplaceDialerModule.java` methods
   - Mock Android system services (TelecomManager)
   - Verify callback invocation with correct values
   - Verify activity result handling (after bug fix)

3. **Layer 3: Integration Tests**
   - Test JavaScript-to-native bridge
   - Test end-to-end dialer status flow
   - Test error scenarios

## Functional Test Requirements

### FR-TEST-001: Native Module Validation

**Test**: `checkNativeModule()` throws error when native module is null

**Coverage**:
- Verify error is thrown when `NativeModules.ReplaceDialerModule` is `null`
- Verify error message contains troubleshooting steps
- Verify error message mentions:
  - Rebuild instructions
  - CocoaPods instructions (for future iOS)
  - Manual linking instructions
  - Unit testing mock instructions
  - GitHub repository for issues

**Test Type**: Unit Test (JavaScript)
**Priority**: HIGH

### FR-TEST-002: isDefaultDialer - Success Case

**Test**: `isDefaultDialer()` invokes callback with `true` when app is default dialer

**Coverage**:
- Mock native module to return `true`
- Verify callback is invoked exactly once
- Verify callback receives `true` parameter
- Verify console.log is called with result

**Test Type**: Unit Test (JavaScript)
**Priority**: HIGH

### FR-TEST-003: isDefaultDialer - Failure Case

**Test**: `isDefaultDialer()` invokes callback with `false` when app is not default dialer

**Coverage**:
- Mock native module to return `false`
- Verify callback is invoked exactly once
- Verify callback receives `false` parameter

**Test Type**: Unit Test (JavaScript)
**Priority**: HIGH

### FR-TEST-004: isDefaultDialer - Pre-M Android

**Test**: `isDefaultDialer()` returns `true` for Android API < 23

**Coverage**:
- Mock `Build.VERSION.SDK_INT` to < 23
- Verify callback is invoked with `true` without checking TelecomManager
- Rationale: Default dialer concept not applicable to pre-M Android

**Test Type**: Unit Test (Native - Android)
**Priority**: MEDIUM

### FR-TEST-005: setDefaultDialer - Success Case

**Test**: `setDefaultDialer()` invokes callback with `true` when user sets app as default

**Coverage**:
- Mock activity result to return `RESULT_OK`
- Verify callback is invoked after activity result
- Verify callback receives `true` parameter
- Verify correct intent is created with package name
- Verify activity is started with correct request code

**Test Type**: Integration Test (Native - Android)
**Priority**: CRITICAL (currently broken - BUG-001)

### FR-TEST-006: setDefaultDialer - Cancellation Case

**Test**: `setDefaultDialer()` invokes callback with `false` when user cancels

**Coverage**:
- Mock activity result to return `RESULT_CANCELED`
- Verify callback is invoked after activity result
- Verify callback receives `false` parameter

**Test Type**: Integration Test (Native - Android)
**Priority**: CRITICAL (currently broken - BUG-001)

### FR-TEST-007: setDefaultDialer - Intent Creation

**Test**: `setDefaultDialer()` creates correct intent

**Coverage**:
- Verify intent action is `TelecomManager.ACTION_CHANGE_DEFAULT_DIALER`
- Verify extra contains correct package name
- Verify request code is `RC_DEFAULT_PHONE` (3289)

**Test Type**: Unit Test (Native - Android)
**Priority**: HIGH

### FR-TEST-008: getName() Returns Correct Module Name

**Test**: `ReplaceDialerModule.getName()` returns "ReplaceDialerModule"

**Coverage**:
- Verify module name matches JavaScript bridge expectation
- Verify name is consistent across platform

**Test Type**: Unit Test (Native - Android)
**Priority**: MEDIUM

### FR-TEST-009: Package Registration

**Test**: `ReplaceDialerModulePackage.createNativeModules()` registers module

**Coverage**:
- Verify module list contains `ReplaceDialerModule` instance
- Verify `createViewManagers()` returns empty list
- Verify module is properly initialized with context

**Test Type**: Unit Test (Native - Android)
**Priority**: MEDIUM

### FR-TEST-010: Callback Thread Safety

**Test**: Multiple concurrent calls to `setDefaultDialer()` are handled safely

**Coverage**:
- Verify static callback field doesn't cause race conditions
- Verify each callback is invoked with correct result
- Verify callbacks are cleared after invocation

**Test Type**: Unit Test (Native - Android)
**Priority**: HIGH (addresses technical debt)

### FR-TEST-011: Activity Result Timeout

**Test**: Callback is invoked with `false` if activity result not received

**Coverage**:
- Implement timeout mechanism (e.g., 30 seconds)
- Verify callback is invoked with `false` on timeout
- Verify callback field is cleared after timeout

**Test Type**: Integration Test (Native - Android)
**Priority**: MEDIUM

### FR-TEST-012: Module Invalidation

**Test**: `invalidate()` cleans up resources

**Coverage**:
- Verify callback is invoked with `false` on module destruction
- Verify callback field is cleared
- Verify activity event listener is unregistered

**Test Type**: Unit Test (Native - Android)
**Priority**: MEDIUM

## Non-Functional Test Requirements

### NFR-TEST-001: Test Coverage

**Requirement**: Minimum 80% code coverage

**Metrics**:
- Line coverage: ≥ 80%
- Branch coverage: ≥ 80%
- Method coverage: ≥ 80%

**Tools**:
- JavaScript: Jest coverage
- Android: JaCoCo

### NFR-TEST-002: Test Execution Time

**Requirement**: All tests complete within 60 seconds

**Metrics**:
- Unit tests: < 10 seconds
- Integration tests: < 50 seconds

### NFR-TEST-003: Test Isolation

**Requirement**: Tests are independent and can run in any order

**Metrics**:
- No shared state between tests
- Each test sets up its own mocks
- Tests can run in parallel

### NFR-TEST-004: Deterministic Tests

**Requirement**: Tests produce same result every time

**Metrics**:
- No flaky tests
- No timing-dependent tests (except explicit timeout tests)
- No external dependencies

## Test Environment Requirements

### JavaScript Tests

**Dependencies**:
- Jest (provided by React Native)
- react-test-renderer
- @testing-library/react-native (optional)

**Mock Requirements**:
- Mock `NativeModules.ReplaceDialerModule`
- Mock `console.log`
- Mock `Build.VERSION` (for Android version tests)

### Native Android Tests

**Dependencies**:
- JUnit 4 or 5
- Mockito for mocking
- Robolectric for Android framework testing
- AndroidX Test libraries

**Mock Requirements**:
- Mock `ReactApplicationContext`
- Mock `TelecomManager`
- Mock `Callback`
- Mock `Intent` resolution

### Integration Tests

**Requirements**:
- Android emulator or device
- App installed with test permissions
- TelecomManager accessible

## Test Organization

### Directory Structure

```
__tests__/
├── javascript/
│   ├── ReplaceDialer.test.js       # JavaScript unit tests
│   └── __mocks__/
│       └── NativeModules.js         # Native module mocks
├── native/
│   ├── ReplaceDialerModuleTest.java # Native unit tests
│   ├── ReplaceDialerModulePackageTest.java
│   └── __mocks__/
│       ├── TelecomManager.java      # Android service mocks
│       └── Callback.java            # Callback mocks
└── integration/
    ├── BridgeIntegrationTest.java   # JS-to-native integration
    └── DialerFlowIntegrationTest.java # End-to-end flows
```

### Test Naming Convention

**Pattern**: `[Method]_[Scenario]_[ExpectedResult]`

**Examples**:
- `isDefaultDialer_ModuleAvailable_InvokesCallbackWithTrue`
- `setDefaultDialer_UserCancels_InvokesCallbackWithFalse`
- `checkNativeModule_ModuleNull_ThrowsError`

## Bug Fix Test Requirements (BUG-001)

### BUG-001-TEST-001: Activity Result Handling

**Test**: `setDefaultDialer()` waits for activity result before invoking callback

**Coverage**:
- Verify callback is NOT invoked immediately
- Verify callback is invoked in `onActivityResult()`
- Verify callback receives correct result based on `resultCode`

**Test Type**: Integration Test (Native - Android)
**Priority**: CRITICAL
**Status**: Currently failing (documents existing bug)

### BUG-001-TEST-002: Callback Not Invoked Twice

**Test**: Callback is invoked exactly once per `setDefaultDialer()` call

**Coverage**:
- Verify callback not invoked before activity result
- Verify callback invoked once after activity result
- Verify callback not invoked on subsequent activity results

**Test Type**: Integration Test (Native - Android)
**Priority**: CRITICAL

### BUG-001-TEST-003: Static Callback Cleared

**Test**: Static callback field is cleared after invocation

**Coverage**:
- Verify callback field is `null` after successful invocation
- Verify callback field is `null` after failed invocation
- Verify prevents memory leaks

**Test Type**: Unit Test (Native - Android)
**Priority**: HIGH

## Test Execution Commands

### JavaScript Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- __tests__/javascript/ReplaceDialer.test.js

# Run in watch mode
npm test -- --watch
```

### Native Android Tests

```bash
# Run unit tests
./gradlew test

# Run with coverage
./gradlew jacocoTestReport

# Run specific test class
./gradlew test --tests "one.telefon.replacedialer.ReplaceDialerModuleTest"
```

### Integration Tests

```bash
# Run on connected device/emulator
./gradlew connectedAndroidTest

# Run specific test
./gradlew connectedAndroidTest --tests "one.telefon.replacedialer.DialerFlowIntegrationTest"
```

## Continuous Integration

### CI Pipeline Requirements

1. **Pre-commit**:
   - Run JavaScript unit tests
   - Run linting

2. **CI Build**:
   - Run all JavaScript tests with coverage
   - Run all native unit tests with coverage
   - Run integration tests on emulator
   - Report coverage metrics

3. **Quality Gates**:
   - Coverage ≥ 80%
   - All tests pass
   - No flaky tests

## Test Data

### Mock Data

```javascript
// Mock callback results
const MOCK_RESULT_TRUE = true;
const MOCK_RESULT_FALSE = false;

// Mock package names
const MOCK_PACKAGE_NAME = 'com.example.dialer';
const MOCK_DEFAULT_DIALER = 'com.other.dialer';

// Mock Android versions
const ANDROID_VERSION_PRE_M = 22; // Lollipop
const ANDROID_VERSION_M = 23;     // Marshmallow
const ANDROID_VERSION_CURRENT = 34; // Current target
```

### Test Fixtures

```java
// Mock TelecomManager responses
when(mockTelecomManager.getDefaultDialerPackage())
    .thenReturn(MOCK_PACKAGE_NAME);  // Success case
when(mockTelecomManager.getDefaultDialerPackage())
    .thenReturn(MOCK_DEFAULT_DIALER); // Failure case
```

## Acceptance Criteria

### Phase 1: JavaScript Tests (COMPLETE)
- [ ] All JavaScript unit tests pass
- [ ] Coverage ≥ 80% for ReplaceDialer.js
- [ ] Mock native module works correctly

### Phase 2: Native Module Tests (PENDING)
- [ ] All native unit tests pass
- [ ] Coverage ≥ 80% for ReplaceDialerModule.java
- [ ] Mock TelecomManager works correctly

### Phase 3: Bug Fix Tests (PENDING - BLOCKED BY BUG-001)
- [ ] BUG-001-TEST-001 passes (activity result handling)
- [ ] BUG-001-TEST-002 passes (callback invoked once)
- [ ] BUG-001-TEST-003 passes (callback cleared)

### Phase 4: Integration Tests (PENDING)
- [ ] Bridge integration tests pass
- [ ] End-to-end flow tests pass
- [ ] All tests run on emulator/device

---

*Generated by /legacy analysis on 2026-03-04*
*Status: DRAFT*
