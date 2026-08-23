# 02-Specifications: Endpoint API

## Module Specification

### Class: Endpoint

**Extends**: `EventEmitter` (from 'events')

**Constructor**:
```javascript
constructor()
```
- Initializes EventEmitter
- Subscribes to 6 native events:
  - `pjSipRegistrationChanged`
  - `pjSipCallReceived`
  - `pjSipCallChanged`
  - `pjSipCallTerminated`
  - `pjSipCallScreenLocked`
  - `pjSipMessageReceived`
  - `pjSipConnectivityChanged`

### Method: start(configuration)

**Signature**:
```javascript
start(configuration: Object) => Promise<{
  accounts: Account[],
  calls: Call[],
  ...extra: Object
}>
```

**Implementation**:
```javascript
start(configuration) {
  return new Promise((resolve, reject) => {
    NativeModules.PjSipModule.start(configuration, (successful, data) => {
      if (successful) {
        let accounts = data.accounts?.map(d => new Account(d)) || [];
        let calls = data.calls?.map(d => new Call(d)) || [];
        let extra = Object.fromEntries(
          Object.entries(data).filter(([k]) => k !== 'accounts' && k !== 'calls')
        );
        resolve({ accounts, calls, ...extra });
      } else {
        reject(data);
      }
    });
  });
}
```

### Method: createAccount(configuration)

**Signature**:
```javascript
createAccount(configuration: {
  name: string,
  username: string,
  domain: string,
  password: string,
  proxy?: string,
  transport?: string,
  regServer?: string,
  regTimeout?: number,
  contactParams?: string,
  contactUriParams?: string,
  regContactParams?: string,
  regHeaders: Object
}) => Promise<Account>
```

**Implementation**:
```javascript
createAccount(configuration) {
  return new Promise((resolve, reject) => {
    NativeModules.PjSipModule.createAccount(configuration, (successful, data) => {
      if (successful) {
        resolve(new Account(data));
      } else {
        reject(data);
      }
    });
  });
}
```

### Method: registerAccount(account, renew)

**Signature**:
```javascript
registerAccount(account: Account, renew: boolean = true) => Promise<void>
```

**Implementation**:
```javascript
registerAccount(account, renew = true) {
  return new Promise((resolve, reject) => {
    NativeModules.PjSipModule.registerAccount(account.getId(), renew, (successful, data) => {
      if (successful) {
        resolve(data);
      } else {
        reject(data);
      }
    });
  });
}
```

### Method: deleteAccount(account)

**Signature**:
```javascript
deleteAccount(account: Account) => Promise<void>
```

### Method: makeCall(account, destination, callSettings, msgData)

**Signature**:
```javascript
makeCall(
  account: Account,
  destination: string,
  callSettings?: {
    flag: number,
    req_keyframe_method: number,
    aud_cnt: number,
    vid_cnt: number
  },
  msgData?: {
    target_uri: string,
    hdr_list: Object,
    content_type: string,
    msg_body: string
  }
) => Promise<Call>
```

**Implementation Details**:
- Normalizes destination URI via `_normalize(account, destination)`
- Returns Call instance on success

### Method: answerCall(call)

**Signature**:
```javascript
answerCall(call: Call) => Promise<void>
```

### Method: hangupCall(call)

**Signature**:
```javascript
hangupCall(call: Call) => Promise<void>
```

**Note**: TODO - Add support for custom code and reason parameters

### Method: declineCall(call)

**Signature**:
```javascript
declineCall(call: Call) => Promise<void>
```

**Behavior**: Sends 603 Decline response

### Method: holdCall(call) / unholdCall(call)

**Signature**:
```javascript
holdCall(call: Call) => Promise<void>
unholdCall(call: Call) => Promise<void>
```

**Behavior**: Sends re-INVITE with appropriate SDP

### Method: muteCall(call) / unMuteCall(call)

**Signature**:
```javascript
muteCall(call: Call) => Promise<void>
unMuteCall(call: Call) => Promise<void>
```

### Method: useSpeaker(call) / useEarpiece(call)

**Signature**:
```javascript
useSpeaker(call: Call) => Promise<void>
useEarpiece(call: Call) => Promise<void>
```

### Method: xferCall(account, call, destination)

**Signature**:
```javascript
xferCall(account: Account, call: Call, destination: string) => Promise<void>
```

**Behavior**: Blind transfer - sends REFER to instruct remote to call destination

### Method: xferReplacesCall(call, destCall)

**Signature**:
```javascript
xferReplacesCall(call: Call, destCall: Call) => Promise<void>
```

**Behavior**: Attended transfer - transfers call to replace destCall

### Method: redirectCall(account, call, destination)

**Signature**:
```javascript
redirectCall(account: Account, call: Call, destination: string) => Promise<void>
```

**Behavior**: Forwards incoming call to destination

### Method: dtmfCall(call, digits)

