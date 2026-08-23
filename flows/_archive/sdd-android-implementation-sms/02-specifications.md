# Specifications: Android Implementation Module

> Technical specifications derived from code analysis.

## Architecture

### Class Structure

```
┌────────────────────────────────────────────────┐
│ FlutterSmsussdPlugin                           │
│ implements FlutterPlugin                       │
│ implements MethodCallHandler                   │
│ implements ActivityAware                       │
├────────────────────────────────────────────────┤
│ - channel: MethodChannel                       │
│ - context: Context                             │
│ - activity: Activity?                          │
│ - REQUIRED_PERMISSIONS: Array<String>          │
│ - SMS_PERMISSION_REQUEST_CODE: Int = 123       │
├────────────────────────────────────────────────┤
│ + onAttachedToEngine()                         │
│ + onDetachedFromEngine()                       │
│ + onAttachedToActivity()                       │
│ + onDetachedFromActivity()                     │
│ + onMethodCall()                               │
│ - sendSms()                                    │
│ - getSmsMessages()                             │
│ - getSmsMessagesByPhoneNumber()                │
│ - requestSmsPermissions()                      │
│ - hasSmsPermissions()                          │
└────────────────────────────────────────────────┘
```

### Interface Implementation

**FlutterPlugin**:
- `onAttachedToEngine(binding)` - Setup method channel
- `onDetachedFromEngine(binding)` - Cleanup

**MethodCallHandler**:
- `onMethodCall(call, result)` - Handle method calls

**ActivityAware**:
- `onAttachedToActivity(binding)` - Store activity
- `onDetachedFromActivity()` - Clear activity
- `onReattachedToActivityForConfigChanges(binding)` - Restore
- `onDetachedFromActivityForConfigChanges()` - Clear temporarily

## Method Specifications

### onMethodCall()

**Signature**:
```kotlin
override fun onMethodCall(call: MethodCall, result: Result)
```

**Method Handlers**:

| Method | Handler | Arguments | Returns |
|--------|---------|-----------|---------|
| `getPlatformVersion` | Direct | None | `"Android {version}"` |
| `sendSms` | `sendSms()` | phoneNumber, message | Boolean |
| `getSmsMessages` | `getSmsMessages()` | None | List<Map> |
| `getSmsMessagesByPhoneNumber` | `getSmsMessagesByPhoneNumber()` | phoneNumber | List<Map> |
| `requestSmsPermissions` | `requestSmsPermissions()` | None | Boolean |
| `hasSmsPermissions` | Direct | None | Boolean |

**Error Handling**:
```kotlin
when (call.method) {
  "sendSms" -> {
    val phoneNumber = call.argument<String>("phoneNumber")
    val message = call.argument<String>("message")
    if (phoneNumber == null || message == null) {
      result.error("INVALID_ARGUMENTS", "...", null)
      return
    }
    sendSms(phoneNumber, message, result)
  }
}
```

### sendSms()

**Signature**:
```kotlin
private fun sendSms(phoneNumber: String, message: String, result: Result)
```

**Flow**:
```
1. Check permissions → return error if denied
2. Get SmsManager instance
3. Divide message into parts
4. IF parts.size > 1:
   - Create sent/delivered PendingIntent arrays
   - Call sendMultipartTextMessage()
5. ELSE:
   - Call sendTextMessage()
6. Return success (true)
7. Catch exceptions → return SMS_SEND_ERROR
```

**Multipart SMS**:
```kotlin
val parts = smsManager.divideMessage(message)
val sentIntents = ArrayList<PendingIntent>()
val deliveredIntents = ArrayList<PendingIntent>()

for (i in parts.indices) {
  sentIntents.add(PendingIntent.getBroadcast(
    context, 0, Intent("SMS_SENT"), PendingIntent.FLAG_IMMUTABLE
  ))
  deliveredIntents.add(PendingIntent.getBroadcast(
    context, 0, Intent("SMS_DELIVERED"), PendingIntent.FLAG_IMMUTABLE
  ))
}

smsManager.sendMultipartTextMessage(
  phoneNumber, null, parts, sentIntents, deliveredIntents
)
```

