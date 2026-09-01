# Specifications: Method Channel Module

> Technical specifications derived from code analysis.

## Architecture

### Class Structure

```
┌──────────────────────────────────────┐
│ MethodChannelFlutterSmsussd          │
│ extends FlutterSmsussdPlatform       │
├──────────────────────────────────────┤
│ - methodChannel: MethodChannel       │
│   (name: "flutter_smsussd")          │
├──────────────────────────────────────┤
│ + getPlatformVersion()               │
│ + sendSms(phoneNumber, message)      │
│ + getSmsMessages()                   │
│ + getSmsMessagesByPhoneNumber()      │
│ + requestSmsPermissions()            │
│ + hasSmsPermissions()                │
└──────────────────────────────────────┘
```

### Communication Flow

```
Flutter Code
     │
     │  Method Call
     ▼
┌─────────────────────────┐
│ MethodChannel           │
│ "flutter_smsussd"       │
└─────────────────────────┘
     │
     │  Platform Channel
     ▼
Native Code (Android/iOS/Web)
     │
     │  Result/Error
     ▼
┌─────────────────────────┐
│ PlatformException       │
│ or Success Result       │
└─────────────────────────┘
     │
     │  Map to Dart
     ▼
Flutter Code (Response)
```

## Method Specifications

### getPlatformVersion()

**Signature**: `Future<String?> getPlatformVersion()`

**Method Channel Call**:
```dart
await methodChannel.invokeMethod<String>('getPlatformVersion')
```

**Arguments**: None

**Returns**: `String?` - Platform version string

**Platform Responses**:
- Android: `"Android {VERSION_RELEASE}"` (e.g., "Android 13")
- iOS: Not implemented (uses default from platform interface)
- Web: User agent string

### sendSms()

**Signature**:
```dart
Future<bool> sendSms({
  required String phoneNumber,
  required String message,
})
```

**Method Channel Call**:
```dart
await methodChannel.invokeMethod<bool>('sendSms', {
  'phoneNumber': phoneNumber,
  'message': message,
})
```

**Arguments**:
```json
{
  "phoneNumber": "+1234567890",
  "message": "Hello World"
}
```

**Returns**: `bool` - `true` if successful, `false` otherwise

**Exception Handling**:
```dart
try {
  final result = await methodChannel.invokeMethod<bool>('sendSms', {...});
  return result ?? false;
} on PlatformException catch (e) {
  if (e.code == 'SMS_NOT_AVAILABLE') {
    throw UnsupportedError('SMS is not available on this device');
  } else if (e.code == 'NO_VIEW_CONTROLLER') {
    throw StateError('No view controller available to present SMS composer');
  } else if (e.code == 'SMS_SEND_ERROR') {
    throw StateError('Failed to send SMS: ${e.message}');
  }
  rethrow;
}
```

**Platform Behavior**:
- Android: Sends SMS directly via SmsManager
- iOS: Opens native SMS composer (user must manually send)
- Web: Not supported

### getSmsMessages()

**Signature**: `Future<List<SmsMessage>> getSmsMessages()`

**Method Channel Call**:
```dart
final List<dynamic> result = await methodChannel.invokeMethod<List<dynamic>>('getSmsMessages');
return result.map((item) => SmsMessage.fromMap(Map<String, dynamic>.from(item))).toList();
```

**Arguments**: None

**Returns**: `List<SmsMessage>` - All SMS messages from device

**Exception Handling**:
```dart
try {
  final List<dynamic> result = await methodChannel.invokeMethod<List<dynamic>>('getSmsMessages');
  // deserialize...
} on PlatformException catch (e) {
  if (e.code == 'NOT_SUPPORTED') {
    throw UnsupportedError('Reading SMS messages is not supported on this platform');
  }
  rethrow;
}
```

**Platform Behavior**:
- Android: Queries Telephony.Sms content provider, returns all messages
- iOS: Throws NOT_SUPPORTED
- Web: Throws NOT_SUPPORTED

### getSmsMessagesByPhoneNumber()

**Signature**: `Future<List<SmsMessage>> getSmsMessagesByPhoneNumber(String phoneNumber)`

**Method Channel Call**:
```dart
final List<dynamic> result = await methodChannel.invokeMethod<List<dynamic>>(
  'getSmsMessagesByPhoneNumber',
  {'phoneNumber': phoneNumber}
);
```

**Arguments**:
```json
{
  "phoneNumber": "+1234567890"
}
```

**Returns**: `List<SmsMessage>` - Filtered SMS messages

