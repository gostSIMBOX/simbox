# ADR-003: JSON Serialization for Android Intent Extras

> Enabling architectural decision: Type-safe data transfer across process boundaries

## Status

DRAFT

## Type

Enabling - This decision enables reliable data transfer between Flutter and native service.

## Context

The service-based architecture (ADR-001) requires passing complex data structures between components:

- Account configuration (credentials, settings, headers)
- Call settings (audio/video stream counts, flags)
- SIP message data (headers, body)
- Event data (call state, registration status)

**Requirements:**
1. Data must survive Android Intent serialization
2. Complex nested structures must be preserved
3. Type information must be maintained
4. Cross-process communication (Flutter → Plugin → Service)
5. Minimal performance overhead

**Constraints:**
- Android Intent extras have limited type support
- Maps/Lists must contain only Parcelable types
- Nested objects require special handling
- Service may run in different process

## Decision

We will use **JSON serialization** for complex data in Intent extras:

### Architecture Pattern

```
┌─────────────────┐
│   Flutter App   │
│  Map<String,    │
│   dynamic>      │
└────────┬────────┘
         │ Platform Message
         ▼
┌─────────────────┐
│FlutterSip2Plugin│  ← Kotlin receives Map
└────────┬────────┘
         │ Convert to DTO
         ▼
┌─────────────────┐
│  DTO Classes    │  ← AccountConfigurationDTO
│  (Kotlin)       │  ← CallSettingsDTO
└────────┬────────┘
         │ toJson()
         ▼
┌─────────────────┐
│  JSON String    │  ← Put in Intent
│  in Intent      │
└────────┬────────┘
         ▼
┌─────────────────┐
│  PjSipService   │  ← fromJson()
└─────────────────┘
```

### Implementation Details

1. **DTO classes for each data structure** (AccountConfigurationDTO, CallSettingsDTO, SipMessageDTO)
2. **toJson() method** converts DTO to JSONObject
3. **fromJson() companion method** reconstructs DTO from JSON
4. **JSON string stored in Intent extra** via putExtra()
5. **ArgumentUtils.fromJson()** parses JSON on service side

### Code Pattern

```kotlin
// AccountConfigurationDTO.kt
data class AccountConfigurationDTO(
    var name: String = "",
    var username: String = "",
    var domain: String = "",
    var password: String = "",
    var proxy: String? = null,
    var transport: String? = null,
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
        json.put("regTimeout", regTimeout)
        json.put("regContactParams", regContactParams)

        // Nested map handling
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
                regTimeout = json.optInt("regTimeout", 3600),
                regContactParams = json.optString("regContactParams"),
                regHeaders = headers
            )
        }
    }
}
```

```java
// PjActions.java - Format Intent with JSON
public static Intent createAccountCreateIntent(int callbackId, Map<String, Object> configuration, Context context) {
    Intent intent = new Intent(context, org.telon.sip2.PjSipService.class);
    intent.setAction(PjActions.ACTION_CREATE_ACCOUNT);
    intent.putExtra("callback_id", callbackId);
    
    // Convert Map to DTO, then to JSON
    AccountConfigurationDTO dto = AccountConfigurationDTO.fromMap(configuration);
    intent.putExtra("configuration", dto.toJson().toString());
    
    return intent;
}
```

```java
// ArgumentUtils.java - Parse JSON in Service
public static Object fromJson(String json) {
    try {
        JSONObject jsonObject = new JSONObject(json);
        // Parse to appropriate type
        return AccountConfigurationDTO.fromJson(jsonObject);
    } catch (JSONException e) {
        Log.e(TAG, "Failed to parse JSON", e);
        return null;
    }
}
```

## Consequences

### Positive

1. **Type Safety**: DTO classes provide compile-time type checking:
   - Required fields enforced by data class
   - Default values for optional fields
   - Type conversions handled explicitly

2. **Complex Structure Support**: JSON handles nested structures:
   - Maps within maps (regHeaders)
   - Lists of complex objects
   - Optional fields (null handling)

3. **Process Boundary Safe**: JSON string survives process death:
   - Parcelable limitations avoided
   - Works across process boundaries
   - Survives Android's process reaping

4. **Debugging Friendly**: JSON is human-readable:
   - Log JSON for debugging
   - Easy to inspect in debugger
   - Can be validated with tools

5. **Version Tolerance**: JSON allows forward/backward compatibility:
   - New fields ignored by old code
   - Missing fields use defaults
   - Easier API evolution

### Negative

1. **Performance Overhead**: JSON serialization/deserialization costs:
   - ~1-5ms per object (depending on size)
   - Memory allocation for JSON strings
   - CPU usage for parsing

2. **Boilerplate Code**: DTO classes require maintenance:
   - toJson()/fromJson() for each class
   - Field duplication (Dart → Kotlin → JSON)
   - Easy to forget new fields

3. **Error Prone**: JSON parsing can fail silently:
   - optString() returns empty string on error
   - Type mismatches may not throw
   - Runtime errors vs compile-time

4. **No Schema Validation**: JSON doesn't enforce structure:
   - Typos in field names not caught
   - Type mismatches at runtime
   - No automatic validation

### Trade-offs

**Rejected Alternative: Parcelable**

We considered Android Parcelable for data transfer:

```kotlin
// Rejected: Parcelable
@Parcelize
data class AccountConfigurationDTO(
    val name: String,
    val username: String,
    // ...
) : Parcelable
```

**Why Rejected:**
- More boilerplate than JSON
- Less debuggable (binary format)
- Tied to Android platform
- Harder to handle nested maps

**Rejected Alternative: Bundle with Primitives**

We considered flattening data into Bundle:

```kotlin
// Rejected: Flat Bundle
val bundle = Bundle()
bundle.putString("name", name)
bundle.putString("username", username)
bundle.putInt("regTimeout", timeout)
// ... for each field
```

**Why Rejected:**
- Verbose for complex structures
- No nested structure support
- Type casting required everywhere
- Easy to make mistakes

**Accepted Trade-off:** Performance for flexibility - JSON overhead accepted for type safety and complex structure support.

## Related Decisions

- **ADR-001**: Service-based architecture (requires data transfer)
- **ADR-004**: Callback ID pattern (callback_id passed separately from JSON data)

## References

- [Android Intent Extras](https://developer.android.com/reference/android/content/Intent#extras)
- [JSONObject Documentation](https://developer.android.com/reference/org/json/JSONObject)
- [AccountConfigurationDTO.kt](../android/src/main/kotlin/org/tele/flutter_sip2/dto/AccountConfigurationDTO.kt)
- [CallSettingsDTO.kt](../android/src/main/kotlin/org/tele/flutter_sip2/dto/CallSettingsDTO.kt)
- [ArgumentUtils.java](../android/src/main/java/org/telon/sip2/utils/ArgumentUtils.java)

---

*Generated by /legacy analysis | 2026-03-04*
