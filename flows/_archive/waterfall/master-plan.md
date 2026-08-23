# Master Plan

> Execution order for all 179 tasks across 3 layers.
> Generated: 2026-03-04
> Dependencies resolved: Layer 0 → Layer 1 → Layer 2

---

## Execution Strategy

**Breadth-First by Layer:**
1. Complete all Layer 0 tasks (shared infrastructure)
2. Complete all Layer 1 tasks (domain/core logic)
3. Complete all Layer 2 tasks (features)

**Within each layer:**
- Order by module dependencies
- Critical path first
- Independent tasks can be parallelized

---

## Phase 1: Layer 0 - Shared Infrastructure (31 tasks)

### Module: core-architecture (6 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 1 | core-arch-001 | Implement DependencyInjection class | - | 4h |
| 2 | core-arch-002 | Implement DependencyLifecycleManager | core-arch-001 | 2h |
| 3 | core-arch-003 | Implement ErrorHandler | - | 3h |
| 4 | core-arch-004 | Implement error storage | core-arch-003 | 2h |
| 5 | core-arch-005 | Implement ErrorBoundary widget | core-arch-003 | 2h |
| 6 | core-arch-006 | Setup MultiProvider in main.dart | - | 1h |

**Module total:** 14h

---

### Module: event-streaming (4 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 7 | event-001 | Implement TeleEndpoint class | - | 3h |
| 8 | event-002 | Implement event routing | event-001 | 2h |
| 9 | event-003 | Implement event types | event-002 | 2h |
| 10 | event-004 | Add dispose() method | event-002 | 1h |

**Module total:** 8h

---

### Module: monitoring (4 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 11 | monitor-001 | Implement ConnectionMonitorService | - | 3h |
| 12 | monitor-002 | Implement ConnectionStats entity | - | 2h |
| 13 | monitor-003 | Implement network quality assessment | monitor-002 | 2h |
| 14 | monitor-004 | Implement speed test integration | monitor-001 | 2h |

**Module total:** 9h

---

### Module: build-system (6 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 15 | build-001 | Create Dockerfile | - | 2h |
| 16 | build-002 | Create build_pjsip.sh | build-001 | 4h |
| 17 | build-003 | Create build_openssl.sh | build-002 | 2h |
| 18 | build-004 | Create build_openh264.sh | build-002 | 2h |
| 19 | build-005 | Create build_opus.sh | build-002 | 2h |
| 20 | build-006 | Create config_site.h | build-002 | 2h |

**Module total:** 14h

---

### Module: release-workflow (4 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 21 | release-001 | Create release.sh | - | 2h |
| 22 | release-002 | Create release_onlytar.sh | release-001 | 1h |
| 23 | release-003 | Create update.sh | release-001 | 2h |
| 24 | release-004 | Fix build_android.sh symlink | build-002 | 0.5h |

**Module total:** 5.5h

---

### Module: patch-management (7 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 25 | patch-001 | Create version-specific patch directories | - | 1h |
| 26 | patch-002 | Create config_site.h | - | 2h |
| 27 | patch-003 | Create android_jni_dev.c | patch-002 | 4h |
| 28 | patch-004 | Create opensl_dev.c | patch-002 | 4h |
| 29 | patch-005 | Create oboe_dev.c | patch-002 | 4h |
| 30 | patch-006 | Create conference.c | patch-002 | 3h |
| 31 | patch-007 | Create pjsua_aud.c and pjsua.h patches | patch-002 | 3h |

**Module total:** 21h

---

## Layer 0 Total: 71.5h (~9 working days)

---

## Phase 2: Layer 1 - Domain/Core Logic (87 tasks)

### Module: sip-core (6 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 32 | sip-core-001 | Implement Endpoint class | - | 4h |
| 33 | sip-core-002 | Implement Redux state structure | sip-core-001 | 3h |
| 34 | sip-core-003 | Implement account operations | sip-core-001 | 3h |
| 35 | sip-core-004 | Implement call operations | sip-core-001 | 4h |
| 36 | sip-core-005 | Implement push notification integration | sip-core-001 | 3h |
| 37 | sip-core-006 | Implement AppState monitoring | sip-core-001 | 2h |

