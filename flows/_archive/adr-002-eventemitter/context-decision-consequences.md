# ADR-002: EventEmitter Pattern for State Management

## Status

DRAFT

## Date

2026-03-04

## Authors

- react-native-sip2 maintainers

## Tags

architecture, eventemitter, state-management, events, react-native

## Context

The SIP protocol is inherently event-driven:
- Registration status changes
- Incoming calls
- Call state transitions
- Message arrivals
- Network connectivity changes

We need a pattern to handle these asynchronous state changes and notify the application layer.

### Requirements

- Real-time state updates
- Multiple subscribers per event type
- Decoupled architecture (native → JS → app)
- React Native compatibility
- Simple API for application developers

### Options Considered

1. **EventEmitter (Chosen)**
   - Node.js EventEmitter pattern
   - Built-in to React Native (`events` package)
   - Publish-subscribe model

2. **Callbacks**
   - Pass callback functions to each method
   - Direct invocation on events
   - No subscription management

3. **Promises/Futures**
   - One-time resolution
   - Chainable operations
   - Not suitable for continuous events

4. **Observables (RxJS)**
   - Reactive programming
   - Powerful operators
   - Additional dependency

5. **Redux/Flux**
   - Centralized state store
   - Predictable state transitions
   - More boilerplate

## Decision

**Chosen: EventEmitter Pattern**

The `Endpoint` class extends Node.js `EventEmitter` and uses it for all state change notifications.

### Implementation

```javascript
import {EventEmitter} from 'events';
import {DeviceEventEmitter} from 'react-native';

export default class Endpoint extends EventEmitter {
  constructor() {
    super();
    
    // Subscribe to native events
    DeviceEventEmitter.addListener('pjSipRegistrationChanged', 
      this._onRegistrationChanged.bind(this));
    DeviceEventEmitter.addListener('pjSipCallReceived', 
      this._onCallReceived.bind(this));
    // ... more subscriptions
  }
  
  // Native event handlers - redistribute to application
  _onRegistrationChanged(data) {
    this.emit("registration_changed", new Account(data));
  }
  
  _onCallReceived(data) {
    this.emit("call_received", new Call(data));
  }
  
  // ... more handlers
}
```

### Application Usage

```javascript
const endpoint = new Endpoint();
await endpoint.start();

// Subscribe to events
endpoint.on("registration_changed", (account) => {
  console.log("Registration:", account.getRegistration().isActive());
});

endpoint.on("call_received", (call) => {
  console.log("Incoming call from:", call.getRemoteNumber());
  // Show incoming call UI
});

endpoint.on("call_changed", (call) => {
  // Update call UI with new state
  updateCallScreen(call);
});
```

## Rationale

### Why EventEmitter

1. **React Native Native**: Uses built-in `events` package, no additional dependencies
2. **Familiar API**: Node.js developers already know EventEmitter
3. **Multiple Listeners**: Support multiple subscribers per event type
4. **Decoupling**: Separates event production from consumption
5. **Simplicity**: Minimal boilerplate, easy to understand
6. **Event Transformation**: Can wrap native data in model classes before emitting

### Why Not Alternatives

**Callbacks:**
- ❌ Callback hell with multiple event types
- ❌ No support for multiple listeners
- ❌ Hard to manage lifecycle
- ❌ Memory leak risks

**Promises:**
- ❌ One-time resolution only
- ❌ Cannot represent continuous event streams
- ❌ Not suitable for state changes

**Observables (RxJS):**
- ✅ Powerful, but overkill for this use case
- ❌ Additional dependency (~30KB minified)
- ❌ Steeper learning curve
- ❌ More complex debugging

**Redux/Flux:**
- ❌ Too much boilerplate for library
- ❌ Requires app-level integration
- ❌ Over-engineering for simple event forwarding

## Consequences

### Positive