**Single SMS**:
```kotlin
smsManager.sendTextMessage(
  phoneNumber, null, message, null, null
)
```

### getSmsMessages()

**Signature**:
```kotlin
private fun getSmsMessages(result: Result)
```

**Flow**:
```
1. Check permissions → return error if denied
2. Get ContentResolver from context
3. Query Telephony.Sms.CONTENT_URI
4. Order by DATE DESC
5. Iterate cursor, build message maps
6. Return list of messages
7. Catch exceptions → return SMS_READ_ERROR
```

**Query**:
```kotlin
val cursor = contentResolver.query(
  Telephony.Sms.CONTENT_URI,
  null,  // All columns
  null,  // No filter
  null,  // No selection args
  "${Telephony.Sms.DATE} DESC"  // Order
)
```

**Cursor Iteration**:
```kotlin
cursor?.use { c ->
  val idIndex = c.getColumnIndex(Telephony.Sms._ID)
  val addressIndex = c.getColumnIndex(Telephony.Sms.ADDRESS)
  val bodyIndex = c.getColumnIndex(Telephony.Sms.BODY)
  val dateIndex = c.getColumnIndex(Telephony.Sms.DATE)
  val typeIndex = c.getColumnIndex(Telephony.Sms.TYPE)

  while (c.moveToNext()) {
    val message = mapOf(
      "id" to c.getString(idIndex),
      "address" to (c.getString(addressIndex) ?: ""),
      "body" to (c.getString(bodyIndex) ?: ""),
      "date" to c.getLong(dateIndex),
      "type" to c.getInt(typeIndex)
    )
    messages.add(message)
  }
}
```

### getSmsMessagesByPhoneNumber()

**Signature**:
```kotlin
private fun getSmsMessagesByPhoneNumber(phoneNumber: String, result: Result)
```

**Query with Filter**:
```kotlin
val cursor = contentResolver.query(
  Telephony.Sms.CONTENT_URI,
  null,
  "${Telephony.Sms.ADDRESS} = ?",  // WHERE clause
  arrayOf(phoneNumber),            // Selection args
  "${Telephony.Sms.DATE} DESC"
)
```

### requestSmsPermissions()

**Signature**:
```kotlin
private fun requestSmsPermissions(result: Result)
```

**Flow**:
```
1. Check if already granted → return true
2. Check if activity available → return NO_ACTIVITY if null
3. Request permissions using ActivityCompat
4. Return true (result comes via callback, not handled here)
```

**Implementation**:
```kotlin
if (hasSmsPermissions()) {
  result.success(true)
  return
}

activity?.let { act ->
  ActivityCompat.requestPermissions(
    act,
    REQUIRED_PERMISSIONS,
    SMS_PERMISSION_REQUEST_CODE
  )
  result.success(true)
} ?: run {
  result.error("NO_ACTIVITY", "...", null)
}
```

### hasSmsPermissions()

**Signature**:
```kotlin
private fun hasSmsPermissions(): Boolean
```

**Implementation**:
```kotlin
private fun hasSmsPermissions(): Boolean {
  return REQUIRED_PERMISSIONS.all { permission ->
    ContextCompat.checkSelfPermission(context, permission) == 
      PackageManager.PERMISSION_GRANTED
  }
}
```

## Permission Specifications

### Required Permissions

```kotlin
private val REQUIRED_PERMISSIONS = arrayOf(
  Manifest.permission.SEND_SMS,      // Send SMS
  Manifest.permission.READ_SMS,      // Read SMS database
  Manifest.permission.RECEIVE_SMS    // Receive SMS (broadcast)
)
```

### Permission Request Code

```kotlin
companion object {
  private const val SMS_PERMISSION_REQUEST_CODE = 123
}
```

### Permission Check Flow