**Exception Handling**: Same as `getSmsMessages()`

**Platform Behavior**:
- Android: Queries with WHERE clause on ADDRESS column
- iOS: Throws NOT_SUPPORTED
- Web: Throws NOT_SUPPORTED

### requestSmsPermissions()

**Signature**: `Future<bool> requestSmsPermissions()`

**Method Channel Call**:
```dart
final result = await methodChannel.invokeMethod<bool>('requestSmsPermissions');
return result ?? false;
```

**Arguments**: None

**Returns**: `bool` - Permission request result

**Platform Behavior**:
- Android: Requests runtime permissions (SEND_SMS, READ_SMS, RECEIVE_SMS)
- iOS: Not needed (uses MessageUI framework)
- Web: Not applicable

### hasSmsPermissions()

**Signature**: `Future<bool> hasSmsPermissions()`

**Method Channel Call**:
```dart
final result = await methodChannel.invokeMethod<bool>('hasSmsPermissions');
return result ?? false;
```

**Arguments**: None

**Returns**: `bool` - Current permission status

**Platform Behavior**:
- Android: Checks all required permissions using ContextCompat
- iOS: Not applicable
- Web: Not applicable

## Exception Mapping Table

| PlatformException Code | Dart Exception | Message |
|------------------------|----------------|---------|
| `SMS_NOT_AVAILABLE` | `UnsupportedError` | "SMS is not available on this device" |
| `NO_VIEW_CONTROLLER` | `StateError` | "No view controller available to present SMS composer" |
| `SMS_SEND_ERROR` | `StateError` | "Failed to send SMS: {message}" |
| `NOT_SUPPORTED` | `UnsupportedError` | "Reading SMS messages is not supported on this platform" |
| Other codes | Rethrow PlatformException | Original error |

## Data Serialization

### Argument Maps

All method arguments passed as `Map<String, dynamic>`:

```dart
// sendSms arguments
{
  'phoneNumber': String,  // required
  'message': String,      // required
}

// getSmsMessagesByPhoneNumber arguments
{
  'phoneNumber': String,  // required
}
```

### Result Deserialization

**List Deserialization**:
```dart
final List<dynamic> result = await methodChannel.invokeMethod<List<dynamic>>('getSmsMessages');
final messages = result
  .map((item) => SmsMessage.fromMap(Map<String, dynamic>.from(item)))
  .toList();
```

**Type Casting**:
- `List<dynamic>` → `List<SmsMessage>`
- Each item: `Map<String, dynamic>` → `SmsMessage`

## Testing Strategy

### Mock Method Channel

```dart
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

test('sendSms returns true on success', () async {
  TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
    .setMockMethodCallHandler(channel, (MethodCall methodCall) async => true);
  
  final result = await plugin.sendSms(
    phoneNumber: '+1234567890',
    message: 'Test message',
  );
  expect(result, true);
});
```

### Test Coverage

**Location**: `test/flutter_smsussd_method_channel_test.dart`

**Tested Scenarios**:
- `getPlatformVersion()` returns string
- `sendSms()` returns true/false
- `getSmsMessages()` returns list of messages
- `getSmsMessagesByPhoneNumber()` returns filtered list
- `requestSmsPermissions()` returns true
- `hasSmsPermissions()` returns true/false

## Implementation Details

### File Structure

```
lib/
└── flutter_smsussd_method_channel.dart
```

### Imports

```dart
import 'package:flutter/foundation.dart';        // visibleForTesting
import 'package:flutter/services.dart';          // MethodChannel, PlatformException
import 'flutter_smsussd_platform_interface.dart'; // Parent class, SmsMessage
```

### Class Declaration

```dart
class MethodChannelFlutterSmsussd extends FlutterSmsussdPlatform {
  @visibleForTesting
  final methodChannel = const MethodChannel('flutter_smsussd');
  
  // Method implementations...
}
```

## Performance Considerations

- **Method Channel Overhead**: ~1-5ms per call (Flutter platform channel latency)
- **Serialization**: Minimal (direct map construction)
- **Deserialization**: O(n) for list operations where n = number of messages
- **Memory**: No caching, all data fetched fresh from native

## Security Considerations

- **Type Safety**: Strong typing prevents injection attacks
- **Argument Validation**: Required parameters enforced at compile time
- **Exception Safety**: All platform exceptions caught and handled
- **No Sensitive Data**: Method channel doesn't store sensitive information

---

*Generated by /legacy analysis on 2026-03-04*
*Status: DRAFT*