**Signature**:
```javascript
dtmfCall(call: Call, digits: string) => Promise<void>
```

**Specification**: Digits must conform to RFC 2833 section 3.10

### Method: sendMessage(account, destination, msg)

**Signature**:
```javascript
sendMessage(account: Account, destination: string, msg: string) => Promise<void>
```

### Method: imTyping(account, destination, isTyping)

**Signature**:
```javascript
imTyping(account: Account, destination: string, isTyping: boolean) => Promise<void>
```

### Method: changeOrientation(orientation)

**Signature**:
```javascript
changeOrientation(
  orientation: 'PJMEDIA_ORIENT_UNKNOWN' 
             | 'PJMEDIA_ORIENT_ROTATE_90DEG'
             | 'PJMEDIA_ORIENT_ROTATE_270DEG'
             | 'PJMEDIA_ORIENT_ROTATE_180DEG'
             | 'PJMEDIA_ORIENT_NATURAL'
) => void
```

**Validation**: Throws Error if orientation is not in valid set

### Method: changeCodecSettings(codecSettings)

**Signature**:
```javascript
changeCodecSettings(codecSettings: Object) => Promise<void>
```

### Method: updateStunServers(accountId, stunServerList)

**Signature**:
```javascript
updateStunServers(accountId: number, stunServerList: string[]) => Promise<void>
```

### Method: activateAudioSession() / deactivateAudioSession()

**Signature**:
```javascript
activateAudioSession() => Promise<void>
deactivateAudioSession() => Promise<void>
```

**Platform**: iOS only

### Method: changeNetworkConfiguration(configuration)

**Signature**:
```javascript
changeNetworkConfiguration(configuration: Object) => Promise<void>
```

### Method: changeServiceConfiguration(configuration)

**Signature**:
```javascript
changeServiceConfiguration(configuration: Object) => Promise<void>
```

### Method: replaceAccount(account, configuration)

**Status**: NOT IMPLEMENTED

**Behavior**: Throws `Error("Not implemented")`

## Private Methods

### Method: _normalize(account, destination)

**Signature**:
```javascript
_normalize(account: Account, destination: string) => string
```

**Logic**:
```javascript
if (!destination.startsWith("sip:")) {
  let realm = account.getRegServer() || account.getDomain();
  // Extract host:port from domain
  let s = realm.indexOf(":");
  if (s > 0) {
    realm = realm.substr(0, s + 1);
  }
  destination = "sip:" + destination + "@" + realm;
}
return destination;
```

## Event Handlers (Private)

All handlers follow the pattern:
```javascript
_on[EventName](data) {
  this.emit("[event_name]", new [Model](data));
}
```

| Handler | Native Event | Emitted Event | Payload |
|---------|-------------|---------------|---------|
| `_onRegistrationChanged` | `pjSipRegistrationChanged` | `registration_changed` | Account |
| `_onCallReceived` | `pjSipCallReceived` | `call_received` | Call |
| `_onCallChanged` | `pjSipCallChanged` | `call_changed` | Call |
| `_onCallTerminated` | `pjSipCallTerminated` | `call_terminated` | Call |
| `_onCallScreenLocked` | `pjSipCallScreenLocked` | `call_screen_locked` | boolean |
| `_onMessageReceived` | `pjSipMessageReceived` | `message_received` | Message |
| `_onConnectivityChanged` | `pjSipConnectivityChanged` | `connectivity_changed` | boolean |

## Data Models

### Account

Properties (via getters):
- `getId(): number`
- `getURI(): string`
- `getName(): string`
- `getUsername(): string`
- `getDomain(): string|null`
- `getPassword(): string`
- `getProxy(): string`
- `getTransport(): string`
- `getContactParams(): string`
- `getContactUriParams(): string`
- `getRegServer(): string`
- `getRegTimeout(): string`
- `getRegContactParams(): string`
- `getRegHeaders(): Object`
- `getRegistration(): AccountRegistration`

### Call

Properties (via getters):
- `getId(): number`
- `getAccountId(): number`
- `getCallId(): string`
- `getTotalDuration(): number` (calculated)
- `getConnectDuration(): number` (calculated)
- `getFormattedTotalDuration(): string` ("MM:SS")
- `getFormattedConnectDuration(): string` ("MM:SS")
- `getLocalContact(): string`
- `getLocalUri(): string`
- `getRemoteContact(): string`
- `getRemoteUri(): string`
- `getRemoteName(): string|null`
- `getRemoteNumber(): string|null`
- `getRemoteFormattedNumber(): string`
- `getState(): string` (PJSIP_INV_STATE_*)
- `getStateText(): string`
- `isHeld(): boolean`
- `isMuted(): boolean`
- `isSpeaker(): boolean`
- `isTerminated(): boolean`
- `getRemoteOfferer(): boolean`
- `getRemoteAudioCount(): number`
- `getRemoteVideoCount(): number`
- `getAudioCount(): number`
- `getVideoCount(): number`
- `getLastStatusCode(): string` (SIP status codes)
- `getLastReason(): string`
- `getMedia(): Object`
- `getProvisionalMedia(): Object`

