# Specifications: flutter_nmsip Test-Driven Development

> Technical specifications for test implementation and execution.

## Test Structure

```
test/
├── flutter_sip2_test.dart          # Dart unit tests
├── account_test.dart               # [Recommended] Account tests
├── call_test.dart                  # [Recommended] Call tests
└── endpoint_test.dart              # [Recommended] Endpoint tests

android/src/test/kotlin/
├── FlutterSip2PluginTest.kt        # Kotlin unit tests
├── PjActionsTest.kt                # [Recommended] Intent factory tests
└── BroadcastRecevierTest.kt        # [Recommended] Receiver tests

example/integration_test/
├── plugin_integration_test.dart    # App integration tests
└── call_flow_test.dart             # [Recommended] Call flow tests
```

## Existing Test Specifications

### 1. Account Deserialization Test

**File**: `test/flutter_sip2_test.dart`

```dart
test('should create Account from map', () {
  final accountData = {
    'id': 1,
    'uri': 'sip:test@example.com',
    'name': 'Test User',
    'username': 'test',
    'domain': 'example.com',
    'password': 'password',
    'proxy': 'proxy.example.com',
    'transport': 'TCP',
    'contactParams': 'test',
    'contactUriParams': null,
    'regServer': 'example.com',
    'regTimeout': 3600,
    'regContactParams': 'test',
    'regHeaders': {'X-Test': 'Value'},
    'registration': {
      'status': true,
      'code': 200,
      'reason': 'OK',
      'expiration': 3600,
      'retryAfter': null,
    }
  };

  final account = Account.fromMap(accountData);

  expect(account.id, 1);
  expect(account.name, 'Test User');
  expect(account.username, 'test');
  expect(account.domain, 'example.com');
  expect(account.registration.status, true);
});
```

**Coverage**:
- ✓ Required fields (id, uri, name, username, domain, password)
- ✓ Optional fields (proxy, transport, regServer, regTimeout)
- ✓ Nested registration object
- ⚠ Missing: toMap() serialization
- ⚠ Missing: equality/hashCode testing

### 2. Call Deserialization Test

```dart
test('should create Call from map', () {
  final callData = {
    'id': 1,
    'callId': 'call_123',
    'accountId': 1,
    'localContact': 'sip:local@example.com',
    'localUri': 'sip:local@example.com',
    'remoteContact': 'sip:remote@example.com',
    'remoteUri': 'sip:remote@example.com',
    'state': 'PJSIP_INV_STATE_CALLING',
    'stateText': 'Calling',
    'held': false,
    'muted': false,
    'speaker': false,
    'connectDuration': 0,
    'totalDuration': 0,
    'remoteOfferer': false,
    'remoteAudioCount': 1,
    'remoteVideoCount': 0,
    'audioCount': 1,
    'videoCount': 0,
    'lastStatusCode': null,
    'lastReason': null,
    'media': null,
    'provisionalMedia': null,
  };

  final call = Call.fromMap(callData);

  expect(call.id, 1);
  expect(call.state, 'PJSIP_INV_STATE_CALLING');
  expect(call.stateText, 'Calling');
  expect(call.held, false);
  expect(call.muted, false);
  expect(call.speaker, false);
});
```

**Coverage**:
- ✓ Call identity fields
- ✓ State fields
- ✓ Boolean flags
- ⚠ Missing: Duration calculation testing

### 3. Duration Formatting Test

```dart
test('should format call duration correctly', () {
  final callData = {
    'id': 1,
    'callId': 'call_123',
    'accountId': 1,
    'state': 'PJSIP_INV_STATE_CONFIRMED',
    'stateText': 'Confirmed',
    'held': false,
    'muted': false,
    'speaker': false,
    'connectDuration': 65,
    'totalDuration': 65,
    'remoteOfferer': false,
    'remoteAudioCount': 1,
    'remoteVideoCount': 0,
    'audioCount': 1,
    'videoCount': 0,
  };

  final call = Call.fromMap(callData);

  expect(call.getFormattedConnectDuration(), '01:05');
  expect(call.getFormattedTotalDuration(), '01:05');
});
```

**Coverage**:
- ✓ Basic duration formatting (65 seconds → "01:05")
- ⚠ Missing: Edge cases (0, 3600, negative)
- ⚠ Missing: Real-time calculation verification

