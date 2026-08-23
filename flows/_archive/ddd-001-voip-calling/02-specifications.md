# 02-Technical Specifications: VoIP Calling Feature

> **Status**: COMPLETE
> **Type**: DDD (Document-Driven Development)
> **Source**: ddd-001-voip-calling stakeholder requirements
> **Date**: 2026-03-07
> **Layer**: 2 (Feature-Specific)

---

## Overview

This document provides technical specifications for the VoIP calling feature based on stakeholder requirements (SR-1 through SR-8).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VoIP Calling Feature                      │
├─────────────────────────────────────────────────────────────┤
│  Presentation Layer                                          │
│  ┌─────────────┬─────────────┬─────────────────────────┐   │
│  │ CallScreen  │ VideoScreen │ IncomingCallScreen      │   │
│  └─────────────┴─────────────┴─────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Domain Layer                                                │
│  ┌─────────────┬─────────────┬─────────────────────────┐   │
│  │ Call Entity │ Account     │ Call Routing Logic      │   │
│  └─────────────┴─────────────┴─────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Application Layer                                           │
│  ┌─────────────┬─────────────┬─────────────────────────┐   │
│  │ SipUseCases │ Call UseCases │ Video UseCases        │   │
│  └─────────────┴─────────────┴─────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                        │
│  ┌─────────────┬─────────────┬─────────────────────────┐   │
│  │ Endpoint    │ GatewayService │ TeleEndpoint         │   │
│  └─────────────┴─────────────┴─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## SR-1: Make Outgoing Calls

### Technical Specification

**Implementation**: Uses `SipService.makeCall()` or `Endpoint.makeCall()`

**Call Flow**:
```
User dials number → DialerService → SipService.makeCall() → Endpoint → PjSIP
                                              ↓
                                      Call state events → UI updates
```

**API**:
```dart
// From layer-1: sip-service or endpoint
final call = await sipService.makeCall(
  accountId: 1,
  destination: '+1234567890',
  settings: CallSettingsDTO(audCnt: 1, vidCnt: 0),
);

// Listen for call state
endpoint.callChanged.listen((call) {
  if (call.state == 'PJSIP_INV_STATE_CONFIRMED') {
    // Call connected
  }
});
```

**Success Criteria**:
- Call initiation: < 500ms
- Call setup (ringing): < 3 seconds
- Audio codec: OPUS/G.711 (negotiated)

---

## SR-2: Receive Incoming Calls

### Technical Specification

**Implementation**: Uses `TeleEndpoint` event streaming with background handling

**Call Flow**:
```
Incoming SIP INVITE → PjSIP → TeleEndpoint → call_received event
                                                    ↓
                                    ┌───────────────┴───────────────┐
                                    │                               │
                              App in foreground              App in background
                                    │                               │
                                    ↓                               ↓
                            CallScreen (modal)              Push notification
                                                                    │
                                                                    ↓
                                                            User taps → CallScreen
```

**Event Handling**:
```dart
// In app initialization
endpoint.callReceived.listen((call) {
  if (call.direction == 'DIRECTION_INCOMING') {
    // Show incoming call screen
    IncomingCallService.showIncomingCall(call);
  }
});

// Background handling (Android)
// HeadlessService receives call events via EventChannel
```

**Push Notification** (iOS):
```dart
// VoIP push handling
VoipPushNotification.onVoipNotificationReceived = (payload) {
  // Wake up app, show incoming call
  IncomingCallService.showIncomingCallFromPush(payload);
};
```

**Success Criteria**:
- Incoming call detection: < 2 seconds
- Ring tone starts: < 1 second after detection
- Background wake: < 3 seconds

---

## SR-3: Video Calling

### Technical Specification

**Implementation**: Uses video widgets from layer-2 video-calling module

**Components**:
- `RemoteVideoView` - Full-screen remote video
- `PreviewVideoView` - PiP local preview (120x160dp)
- `VideoCallControls` - Control bar with video toggle
- `VideoQualityIndicator` - Quality status display

**Video Call Flow**:
```
User enables video → SipService.toggleVideo(callId, enable: true)
                              ↓
                    PjSIP negotiates video codec
                              ↓
                    RemoteVideoView receives windowId
                    PreviewVideoView starts camera
                              ↓
                    Bidirectional video streaming
```

**API**:
```dart
// Enable video during call
await sipService.enableVideo(callId: call.id);

// Switch camera
await sipService.switchCamera(callId: call.id, useFront: !useFront);

// Video state events
endpoint.callChanged.listen((call) {
  if (call.videoCount > 0) {
    // Video is active
  }
});
```

**Codecs** (negotiated in order):
1. H.264 (baseline profile)
2. H.263+
3. VP8 (if supported)

**Success Criteria**:
- Video frame rate: > 15 FPS (target 30 FPS)
- Video latency: < 300ms
- Resolution: 640x480 (VGA) minimum

---

## SR-4: Call Management

### Technical Specification

**Implementation**: Uses `SipService` call control methods

**Hold/Resume**:
```dart
await sipService.holdCall(callId: call.id);
await sipService.unholdCall(callId: call.id);
```

**Transfer** (Blind):
```dart
await sipService.transferCall(
  callId: call.id,
  destination: '+0987654321',
);
```

**Transfer** (Attended):
```dart
// First, make call to transfer target
final transferCall = await sipService.makeCall(...);

// Wait for answer, then execute attended transfer
await sipService.attendedTransfer(
  callId: originalCall.id,
  destCallId: transferCall.id,
);
```

