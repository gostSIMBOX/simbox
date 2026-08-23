# ADR-003: Promise Wrapper Around Native Callbacks

## Status

DRAFT

## Date

2026-03-04

## Authors

- react-native-sip2 maintainers

## Tags

architecture, promises, async, callbacks, react-native-bridge

## Context

The React Native bridge uses a callback pattern for asynchronous native module communication:

```javascript
NativeModules.PjSipModule.method(args, (successful, data) => {
  // Handle result
});
```

We need a consistent pattern for application code to handle these asynchronous operations.

### Requirements

- Handle asynchronous native module calls
- Error propagation
- Chainable operations
- React Native compatibility
- Simple error handling

### Options Considered

1. **Direct Callbacks**
   - Pass callbacks to each method
   - Native pattern: `(successful, data) => {}`
   
2. **Promise Wrapper (Chosen)**
   - Wrap native callbacks in Promises
   - Standard async/await support
   
3. **Callback + Promise Hybrid**
   - Support both callbacks and Promises
   - Like Node.js many APIs

## Decision

**Chosen: Promise Wrapper Pattern**

All methods that call native modules return Promises:

```javascript
start(configuration) {
  return new Promise((resolve, reject) => {
    NativeModules.PjSipModule.start(configuration, (successful, data) => {
      if (successful) {
        resolve(data);
      } else {
        reject(data);
      }
    });
  });
}
```

### Usage

```javascript
// Promise style
endpoint.start(config)
  .then(state => console.log('Started:', state))
  .catch(error => console.error('Failed:', error));

// Async/await style (preferred)
try {
  const state = await endpoint.start(config);
  console.log('Started:', state);
} catch (error) {
  console.error('Failed:', error);
}
```

## Rationale

### Why Promises

1. **Async/Await Support**: Modern JavaScript syntax, cleaner than callbacks
2. **Error Handling**: Standard try/catch blocks
3. **Chaining**: Can chain operations with `.then()`
4. **Consistency**: All async operations use same pattern
5. **React Native Standard**: Matches React Native async APIs

### Why Not Direct Callbacks

**Direct Callback Pattern:**
```javascript
endpoint.start(config, (successful, data) => {
  if (successful) {
    // Handle success
  } else {
    // Handle error
  }
});
```

**Problems:**
- ❌ Callback hell with sequential operations
- ❌ Non-standard error handling (successful flag)
- ❌ Cannot use async/await
- ❌ Harder to compose operations
- ❌ Inconsistent with modern JavaScript

### Why Not Hybrid

**Hybrid Pattern:**
```javascript
start(config, callback) {
  if (callback) {
    // Use callback
  } else {
    // Return Promise
  }
}
```

**Problems:**
- ❌ More complex implementation
- ❌ Two APIs to document
- ❌ Confusing for users
- ❌ No significant benefit

## Consequences

### Positive

- ✅ Clean async/await syntax
- ✅ Standard error handling (try/catch)
- ✅ Composable with Promise utilities
- ✅ Consistent API across all methods
- ✅ Future-proof (async/await is standard)

### Negative

- ⚠️ **Error Data Structure**: Errors are raw native data objects, not Error instances
- ⚠️ **No Stack Trace**: Rejected Promises don't include JavaScript stack trace
- ⚠️ **Successful Flag**: Native `(successful, data)` pattern leaks into Promise logic
- ⚠️ **No Timeout**: Promises can hang indefinitely if native module doesn't callback

### Technical Implications

1. **Error Format**: Errors are native data objects, not `Error` instances
   ```javascript
   try {
     await endpoint.start(config);
   } catch (error) {
     // error is raw native data, not Error object
     console.error(error); // { code: "E_INIT_FAILED", message: "..." }
   }
   ```

2. **No Cancellation**: Promises cannot be cancelled once started
   ```javascript
   const promise = endpoint.makeCall(account, destination);
   // No way to cancel if user changes mind
   ```

3. **All-or-Nothing**: Promise resolves once with all data
   ```javascript
   // Cannot stream partial results
   const accounts = await endpoint.start(config); // All at once
   ```

## Compliance

### Promise Pattern Requirements

All methods calling native modules MUST:

1. Return a Promise
2. Resolve with typed data on success
3. Reject with native error data on failure
4. Never throw synchronously

### Standard Implementation

```javascript
methodName(args) {
  return new Promise((resolve, reject) => {
    NativeModules.PjSipModule.methodName(args, (successful, data) => {
      if (successful) {
        resolve(data);
      } else {
        reject(data);
      }
    });
  });
}
```

### Method Categories

**Methods Returning Promises:**

| Method | Resolves With | Rejects With |
|--------|---------------|--------------|
| `start(config)` | `{accounts, calls, settings}` | Error data |
| `createAccount(config)` | Account instance | Error data |
| `makeCall(account, dest)` | Call instance | Error data |
| `answerCall(call)` | void | Error data |
| `hangupCall(call)` | void | Error data |
| `sendMessage(account, dest, msg)` | void | Error data |
| `holdCall(call)` | void | Error data |
| `dtmfCall(call, digits)` | void | Error data |
| ... | ... | ... |

**Methods NOT Returning Promises:**

| Method | Return Type | Reason |
|--------|-------------|--------|
| `constructor()` | Endpoint | Synchronous initialization |
| `on(event, listener)` | Endpoint | EventEmitter method |
| `changeOrientation(orientation)` | void | Validates synchronously |
| `_normalize(account, dest)` | string | Private helper |

## Related Decisions

- ADR-001: PjSIP Native Integration
- ADR-002: EventEmitter Pattern for State Management
- ADR-004: Immutable Data Models

## Migration Path

### If Moving to Error Objects

```javascript
methodName(args) {
  return new Promise((resolve, reject) => {
    NativeModules.PjSipModule.methodName(args, (successful, data) => {
      if (successful) {
        resolve(data);
      } else {
        // Wrap in Error object
        reject(new Error(data.message || 'Unknown error'));
      }
    });
  });
}
```

### If Adding Timeout

```javascript
methodName(args, timeout = 30000) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error('Timeout'));
    }, timeout);
    
    NativeModules.PjSipModule.methodName(args, (successful, data) => {
      clearTimeout(timer);
      if (successful) {
        resolve(data);
      } else {
        reject(data);
      }
    });
  });
}
```

## References

- [JavaScript Promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)
- [Async/Await](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous/Async_await)
- [React Native Bridge](https://reactnative.dev/docs/native-modules-intro)

## Notes

**Legacy Analysis Discovery** (2026-03-04):

From code analysis of `Endpoint.js`:
- All 40+ native module calls wrapped in Promises
- Consistent pattern across all methods
- Error data is raw native object, not Error instance
- No timeout handling
- No cancellation support

**Example from Endpoint.js**:
```javascript
makeCall(account, destination, callSettings, msgData) {
  destination = this._normalize(account, destination);
  
  return new Promise((resolve, reject) => {
    NativeModules.PjSipModule.makeCall(
      account.getId(), 
      destination, 
      callSettings, 
      msgData, 
      (successful, data) => {
        if (successful) {
          resolve(new Call(data));
        } else {
          reject(data); // Raw native data, not Error object
        }
      }
    );
  });
}
```

**Identified Issues**:
1. No error wrapping - native error format exposed to application
2. No timeout - calls can hang indefinitely
3. No cancellation - cannot abort pending operations
4. Inconsistent error structure - depends on native implementation

**Recommendation**: Wrap errors in standard Error objects with consistent structure.

---

*This ADR was generated by /legacy analysis of existing codebase*
