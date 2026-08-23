# ADR-004: Immutable Data Models

## Status

DRAFT

## Date

2026-03-04

## Authors

- react-native-sip2 maintainers

## Tags

architecture, data-models, immutability, encapsulation

## Context

The library needs to represent SIP entities (accounts, calls, messages) in JavaScript. These entities have complex state that changes over time.

### Requirements

- Represent SIP accounts, calls, and messages
- Expose properties to application code
- Prevent accidental mutation
- Type safety (via JSDoc)
- Easy serialization for debugging

### Options Considered

1. **Plain Objects**
   - Return raw objects from native
   - Direct property access
   - Mutable

2. **Classes with Getters (Chosen)**
   - Private properties with getter methods
   - No setters
   - Immutable after construction

3. **Object.freeze()**
   - Freeze objects after creation
   - Prevents mutation
   - Less control over access

4. **Immutable.js**
   - Full immutable data structures
   - Persistent data structures
   - Additional dependency

## Decision

**Chosen: Classes with Getters (Immutable Pattern)**

All data models use private properties with public getter methods:

```javascript
export default class Account {
  constructor(data) {
    this._data = data;
    this._registration = new AccountRegistration(data['registration']);
  }

  getId() {
    return this._data.id;
  }

  getURI() {
    return this._data.uri;
  }

  // No setters - immutable after construction
}
```

### Models

| Model | Properties | Getters | Purpose |
|-------|------------|---------|---------|
| Account | 2 private | 15 getters | SIP account configuration |
| AccountRegistration | 4 private | 5 methods | Registration status |
| Call | 20+ private | 30+ getters | Call state and metadata |
| Message | 8 private | 8 getters | SIP message data |

## Rationale

### Why Getters

1. **Encapsulation**: Hide internal data structure
2. **Immutability**: No setters prevents accidental mutation
3. **Type Hints**: JSDoc `@returns` annotations for IDE support
4. **Computed Properties**: Can calculate values on-the-fly
5. **Stability**: Internal structure can change without breaking API

### Why Not Alternatives

**Plain Objects:**
```javascript
// ❌ Mutable, no encapsulation
const account = { id: 1, username: "john" };
account.id = 999; // Oops!
```

**Problems:**
- ❌ Can be mutated accidentally
- ❌ No type hints
- ❌ No validation
- ❌ Breaking changes if structure changes

**Object.freeze():**
```javascript
// ❌ Shallow freeze only
const account = Object.freeze({ id: 1, settings: { theme: 'dark' } });
account.settings.theme = 'light'; // Still mutable!
```

**Problems:**
- ❌ Shallow freeze (nested objects still mutable)
- ❌ No encapsulation
- ❌ Cannot add computed properties

**Immutable.js:**
- ✅ Deep immutability
- ❌ Additional dependency (~30KB)
- ❌ Learning curve for users
- ❌ Overkill for simple data wrappers

## Consequences

### Positive

- ✅ True encapsulation (private properties)
- ✅ Immutable by design (no setters)
- ✅ Type hints via JSDoc
- ✅ Computed properties possible (e.g., duration calculation)
- ✅ Clear API surface (getters only)
- ✅ No external dependencies

### Negative

- ⚠️ **Verbosity**: 30+ getter methods in Call class
- ⚠️ **Boilerplate**: Each property needs getter method
- ⚠️ **No Direct Serialization**: Cannot JSON.stringify directly
- ⚠️ **Property Access**: Must use methods, not dot notation

### Technical Implications

1. **Construction Pattern**: All models receive raw data object
   ```javascript
   constructor({ id, callId, accountId, ...rest }) {
     this._id = id;
     this._callId = callId;
     // ...
   }
   ```

2. **No Setters**: Properties cannot change after creation
   ```javascript
   const call = new Call(data);
   call.getId(); // ✓
   call._id = 999; // ✗ (private by convention)
   ```

3. **Computed Properties**: Some getters calculate values
   ```javascript
   getConnectDuration() {
     const time = Math.round(new Date().getTime() / 1000);
     const offset = time - this._constructionTime;
     return this._connectDuration + offset; // Live calculation
   }
   ```