**Conference**:
```dart
// Add second call to conference
await sipService.addToConference(
  mainCallId: call1.id,
  otherCallId: call2.id,
);
```

**DTMF**:
```dart
// Send DTMF digit
await sipService.sendDtmf(
  callId: call.id,
  digit: '5',
  method: DtmfMethod.RFC2833, // or INFO or INBAND
);
```

**Success Criteria**:
- Hold/Resume: < 500ms
- Transfer initiation: < 1 second
- DTMF detection: < 200ms

---

## SR-5: Account Configuration

### Technical Specification

**Implementation**: Uses `SipService.createAccount()` or `Endpoint.createAccount()`

**Account Creation**:
```dart
final account = await sipService.createAccount(SipAccount(
  username: '50363',
  password: 'pass50363',
  domain: '172.16.104.17',
  port: 5060,
  transport: Transport.UDP,
  regTimeout: 3600,
));
```

**Account Configuration**:
```dart
class SipAccount {
  final String username;
  final String password;
  final String domain;
  final int port;
  final Transport transport; // UDP, TCP, TLS
  final int regTimeout; // seconds
  final String? proxy;
  final bool useSecure;
  final Map<String, String> regHeaders;
}
```

**Registration Events**:
```dart
endpoint.registrationChanged.listen((event) {
  final status = event.data['status']; // 'active', 'inactive', 'error'
  final code = event.data['code']; // 200, 401, 403, 404, 503
});
```

**Success Criteria**:
- Account creation: < 1 second
- Registration: < 3 seconds
- Re-registration: Automatic on expiry

---

## SR-6: Network Resilience

### Technical Specification

**Implementation**: Uses `ConnectionMonitorService` from layer-0

**Network Monitoring**:
```dart
// Connection monitor provides:
- Network type (WiFi, 4G, 3G, Edge)
- Signal strength
- Latency measurement
- Bandwidth estimation
```

**Reconnection Logic**:
```dart
// In SipService
_connectivityController.stream.listen((isConnected) {
  if (!isConnected) {
    _connectionState = ConnectionState.disconnected;
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer.periodic(
      Duration(seconds: 5),
      (_) => _attemptReconnect(),
    );
  } else {
    _reconnectTimer?.cancel();
    _attemptReconnect();
  }
});
```

**Network Quality Assessment**:
```dart
enum NetworkQuality {
  excellent, // < 50ms latency, > 1Mbps
  good,      // 50-100ms, > 500Kbps
  fair,      // 100-200ms, > 100Kbps
  poor,      // > 200ms or < 100Kbps
}
```

**Success Criteria**:
- Network change detection: < 2 seconds
- Reconnection attempt: Every 5 seconds
- Registration recovery: < 10 seconds after reconnect

---

## SR-7: Battery Efficiency

### Technical Specification

**Implementation**: Uses `HeadlessService` for background operation

**Background Optimization**:
```dart
// Headless service with 2-second polling
class HeadlessService extends Service {
  // Polling interval: 2000ms
  // Wake lock: Only during task execution
  // Timeout: 5 seconds per task
}
```

**Push Notification Strategy**:
```dart
// iOS: VoIP push for incoming calls
// Android: FCM high-priority for incoming calls
// Reduces need for constant polling
```

**Battery Optimization**:
- Reduce polling interval when screen off
- Use push notifications instead of polling when available
- Acquire wake lock only during active tasks
- Release resources on call termination

**Success Criteria**:
- Background battery drain: < 5%/hour
- Push notification wake: < 3 seconds
- Headless task timeout: 5 seconds max

---

## SR-8: Security & Privacy

### Technical Specification

**Implementation**: TLS for signaling, SRTP for media

**TLS Configuration**:
```dart
final account = SipAccount(
  username: 'user',
  password: 'pass',
  domain: 'sip.example.com',
  useSecure: true, // Enable TLS
  // Transport.TRANSPORT_TLS
);
```

**SRTP Configuration**:
```dart
final config = EndpointConfiguration(
  useSrtp: true,
  srtpKeying: SrtpKeying.SDES, // or DTLS-SRTP
  requireSrtp: false, // Allow non-SRTP calls
);
```

**Authentication**:
- SIP Digest Authentication (RFC 2617)
- Password never transmitted in clear
- Challenge-response mechanism

**Success Criteria**:
- TLS handshake: < 2 seconds
- SRTP negotiation: Automatic during call setup
- Authentication: On every registration

---

## Success Metrics

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

## Dependencies

**Layer 0** (Shared Infrastructure):
- `ConnectionMonitorService` - Network monitoring
- `HeadlessService` - Background operation
- `ErrorHandler` - Error handling

**Layer 1** (Domain/Core):
- `SipService` - SIP operations
- `Endpoint` / `TeleEndpoint` - PjSIP interface
- `Call` / `TeleCall` - Call models
- `GatewayService` - Call routing (if bridging)

---

## Testing Strategy

### Unit Tests
- Test call state machine transitions
- Test account registration flows
- Test DTMF encoding/decoding

### Integration Tests
- Test end-to-end call flow
- Test network change handling
- Test background operation

### Manual Tests
- Test on various network conditions (WiFi, 4G, 3G)
- Test with different SIP servers
- Test battery drain over extended period

---

*Status: COMPLETE | Type: DDD | Generated: 2026-03-07*
*All 9 voip-calling tasks complete*