**Module total:** 19h

---

### Module: sip (5 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 38 | sip-001 | Implement SipService singleton | - | 3h |
| 39 | sip-002 | Implement SipAccount data class | - | 1h |
| 40 | sip-003 | Implement SipCall data class | sip-002 | 2h |
| 41 | sip-004 | Implement SipConnectionState | sip-001 | 2h |
| 42 | sip-005 | Implement SipCallState | sip-003 | 2h |

**Module total:** 10h

---

### Module: telephony (4 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 43 | telephony-001 | Implement TelephonyService | - | 3h |
| 44 | telephony-002 | Implement native methods | telephony-001 | 4h |
| 45 | telephony-003 | Implement permission handling | telephony-001 | 2h |
| 46 | telephony-004 | Implement additional methods | telephony-001 | 2h |

**Module total:** 11h

---

### Module: call (6 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 47 | call-001 | Implement Call class | - | 4h |
| 48 | call-002 | Implement duration calculation | call-001 | 2h |
| 49 | call-003 | Implement URI parsing | call-001 | 2h |
| 50 | call-004 | Implement CallSettingsDTO | - | 1h |
| 51 | call-005 | Implement 20+ call operations | call-001 | 6h |
| 52 | call-006 | Implement call state machine | call-001 | 2h |

**Module total:** 17h

---

### Module: call-model (6 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 53 | callmodel-001 | Implement TeleCall Dart class | - | 4h |
| 54 | callmodel-002 | Implement TeleCall Kotlin class | - | 2h |
| 55 | callmodel-003 | **GAP-007**: Fix model mismatch | callmodel-001, callmodel-002 | 3h |
| 56 | callmodel-004 | Implement event types | callmodel-002 | 2h |
| 57 | callmodel-005 | Fix time zone handling | callmodel-001 | 1h |
| 58 | callmodel-006 | Improve regex robustness | callmodel-001 | 1h |

**Module total:** 13h

---

### Module: account (5 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 59 | account-001 | Implement Account class | - | 3h |
| 60 | account-002 | Implement AccountRegistration | account-001 | 2h |
| 61 | account-003 | Implement AccountConfigurationDTO | account-001 | 2h |
| 62 | account-004 | Implement registration status codes | account-002 | 2h |
| 63 | account-005 | Implement multiple concurrent accounts | account-001 | 2h |

**Module total:** 11h

---

### Module: endpoint (8 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 64 | endpoint-001 | Implement Endpoint class | - | 4h |
| 65 | endpoint-002 | Implement start() method | endpoint-001 | 2h |
| 66 | endpoint-003 | Implement account methods | endpoint-001 | 3h |
| 67 | endpoint-004 | Implement call methods | endpoint-001 | 4h |
| 68 | endpoint-005 | Implement messaging | endpoint-001 | 2h |
| 69 | endpoint-006 | Implement events | endpoint-001 | 3h |
| 70 | endpoint-007 | **GAP-008**: Add cleanup/destructor | endpoint-001 | 2h |
| 71 | endpoint-008 | **GAP-009**: Implement replaceAccount() | endpoint-001 | 3h |

**Module total:** 23h

---

### Module: gateway-service (7 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 72 | gateway-001 | Implement GatewayService singleton | - | 4h |
| 73 | gateway-002 | Implement GatewayConfig | gateway-001 | 2h |
| 74 | gateway-003 | Implement GatewayStatus | gateway-001 | 2h |
| 75 | gateway-004 | Implement CallRouting | gateway-001 | 3h |
| 76 | gateway-005 | Implement SIP→GSM routing | gateway-004, sip-001, telephony-001 | 4h |
| 77 | gateway-006 | Implement GSM→SIP routing | gateway-004, sip-001, telephony-001 | 4h |
| 78 | gateway-007 | Implement state synchronization | gateway-004 | 3h |