```
hasSmsPermissions()
    │
    ├─► Check SEND_SMS ✓
    ├─► Check READ_SMS ✓
    └─► Check RECEIVE_SMS ✓
        
        All granted? → true : false
```

## Error Code Specifications

| Error Code | HTTP-style | Description | When Returned |
|------------|------------|-------------|---------------|
| `INVALID_ARGUMENTS` | 400 | Missing required parameters | Null arguments |
| `PERMISSION_DENIED` | 403 | SMS permissions not granted | Permission check fails |
| `SMS_SEND_ERROR` | 500 | Failed to send SMS | Exception during send |
| `SMS_READ_ERROR` | 500 | Failed to read SMS | Exception during read |
| `NO_ACTIVITY` | 503 | No activity for permission request | Activity is null |

## Data Serialization

### Message Map Format

```kotlin
mapOf(
  "id" to String,        // SMS _ID from database
  "address" to String,   // Phone number
  "body" to String,      // Message content
  "date" to Long,        // Timestamp (milliseconds)
  "type" to Int          // SMS type index (0=inbox, 1=sent, etc.)
)
```

### Column Mapping

| Database Column | Map Key | Type | Notes |
|-----------------|---------|------|-------|
| `_ID` | `id` | String | Unique identifier |
| `ADDRESS` | `address` | String | Phone number, nullable |
| `BODY` | `body` | String | Message content, nullable |
| `DATE` | `date` | Long | Milliseconds since epoch |
| `TYPE` | `type` | Int | SmsType enum index |

## Lifecycle Management

### Engine Lifecycle

```
onAttachedToEngine(binding)
    │
    ├─► Create MethodChannel("flutter_smsussd")
    └─► Set MethodCallHandler (this)

onDetachedFromEngine(binding)
    │
    └─► Set MethodCallHandler (null)
```

### Activity Lifecycle

```
onAttachedToActivity(binding)
    │
    └─► activity = binding.activity

onDetachedFromActivity()
    │
    └─► activity = null

onReattachedToActivityForConfigChanges(binding)
    │
    └─► activity = binding.activity

onDetachedFromActivityForConfigChanges()
    │
    └─► activity = null
```

## Implementation Details

### File Structure

```
android/src/main/kotlin/net/nativemind/libs/flutter/smsussd/flutter_smsussd/
└── FlutterSmsussdPlugin.kt
```

### Imports

```kotlin
import android.Manifest
import android.app.Activity
import android.content.ContentResolver
import android.content.Context
import android.content.pm.PackageManager
import android.database.Cursor
import android.net.Uri
import android.provider.Telephony
import android.telephony.SmsManager
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import io.flutter.embedding.engine.plugins.FlutterPlugin
import io.flutter.embedding.engine.plugins.activity.ActivityAware
import io.flutter.embedding.engine.plugins.activity.ActivityPluginBinding
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import io.flutter.plugin.common.MethodChannel.MethodCallHandler
import io.flutter.plugin.common.MethodChannel.Result
import java.util.*
```

### Companion Object

```kotlin
companion object {
  private const val SMS_PERMISSION_REQUEST_CODE = 123
  private val REQUIRED_PERMISSIONS = arrayOf(
    Manifest.permission.SEND_SMS,
    Manifest.permission.READ_SMS,
    Manifest.permission.RECEIVE_SMS
  )
}
```

## Performance Considerations

- **Cursor Management**: Uses `use {}` block for automatic resource cleanup
- **Query Optimization**: Orders by date DESC for most-recent-first
- **Permission Caching**: Checks permissions before each operation
- **Multipart Detection**: Uses SmsManager.divideMessage() for accurate splitting

## Security Considerations

- **Permission-First**: All operations check permissions before execution
- **Activity Context**: Uses activity context for permission requests
- **No Logging**: Sensitive SMS data not logged
- **Null Safety**: Kotlin null safety prevents NPEs

---

*Generated by /legacy analysis on 2026-03-04*
*Status: DRAFT*