### AccountRegistration

Properties:
- `getStatus(): string|null` (SIP status code)
- `getStatusText(): string|null`
- `isActive(): boolean`
- `getReason(): string|null`

### Message

Properties:
- `getAccountId(): number`
- `getContactUri(): string`
- `getFromUri(): string`
- `getFromName(): string|null`
- `getFromNumber(): string|null`
- `getToUri(): string`
- `getBody(): string|null`
- `getContentType(): string|null`

## Error Handling

All native calls use the pattern:
```javascript
NativeModules.PjSipModule.method(args, (successful, data) => {
  if (successful) {
    resolve(data);
  } else {
    reject(data);
  }
});
```

**Note**: Error details are in the `data` parameter, not thrown exceptions.

## Call States

Valid values for `Call.getState()`:

| Constant | Description |
|----------|-------------|
| `PJSIP_INV_STATE_NULL` | Before INVITE sent/received |
| `PJSIP_INV_STATE_CALLING` | After INVITE sent |
| `PJSIP_INV_STATE_INCOMING` | After INVITE received |
| `PJSIP_INV_STATE_EARLY` | After response with To tag |
| `PJSIP_INV_STATE_CONNECTING` | After 2xx sent/received |
| `PJSIP_INV_STATE_CONFIRMED` | After ACK sent/received |
| `PJSIP_INV_STATE_DISCONNECTED` | Session terminated |

## Status Codes

Valid values for `Call.getLastStatusCode()` and `AccountRegistration.getStatus()`:

**Informational (1xx)**: 100, 180, 181, 182, 183

**Success (2xx)**: 200, 202

**Redirection (3xx)**: 300, 301, 302, 305, 380

**Client Error (4xx)**: 400-493 (see RFC 3261)

**Server Error (5xx)**: 500-580

**Global Failure (6xx)**: 600-606

---

## Known Issues and Resolutions

### Issue 1: Missing cleanup/destructor method - RESOLVED (2026-03-04)

**Problem**: Endpoint class has no cleanup/destructor method, causing potential memory leaks.

**Impact**:
- EventChannel subscriptions may persist after Endpoint disposal
- Memory leak if Endpoint not properly cleaned up
- Native module references may hold stale objects

**Resolution**:
Add `dispose()` method to Endpoint class:
```javascript
/**
 * Cleanup method to release resources and prevent memory leaks
 */
dispose() {
  // Remove all event listeners
  this.removeAllListeners();
  
  // Notify native module to release resources
  return new Promise((resolve, reject) => {
    NativeModules.PjSipModule.dispose((successful) => {
      if (successful) {
        resolve();
      } else {
        reject(new Error('Failed to dispose endpoint'));
      }
    });
  });
}
```

**Implementation Tasks**:
- endpoint-007: Add dispose() method to Endpoint class
- Add native module cleanup handler in Android/iOS

**Status**: RESOLVED - Task endpoint-007 added to layer-1.md

### Issue 2: replaceAccount() not implemented - RESOLVED (2026-03-04)

**Problem**: `replaceAccount()` method throws `Error("Not implemented")`.

**Impact**:
- Account replacement requires delete+create workaround
- Potential race conditions during account updates
- More complex client code

**Resolution**:
Implement `replaceAccount()` in native module:
```javascript
replaceAccount(account, configuration) {
  return new Promise((resolve, reject) => {
    NativeModules.PjSipModule.replaceAccount(
      account.getId(),
      configuration,
      (successful, data) => {
        if (successful) {
          resolve(new Account(data));
        } else {
          reject(data);
        }
      }
    );
  });
}
```

**Native Implementation** (Android Kotlin):
```kotlin
@ReactMethod
fun replaceAccount(accountId: Int, configuration: ReadableMap, promise: Promise) {
    try {
        val account = accountManager.getAccount(accountId)
        if (account == null) {
            promise.reject("ACCOUNT_NOT_FOUND", "Account $accountId not found")
            return
        }
        
        // Update account configuration
        val updatedAccount = accountManager.updateAccount(account, configuration)
        
        // Emit account changed event
        emitAccountChanged(updatedAccount)
        
        // Resolve with updated account data
        promise.resolve(accountToMap(updatedAccount))
    } catch (e: Exception) {
        promise.reject("REPLACE_ACCOUNT_FAILED", e.message)
    }
}
```

**Implementation Tasks**:
- endpoint-008: Implement replaceAccount() in native module
- Update AccountManager with updateAccount() method
- Add replace_account Android/iOS native handlers

**Status**: RESOLVED - Task endpoint-008 added to layer-1.md

---

*Status: DRAFT | Type: SDD | Generated by /legacy*
*Updated: 2026-03-04 - GAP-008 and GAP-009 resolved*