**Module total:** 22h

---

### Module: headless-service (6 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 79 | headless-001 | Implement HeadlessModule | - | 3h |
| 80 | headless-002 | Implement HeadlessService | headless-001 | 2h |
| 81 | headless-003 | Implement HeadlessEventService | headless-001 | 2h |
| 82 | headless-004 | Implement BootUpReceiver | headless-002 | 2h |
| 83 | headless-005 | Implement JavaScript API | headless-001 | 2h |
| 84 | headless-006 | Add permissions | headless-002 | 1h |

**Module total:** 12h

---

### Module: native-android-module (4 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 85 | dialer-native-001 | Implement ReplaceDialerModule | - | 2h |
| 86 | dialer-native-002 | **GAP-010**: Fix callback timing | dialer-native-001 | 2h |
| 87 | dialer-native-003 | **GAP-013**: Implement ActivityEventListener | dialer-native-001 | 3h |
| 88 | dialer-native-004 | Add thread synchronization | dialer-native-001 | 1h |

**Module total:** 8h

---

### Module: android-plugin (5 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 89 | dialer-flutter-001 | Implement FlutterDialerPlugin | - | 2h |
| 90 | dialer-flutter-002 | Implement isDefaultDialer() | dialer-flutter-001 | 1h |
| 91 | dialer-flutter-003 | Implement setDefaultDialer() | dialer-flutter-001 | 2h |
| 92 | dialer-flutter-004 | Implement canSetDefaultDialer() | dialer-flutter-001 | 1h |
| 93 | dialer-flutter-005 | Add thread synchronization | dialer-flutter-001 | 1h |

**Module total:** 7h

---

### Module: unisim (6 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 94 | unisim-001 | Implement EsProfile class | - | 2h |
| 95 | unisim-002 | Implement EsimSecurity | unisim-001 | 3h |
| 96 | unisim-003 | Implement QR code format | unisim-001 | 2h |
| 97 | unisim-004 | Implement profile statuses | unisim-001 | 1h |
| 98 | unisim-005 | Implement operator API client | unisim-001 | 4h |
| 99 | unisim-006 | **GAP-002**: Create specs document | - | 2h |

**Module total:** 14h

---

### Module: activity-intents (2 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 100 | intent-001 | Implement ActivityIntentService | - | 2h |
| 101 | intent-002 | Implement navigation routing | intent-001 | 2h |

**Module total:** 4h

---

### Module: foreground-management (2 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 102 | fg-001 | Implement ForegroundService | - | 2h |
| 103 | fg-002 | Implement service lifecycle | fg-001 | 2h |

**Module total:** 4h

---

### Module: telephony-integration (2 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 104 | telephony-int-001 | Implement TelephonyIntegration | - | 3h |
| 105 | telephony-int-002 | Implement call state synchronization | telephony-int-001 | 2h |

**Module total:** 5h

---

### Module: dialer (2 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 106 | dialer-001 | Implement DialerService | - | 2h |
| 107 | dialer-002 | Implement contact integration | dialer-001 | 2h |

**Module total:** 4h

---

### Module: android-telecom-integration (2 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 108 | telecom-001 | Implement AndroidTelecomService | - | 3h |
| 109 | telecom-002 | Implement Connection | telecom-001 | 2h |

**Module total:** 5h

---

### Module: android-implementation-sms (2 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 110 | sms-001 | Implement SmsService | - | 2h |
| 111 | sms-002 | Implement SMS receiver | sms-001 | 2h |

**Module total:** 4h

---

### Module: endpoint-2 (1 task)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 112 | endpoint2-001 | Implement Endpoint2 | - | 4h |

**Module total:** 4h

---

## Layer 1 Total: 207h (~26 working days)

---

