# Specifications: Split Library and Example

> Version: 1.0
> Status: REVIEW
> Last Updated: 2026-03-15

## System Architecture

### Library Structure: `flutter_gsmsip`

```
flutter_gsmsip/
├── pubspec.yaml              # Package definition
├── lib/
│   ├── flutter_gsmsip.dart   # Main export
│   ├── src/
│   │   ├── domain/           # Entities, repositories interfaces, use cases
│   │   ├── data/             # Repository implementations, services
│   │   └── gsm_sip_bridge.dart  # Main API facade
├── android/
│   ├── build.gradle          # Android build config
│   ├── settings.gradle       # Android settings
│   ├── src/
│   │   ├── main/
│   │   │   ├── AndroidManifest.xml
│   │   │   ├── kotlin/       # Kotlin code
│   │   │   │   └── org/telon/flutter_gsmsip/
│   │   │   │       ├── FlutterGsmSipPlugin.kt  # Plugin entry point
│   │   │   │       ├── sip/                    # SIP native code
│   │   │   │       ├── smpp/                   # SMPP code
│   │   │   │       └── gsm/                    # GSM telephony code
│   │   │   └── java/         # Java code (if any)
│   │   └── main/
├── example/
│   ├── pubspec.yaml          # Depends on flutter_gsmsip
│   ├── lib/
│   │   ├── main.dart         # Example app entry
│   │   ├── presentation/     # UI, providers, screens
│   │   └── app_logic.dart    # App-specific logic using library
│   └── android/              # Example app Android config
└── test/                     # Library tests
```

### Code Distribution

| Component | Location | Rationale |
|-----------|----------|-----------|
| **PJSIP native code** | `flutter_gsmsip/android/src/main/kotlin/` | Core SIP stack, reusable |
| **Kotlin SIP service** | `flutter_gsmsip/android/src/main/kotlin/sip/` | Native SIP operations |
| **Kotlin GSM service** | `flutter_gsmsip/android/src/main/kotlin/gsm/` | GSM telephony |
| **Kotlin SMPP service** | `flutter_gsmsip/android/src/main/kotlin/smpp/` | SMPP messaging |
| **Dart SIP service** | `flutter_gsmsip/lib/src/data/services/` | Dart wrapper for native |
| **Dart GSM service** | `flutter_gsmsip/lib/src/data/services/` | Dart wrapper for native |
| **Dart SMPP service** | `flutter_gsmsip/lib/src/data/services/` | Dart wrapper for native |
| **Domain entities** | `flutter_gsmsip/lib/src/domain/entities/` | Business models |
| **Domain repositories** | `flutter_gsmsip/lib/src/domain/repositories/` | Interfaces |
| **Use cases** | `flutter_gsmsip/lib/src/domain/usecases/` | Business logic |
| **Repository implementations** | `flutter_gsmsip/lib/src/data/repositories/` | Data layer |
| **Main API facade** | `flutter_gsmsip/lib/flutter_gsmsip.dart` | Clean public API |
| **UI providers** | `flutter_gsmsip/example/lib/presentation/` | App-specific |
| **Screens** | `flutter_gsmsip/example/lib/` | App UI |
| **Widgets** | `flutter_gsmsip/example/lib/widgets/` | App UI components |
| **Dependency injection** | `flutter_gsmsip/example/lib/` | App-specific setup |

## Library Public API

The library will expose a clean facade:

```dart
// flutter_gsmsip/lib/flutter_gsmsip.dart
import 'src/gsm_sip_bridge.dart';
import 'src/sip_service.dart';
import 'src/gsm_service.dart';
import 'src/smpp_service.dart';
import 'src/domain/entities/*.dart';

// Main API
export 'src/gsm_sip_bridge.dart';
export 'src/sip_service.dart';
export 'src/gsm_service.dart';
export 'src/smpp_service.dart';

// Entities
export 'src/domain/entities/sip_account.dart';
export 'src/domain/entities/sip_call.dart';
export 'src/domain/entities/gateway_config.dart';
export 'src/domain/entities/gateway_status.dart';
export 'src/domain/entities/call_routing.dart';

// Events
export 'src/domain/entities/sip_event.dart';
```

## Native Code Structure

### Kotlin Plugin Entry Point

```kotlin
// FlutterGsmSipPlugin.kt
class FlutterGsmSipPlugin: FlutterPlugin, MethodCallHandler {
    private var sipService: SipService? = null
    private var gsmService: GsmService? = null
    private var smppService: SmppService? = null
    
    override fun onMethodCall(call: MethodCall, result: Result) {
        when (call.method) {
            "initializeSip" -> sipService?.initialize(call.arguments, result)
            "makeCall" -> sipService?.makeCall(call.arguments, result)
            "sendSms" -> gsmService?.sendSms(call.arguments, result)
            // ... etc
        }
    }
}
```

### PJSIP Integration

The PJSIP native library will be included in the library's Android module:

```
flutter_gsmsip/android/libs/
├── libpjlib-util-arm64-v8a.so
├── libpjmedia-arm64-v8a.so
├── libpjsip-arm64-v8a.so
├── libpjsua2-arm64-v8a.so
└── ... (other ABIs)
```

## Affected Files

### Files Moving to Library (`flutter_gsmsip/lib/`)

