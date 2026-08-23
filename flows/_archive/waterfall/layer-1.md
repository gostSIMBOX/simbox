# Layer 1: Domain/Core Logic

> COMPILED from flows. Do not edit directly.
> Last compiled: 2026-03-04
> Source flows: sdd-sip-core, sdd-sip, sdd-telephony, sdd-call, sdd-call-model, sdd-account, sdd-endpoint, sdd-gateway-service, sdd-headless-service, sdd-native-android-module, sdd-android-plugin, sdd-unisim, sdd-activity-intents, sdd-foreground-management, sdd-telephony-integration, sdd-endpoint-2, sdd-dialer, sdd-android-telecom-integration, sdd-android-implementation-sms

---

## Overview

- **Total tasks**: 87
- **Modules**: 13
- **Dependencies on lower layers**: layer-0 (core-architecture, event-streaming)

---

## Module: sip-core

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Endpoint | class | SIP endpoint with EventEmitter, account/call management | sdd-sip-core |
| Redux State | state | Global state with endpoint, accounts, calls, tokens | sdd-sip-core |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| EventChannel | event streaming | layer-0 (event-streaming) |
| DependencyInjection | DI | layer-0 (core-architecture) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 1 | sip-core-001 | Implement Endpoint class extending EventEmitter | - | sdd-sip-core |
| 2 | sip-core-002 | Implement Redux state structure with endpoint, accounts, calls, tokens, connectivity | sip-core-001 | sdd-sip-core |
| 3 | sip-core-003 | Implement account operations: createAccount, deleteAccount, registerAccount | sip-core-001 | sdd-sip-core |
| 4 | sip-core-004 | Implement call operations: makeCall, answerCall, hangupCall, holdCall, muteCall, transfer, redirect, dtmfCall | sip-core-001 | sdd-sip-core |
| 5 | sip-core-005 | Implement push notification integration for iOS VoIP tokens | sip-core-001 | sdd-sip-core |
| 6 | sip-core-006 | Implement AppState monitoring for iOS background handling | sip-core-001 | sdd-sip-core |

---

## Module: sip

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| SipService | singleton | SIP service with account and call management | sdd-sip |
| SipAccount | data class | Account configuration (username, password, domain) | sdd-sip |
| SipCall | data class | Call state (id, remoteNumber, direction, state) | sdd-sip |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| Logger | logging | layer-0 (core-architecture) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 7 | sip-001 | Implement SipService singleton with connection state machine | - | sdd-sip |
| 8 | sip-002 | Implement SipAccount data class with username, password, domain, proxy, port, useSecure | - | sdd-sip |
| 9 | sip-003 | Implement SipCall data class with id, remoteNumber, direction, state, startTime, duration | sip-002 | sdd-sip |
| 10 | sip-004 | Implement SipConnectionState: disconnected → connecting → connected → error | sip-001 | sdd-sip |
| 11 | sip-005 | Implement SipCallState: connecting → ringing → active → hold → ended/failed | sip-003 | sdd-sip |

---

## Module: telephony

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| TelephonyService | singleton | GSM telephony via MethodChannel | sdd-telephony |
| TelephonyCall | data class | Call representation for GSM calls | sdd-telephony |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| MethodChannel | Flutter | Package dependency |
| permission_handler | package | Package dependency |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 12 | telephony-001 | Implement TelephonyService singleton with MethodChannel 'gsm_sip_gateway/telephony' | - | sdd-telephony |
| 13 | telephony-002 | Implement native methods: initialize, makeCall, answerCall, endCall, getPhoneNumber | telephony-001 | sdd-telephony |
| 14 | telephony-003 | Implement permission handling with TelephonyPermissionStatus enum | telephony-001 | sdd-telephony |
| 15 | telephony-004 | Implement getNetworkOperatorName, getSimSerialNumber, getSignalStrength, sendUssd | telephony-001 | sdd-telephony |

---

## Module: call

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Call | class | SIP call with 40+ fields for full state tracking | sdd-call |
| CallSettingsDTO | DTO | Call settings (flag, reqKeyframeMethod, audCnt, vidCnt) | sdd-call |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| EventChannel | events | layer-0 (event-streaming) |
| Endpoint | SIP | layer-1 (sip-core or endpoint) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 16 | call-001 | Implement Call class with id, accountId, state, held, muted, speaker, duration fields | - | sdd-call |
| 17 | call-002 | Implement duration calculation: getTotalDuration(), getConnectDuration(), _formatTime() | call-001 | sdd-call |
| 18 | call-003 | Implement URI parsing: _parseRemoteNumber, _parseRemoteName, _parseLocalNumber | call-001 | sdd-call |
| 19 | call-004 | Implement CallSettingsDTO with audCnt (default 1), vidCnt (default 0) | - | sdd-call |
| 20 | call-005 | Implement 20+ call operations: makeCall, answerCall, hangupCall, holdCall, unholdCall, muteCall, unmuteCall, useSpeaker, useEarpiece, dtmfCall, xferCall, redirectCall | call-001 | sdd-call |
| 21 | call-006 | Implement call state machine with PJSIP_INV_STATE_* constants | call-001 | sdd-call |