## Phase 3: Layer 2 - Feature-Specific (61 tasks)

### Module: testing (7 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 113 | test-001 | Create test directory structure | - | 1h |
| 114 | test-002 | Implement unit tests | test-001 | 4h |
| 115 | test-003 | Implement widget tests | test-001 | 3h |
| 116 | test-004 | Implement integration tests | test-001 | 4h |
| 117 | test-005 | Setup mockito | test-002 | 2h |
| 118 | test-006 | Implement test naming convention | test-002 | 1h |
| 119 | test-007 | Setup dependencies | test-001 | 1h |

**Module total:** 16h

---

### Module: ui-theming (6 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 120 | theme-001 | Implement ThemeService | - | 3h |
| 121 | theme-002 | Implement ThemeMode enum | theme-001 | 1h |
| 122 | theme-003 | Implement ThemeOption class | theme-001 | 1h |
| 123 | theme-004 | Implement persistent storage | theme-001 | 2h |
| 124 | theme-005 | Implement status color palette | theme-001 | 2h |
| 125 | theme-006 | Implement Material 3 customization | theme-001 | 2h |

**Module total:** 11h

---

### Module: video-calling (11 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 126 | video-001 | Implement RemoteVideoView | - | 3h |
| 127 | video-002 | Implement PreviewVideoView | video-001 | 3h |
| 128 | video-003 | Implement CallControlsBar | video-001 | 4h |
| 129 | video-004 | Implement Call Information Overlay | video-001 | 2h |
| 130 | video-005 | Implement Incoming Call Screen | video-001 | 3h |
| 131 | video-006 | Implement VideoQualityIndicator | video-001 | 2h |
| 132 | video-007 | Implement camera switch | video-002 | 2h |
| 133 | video-008 | Implement video on/off toggle | video-001 | 2h |
| 134 | video-009 | Implement accessibility | video-003 | 2h |
| 135 | video-010 | Implement VoiceOver/TalkBack | video-003 | 2h |
| 136 | video-011 | **GAP-002**: Create specs document | - | 3h |

**Module total:** 28h

---

### Module: call-ui (3 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 137 | callui-001 | Implement CallScreen widget | - | 3h |
| 138 | callui-002 | Implement caller ID display | callui-001 | 2h |
| 139 | callui-003 | Implement call duration display | callui-001 | 2h |

**Module total:** 7h

---

### Module: screens (2 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 140 | screens-001 | Define screen structure | - | 2h |
| 141 | screens-002 | **GAP-006**: Create requirements document | - | 2h |

**Module total:** 4h

---

### Module: voip-calling (9 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 142 | voip-001 | Implement SR-1: Make Outgoing Calls | endpoint-004 | 3h |
| 143 | voip-002 | Implement SR-2: Receive Incoming Calls | endpoint-006 | 3h |
| 144 | voip-003 | Implement SR-3: Video Calling | video-007 | 4h |
| 145 | voip-004 | Implement SR-4: Call Management | call-005 | 4h |
| 146 | voip-005 | Implement SR-5: Account Configuration | account-001 | 2h |
| 147 | voip-006 | Implement SR-6: Network Resilience | monitor-001 | 3h |
| 148 | voip-007 | Implement SR-7: Battery Efficiency | headless-002 | 2h |
| 149 | voip-008 | Implement SR-8: Security & Privacy | endpoint-001 | 3h |
| 150 | voip-009 | **GAP-003**: Create specs document | - | 3h |

**Module total:** 27h

---

### Module: imei-modification (8 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 151 | imei-001 | Implement DeviceCommunicator | - | 3h |
| 152 | imei-002 | Implement HuaweiNVManager | imei-001 | 3h |
| 153 | imei-003 | Implement AT commands | imei-001 | 3h |
| 154 | imei-004 | Implement IMEI validation | imei-003 | 2h |
| 155 | imei-005 | Implement IMEI backup | imei-001 | 2h |
| 156 | imei-006 | Implement IMEI restore | imei-005 | 2h |
| 157 | imei-007 | **GAP-004**: Create specs document | - | 2h |
| 158 | imei-008 | Add legal warnings | imei-001 | 1h |

