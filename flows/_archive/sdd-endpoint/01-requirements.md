# 01-Requirements: Endpoint API

## Overview

The Endpoint module serves as the primary interface for interacting with the PjSIP (SIP/VoIP) library in React Native applications. It provides a unified API for account management, call control, messaging, and configuration.

## Functional Requirements

### FR-1: Library Initialization

**Description**: Application must initialize the PjSIP library before any operations.

**Requirements**:
- FR-1.1: Provide `start(configuration)` method that returns a Promise
- FR-1.2: Resolve Promise with initial state (accounts, calls, extra data)
- FR-1.3: Reject Promise with error data if initialization fails
- FR-1.4: Transform raw native data into typed Account and Call objects

**Acceptance Criteria**:
```javascript
const endpoint = new Endpoint();
const state = await endpoint.start(configuration);
// state.accounts: Account[]
// state.calls: Call[]
```

### FR-2: Event Subscription

**Description**: Application must receive real-time updates for SIP state changes.

**Requirements**:
- FR-2.1: Extend EventEmitter to enable event subscription
- FR-2.2: Subscribe to native events automatically in constructor
- FR-2.3: Emit typed events with model objects as payloads
- FR-2.4: Support standard EventEmitter methods (on, off, emit)

**Events**:
- `registration_changed` - Account registration status changed
- `call_received` - Incoming call received
- `call_changed` - Call state updated
- `call_terminated` - Call ended
- `call_screen_locked` - Screen lock state changed
- `message_received` - SIP MESSAGE received
- `connectivity_changed` - Network connectivity changed

**Acceptance Criteria**:
```javascript
endpoint.on('registration_changed', (account) => {
  console.log('Registration:', account.getRegistration());
});
```

### FR-3: Account Management

**Description**: Application must be able to create, manage, and delete SIP accounts.

**Requirements**:
- FR-3.1: `createAccount(configuration)` - Create new SIP account
- FR-3.2: `registerAccount(account, renew)` - Update registration manually
- FR-3.3: `deleteAccount(account)` - Remove account and unregister
- FR-3.4: Return Account objects with registration status

**Acceptance Criteria**:
```javascript
const account = await endpoint.createAccount({
  name: "John Doe",
  username: "100",
  domain: "pbx.com",
  password: "secret"
});
```

### FR-4: Call Control

**Description**: Application must support full call lifecycle management.

**Requirements**:
- FR-4.1: **Basic Operations**:
  - `makeCall(account, destination, callSettings, msgData)` - Outgoing call
  - `answerCall(call)` - Answer incoming call
  - `hangupCall(call)` - End call
  - `declineCall(call)` - Reject with 603 status

- FR-4.2: **State Control**:
  - `holdCall(call)` - Put call on hold
  - `unholdCall(call)` - Resume from hold
  - `muteCall(call)` - Mute microphone
  - `unMuteCall(call)` - Unmute microphone

- FR-4.3: **Audio Routing**:
  - `useSpeaker(call)` - Route audio to speaker
  - `useEarpiece(call)` - Route audio to earpiece

- FR-4.4: **Call Transfer**:
  - `xferCall(account, call, destination)` - Blind transfer
  - `xferReplacesCall(call, destCall)` - Attended transfer

- FR-4.5: **Call Redirect**:
  - `redirectCall(account, call, destination)` - Forward call

- FR-4.6: **DTMF**:
  - `dtmfCall(call, digits)` - Send DTMF tones

- FR-4.7: **Signaling**:
  - `ringingCall(call)` - Send 180 Ringing
  - `progressCall(call)` - Send 183 Progress

**Acceptance Criteria**:
```javascript
// Make a call
const call = await endpoint.makeCall(account, "sip:200@pbx.com");

// Put on hold
await endpoint.holdCall(call);

// Resume
await endpoint.unholdCall(call);

// Transfer
await endpoint.xferCall(account, call, "sip:300@pbx.com");
```

### FR-5: Messaging

**Description**: Application must support SIP instant messaging.

**Requirements**:
- FR-5.1: `sendMessage(account, destination, msg)` - Send MESSAGE
- FR-5.2: `imTyping(account, destination, isTyping)` - Send typing indicator
- FR-5.3: Emit `message_received` event for incoming messages

**Acceptance Criteria**:
```javascript
await endpoint.sendMessage(account, "sip:200@pbx.com", "Hello!");
await endpoint.imTyping(account, "sip:200@pbx.com", true);
```

### FR-6: Configuration

**Description**: Application must be able to configure library behavior.

**Requirements**:
- FR-6.1: `changeNetworkConfiguration(configuration)` - Network settings
- FR-6.2: `changeServiceConfiguration(configuration)` - Service settings
- FR-6.3: `changeCodecSettings(codecSettings)` - Codec configuration
- FR-6.4: `changeOrientation(orientation)` - Video orientation
- FR-6.5: `updateStunServers(accountId, stunServerList)` - STUN servers
- FR-6.6: `activateAudioSession()` / `deactivateAudioSession()` - iOS audio

**Acceptance Criteria**:
```javascript
await endpoint.changeOrientation('PJMEDIA_ORIENT_NATURAL');
await endpoint.updateStunServers(accountId, ['stun:stun.l.google.com:19302']);
```

## Non-Functional Requirements

### NFR-1: API Consistency

- All asynchronous operations return Promises
- Error handling uses consistent `(successful, data)` callback pattern
- SIP URI normalization is automatic and transparent

### NFR-2: Type Safety

- All data models provide getter methods for properties
- Input validation for orientation constants
- Consistent object structure across all operations

### NFR-3: Performance

- Duration calculations use local time offset to avoid native calls
- Event emission is synchronous and non-blocking
- No blocking operations in event handlers

## Constraints

### C-1: Native Dependency

- All operations delegate to NativeModules.PjSipModule
- JavaScript layer is pure orchestration (no business logic)
- Native module must be initialized before any operations

### C-2: Event Subscription Lifecycle

- Events are subscribed automatically in constructor
- No cleanup/destructor method provided
- Potential memory leak if Endpoint is recreated

### C-3: Incomplete Features

- `replaceAccount()` is not implemented (throws Error)

## Dependencies

| Dependency | Purpose |
|------------|---------|
| react-native (NativeModules) | Native module bridge |
| react-native (DeviceEventEmitter) | Native event subscription |
| events.EventEmitter | Event emission to application |
| Account, Call, Message | Data models |

---

*Status: DRAFT | Type: SDD | Generated by /legacy*