4. **Serialization**: Only AccountRegistration has `toJson()`
   ```javascript
   registration.toJson(); // { status, statusText, active, reason }
   ```

## Compliance

### Model Structure Requirements

All data models MUST:

1. Use private properties (underscore prefix: `_property`)
2. Provide public getter methods (no setters)
3. Include JSDoc `@returns` annotations
4. Accept data object in constructor
5. Not mutate data after construction

### Getter Naming

Getters SHOULD follow these patterns:

| Pattern | Example | Returns |
|---------|---------|---------|
| `get[Property]()` | `getId()` | Direct property value |
| `is[State]()` | `isHeld()`, `isMuted()` | Boolean state |
| `getFormatted[Property]()` | `getFormattedTotalDuration()` | Formatted string |
| `get[Entity]()` | `getRegistration()` | Related model instance |

### JSDoc Requirements

All getters MUST have `@returns` annotation:

```javascript
/**
 * The account ID.
 * @returns {int}
 */
getId() {
  return this._data.id;
}

/**
 * Last registration status code.
 * @returns {string|null}
 */
getStatus() {
  return this._status;
}
```

## Related Decisions

- ADR-001: PjSIP Native Integration
- ADR-002: EventEmitter Pattern for State Management
- ADR-003: Promise Wrapper Around Native Callbacks

## Migration Path

### If Moving to Class Fields (Modern JS)

```javascript
export default class Account {
  #data; // Private field (ES2022)
  #registration;
  
  constructor(data) {
    this.#data = data;
    this.#registration = new AccountRegistration(data['registration']);
  }
  
  getId() {
    return this.#data.id;
  }
}
```

### If Adding Serialization

```javascript
// Add toJson() to all models
toJson() {
  return {
    id: this._id,
    uri: this._uri,
    name: this._name,
    registration: this._registration.toJson()
  };
}
```

## References

- [JavaScript Getters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/get)
- [Encapsulation in JavaScript](https://developer.mozilla.org/en-US/docs/Glossary/Encapsulation)
- [Immutable Data Structures](https://en.wikipedia.org/wiki/Persistent_data_structure)

## Notes

**Legacy Analysis Discovery** (2026-03-04):

From code analysis:

**Account.js** (15 getters):
```javascript
getId(), getURI(), getName(), getUsername(), getDomain(),
getPassword(), getProxy(), getTransport(), getContactParams(),
getContactUriParams(), getRegServer(), getRegTimeout(),
getRegContactParams(), getRegHeaders(), getRegistration()
```

**Call.js** (30+ getters):
```javascript
getId(), getAccountId(), getCallId(),
getTotalDuration(), getConnectDuration(), // Computed!
getFormattedTotalDuration(), getFormattedConnectDuration(),
getState(), getStateText(), isHeld(), isMuted(), isSpeaker(),
getRemoteName(), getRemoteNumber(), getRemoteFormattedNumber(),
// ... and 15 more
```

**AccountRegistration.js** (has toJson):
```javascript
getStatus(), getStatusText(), isActive(), getReason(), toJson()
```

**Message.js** (8 getters):
```javascript
getAccountId(), getContactUri(), getFromUri(), getFromName(),
getFromNumber(), getToUri(), getBody(), getContentType()
```

**Special Case - Call Duration Calculation**:
```javascript
// Clever optimization - avoids native calls for live duration
constructor(...) {
  this._constructionTime = Math.round(new Date().getTime() / 1000);
}

getTotalDuration() {
  let time = Math.round(new Date().getTime() / 1000);
  let offset = time - this._constructionTime;
  return this._totalDuration + offset; // Live value!
}
```

**Identified Issues**:
1. No `toJson()` on Account and Call (only AccountRegistration has it)
2. Cannot directly JSON.stringify for logging
3. Verbose - 30+ getters in Call class
4. Private properties by convention only (no true privacy)

**Recommendation**: Add `toJson()` methods to all models for easier debugging.

---

*This ADR was generated by /legacy analysis of existing codebase*