- ✅ Simple, familiar API
- ✅ Multiple listeners supported
- ✅ No external dependencies
- ✅ Easy to debug (standard EventEmitter)
- ✅ Natural fit for event-driven SIP protocol
- ✅ Works well with React component lifecycle

### Negative

- ⚠️ **No Cleanup Method**: Events subscribed in constructor, never unsubscribed
- ⚠️ **Memory Leak Risk**: If Endpoint is recreated, old listeners remain
- ⚠️ **No Backpressure**: EventEmitter doesn't handle event flooding
- ⚠️ **Error Handling**: Uncaught errors in listeners can break event flow

### Technical Implications

1. **Singleton Pattern Implied**: Endpoint should be created once per app lifetime
2. **Constructor Side Effects**: Event subscription happens automatically
3. **No Destructor**: Missing `destroy()` or `dispose()` method
4. **Event Names**: String-based, no type safety
5. **Listener Order**: Listeners called in registration order (not guaranteed)

## Compliance

### Event Subscription Map

| Native Event | Emitted Event | Payload | Handler |
|--------------|---------------|---------|---------|
| `pjSipRegistrationChanged` | `registration_changed` | Account | `_onRegistrationChanged` |
| `pjSipCallReceived` | `call_received` | Call | `_onCallReceived` |
| `pjSipCallChanged` | `call_changed` | Call | `_onCallChanged` |
| `pjSipCallTerminated` | `call_terminated` | Call | `_onCallTerminated` |
| `pjSipCallScreenLocked` | `call_screen_locked` | boolean | `_onCallScreenLocked` |
| `pjSipMessageReceived` | `message_received` | Message | `_onMessageReceived` |
| `pjSipConnectivityChanged` | `connectivity_changed` | boolean | `_onConnectivityChanged` |

### Pattern Requirements

All event handlers MUST:
1. Receive native data object
2. Wrap in appropriate model class (Account, Call, Message)
3. Emit via `this.emit(event_name, model_instance)`

Example:
```javascript
_onMessageReceived(data) {
  this.emit("message_received", new Message(data));
}
```

## Related Decisions

- ADR-001: PjSIP Native Integration
- ADR-003: Promise Wrapper Around Native Callbacks
- ADR-004: Immutable Data Models

## Migration Path

### If Moving to Observables

```javascript
import { Subject } from 'rxjs';

export default class Endpoint {
  constructor() {
    this.registrationChanged$ = new Subject();
    this.callReceived$ = new Subject();
    // ...
  }
  
  _onRegistrationChanged(data) {
    this.registrationChanged$.next(new Account(data));
  }
}
```

### If Adding Cleanup

```javascript
constructor() {
  super();
  this._listeners = [];
}

addListener(event, listener) {
  const wrapped = listener.bind(this);
  this._listeners.push({ event, wrapped });
  super.addListener(event, wrapped);
}

destroy() {
  this._listeners.forEach(({ event, wrapped }) => {
    this.removeListener(event, wrapped);
  });
  this._listeners = [];
}
```

## References

- [Node.js EventEmitter Documentation](https://nodejs.org/api/events.html)
- [React Native EventEmitter](https://reactnative.dev/docs/eventemitter)
- [Observer Pattern](https://en.wikipedia.org/wiki/Observer_pattern)

## Notes

**Legacy Analysis Discovery** (2026-03-04):

From code analysis of `Endpoint.js`:
- Extends `EventEmitter` from 'events' package
- Subscribes to 7 native events in constructor
- No unsubscribe mechanism found
- All handlers follow pattern: native data → model class → emit
- Potential memory leak if Endpoint is recreated

**Identified Issue**:
```javascript
constructor() {
  super();
  // These listeners are NEVER removed
  DeviceEventEmitter.addListener('pjSipRegistrationChanged', ...);
  DeviceEventEmitter.addListener('pjSipCallReceived', ...);
  // ... no corresponding removeListener calls
}
```

**Recommendation**: Add `destroy()` method or document that Endpoint should be singleton.

---

*This ADR was generated by /legacy analysis of existing codebase*
