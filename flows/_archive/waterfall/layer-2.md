# Layer 2: Feature-Specific

> COMPILED from flows. Do not edit directly.
> Last compiled: 2026-03-04
> Source flows: tdd-testing, tdd-android-plugin, tdd-incall-service, tdd-native-bridge, tdd-plugin-tests, tdd-replace-dialer, tdd-telephony-testing, vdd-ui-theming, vdd-001-video-calling, vdd-call-ui, ddd-001-voip-calling, ddd-imei-modification

---

## Overview

- **Total tasks**: 35
- **Modules**: 10
- **Dependencies on lower layers**: layer-0 (core-architecture), layer-1 (all domain modules)

---

## Module: testing

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Test Structure | directory | Organized tests by layer | tdd-testing |
| Test Patterns | pattern | AAA pattern, mockito mocking | tdd-testing |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| DependencyInjection | DI | layer-0 (core-architecture) |
| All services | services | layer-1 (all domain modules) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 1 | test-001 | Create test directory structure: test/unit/, test/core/, test/services/, test/presentation/, test/integration/, test/widgets/ | - | tdd-testing |
| 2 | test-002 | Implement unit tests for domain layer use cases with AAA pattern | - | tdd-testing |
| 3 | test-003 | Implement widget tests for presentation layer components | test-001 | tdd-testing |
| 4 | test-004 | Implement integration tests for data layer repositories | test-001 | tdd-testing |
| 5 | test-005 | Setup mockito for mocking external dependencies | test-002 | tdd-testing |
| 6 | test-006 | Implement test naming convention: 'ClassName.method should expectedBehavior when condition' | test-002 | tdd-testing |
| 7 | test-007 | Setup flutter_test, mockito ^5.4.4, build_runner ^2.4.7, integration_test | test-001 | tdd-testing |

---

## Module: ui-theming

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| ThemeService | class | Material 3 theme with Light/Dark/System modes | vdd-ui-theming |
| ThemeMode | enum | light, dark, system | vdd-ui-theming |
| ThemeOption | class | Theme configuration option | vdd-ui-theming |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| SharedPreferences | storage | layer-0 (core-architecture) |
| ChangeNotifier | Flutter | Package dependency |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 8 | theme-001 | Implement ThemeService extending ChangeNotifier | - | vdd-ui-theming |
| 9 | theme-002 | Implement ThemeMode enum: light, dark, system (default: dark) | theme-001 | vdd-ui-theming |
| 10 | theme-003 | Implement ThemeOption class with mode, name, description, icon | theme-001 | vdd-ui-theming |
| 11 | theme-004 | Implement persistent storage with SharedPreferences key 'gost_simbox_theme' | theme-001 | vdd-ui-theming |
| 12 | theme-005 | Implement status color palette: Connection (green/yellow/red), Signal (5 levels), Call (green/red/yellow) | theme-001 | vdd-ui-theming |
| 13 | theme-006 | Implement Material 3 customization: seedColor #1E88E5, AppBar centerTitle, Card elevation 2 | theme-001 | vdd-ui-theming |

---

## Module: video-calling

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| RemoteVideoView | widget | Full screen remote video | vdd-001-video-calling |
| PreviewVideoView | widget | Picture-in-picture local preview (120x160) | vdd-001-video-calling |
| CallControlsBar | widget | Call control buttons | vdd-001-video-calling |
| VideoQualityIndicator | widget | Video quality status display | vdd-001-video-calling |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| Call | call state | layer-1 (call or call-model) |
| Endpoint | SIP API | layer-1 (endpoint or sip-core) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 14 | video-001 | Implement RemoteVideoView widget for full screen remote video | - | vdd-001-video-calling |
| 15 | video-002 | Implement PreviewVideoView widget (120x160 picture-in-picture) | video-001 | vdd-001-video-calling |
| 16 | video-003 | Implement CallControlsBar with End Call (red, center), Mute, Speaker, Video Toggle, Hold, More | video-001 | vdd-001-video-calling |
| 17 | video-004 | Implement Call Information Overlay with duration, caller info | video-001 | vdd-001-video-calling |
| 18 | video-005 | Implement Incoming Call Screen with answer/decline | video-001 | vdd-001-video-calling |
| 19 | video-006 | Implement VideoQualityIndicator: Excellent (3 bars, green), Good (2 bars), Fair (1 bar), Poor (warning, red) | video-001 | vdd-001-video-calling |
| 20 | video-007 | Implement camera switch (front/back) during video call | video-002 | vdd-001-video-calling |
| 21 | video-008 | Implement video on/off toggle during call | video-001 | vdd-001-video-calling |
| 22 | video-009 | Implement accessibility: 44x44dp min touch targets, 4.5:1 contrast ratio | video-003 | vdd-001-video-calling |
| 23 | video-010 | Implement VoiceOver/TalkBack labels for all controls | video-003 | vdd-001-video-calling |
| 24 | video-011 | Create technical specifications document (currently missing) | - | vdd-001-video-calling |

