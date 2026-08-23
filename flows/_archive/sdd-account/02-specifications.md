# Specifications: SIP Account Management

> Technical specification for account creation, registration, and lifecycle.

## Architecture Overview

```
┌─────────────────┐
│   Flutter App   │
└────────┬────────┘
         │ createAccount(config)
         │ registerAccount(account)
         │ deleteAccount(account)
         ▼
┌─────────────────┐
│  FlutterSip2    │  ← MethodChannel calls
│   (Facade)      │
└────────┬────────┘
         │ Platform Messages
         ▼
┌─────────────────┐
│FlutterSip2Plugin│  ← Kotlin handler
│   (Android)     │
└────────┬────────┘
         │ Intents + callback_id
         ▼
┌─────────────────┐
│  PjSipService   │  ← Account operations
│   (Native)      │  ← PJSIP account API
└────────┬────────┘
         │ Broadcast Intents
         ▼
┌─────────────────┐
│PjSipBroadcast   │  ← registration_changed
│   Receiver      │  ← EVENT_ACCOUNT_CREATED
└─────────────────┘
```

## Component Specifications

### 1. Account Creation (Dart)

**File**: `lib/flutter_nmsip.dart`

```dart
static Future<Account> createAccount(Map<String, dynamic> configuration) async {
  try {
    final result = await _channel.invokeMethod('createAccount', configuration);
    return Account.fromMap(result);
  } on PlatformException catch (e) {
    throw FlutterSip2Exception(e.code, e.message);
  }
}
```

**Configuration Map**:
```dart
{
  'name': 'John Doe',              // Required
  'username': '100',                // Required
  'domain': 'pbx.example.com',      // Required
  'password': 'secret',             // Required
  'proxy': '192.168.1.100:5060',   // Optional
  'transport': 'TCP',               // Optional, default TCP
  'regServer': 'pbx.example.com',   // Optional
  'regTimeout': 3600,               // Optional, default 3600
  'regHeaders': {                   // Optional
    'X-Custom-Header': 'Value'
  },
  'regContactParams': ';device-token=XXX'  // Optional
}
```

### 2. Account Registration (Dart)

```dart
static Future<void> registerAccount(Account account, {bool renew = true}) async {
  try {
    await _channel.invokeMethod('registerAccount', {
      'accountId': account.id,
      'renew': renew,
    });
  } on PlatformException catch (e) {
    throw FlutterSip2Exception(e.code, e.message);
  }
}
```

**Parameters**:
- `accountId`: Account ID from created account
- `renew`: true = register/renew, false = unregister

### 3. Account Deletion (Dart)

```dart
static Future<void> deleteAccount(Account account) async {
  try {
    await _channel.invokeMethod('deleteAccount', account.id);
  } on PlatformException catch (e) {
    throw FlutterSip2Exception(e.code, e.message);
  }
}
```

### 4. Account Model (Dart)

**File**: `lib/src/account.dart`

```dart
class Account {
  final int id;
  final String uri;
  final String name;
  final String username;
  final String domain;
  final String password;
  final String? proxy;
  final String? transport;
  final String? contactParams;
  final String? contactUriParams;
  final String? regServer;
  final int? regTimeout;
  final String? regContactParams;
  final Map<String, dynamic>? regHeaders;
  final AccountRegistration registration;

  // Factory constructor for deserialization
  factory Account.fromMap(Map<String, dynamic> map) {
    return Account(
      id: map['id'] as int,
      uri: map['uri'] as String,
      name: map['name'] as String,
      username: map['username'] as String,
      domain: map['domain'] as String,
      password: map['password'] as String,
      proxy: map['proxy'] as String?,
      transport: map['transport'] as String?,
      contactParams: map['contactParams'] as String?,
      contactUriParams: map['contactUriParams'] as String?,
      regServer: map['regServer'] as String?,
      regTimeout: map['regTimeout'] as int?,
      regContactParams: map['regContactParams'] as String?,
      regHeaders: map['regHeaders'] as Map<String, dynamic>?,
      registration: AccountRegistration.fromMap(map['registration'] as Map<String, dynamic>),
    );
  }

  // Serialization
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'uri': uri,
      'name': name,
      'username': username,
      'domain': domain,
      'password': password,
      'proxy': proxy,
      'transport': transport,
      'contactParams': contactParams,
      'contactUriParams': contactUriParams,
      'regServer': regServer,
      'regTimeout': regTimeout,
      'regContactParams': regContactParams,
      'regHeaders': regHeaders,
      'registration': registration.toMap(),
    };
  }

  // Equality by ID only
  @override
  bool operator ==(Object other) => other is Account && other.id == id;
  
  @override
  int get hashCode => id.hashCode;
}
```

### 5. AccountRegistration Model (Dart)

**File**: `lib/src/account_registration.dart`

```dart
class AccountRegistration {
  final bool status;
  final int? code;
  final String? reason;
  final int? expiration;
  final int? retryAfter;

  AccountRegistration({
    required this.status,
    this.code,
    this.reason,
    this.expiration,
    this.retryAfter,
  });

  factory AccountRegistration.fromMap(Map<String, dynamic> map) {
    return AccountRegistration(
      status: map['status'] as bool? ?? false,
      code: map['code'] as int?,
      reason: map['reason'] as String?,
      expiration: map['expiration'] as int?,
      retryAfter: map['retryAfter'] as int?,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'status': status,
      'code': code,
      'reason': reason,
      'expiration': expiration,
      'retryAfter': retryAfter,
    };
  }
}
```

### 6. AccountConfigurationDTO (Kotlin)

