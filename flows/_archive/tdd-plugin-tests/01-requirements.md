# Requirements: flutter_nmsip Test-Driven Development

> Test specifications for plugin unit testing and integration testing.

## Overview

This document specifies the testing strategy for flutter_nmsip. Currently the plugin has basic unit tests with room for expansion to achieve comprehensive test coverage.

## Current Test Coverage

### Dart Unit Tests (test/flutter_sip2_test.dart)

| Test | Coverage | Status |
|------|----------|--------|
| Account.fromMap() | Data deserialization | ✓ Implemented |
| Call.fromMap() | Data deserialization | ✓ Implemented |
| Call.getFormattedConnectDuration() | Duration formatting | ✓ Implemented |
| Call.remoteNumber parsing | URI parsing | ✓ Implemented |
| Call.remoteName parsing | URI parsing | ✓ Implemented |

### Kotlin Unit Tests (android/src/test/kotlin/)

| Test | Coverage | Status |
|------|----------|--------|
| onMethodCall getPlatformVersion | Basic method handling | ⚠ Placeholder |

### Integration Tests (example/integration_test/)

| Test | Coverage | Status |
|------|----------|--------|
| App starts correctly | Basic smoke test | ✓ Implemented |

## Functional Requirements

### FR-1: Data Model Testing

The test suite SHALL verify data model behavior:

- Account.fromMap() deserializes all fields correctly
- Account.toMap() serializes all fields correctly
- Account equality compares by ID only
- AccountRegistration.fromMap() handles null values
- Call.fromMap() deserializes nested registration data
- Call duration calculation is accurate
- Call URI parsing handles all formats

**Acceptance Criteria**:
- [ ] All Account fields tested
- [ ] Null handling tested for optional fields
- [ ] Equality/hashCode contract verified
- [ ] Duration formatting tested with edge cases (0, 60, 3600 seconds)
- [ ] URI parsing tested with multiple formats

### FR-2: Platform Channel Testing

The test suite SHALL verify platform channel communication:

- MethodChannel method names are correct
- Argument types are validated
- Exception translation works correctly
- EventChannel streams events properly

**Acceptance Criteria**:
- [ ] Mock MethodChannel for unit testing
- [ ] Verify method invocation with correct arguments
- [ ] Test FlutterSip2Exception translation
- [ ] Test event stream subscription

### FR-3: Call Operation Testing

The test suite SHALL verify call operations:

- makeCall() sends correct parameters
- answerCall() sends call ID
- hangupCall() sends call ID
- holdCall/unholdCall toggle hold state
- muteCall/unmuteCall toggle mute state
- dtmfCall() sends digits correctly
- xferCall() sends destination correctly

**Acceptance Criteria**:
- [ ] Each call operation tested with mock channel
- [ ] Parameter validation for each operation
- [ ] Exception handling for each operation

### FR-4: Account Operation Testing

The test suite SHALL verify account operations:

- createAccount() sends configuration correctly
- registerAccount() sends accountId and renew flag
- deleteAccount() sends accountId
- Account configuration validation

**Acceptance Criteria**:
- [ ] Account creation with full configuration
- [ ] Registration with renew=true and renew=false
- [ ] Account deletion
- [ ] Configuration validation

### FR-5: Event Stream Testing

The test suite SHALL verify event stream behavior:

- eventStream is lazy-initialized (singleton)
- Events are properly typed
- Event filtering works correctly
- Multiple subscribers supported

**Acceptance Criteria**:
- [ ] Singleton pattern verified
- [ ] Event type mapping tested
- [ ] Multiple subscriptions tested
- [ ] Event cancellation tested

### FR-6: Integration Testing

The integration test suite SHALL verify end-to-end behavior:

- Plugin initializes correctly
- Account creation flow works
- Call flow works (mocked or test server)
- Event stream receives events

**Acceptance Criteria**:
- [ ] App starts without errors
- [ ] SIP initialization completes
- [ ] Account can be created (mocked)
- [ ] Events are received

## Non-Functional Requirements

### NFR-1: Test Coverage

- Minimum 80% line coverage for Dart code
- Minimum 60% line coverage for Kotlin code
- All critical paths tested
- Edge cases documented

### NFR-2: Test Execution Time