| Source File | Destination |
|-------------|-------------|
| `lib/domain/entities/*.dart` | `flutter_gsmsip/lib/src/domain/entities/` |
| `lib/domain/repositories/*.dart` | `flutter_gsmsip/lib/src/domain/repositories/` |
| `lib/domain/usecases/*.dart` | `flutter_gsmsip/lib/src/domain/usecases/` |
| `lib/data/repositories/*.dart` | `flutter_gsmsip/lib/src/data/repositories/` |
| `lib/data/services/sip_service.dart` | `flutter_gsmsip/lib/src/data/services/` |
| `lib/data/services/gateway_service.dart` | `flutter_gsmsip/lib/src/data/services/` |
| `lib/services/sms_service.dart` | `flutter_gsmsip/lib/src/data/services/` |
| `lib/services/smpp_service.dart` | `flutter_gsmsip/lib/src/data/services/` |
| `lib/services/telephony_service.dart` | `flutter_gsmsip/lib/src/data/services/` |
| `android/app/src/main/kotlin/.../sip/` | `flutter_gsmsip/android/src/main/kotlin/sip/` |
| `android/app/src/main/kotlin/.../gsm/` | `flutter_gsmsip/android/src/main/kotlin/gsm/` |
| `android/app/src/main/kotlin/.../smpp/` | `flutter_gsmsip/android/src/main/kotlin/smpp/` |

### Files Moving to Example (`flutter_gsmsip/example/`)

**All remaining files** - The entire current app is moved to example:

| Source File | Destination |
|-------------|-------------|
| `lib/main.dart` | `flutter_gsmsip/example/lib/main.dart` |
| `lib/presentation/` | `flutter_gsmsip/example/lib/presentation/` |
| `lib/screens/` | `flutter_gsmsip/example/lib/screens/` |
| `lib/widgets/` | `flutter_gsmsip/example/lib/widgets/` |
| `lib/core/` | `flutter_gsmsip/example/lib/core/` |
| `lib/services/` | `flutter_gsmsip/example/lib/services/` |
| `lib/models/` | `flutter_gsmsip/example/lib/models/` |
| `lib/utils/` | `flutter_gsmsip/example/lib/utils/` |
| `android/app/` | `flutter_gsmsip/example/android/app/` |
| `test/` | `flutter_gsmsip/example/test/` |
| `pubspec.yaml` | `flutter_gsmsip/example/pubspec.yaml` (updated) |

## Library Dependencies (pubspec.yaml)

```yaml
name: flutter_gsmsip
description: Flutter GSM SIP SMPP library for Android
version: 0.1.0
platforms:
  android:

dependencies:
  flutter:
    sdk: flutter
  dartz: ^0.10.1  # Either type for error handling
  equatable: ^2.0.5  # Value equality
  logger: ^2.0.1  # Logging

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
```

## Example App Dependencies (pubspec.yaml)

```yaml
name: flutter_gsmsip_example
description: Example app for flutter_gsmsip
version: 1.0.0

dependencies:
  flutter:
    sdk: flutter
  flutter_gsmsip:
    path: ../  # Local dependency
  provider: ^6.0.0  # State management
  get_it: ^7.6.0  # DI
  # ... other app-specific deps
```

## Edge Cases

### 1. Method Channel Communication

Library must handle async method channel calls properly:

```dart
class SipService {
  static const MethodChannel _channel = MethodChannel('flutter_gsmsip/sip');
  
  Future<bool> initialize() async {
    try {
      final result = await _channel.invokeMethod<bool>('initialize');
      return result ?? false;
    } on PlatformException catch (e) {
      throw SipException('Failed to initialize: ${e.message}');
    }
  }
}
```

### 2. Event Streaming

Native events must be streamed to Dart:

```kotlin
// Kotlin
private val eventChannel = EventChannel(binding.binaryMessenger, "flutter_gsmsip/sip_events")
private val eventSink = AtomicReference<EventChannel.EventSink?>()

override fun onAttachedToEngine(binding: FlutterPlugin.FlutterPluginBinding) {
    eventChannel.setStreamHandler(object : EventChannel.StreamHandler {
        override fun onListen(args: Any?, sink: EventChannel.EventSink) {
            eventSink.set(sink)
        }
        override fun onCancel(args: Any?) {
            eventSink.set(null)
        }
    })
}
```

```dart
// Dart
final _eventChannel = const EventChannel('flutter_gsmsip/sip_events');
Stream<SipEvent> get eventStream => 
    _eventChannel.receiveBroadcastStream().map((data) => SipEvent.fromJson(data));
```

### 3. Multiple Instance Support

Library should support multiple SIP accounts:

```dart
class GsmSipBridge {
  final Map<String, SipAccount> _accounts = {};
  
  Future<void> addAccount(SipAccount account) async {
    _accounts[account.id] = account;
    await _channel.invokeMethod('addAccount', account.toJson());
  }
}
```

## Testing Strategy

### Library Tests

1. **Unit tests**: Test Dart service wrappers
2. **Integration tests**: Test method channel communication
3. **Native tests**: Test Kotlin code with JUnit

### Example App Tests

1. **Widget tests**: Test UI components
2. **Integration tests**: Test full app flows

## Migration Steps

1. Create `flutter_gsmsip` Flutter plugin
2. Copy native Kotlin code to library
3. Copy Dart library code
4. Create example app structure
5. Move presentation code to example
6. Update imports and dependencies
7. Test library builds independently
8. Test example app runs correctly

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]