---

## Module: call-model

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| TeleCall (Dart) | class | Comprehensive call model with 40+ fields | sdd-call-model |
| TeleCall (Kotlin) | data class | Minimal call model for event streaming (10 fields) | sdd-call-model |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| EventChannel | events | layer-0 (event-streaming) |
| MethodChannel | Flutter | Package dependency |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 22 | callmodel-001 | Implement TeleCall Dart class with identity, participant, state, timing, media fields | - | sdd-call-model |
| 23 | callmodel-002 | Implement TeleCall Kotlin data class with id, destination, sim, state, held, muted, speaker, direction, remoteNumber, remoteName | - | sdd-call-model |
| 24 | callmodel-003 | Fix model mismatch: sync Kotlin 10 fields with Dart 40+ fields | callmodel-001, callmodel-002 | sdd-call-model |
| 25 | callmodel-004 | Implement event types: service_started, call_received, call_changed, call_terminated, call_error | callmodel-002 | sdd-call-model |
| 26 | callmodel-005 | Fix time zone handling in duration calculations | callmodel-001 | sdd-call-model |
| 27 | callmodel-006 | Improve regex robustness for SIP URI parsing | callmodel-001 | sdd-call-model |

---

## Module: account

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Account | class | SIP account with registration tracking | sdd-account |
| AccountRegistration | class | Registration status (code, reason, expiration) | sdd-account |
| AccountConfigurationDTO | DTO | Kotlin serialization | sdd-account |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| EventChannel | events | layer-0 (event-streaming) |
| Endpoint | SIP | layer-1 (endpoint) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 28 | account-001 | Implement Account class with id, uri, name, username, domain, password, proxy, transport | - | sdd-account |
| 29 | account-002 | Implement AccountRegistration with status, code, reason, expiration, retryAfter | account-001 | sdd-account |
| 30 | account-003 | Implement AccountConfigurationDTO for Kotlin serialization | account-001 | sdd-account |
| 31 | account-004 | Implement registration status codes: 200 (OK), 401 (Unauthorized), 403 (Forbidden), 404, 408, 503 | account-002 | sdd-account |
| 32 | account-005 | Implement multiple concurrent accounts with independent registration tracking | account-001 | sdd-account |

---

## Module: endpoint

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Endpoint | class | Primary PjSIP interface with EventEmitter | sdd-endpoint |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| NativeModules | React Native | Platform dependency |
| DeviceEventEmitter | React Native | Platform dependency |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 33 | endpoint-001 | Implement Endpoint class extending EventEmitter | - | sdd-endpoint |
| 34 | endpoint-002 | Implement start() method for endpoint initialization | endpoint-001 | sdd-endpoint |
| 35 | endpoint-003 | Implement account methods: createAccount, registerAccount, deleteAccount | endpoint-001 | sdd-endpoint |
| 36 | endpoint-004 | Implement call methods: makeCall, answerCall, hangupCall, holdCall, muteCall, xferCall | endpoint-001 | sdd-endpoint |
| 37 | endpoint-005 | Implement messaging: sendMessage | endpoint-001 | sdd-endpoint |
| 38 | endpoint-006 | Implement events: registration_changed, call_received, call_changed, call_terminated, message_received, connectivity_changed | endpoint-001 | sdd-endpoint |
| 39 | endpoint-007 | Add cleanup/destructor method to prevent memory leak | endpoint-001 | sdd-endpoint |
| 40 | endpoint-008 | Implement replaceAccount() method (currently not implemented) | endpoint-001 | sdd-endpoint |

---

