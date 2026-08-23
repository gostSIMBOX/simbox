# Activity Intents Implementation Log

**Flow**: sdd-activity-intents
**Date**: 2026-03-06
**Status**: IMPLEMENTED

---

## Tasks Completed

### intent-001: Implement ActivityIntentService (navigation routing)

**File**: `lib/services/activity_intent_service.dart`

**Implementation Details**:

- Created `ActivityIntentService` singleton class
- Implemented MethodChannel communication with native Android (`gsm_sip_gateway/activity_intent`)
- Added intent type enumeration: `view`, `dial`, `unknown`
- Created `ActivityIntentData` class for intent data structure
- Implemented stream-based event handling for intent reception
- Added logging via `logger` package

**Key Methods**:
- `initialize()` - Sets up method channel handler
- `_handleMethodCall()` - Handles native method calls
- `_handleIntentReceived()` - Processes incoming intents
- `registerIntentHandler()` - Allows custom intent handlers
- `isValidPhoneNumber()` - Static validation utility
- `sanitizePhoneNumber()` - Static sanitization utility
- `parseTelUri()` - Static tel: URI parser

**Data Models**:
- `ActivityIntentType` enum
- `ActivityIntentData` class
- `NavigationRoute` class

---

### intent-002: Implement navigation routing (deep links, internal navigation)

**File**: `lib/services/activity_intent_service.dart`

**Implementation Details**:

- Implemented navigation routing based on intent type
- Created `NavigationRoute` class for route information
- Added route handler registration system
- Implemented automatic routing for VIEW and DIAL intents
- Both intent types route to `/dialer` with phone number pre-filled

**Navigation Flow**:
```
Intent Received (VIEW/DIAL)
      │
      ▼
Extract Phone Number
      │
      ▼
Validate/Sanitize
      │
      ▼
Create NavigationRoute
      │
      ▼
Emit to navigationStream
      │
      ▼
Flutter UI handles navigation
```

**Route Handlers**:
- `_handleViewIntent()` - Handles tel: URLs from browsers, emails
- `_handleDialIntent()` - Handles dial requests from voice assistants
- `navigate()` - Internal navigation method
- `registerRouteHandler()` - Custom route handler registration

---

## Integration Points

### With Existing Services

| Service | Integration | Status |
|---------|-------------|--------|
| TelephonyService | None (independent) | N/A |
| SipService | None (independent) | N/A |
| GatewayService | None (independent) | N/A |

### With Native Android

| Method Channel | Purpose | Status |
|----------------|---------|--------|
| `gsm_sip_gateway/activity_intent` | Intent reception | Requires native implementation |
| `getInitialIntent` | Get launch intent | Requires native implementation |
| `onIntentReceived` | New intent callback | Requires native implementation |
| `onNavigationRequested` | Navigation callback | Requires native implementation |

---

## Design Decisions

### 1. Stream-Based Architecture
**Decision**: Use `StreamController.broadcast()` for intent and navigation events

**Rationale**:
- Consistent with existing service patterns (SipService, TelephonyService)
- Allows multiple listeners
- Decouples intent reception from handling

### 2. Static Utility Methods
**Decision**: Make phone validation/sanitization methods static

**Rationale**:
- No instance state required
- Easy to use anywhere in the app
- Testable in isolation

### 3. Intent Type Enumeration
**Decision**: Use enum instead of string matching

**Rationale**:
- Type safety
- IDE autocomplete support
- Compile-time checking

### 4. Handler Registration Pattern
**Decision**: Allow custom intent/route handlers via registration

**Rationale**:
- Flexible architecture
- Allows app-specific handling
- Default behavior provided but overridable

---

## Security Considerations

### Input Validation
- Phone numbers validated against regex: `^[0-9+*#\- ]+$`
- Maximum length: 20 characters
- Sanitization removes invalid characters

### Intent Validation
- Null checks on all intent data
- Scheme validation (tel: only)
- Action validation (VIEW/DIAL only)

---

## Testing Recommendations

### Unit Tests
- [ ] `isValidPhoneNumber()` with valid/invalid inputs
- [ ] `sanitizePhoneNumber()` with various formats
- [ ] `parseTelUri()` with different URI formats
- [ ] `ActivityIntentData.fromMap()` with valid/invalid maps

### Integration Tests
- [ ] Intent reception from native code
- [ ] Navigation route emission
- [ ] Handler registration and invocation

### Manual Tests
- [ ] Browser tel: link clicking
- [ ] Voice assistant dial commands
- [ ] Email client tel: links
- [ ] QR scanner tel: results

---

## Native Android Requirements

The following native Android implementation is required:

### MainActivity.kt
```kotlin
class MainActivity: FlutterActivity() {
    private val channel = MethodChannel(flutterEngine!!.dartExecutor.binaryMessenger,
        "gsm_sip_gateway/activity_intent")

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)

        if (intent.action == Intent.ACTION_VIEW ||
            intent.action == Intent.ACTION_DIAL) {
            val data = intent.data
            if (data != null && data.scheme == "tel") {
                val phoneNumber = data.schemeSpecificPart
                val intentData = mapOf(
                    "type" to intent.action.toLowerCase(),
                    "phoneNumber" to phoneNumber,
                    "action" to intent.action
                )
                channel.invokeMethod("onIntentReceived", intentData)
            }
        }
    }

    // Method channel handler
    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger,
            "gsm_sip_gateway/activity_intent").setMethodCallHandler { call, result ->
            when (call.method) {
                "getInitialIntent" -> {
                    // Return initial intent if available
                }
                else -> result.notImplemented()
            }
        }
    }
}
```

### AndroidManifest.xml
```xml
<activity android:name=".MainActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <action android:name="android.intent.action.DIAL" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="tel"/>
    </intent-filter>

    <intent-filter>
        <action android:name="android.intent.action.DIAL"/>
        <category android:name="android.intent.category.DEFAULT"/>
    </intent-filter>
</activity>
```

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `lib/services/activity_intent_service.dart` | ~280 | Complete service implementation |

---

## Issues/Notes

1. **Native Implementation Required**: The service requires native Android code to send intents via MethodChannel
2. **Future Enhancement**: Auto-dial functionality could be added as optional feature
3. **Future Enhancement**: Contact integration for phone number lookup

---

*Implementation completed: 2026-03-06*