**Module total:** 18h

---

### Module: android-plugin-tests (3 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 159 | test-android-001 | Test isDefaultDialer() | dialer-flutter-002 | 2h |
| 160 | test-android-002 | Test setDefaultDialer() | dialer-flutter-003 | 2h |
| 161 | test-android-003 | Test canSetDefaultDialer() | dialer-flutter-004 | 2h |

**Module total:** 6h

---

### Module: incall-service-tests (2 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 162 | test-incall-001 | Test InCallService lifecycle | telecom-001 | 2h |
| 163 | test-incall-002 | Test Connection state | telecom-002 | 2h |

**Module total:** 4h

---

### Module: native-bridge-tests (2 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 164 | test-bridge-001 | Test AccountConfigurationDTO | account-003 | 2h |
| 165 | test-bridge-002 | Test PjActions intent factory | endpoint-003 | 2h |

**Module total:** 4h

---

### Module: plugin-tests (2 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 166 | test-plugin-001 | Create plugin test utilities | test-001 | 2h |
| 167 | test-plugin-002 | Create plugin registration tests | test-001 | 2h |

**Module total:** 4h

---

### Module: replace-dialer-tests (2 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 168 | test-replace-001 | Test isDefaultDialer() | dialer-native-001 | 2h |
| 169 | test-replace-002 | Test setDefaultDialer() callback | dialer-native-002 | 2h |

**Module total:** 4h

---

### Module: telephony-testing (4 tasks)

| Order | Task ID | Description | Dependencies | Estimated Effort |
|-------|---------|-------------|--------------|------------------|
| 170 | test-telephony-001 | Test makeCall() | telephony-002 | 2h |
| 171 | test-telephony-002 | Test answerCall() | telephony-002 | 2h |
| 172 | test-telephony-003 | Test endCall() | telephony-002 | 2h |
| 173 | test-telephony-004 | Test permission handling | telephony-003 | 2h |

**Module total:** 8h

---

## Layer 2 Total: 137h (~17 working days)

---

## Summary

| Phase | Layer | Tasks | Total Hours | Working Days |
|-------|-------|-------|-------------|--------------|
| 1 | Layer 0 | 31 | 71.5h | ~9 days |
| 2 | Layer 1 | 87 | 207h | ~26 days |
| 3 | Layer 2 | 61 | 137h | ~17 days |
| **TOTAL** | **All** | **179** | **415.5h** | **~52 days** |

---

## Critical Path

```
core-arch-001 → event-001 → callmodel-001 → call-001 → gateway-001 → voip-004
     ↓              ↓            ↓              ↓
build-001 → patch-002    endpoint-001 → video-001 → callui-001
     ↓
release-001
```

**Critical path tasks:** 14 tasks, ~50h

---

## Gap Resolution Tasks (Blocking)

| Gap | Task | Layer | Priority |
|-----|------|-------|----------|
| GAP-001 | Create plan.md strategy | All | P0 |
| GAP-007 | callmodel-003 | Layer 1 | P0 |
| GAP-008 | endpoint-007 | Layer 1 | P1 |
| GAP-009 | endpoint-008 | Layer 1 | P1 |
| GAP-010 | dialer-native-002 | Layer 1 | P1 |
| GAP-013 | dialer-native-003 | Layer 1 | P1 |
| GAP-002 | unisim-006 | Layer 1 | P2 |
| GAP-003 | voip-009 | Layer 2 | P2 |
| GAP-004 | imei-007 | Layer 2 | P2 |
| GAP-005 | (callui requirements) | Layer 2 | P2 |
| GAP-006 | screens-002 | Layer 2 | P2 |

---

*Generated by /waterfall. Execute tasks in order, update status as progress is made.*