## Module: gateway-service

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| GatewayService | singleton | Bidirectional GSM↔SIP/SMPP routing orchestration | sdd-gateway-service |
| GatewayConfig | config | Gateway configuration with routing rules | sdd-gateway-service |
| GatewayStatus | status | Gateway runtime status | sdd-gateway-service |
| CallRouting | class | Call routing state between SIP and GSM | sdd-gateway-service |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| SharedPreferences | storage | Package dependency |
| Logger | logging | layer-0 (core-architecture) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 41 | gateway-001 | Implement GatewayService singleton orchestrating sub-services | - | sdd-gateway-service |
| 42 | gateway-002 | Implement GatewayConfig with sipAccount, smppConfig, routing flags, maxConcurrentCalls | gateway-001 | sdd-gateway-service |
| 43 | gateway-003 | Implement GatewayStatus with isRunning, sipState, smppState, activeCalls, uptime | gateway-001 | sdd-gateway-service |
| 44 | gateway-004 | Implement CallRouting with sipCallId, telephonyCallId, number, direction, state | gateway-001 | sdd-gateway-service |
| 45 | gateway-005 | Implement SIP→GSM call routing logic | gateway-004, sip-001, telephony-001 | sdd-gateway-service |
| 46 | gateway-006 | Implement GSM→SIP call routing logic | gateway-004, sip-001, telephony-001 | sdd-gateway-service |
| 47 | gateway-007 | Implement state synchronization between SIP and GSM calls | gateway-004 | sdd-gateway-service |

---

## Module: headless-service

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| HeadlessModule | class | React Native module for headless JS | sdd-headless-service |
| HeadlessService | Service | Foreground service with 2s polling | sdd-headless-service |
| HeadlessEventService | Service | Headless task with 5s timeout | sdd-headless-service |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| React Native | framework | >= 0.40.0 |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 48 | headless-001 | Implement HeadlessModule extending ReactContextBaseJavaModule | - | sdd-headless-service |
| 49 | headless-002 | Implement HeadlessService with 2-second polling interval | headless-001 | sdd-headless-service |
| 50 | headless-003 | Implement HeadlessEventService with 5-second timeout | headless-001 | sdd-headless-service |
| 51 | headless-004 | Implement BootUpReceiver for BOOT_COMPLETED broadcast | headless-002 | sdd-headless-service |
| 52 | headless-005 | Implement JavaScript API: startService, stopService, toForeground, toBackground | headless-001 | sdd-headless-service |
| 53 | headless-006 | Add FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED, WAKE_LOCK permissions | headless-002 | sdd-headless-service |

---

## Module: native-android-module (react-native-replace-dialer)

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| ReplaceDialerModule | class | Default dialer check/request module | sdd-native-android-module |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| TelecomManager | Android | API 23+ |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 54 | dialer-native-001 | Implement ReplaceDialerModule with isDefaultDialer(Callback), setDefaultDialer(Callback) | - | sdd-native-android-module |
| 55 | dialer-native-002 | Fix setDefaultDialer() to invoke callback after activity result (not immediately) | dialer-native-001 | sdd-native-android-module |
| 56 | dialer-native-003 | Implement ActivityEventListener for activity result handling | dialer-native-001 | sdd-native-android-module |
| 57 | dialer-native-004 | Add thread synchronization for concurrent calls | dialer-native-001 | sdd-native-android-module |

---

## Module: android-plugin (flutter_dialer)

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| FlutterDialerPlugin | class | Flutter plugin for dialer management | sdd-android-plugin |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| MethodChannel | Flutter | Package dependency |
| TelecomManager | Android | API 23+ |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 58 | dialer-flutter-001 | Implement FlutterDialerPlugin with MethodChannel 'flutter_dialer' | - | sdd-android-plugin |
| 59 | dialer-flutter-002 | Implement isDefaultDialer() method | dialer-flutter-001 | sdd-android-plugin |
| 60 | dialer-flutter-003 | Implement setDefaultDialer() with proper result handling | dialer-flutter-001 | sdd-android-plugin |
| 61 | dialer-flutter-004 | Implement canSetDefaultDialer() method | dialer-flutter-001 | sdd-android-plugin |
| 62 | dialer-flutter-005 | Add thread synchronization for concurrent calls | dialer-flutter-001 | sdd-android-plugin |

---

## Module: unisim (eSIM Management)

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| EsProfile | class | eSIM profile with iccid, eid, operator, status | sdd-unisim |
| EsimSecurity | class | AES-256 encryption, HMAC-SHA256 integrity | sdd-unisim |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| GSMA SGP.22 | protocol | Consumer protocol |
| GSMA SGP.32 | protocol | IoT protocol |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 63 | unisim-001 | Implement EsProfile class with iccid, eid, profile_name, operator, status, activation_code | - | sdd-unisim |
| 64 | unisim-002 | Implement EsimSecurity with AES-256 encryption and HMAC-SHA256 integrity | unisim-001 | sdd-unisim |
| 65 | unisim-003 | Implement QR code format: LPA:1$<SM-DP+ Address>$<Activation Code> | unisim-001 | sdd-unisim |
| 66 | unisim-004 | Implement profile statuses: downloaded, active, inactive, deleted | unisim-001 | sdd-unisim |
| 67 | unisim-005 | Implement operator API client for MTS, Beeline, MegaFon, Tele2 | unisim-001 | sdd-unisim |
| 68 | unisim-006 | Create full specifications document (currently missing) | - | sdd-unisim |