---

## Module: call-ui

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| CallScreen | widget | Call screen UI | vdd-call-ui |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| Call | call state | layer-1 (call or call-model) |
| ThemeService | theme | layer-2 (ui-theming) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 25 | callui-001 | Implement CallScreen widget with call state integration | - | vdd-call-ui |
| 26 | callui-002 | Implement caller ID display with number/name parsing | callui-001 | vdd-call-ui |
| 27 | callui-003 | Implement call duration display with real-time updates | callui-001 | vdd-call-ui |

---

## Module: screens

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Screen definitions | TBD | Screen structure | vdd-screens |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| Navigation | routing | layer-1 (activity-intents or navigation) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 28 | screens-001 | Define screen structure and navigation flow | - | vdd-screens |
| 29 | screens-002 | Create requirements document (currently missing) | - | vdd-screens |

---

## Module: voip-calling (DDD)

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Stakeholder Requirements | requirements | Business requirements for VoIP | ddd-001-voip-calling |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| Endpoint | SIP API | layer-1 (endpoint) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 30 | voip-001 | Implement SR-1: Make Outgoing Calls with dial pad and SIP address support | endpoint-004 | ddd-001-voip-calling |
| 31 | voip-002 | Implement SR-2: Receive Incoming Calls with push notification support | endpoint-006 | ddd-001-voip-calling |
| 32 | voip-003 | Implement SR-3: Video Calling with front/back camera switch | video-007 | ddd-001-voip-calling |
| 33 | voip-004 | Implement SR-4: Call Management (hold, transfer, conference, mute, DTMF) | call-005 | ddd-001-voip-calling |
| 34 | voip-005 | Implement SR-5: Account Configuration with SIP username/password | account-001 | ddd-001-voip-calling |
| 35 | voip-006 | Implement SR-6: Network Resilience with reconnection logic | monitor-001 | ddd-001-voip-calling |
| 36 | voip-007 | Implement SR-7: Battery Efficiency with background optimization | headless-002 | ddd-001-voip-calling |
| 37 | voip-008 | Implement SR-8: Security & Privacy with TLS/SRTP support | endpoint-001 | ddd-001-voip-calling |
| 38 | voip-009 | Create technical specifications document (currently missing) | - | ddd-001-voip-calling |

---

## Module: imei-modification (DDD)

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| DeviceCommunicator | class | Serial communication with device | ddd-imei-modification |
| HuaweiNVManager | class | NV item management for Huawei | ddd-imei-modification |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| pyserial | package | USB communication |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 39 | imei-001 | Implement DeviceCommunicator with serial communication | - | ddd-imei-modification |
| 40 | imei-002 | Implement HuaweiNVManager for NV item management | imei-001 | ddd-imei-modification |
| 41 | imei-003 | Implement AT commands: AT+CGSN (read IMEI), AT^CIMEI=<IMEI> (write), AT+CFUN=1,1 (reboot) | imei-001 | ddd-imei-modification |
| 42 | imei-004 | Implement IMEI validation with Luhn algorithm | imei-003 | ddd-imei-modification |
| 43 | imei-005 | Implement IMEI backup: JSON with device info, original IMEI, NV items, checksum | imei-001 | ddd-imei-modification |
| 44 | imei-006 | Implement IMEI restore from backup | imei-005 | ddd-imei-modification |
| 45 | imei-007 | Create technical specifications document (currently missing) | - | ddd-imei-modification |
| 46 | imei-008 | Add legal warnings about permitted use cases | imei-001 | ddd-imei-modification |

---

## Module: android-plugin-tests

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Test specs | tests | Test specifications for android plugin | tdd-android-plugin |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| FlutterDialerPlugin | plugin | layer-1 (android-plugin) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 47 | test-android-001 | Create tests for FlutterDialerPlugin.isDefaultDialer() | dialer-flutter-002 | tdd-android-plugin |
| 48 | test-android-002 | Create tests for FlutterDialerPlugin.setDefaultDialer() | dialer-flutter-003 | tdd-android-plugin |
| 49 | test-android-003 | Create tests for FlutterDialerPlugin.canSetDefaultDialer() | dialer-flutter-004 | tdd-android-plugin |