- Unit tests complete in < 10 seconds
- Integration tests complete in < 60 seconds
- Tests can run in CI/CD pipeline

### NFR-3: Test Reliability

- Tests are deterministic (no flakiness)
- Tests are isolated (no order dependency)
- Tests are repeatable (same result every time)
- Mocks are used for external dependencies

### NFR-4: Test Maintainability

- Tests follow AAA pattern (Arrange-Act-Assert)
- Test names describe expected behavior
- Test code is DRY (Don't Repeat Yourself)
- Test fixtures are reusable

## Missing Tests (Gap Analysis)

### High Priority

| Area | Missing Tests | Impact |
|------|---------------|--------|
| FlutterSip2.start() | Initialization testing | HIGH |
| Exception handling | Error scenario testing | HIGH |
| Event stream | Event reception testing | HIGH |
| Call duration | Edge case testing | MEDIUM |

### Medium Priority

| Area | Missing Tests | Impact |
|------|---------------|--------|
| URI parsing | All format variations | MEDIUM |
| Account equality | HashCode contract | MEDIUM |
| Codec settings | Configuration testing | MEDIUM |
| STUN servers | Update testing | MEDIUM |

### Low Priority

| Area | Missing Tests | Impact |
|------|---------------|--------|
| Network configuration | Change testing | LOW |
| Service configuration | Change testing | LOW |
| Call transfer | Transfer testing | LOW |
| Call redirect | Redirect testing | LOW |

## Test Architecture

### Unit Test Pattern

```dart
// Arrange
final accountData = {
  'id': 1,
  'name': 'Test User',
  // ...
};

// Act
final account = Account.fromMap(accountData);

// Assert
expect(account.id, 1);
expect(account.name, 'Test User');
```

### Mock Platform Channel Pattern

```dart
// Mock MethodChannel
final channel = MethodChannel('flutter_sip2');
final calls = <MethodCall>[];

TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
    .setMockMethodCallHandler(channel, (call) async {
  calls.add(call);
  return mockResponse;
});

// Test
await FlutterSip2.createAccount(config);

// Verify
expect(calls.first.method, 'createAccount');
expect(calls.first.arguments, config);
```

### Integration Test Pattern

```dart
testWidgets('should create account', (tester) async {
  app.main();
  await tester.pumpAndSettle();

  // Tap create account button
  await tester.tap(find.text('Create Account'));
  await tester.pumpAndSettle();

  // Verify account created
  expect(find.textContaining('Account:'), findsOneWidget);
});
```

## Recommended Test Additions

### 1. Exception Translation Tests

```dart
test('should translate PlatformException to FlutterSip2Exception', () async {
  // Setup mock to throw PlatformException
  TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
      .setMockMethodCallHandler(channel, (call) async {
    throw PlatformException(code: 'SIP_ERROR', message: 'Test error');
  });

  // Verify exception translation
  expect(
    () => FlutterSip2.createAccount(config),
    throwsA(isA<FlutterSip2Exception>()),
  );
});
```

### 2. Event Stream Tests

```dart
test('should stream events', () async {
  final events = <Map<String, dynamic>>[];
  final subscription = FlutterSip2.eventStream.listen(events.add);

  // Emit mock event
  TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
      .handlePlatformMessage('flutter_sip2_events', ...);

  await tester.pump();

  expect(events.length, 1);
  expect(events.first['event'], 'pjSipCallReceived');
  
  subscription.cancel();
});
```

### 3. Duration Edge Case Tests

```dart
test('should format zero duration', () {
  final call = Call.fromMap({...callData, 'connectDuration': 0});
  expect(call.getFormattedConnectDuration(), '00:00');
});

test('should format hour duration', () {
  final call = Call.fromMap({...callData, 'connectDuration': 3600});
  expect(call.getFormattedConnectDuration(), '60:00');
});

test('should format negative duration', () {
  final call = Call.fromMap({...callData, 'connectDuration': -1});
  expect(call.getFormattedConnectDuration(), '00:00');
});
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: subosito/flutter-action@v2
      - run: flutter pub get
      - run: flutter test
      - run: cd example && flutter test integration_test/
```

### Coverage Reporting

```bash
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
```

---

*Status: DRAFT | Type: TDD | Generated by /legacy*