### 4. URI Parsing Test

```dart
test('should parse remote number from URI', () {
  final callData = {
    'id': 1,
    'callId': 'call_123',
    'accountId': 1,
    'state': 'PJSIP_INV_STATE_CALLING',
    'stateText': 'Calling',
    'held': false,
    'muted': false,
    'speaker': false,
    'connectDuration': 0,
    'totalDuration': 0,
    'remoteOfferer': false,
    'remoteAudioCount': 1,
    'remoteVideoCount': 0,
    'audioCount': 1,
    'videoCount': 0,
    'remoteUri': '"John Doe" <sip:123456@example.com>',
  };

  final call = Call.fromMap(callData);

  expect(call.remoteNumber, '123456');
  expect(call.remoteName, 'John Doe');
});
```

**Coverage**:
- ✓ Display name parsing ("John Doe")
- ✓ Number extraction from SIP URI
- ⚠ Missing: tel: URI format
- ⚠ Missing: URI without display name
- ⚠ Missing: Malformed URI handling

### 5. Kotlin Plugin Test

**File**: `android/src/test/kotlin/org/tele/flutter_sip2/FlutterSip2PluginTest.kt`

```kotlin
@Test
fun onMethodCall_getPlatformVersion_returnsExpectedValue() {
  val plugin = FlutterSip2Plugin()

  val call = MethodCall("getPlatformVersion", null)
  val mockResult: MethodChannel.Result = Mockito.mock(MethodChannel.Result::class.java)
  plugin.onMethodCall(call, mockResult)

  Mockito.verify(mockResult).success("Android " + android.os.Build.VERSION.RELEASE)
}
```

