# Specifications: Platform Interface Module

> Technical specifications derived from code analysis.

## Architecture

### Platform Interface Pattern

```
┌─────────────────────────────────────┐
│   FlutterSmsussdPlatform (abstract) │
│   - static _token: Object           │
│   - static _instance: Platform      │
│   + static instance: Platform       │
│   + getPlatformVersion()            │
│   + sendSms()                       │
│   + getSmsMessages()                │
│   + getSmsMessagesByPhoneNumber()   │
│   + requestSmsPermissions()         │
│   + hasSmsPermissions()             │
└─────────────────────────────────────┘
                ▲
                │ extends
    ┌───────────┼───────────┬──────────────┐
    │           │           │              │
┌───┴───┐  ┌───┴────┐  ┌───┴────┐  ┌─────┴────┐
│Method │  │Android │  │  iOS   │  │   Web    │
│Channel│  │ Imple- │  │ Imple- │  │ Imple-   │
│ Imple │  │ mentation│  │mentation│ │mentation│
└───────┘  └────────┘  └────────┘  └──────────┘
```

## Data Model Specifications

### SmsMessage

```dart
class SmsMessage {
  final String id;           // Unique message identifier
  final String address;      // Phone number
  final String body;         // Message content
  final DateTime date;       // Timestamp (from milliseconds)
  final SmsType type;        // Message type enum
}
```

**Serialization Format**:
```json
{
  "id": "123",
  "address": "+1234567890",
  "body": "Hello World",
  "date": 1640995200000,
  "type": 0
}
```

**Methods**:
- `fromMap(Map<String, dynamic>)` - Factory constructor for deserialization
- `toMap()` - Returns Map<String, dynamic> for serialization

### SmsType Enum

```dart
enum SmsType {
  inbox,    // index: 0 - Received messages
  sent,     // index: 1 - Sent messages
  draft,    // index: 2 - Draft messages
  outbox,   // index: 3 - Outbox messages
  failed,   // index: 4 - Failed messages
  queued,   // index: 5 - Queued messages
}
```

**Mapping to Android Telephony Contract**:
- Matches `android.provider.Telephony.Sms` type constants
- Index-based serialization for efficiency

## Method Specifications

### getPlatformVersion()

**Signature**: `Future<String?> getPlatformVersion()`

**Behavior**:
- Returns platform-specific version string
- May return null if platform doesn't provide version

**Platform Implementations**:
- Android: Returns "Android {VERSION_RELEASE}"
- iOS: Not implemented (uses default)
- Web: Returns user agent string

### sendSms()

**Signature**: 
```dart
Future<bool> sendSms({
  required String phoneNumber,
  required String message,
})
```

**Parameters**:
- `phoneNumber` - Recipient phone number (required)
- `message` - SMS message content (required)

**Returns**: `true` if successful, `false` otherwise

**Error Handling**:
- Throws `UnimplementedError` if not overridden
- Platform-specific exceptions wrapped in PlatformException

### getSmsMessages()

**Signature**: `Future<List<SmsMessage>> getSmsMessages()`

**Returns**: List of all SMS messages from device

**Platform Support**:
- Android: ✅ Full implementation
- iOS: ❌ Not supported (opens composer only)
- Web: ❌ Not supported

### getSmsMessagesByPhoneNumber()

**Signature**: `Future<List<SmsMessage>> getSmsMessagesByPhoneNumber(String phoneNumber)`

**Parameters**:
- `phoneNumber` - Filter messages by this number

**Returns**: List of matching SMS messages

**Platform Support**:
- Android: ✅ Full implementation
- iOS: ❌ Not supported
- Web: ❌ Not supported

### requestSmsPermissions()

**Signature**: `Future<bool> requestSmsPermissions()`

**Returns**: `true` if permissions granted, `false` otherwise

**Platform Support**:
- Android: ✅ Runtime permission request
- iOS: ❌ Not needed (uses MessageUI framework)
- Web: ❌ Not applicable

### hasSmsPermissions()

**Signature**: `Future<bool> hasSmsPermissions()`

**Returns**: Current permission status

**Platform Support**:
- Android: ✅ Checks all required permissions
- iOS: ❌ Not applicable
- Web: ❌ Not applicable

## Token Verification Pattern

```dart
static final Object _token = Object();

static set instance(FlutterSmsussdPlatform instance) {
  PlatformInterface.verifyToken(instance, _token);
  _instance = instance;
}
```

**Purpose**: Prevents unauthorized classes from being set as platform instance

**Verification**: Runtime check ensures only subclasses of `FlutterSmsussdPlatform` can be assigned

## Error Handling Strategy

### Default Implementation

All methods throw `UnimplementedError`:
```dart
Future<String?> getPlatformVersion() {
  throw UnimplementedError('getPlatformVersion() has not been implemented.');
}
```

### Platform Exceptions

Method channel catches `PlatformException` and maps to Dart exceptions:
- `SMS_NOT_AVAILABLE` → `UnsupportedError`
- `NO_VIEW_CONTROLLER` → `StateError`
- `SMS_SEND_ERROR` → `StateError`
- `NOT_SUPPORTED` → `UnsupportedError`

## Testing Strategy

### Unit Tests

**Location**: `test/flutter_smsussd_test.dart`

**Coverage**:
- SmsMessage serialization/deserialization
- SmsType enum values
- fromMap/toMap correctness

### Mocking Platform

```dart
TestWidgetsFlutterBinding.ensureInitialized();

// Set mock platform instance
FlutterSmsussdPlatform.instance = MockPlatform();
```

## Implementation Details

### File Structure

```
lib/
└── flutter_smsussd_platform_interface.dart
```

### Exports

The file exports:
- `FlutterSmsussdPlatform` abstract class
- `SmsMessage` data class
- `SmsType` enum

### Dependencies

```yaml
dependencies:
  plugin_platform_interface: ^3.0.0
```

## Performance Considerations

- Token verification: O(1) constant time
- Data serialization: Minimal overhead (direct map conversion)
- No reflection or runtime code generation
- Immutable data models for thread safety

## Security Considerations

- Token-based verification prevents malicious platform injection
- Type-safe method signatures prevent injection attacks
- No sensitive data stored in platform interface layer

---

*Generated by /legacy analysis on 2026-03-04*
*Status: DRAFT*