**File**: `android/src/main/kotlin/org/tele/flutter_sip2/dto/AccountConfigurationDTO.kt`

```kotlin
data class AccountConfigurationDTO(
    var name: String = "",
    var username: String = "",
    var domain: String = "",
    var password: String = "",
    var proxy: String? = null,
    var transport: String? = null,
    var regServer: String? = null,
    var regTimeout: Int = 3600,
    var regHeaders: Map<String, String> = emptyMap(),
    var regContactParams: String? = null
) {
    fun toJson(): JSONObject {
        val json = JSONObject()
        json.put("name", name)
        json.put("username", username)
        json.put("domain", domain)
        json.put("password", password)
        json.put("proxy", proxy)
        json.put("transport", transport)
        json.put("regServer", regServer)
        json.put("regTimeout", regTimeout)
        json.put("regContactParams", regContactParams)

        val headersJson = JSONObject()
        regHeaders.forEach { (key, value) ->
            headersJson.put(key, value)
        }
        json.put("regHeaders", headersJson)

        return json
    }

    companion object {
        fun fromJson(json: JSONObject): AccountConfigurationDTO {
            val headers = mutableMapOf<String, String>()
            json.optJSONObject("regHeaders")?.let { headersJson ->
                headersJson.keys().forEach { key ->
                    headers[key] = headersJson.getString(key)
                }
            }

            return AccountConfigurationDTO(
                name = json.optString("name", ""),
                username = json.optString("username", ""),
                domain = json.optString("domain", ""),
                password = json.optString("password", ""),
                proxy = json.optString("proxy"),
                transport = json.optString("transport"),
                regServer = json.optString("regServer"),
                regTimeout = json.optInt("regTimeout", 3600),
                regContactParams = json.optString("regContactParams"),
                regHeaders = headers
            )
        }
    }
}
```

### 7. Kotlin Method Handlers

**File**: `android/src/main/kotlin/org/tele/flutter_sip2/FlutterSip2Plugin.kt`

```kotlin
"createAccount" -> {
    val configuration = call.arguments as? Map<String, Any>
    val callbackId = broadcastReceiver.register(result)
    val intent = PjActions.createAccountCreateIntent(callbackId, configuration, context)
    context.startService(intent)
}
"registerAccount" -> {
    val args = call.arguments as? Map<String, Any>
    val accountId = args?.get("accountId") as? Int ?: 0
    val renew = args?.get("renew") as? Boolean ?: true
    val callbackId = broadcastReceiver.register(result)
    val intent = PjActions.createAccountRegisterIntent(callbackId, accountId, renew, context)
    context.startService(intent)
}
"deleteAccount" -> {
    val accountId = call.arguments as? Int ?: 0
    val callbackId = broadcastReceiver.register(result)
    val intent = PjActions.createAccountDeleteIntent(callbackId, accountId, context)
    context.startService(intent)
}
```

### 8. PjActions Intent Factory

**File**: `android/src/main/java/org/tele/flutter_sip2/PjActions.java`

```java
public static Intent createAccountCreateIntent(int callbackId, Map<String, Object> configuration, Context context) {
    Intent intent = new Intent(context, org.telon.sip2.PjSipService.class);
    intent.setAction(PjActions.ACTION_CREATE_ACCOUNT);
    intent.putExtra("callback_id", callbackId);
    formatIntent(intent, configuration);
    return intent;
}

public static Intent createAccountRegisterIntent(int callbackId, int accountId, boolean renew, Context context) {
    Intent intent = new Intent(context, org.telon.sip2.PjSipService.class);
    intent.setAction(PjActions.ACTION_REGISTER_ACCOUNT);
    intent.putExtra("callback_id", callbackId);
    intent.putExtra("account_id", accountId);
    intent.putExtra("renew", renew);
    return intent;
}

public static Intent createAccountDeleteIntent(int callbackId, int accountId, Context context) {
    Intent intent = new Intent(context, org.telon.sip2.PjSipService.class);
    intent.setAction(PjActions.ACTION_DELETE_ACCOUNT);
    intent.putExtra("callback_id", callbackId);
    intent.putExtra("account_id", accountId);
    return intent;
}
```

## Event Types

| Event | Data Structure | Trigger |
|-------|----------------|---------|
| `pjSipAccountCreated` | `{account: Account}` | Account successfully created |
| `pjSipRegistrationChanged` | `{account_id, status, code, reason, expiration}` | Registration status updated |

## Registration Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK (registered successfully) |
| 401 | Unauthorized (invalid credentials) |
| 403 | Forbidden (account disabled) |
| 404 | Not Found (domain not found) |
| 408 | Request Timeout (server unreachable) |
| 503 | Service Unavailable (server down) |

## Error Handling

### Exception Types

```dart
class FlutterSip2Exception implements Exception {
  final String code;
  final String? message;

  FlutterSip2Exception(this.code, this.message);
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `SIP_ERROR` | Generic account operation failed |
| `ECONNREFUSED` | SIP server unreachable |
| `EAUTHFAILED` | Authentication failed (wrong credentials) |

## Testing Considerations

### Unit Tests (Dart)

- Test Account.fromMap/toMap serialization
- Test AccountRegistration status parsing
- Verify equality by ID only
- Test exception translation

### Integration Tests

- Account creation with mock platform channel
- Registration flow simulation
- Event stream subscription for registration changes

### Manual Testing

- Multi-account scenarios
- Registration timeout handling
- Network change during registration
- Account deletion and recreation

---

*Status: DRAFT | Type: SDD | Generated by /legacy*