---

## Module: activity-intents

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| ActivityIntentService | class | Navigation/intent handling service | sdd-activity-intents |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| MethodChannel | Flutter | Package dependency |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 69 | intent-001 | Implement ActivityIntentService for Android intent handling | - | sdd-activity-intents |
| 70 | intent-002 | Implement navigation routing based on intent type | intent-001 | sdd-activity-intents |

---

## Module: foreground-management

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| ForegroundService | class | Foreground service lifecycle management | sdd-foreground-management |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| Notification | Android | Foreground notification |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 71 | fg-001 | Implement ForegroundService with notification management | - | sdd-foreground-management |
| 72 | fg-002 | Implement service lifecycle: start, stop, update | fg-001 | sdd-foreground-management |

---

## Module: telephony-integration

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| TelephonyIntegration | class | Telecom integration service | sdd-telephony-integration |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| TelecomManager | Android | API 23+ |
| ConnectionService | Android | Call integration |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 73 | telephony-int-001 | Implement TelephonyIntegration with ConnectionService | - | sdd-telephony-integration |
| 74 | telephony-int-002 | Implement call state synchronization with TelecomManager | telephony-int-001 | sdd-telephony-integration |

---

## Module: dialer

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| DialerService | class | Dialer functionality service | sdd-dialer |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| MethodChannel | Flutter | Package dependency |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 75 | dialer-001 | Implement DialerService with dial pad and call initiation | - | sdd-dialer |
| 76 | dialer-002 | Implement contact integration for dialer | dialer-001 | sdd-dialer |

---

## Module: android-telecom-integration

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| AndroidTelecomService | class | Android Telecom API integration | sdd-android-telecom-integration |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| InCallService | Android | Call UI integration |
| Connection | Android | Call connection |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 77 | telecom-001 | Implement AndroidTelecomService with InCallService | - | sdd-android-telecom-integration |
| 78 | telecom-002 | Implement Connection for call state management | telecom-001 | sdd-android-telecom-integration |

---

## Module: android-implementation-sms

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| SmsService | class | SMS implementation service | sdd-android-implementation-sms |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| SmsManager | Android | SMS sending |
| Telephony | Android | SMS receiving |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 79 | sms-001 | Implement SmsService with SmsManager for sending SMS | - | sdd-android-implementation-sms |
| 80 | sms-002 | Implement SMS receiver with Telephony broadcast | sms-001 | sdd-android-implementation-sms |

---

## Module: endpoint-2

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Endpoint2 | class | Alternative endpoint implementation | sdd-endpoint-2 |

### Required Interfaces (from Layer 0)

| Interface | Type | Expected From |
|-----------|------|---------------|
| NativeModules | React Native | Platform dependency |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 81 | endpoint2-001 | Implement Endpoint2 as alternative to Endpoint | - | sdd-endpoint-2 |

---

## Cross-Module Dependencies

```
sip-core-001 ──► account-001, call-001, endpoint-001 (provides SIP foundation)
telephony-001 ──► callmodel-001, gateway-001 (provides GSM telephony)
call-001 ──► gateway-004, video-calling (provides call state)
gateway-001 ──► sip-001, telephony-001 (orchestrates routing)
endpoint-001 ──► account-001, call-001 (provides PjSIP API)
event-streaming ──► callmodel-004, telephony-001 (provides events)
```

---

## Known Gaps

| Gap ID | Description | Affected Flows | Resolution |
|--------|-------------|----------------|------------|
| GAP-L1-001 | No explicit plan.md in any Layer 1 flow | All | Extract tasks from specifications |
| GAP-L1-002 | Model mismatch between Dart (40+ fields) and Kotlin (10 fields) TeleCall | sdd-call-model | Fix in callmodel-003 |
| GAP-L1-003 | Missing cleanup/destructor in Endpoint | sdd-endpoint | Fix in endpoint-007 |
| GAP-L1-004 | replaceAccount() not implemented | sdd-endpoint | Fix in endpoint-008 |
| GAP-L1-005 | setDefaultDialer() invokes callback prematurely | sdd-native-android-module | Fix in dialer-native-002 |
| GAP-L1-006 | Missing full specifications for unisim | sdd-unisim | Create specs, then unisim-006 |
| GAP-L1-007 | ActivityEventListener commented out | sdd-native-android-module | Fix in dialer-native-003 |

---

*Compiled by /waterfall. Regenerate with `/waterfall compile`*