---

## Module: incall-service-tests

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Test specs | tests | Test specifications for InCallService | tdd-incall-service |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| InCallService | Android | layer-1 (android-telecom-integration) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 50 | test-incall-001 | Create tests for InCallService lifecycle | telecom-001 | tdd-incall-service |
| 51 | test-incall-002 | Create tests for Connection state management | telecom-002 | tdd-incall-service |

---

## Module: native-bridge-tests

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Test specs | tests | Test specifications for native bridge | tdd-native-bridge |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| AccountConfigurationDTO | DTO | layer-1 (account) |
| PjActions | actions | layer-1 (endpoint or sip-core) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 52 | test-bridge-001 | Create tests for AccountConfigurationDTO serialization | account-003 | tdd-native-bridge |
| 53 | test-bridge-002 | Create tests for PjActions intent factory | endpoint-003 | tdd-native-bridge |

---

## Module: plugin-tests

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Test specs | tests | General plugin testing | tdd-plugin-tests |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| All plugins | plugins | layer-1 (all plugin modules) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 54 | test-plugin-001 | Create general plugin test utilities | test-001 | tdd-plugin-tests |
| 55 | test-plugin-002 | Create plugin registration tests | test-001 | tdd-plugin-tests |

---

## Module: replace-dialer-tests

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Test specs | tests | Test specifications for replace dialer | tdd-replace-dialer |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| ReplaceDialerModule | module | layer-1 (native-android-module) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 56 | test-replace-001 | Create tests for ReplaceDialerModule.isDefaultDialer() | dialer-native-001 | tdd-replace-dialer |
| 57 | test-replace-002 | Create tests for ReplaceDialerModule.setDefaultDialer() callback timing | dialer-native-002 | tdd-replace-dialer |

---

## Module: telephony-testing

### Provided Interfaces

| Interface | Type | Description | Source |
|-----------|------|-------------|--------|
| Test specs | tests | Test specifications for telephony | tdd-telephony-testing |

### Required Interfaces (from Lower Layers)

| Interface | Type | Expected From |
|-----------|------|---------------|
| TelephonyService | service | layer-1 (telephony) |

### Tasks

| # | Task ID | Description | Dependencies | Source Flow |
|---|---------|-------------|--------------|-------------|
| 58 | test-telephony-001 | Create tests for TelephonyService.makeCall() | telephony-002 | tdd-telephony-testing |
| 59 | test-telephony-002 | Create tests for TelephonyService.answerCall() | telephony-002 | tdd-telephony-testing |
| 60 | test-telephony-003 | Create tests for TelephonyService.endCall() | telephony-002 | tdd-telephony-testing |
| 61 | test-telephony-004 | Create tests for permission handling | telephony-003 | tdd-telephony-testing |

---

## Cross-Module Dependencies

```
test-001 ──► All test modules (provides test structure)
theme-001 ──► callui-001, video-001 (provides theming)
video-001 ──► voip-003 (provides video calling)
call-001 ──► callui-001, voip-004 (provides call state)
endpoint-001 ──► voip-001, voip-002 (provides SIP API)
```

---

## Known Gaps

| Gap ID | Description | Affected Flows | Resolution |
|--------|-------------|----------------|------------|
| GAP-L2-001 | No explicit plan.md in any Layer 2 flow | All | Extract tasks from specifications |
| GAP-L2-002 | Missing specifications for vdd-001-video-calling | vdd-001-video-calling | Create specs, then video-011 |
| GAP-L2-003 | Missing requirements for vdd-call-ui | vdd-call-ui | Create requirements |
| GAP-L2-004 | Missing requirements and specs for vdd-screens | vdd-screens | Create both docs |
| GAP-L2-005 | Missing specifications for ddd-001-voip-calling | ddd-001-voip-calling | Create specs, then voip-009 |
| GAP-L2-006 | Missing specifications for ddd-imei-modification | ddd-imei-modification | Create specs, then imei-007 |

---

## Success Metrics (from ddd-001-voip-calling)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Call Setup Time | < 3 seconds | Time from dial to ringing |
| Call Success Rate | > 95% | Successful connects / attempts |
| Audio Quality (MOS) | > 4.0 | Mean Opinion Score |
| Video Frame Rate | > 15 FPS | Frames per second |
| Battery Drain (idle) | < 5%/hour | Background consumption |
| Registration Success | > 99% | Successful registrations |
| Crash Rate | < 0.1% | Crashes per session |

---

*Compiled by /waterfall. Regenerate with `/waterfall compile`*