**Coverage**:
- ⚠ Placeholder test (getPlatformVersion doesn't exist in current implementation)
- ⚠ Missing: Actual method testing (start, createAccount, etc.)
- ⚠ Missing: Exception handling testing

### 6. Integration Test

**File**: `example/integration_test/plugin_integration_test.dart`

```dart
testWidgets('verify app starts correctly', (tester) async {
  app.main();
  await tester.pumpAndSettle();

  // Verify that the app starts with the correct title
  expect(find.text('Flutter SIP2 Example'), findsOneWidget);

  // Verify that the status shows initialization
  expect(find.textContaining('Initializing'), findsOneWidget);
});
```

**Coverage**:
- ✓ App startup verification
- ⚠ Missing: Account creation flow
- ⚠ Missing: Call flow
- ⚠ Missing: Event reception

## Recommended Test Implementations

### 1. Account Equality Test

```dart
test('should compare accounts by ID', () {
  final account1 = Account(
    id: 1,
    uri: 'sip:a@example.com',
    name: 'A',
    username: 'a',
    domain: 'example.com',
    password: 'a',
    registration: AccountRegistration(status: true),
  );

  final account2 = Account(
    id: 1,  // Same ID
    uri: 'sip:b@example.com',  // Different everything else
    name: 'B',
    username: 'b',
    domain: 'example.com',
    password: 'b',
    registration: AccountRegistration(status: false),
  );

  expect(account1, equals(account2));  // Equal despite different data
  expect(account1.hashCode, equals(account2.hashCode));
});

test('should hash accounts by ID', () {
  final account = Account(
    id: 42,
    uri: 'sip:test@example.com',
    name: 'Test',
    username: 'test',
    domain: 'example.com',
    password: 'test',
    registration: AccountRegistration(status: true),
  );

  expect(account.hashCode, equals(42.hashCode));
});
```

### 2. Exception Translation Test

```dart
test('should translate PlatformException to FlutterSip2Exception', () async {
  final channel = MethodChannel('flutter_sip2');
  
  TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
      .setMockMethodCallHandler(channel, (call) async {
    throw PlatformException(code: 'SIP_ERROR', message: 'Test error');
  });

  expect(
    () => FlutterSip2.createAccount({
      'name': 'Test',
      'username': 'test',
      'domain': 'example.com',
      'password': 'test',
    }),
    throwsA(isA<FlutterSip2Exception>()
        .having((e) => e.code, 'code', 'SIP_ERROR')
        .having((e) => e.message, 'message', 'Test error')),
  );
});
```

### 3. Duration Edge Cases Test

```dart
group('Call duration formatting', () {
  test('should format zero duration', () {
    final call = Call.fromMap({
      ...baseCallData,
      'connectDuration': 0,
      'totalDuration': 0,
    });

    expect(call.getFormattedConnectDuration(), '00:00');
    expect(call.getFormattedTotalDuration(), '00:00');
  });

  test('should format exact minute', () {
    final call = Call.fromMap({
      ...baseCallData,
      'connectDuration': 60,
      'totalDuration': 60,
    });

    expect(call.getFormattedConnectDuration(), '01:00');
  });

  test('should format exact hour', () {
    final call = Call.fromMap({
      ...baseCallData,
      'connectDuration': 3600,
      'totalDuration': 3600,
    });

    expect(call.getFormattedConnectDuration(), '60:00');
  });

  test('should format negative duration', () {
    final call = Call.fromMap({
      ...baseCallData,
      'connectDuration': -1,
      'totalDuration': -1,
    });

    expect(call.getFormattedConnectDuration(), '00:00');
  });
});
```

### 4. URI Parsing Test Suite

```dart
group('URI parsing', () {
  test('should parse SIP URI without display name', () {
    final call = Call.fromMap({
      ...baseCallData,
      'remoteUri': 'sip:123456@example.com',
    });

    expect(call.remoteNumber, '123456');
    expect(call.remoteName, isNull);
  });

  test('should parse tel: URI', () {
    final call = Call.fromMap({
      ...baseCallData,
      'localUri': 'tel:+1-555-123-4567',
    });

    expect(call.localNumber, '+1-555-123-4567');
  });

  test('should parse URI with special characters', () {
    final call = Call.fromMap({
      ...baseCallData,
      'remoteUri': '"John & Jane" <sip:123@example.com>',
    });

    expect(call.remoteName, 'John & Jane');
  });

  test('should handle null URI', () {
    final call = Call.fromMap({
      ...baseCallData,
      'remoteUri': null,
    });

    expect(call.remoteNumber, isNull);
    expect(call.remoteName, isNull);
  });
});
```

### 5. Mock Platform Channel Test

```dart
group('FlutterSip2 platform calls', () {
  late List<MethodCall> calls;

  setUp(() {
    calls = [];
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(MethodChannel('flutter_sip2'), (call) async {
      calls.add(call);
      return {'success': true};
    });
  });

  test('start should invoke method channel', () async {
    final config = {'userAgent': 'Test'};
    await FlutterSip2.start(config);

    expect(calls.length, 1);
    expect(calls.first.method, 'start');
    expect(calls.first.arguments, config);
  });

  test('createAccount should invoke method channel', () async {
    final accountConfig = {
      'name': 'Test',
      'username': 'test',
      'domain': 'example.com',
      'password': 'test',
    };
    await FlutterSip2.createAccount(accountConfig);

    expect(calls.length, 1);
    expect(calls.first.method, 'createAccount');
    expect(calls.first.arguments, accountConfig);
  });

  test('registerAccount should include renew flag', () async {
    final account = Account(
      id: 1,
      uri: 'sip:test@example.com',
      name: 'Test',
      username: 'test',
      domain: 'example.com',
      password: 'test',
      registration: AccountRegistration(status: true),
    );

    await FlutterSip2.registerAccount(account, renew: false);

    expect(calls.length, 1);
    expect(calls.first.method, 'registerAccount');
    expect(calls.first.arguments['accountId'], 1);
    expect(calls.first.arguments['renew'], false);
  });
});
```

## Test Execution

### Run Unit Tests

```bash
flutter test
```

### Run with Coverage

```bash
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
open coverage/html/index.html
```

### Run Integration Tests

```bash
cd example
flutter test integration_test/
```

### Run Kotlin Tests

```bash
cd example/android
./gradlew testDebugUnitTest
```

## CI/CD Configuration

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.24.0'
      
      - name: Install dependencies
        run: flutter pub get
      
      - name: Run unit tests
        run: flutter test --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: coverage/lcov.info
      
      - name: Run integration tests
        run: |
          cd example
          flutter test integration_test/
```

---

*Status: DRAFT | Type: TDD | Generated by /legacy*
