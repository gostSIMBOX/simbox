# 02-Technical Specifications: Video Calling

> **Status**: DRAFT
> **Type**: VDD (Visual-Driven Development)
> **Date**: 2026-03-07
> **Module**: video-calling

---

## Overview

This document specifies the technical implementation of video calling features for the GOSTsimbox Gateway application. Video calling enables face-to-face communication during SIP calls with local preview and remote video display.

---

## Architecture

### Component Hierarchy

```
VideoCallScreen
├── RemoteVideoView (full screen)
├── PreviewVideoView (PiP overlay, 120x160)
├── CallInformationOverlay
│   ├── Duration display
│   └── Caller info
├── VideoQualityIndicator
└── CallControlsBar
    ├── End Call (red, center)
    ├── Mute/Unmute
    ├── Speaker/Earpiece
    ├── Video On/Off
    ├── Hold/Resume
    └── More (menu)
```

### Native Integration

Video rendering uses native platform components for optimal performance:

**Android:**
- `SurfaceView` or `TextureView` for video rendering
- PjSIP video window integration via JNI
- Camera access via Android Camera2 API

**iOS:**
- `UIView` with `AVCaptureVideoPreviewLayer` for local preview
- PjSIP video window for remote video
- Camera access via AVFoundation

---

## Widget Specifications

### RemoteVideoView

**Purpose**: Display full-screen remote participant video

**Props**:
```dart
class RemoteVideoViewProps {
  final String? windowId;        // PjSIP remote video window ID
  final VideoFitMode fitMode;    // 'contain' | 'cover' (default: 'cover')
  final bool mirror;             // Mirror video horizontally (default: false)
}
```

**Behavior**:
- Renders remote video stream from PjSIP
- Fills available space (full screen)
- Handles video stream lifecycle (start/stop)
- Shows placeholder when no video available

**Implementation**:
```dart
class RemoteVideoView extends StatefulWidget {
  final String? windowId;
  final VideoFitMode fitMode;
  final bool mirror;

  const RemoteVideoView({
    Key? key,
    this.windowId,
    this.fitMode = VideoFitMode.cover,
    this.mirror = false,
  }) : super(key: key);

  @override
  State<RemoteVideoView> createState() => _RemoteVideoViewState();
}
```

---

### PreviewVideoView

**Purpose**: Display local camera preview (Picture-in-Picture)

**Props**:
```dart
class PreviewVideoViewProps {
  final int? deviceId;           // Camera device ID (null = default)
  final VideoFitMode fitMode;    // 'contain' | 'cover' (default: 'contain')
  final bool mirror;             // Mirror preview (default: true for front camera)
  final double width;            // PiP width (default: 120)
  final double height;           // PiP height (default: 160)
  final Offset position;         // PiP position (default: top-right)
}
```

**Behavior**:
- Shows local camera feed
- Default size: 120x160dp (4:3 aspect ratio)
- Draggable within screen bounds
- Snaps to corners when released
- Double-tap to toggle size (small/large)

**Implementation**:
```dart
class PreviewVideoView extends StatefulWidget {
  final int? deviceId;
  final VideoFitMode fitMode;
  final bool mirror;
  final double width;
  final double height;
  final Offset position;

  const PreviewVideoView({
    Key? key,
    this.deviceId,
    this.fitMode = VideoFitMode.contain,
    this.mirror = true,
    this.width = 120,
    this.height = 160,
    this.position = const Offset(16, 100),
  }) : super(key: key);

  @override
  State<PreviewVideoView> createState() => _PreviewVideoViewState();
}
```

---

### CallControlsBar

**Purpose**: Display call control buttons during video call

**Props**:
```dart
class CallControlsBarProps {
  final bool isMuted;            // Microphone muted state
  final bool isSpeakerOn;        // Speaker mode active
  final bool isVideoOn;          // Video transmission active
  final bool isOnHold;           // Call on hold
  final VoidCallback onEndCall;  // End call action
  final VoidCallback onToggleMute;  // Toggle mute
  final VoidCallback onToggleSpeaker;  // Toggle speaker
  final VoidCallback onToggleVideo;  // Toggle video
  final VoidCallback onToggleHold;  // Toggle hold
  final VoidCallback onShowMore;  // Show more options
}
```

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  [Mute]  [Speaker]  [Video]  [END]  [Hold]  [More]     │
│   ○        ○         ○       [●]     ○        ○         │
└─────────────────────────────────────────────────────────┘
```

**Button Specifications**:

| Button | Icon (On) | Icon (Off) | Color | Size |
|--------|-----------|------------|-------|------|
| End Call | call_end | - | Red (#F44336) | 64x64dp |
| Mute | mic_off | mic | White/Gray | 48x48dp |
| Speaker | volume_up | volume_off | White/Gray | 48x48dp |
| Video | videocam_off | videocam | White/Gray | 48x48dp |
| Hold | play_arrow | pause | White/Gray | 48x48dp |
| More | more_horiz | - | White | 48x48dp |

**Accessibility**:
- Minimum touch target: 44x44dp (WCAG 2.1)
- Recommended touch target: 48x48dp
- Content descriptions for screen readers
- High contrast mode support

---

### VideoQualityIndicator

**Purpose**: Display current video quality status

**Props**:
```dart
class VideoQualityIndicatorProps {
  final VideoQuality quality;  // Quality level
  final bool showLabel;        // Show text label (default: true)
  final bool showBars;         // Show quality bars (default: true)
}

enum VideoQuality {
  excellent,  // 3 bars, green
  good,       // 2 bars, light green
  fair,       // 1 bar, yellow
  poor,       // warning, red
  unknown     // gray, no signal
}
```

**Visual Design**:
```
Excellent:  [▮▮▮] Green (#10B981)
Good:       [▮▮▯] Light Green (#34D399)
Fair:       [▮▯▯] Yellow (#F59E0B)
Poor:       [▯▯▯] Red (#EF4444) + warning icon
Unknown:    [▯▯▯] Gray (#6B7280)
```

**Quality Calculation**:
```dart
VideoQuality calculateQuality({
  required double packetLoss,    // 0.0 - 1.0
  required int jitter,           // milliseconds
  required int bitrate,          // kbps
}) {
  if (packetLoss < 0.01 && jitter < 30 && bitrate >= 1000) {
    return VideoQuality.excellent;
  } else if (packetLoss < 0.05 && jitter < 60 && bitrate >= 500) {
    return VideoQuality.good;
  } else if (packetLoss < 0.10 && jitter < 100 && bitrate >= 200) {
    return VideoQuality.fair;
  } else {
    return VideoQuality.poor;
  }
}
```

---

### IncomingCallScreen

**Purpose**: Display incoming video call with answer/decline options

**Layout**:
```
┌─────────────────────────────────────────┐
│                                         │
│  [Caller Avatar]                        │
│  (large circular, 120dp)                │
│                                         │
│  John Doe                               │
│  +1 (555) 123-4567                      │
│  "Video Call"                           │
│                                         │
│  [PreviewVideoView]                     │
│  (small PiP, 80x120)                    │
│                                         │
│  ┌─────────────┐ ┌─────────────┐       │
│  │  [Decline]  │ │  [Answer]   │       │
│  │     ○       │ │     ○       │       │
│  │   Red       │ │   Green     │       │
│  └─────────────┘ └─────────────┘       │
│                                         │
└─────────────────────────────────────────┘
```

**Behavior**:
- Full-screen modal overlay
- Shows caller information
- Local preview (small PiP)
- Answer button (green, with video icon)
- Decline button (red, with call_end icon)
- Auto-timeout after 30 seconds (configurable)
- Vibration pattern for incoming call

---

## Camera Management

### Camera Switch

**API**:
```dart
class CameraController {
  /// Get available cameras
  Future<List<CameraDevice>> getAvailableCameras();

  /// Switch to specific camera
  Future<void> switchCamera(int deviceId);

  /// Switch between front/back
  Future<void> toggleCamera();

  /// Get current camera
  CameraDevice getCurrentCamera();
}

class CameraDevice {
  final int id;
  final String name;
  final CameraPosition position;  // front | back
  final List<Resolution> supportedResolutions;
}
```

**Implementation Notes**:
- Cache camera capabilities on initialization
- Handle camera permission gracefully
- Smooth transition during switch (fade effect)
- Maintain video state (on/off) during switch

---

## Video Toggle

**States**:
```dart
enum VideoState {
  enabled,    // Camera on, sending video
  disabled,   // Camera off, black screen
  unavailable // Camera error/not available
}
```

**Behavior**:
- Toggle button changes icon based on state
- When disabled: show placeholder with user icon
- When unavailable: show error message
- Notify remote party of video state change

---

## Accessibility Requirements

### Touch Targets

| Element | Minimum Size | Recommended Size |
|---------|--------------|------------------|
| Primary buttons (End Call) | 44x44dp | 64x64dp |
| Secondary buttons | 44x44dp | 48x48dp |
| PiP video view | 44x44dp (draggable area) | 120x160dp |

### Screen Reader Support

```dart
Semantics(
  label: 'End call',
  hint: 'Double-tap to end the current video call',
  button: true,
  child: IconButton(...),
)
```

**Required Labels**:
- End Call: "End call"
- Mute: "Mute microphone" / "Unmute microphone"
- Speaker: "Enable speaker" / "Disable speaker"
- Video: "Turn video off" / "Turn video on"
- Hold: "Hold call" / "Resume call"
- Camera Switch: "Switch to front camera" / "Switch to back camera"

### Contrast Ratio

- All text: minimum 4.5:1 contrast ratio
- Icons: minimum 3:1 contrast ratio
- Active states: high contrast indicators

---

## Technical Specifications

### Video Codec Support

| Codec | Priority | Min Bitrate | Max Bitrate |
|-------|----------|-------------|-------------|
| H.264 | 1 (default) | 200 kbps | 4000 kbps |
| VP8 | 2 | 200 kbps | 2000 kbps |
| H.263 | 3 (fallback) | 64 kbps | 384 kbps |

### Resolution Support

| Resolution | Aspect Ratio | Frame Rate |
|------------|--------------|------------|
| QCIF (176x144) | 11:9 | 15 FPS |
| CIF (352x288) | 11:9 | 15 FPS |
| VGA (640x480) | 4:3 | 30 FPS |
| HD 720p (1280x720) | 16:9 | 30 FPS |

### Network Adaptation

```dart
class VideoQualityAdapter {
  /// Adjust video quality based on network conditions
  void adaptToNetwork({
    required double packetLoss,
    required int rtt,
    required int availableBandwidth,
  });

  /// Get recommended resolution
  Resolution getRecommendedResolution();

  /// Get recommended bitrate
  int getRecommendedBitrate();
}
```

---

## Error Handling

### Video Errors

| Error Code | Description | User Message | Recovery |
|------------|-------------|--------------|----------|
| VIDEO_001 | Camera permission denied | "Camera access denied. Please enable in settings." | Show settings link |
| VIDEO_002 | Camera unavailable | "Camera is being used by another app." | Retry button |
| VIDEO_003 | Video encoding failed | "Video encoding error. Switching to audio-only." | Auto-fallback |
| VIDEO_004 | Network too slow | "Network too slow for video. Switching to audio." | Auto-fallback |
| VIDEO_005 | Remote video not available | "Remote video not available." | Show placeholder |

### Error Recovery

```dart
class VideoErrorHandler {
  Future<void> handleError(VideoError error) async {
    switch (error.code) {
      case 'VIDEO_001':
        await _requestCameraPermission();
        break;
      case 'VIDEO_002':
        await _waitForCamera();
        break;
      case 'VIDEO_003':
      case 'VIDEO_004':
        await _fallbackToAudioOnly();
        break;
      case 'VIDEO_005':
        _showPlaceholder();
        break;
    }
  }
}
```

---

## Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Video startup time | < 2 seconds | Time from answer to first frame |
| Camera switch time | < 500ms | Time to show new camera feed |
| Video freeze duration | < 100ms | During network adaptation |
| Memory usage | < 50MB | For video rendering |
| CPU usage | < 15% | During video encoding |
| Battery drain | < 10%/hour | During video call |

---

## Testing Requirements

### Unit Tests

- VideoQualityIndicator color calculation
- Camera device selection logic
- Video state transitions
- Error handling scenarios

### Widget Tests

- RemoteVideoView rendering
- PreviewVideoView drag and drop
- CallControlsBar button states
- VideoQualityIndicator visual states

### Integration Tests

- Full video call flow
- Camera switch during call
- Video toggle during call
- Network quality adaptation
- Incoming call handling

---

## Dependencies

### Flutter Packages

```yaml
dependencies:
  camera: ^0.10.5          # Camera access
  permission_handler: ^11.0  # Runtime permissions
```

### Native Dependencies

**Android**:
- PjSIP video library
- Camera2 API
- SurfaceView/TextureView

**iOS**:
- PjSIP video library
- AVFoundation
- AVCaptureVideoPreviewLayer

---

## Open Questions

1. **PiP Persistence**: Should PiP position be saved between calls?
2. **Multi-party Video**: Support for conference calls with multiple videos?
3. **Video Recording**: Allow recording video calls (legal considerations)?
4. **Virtual Backgrounds**: Support for background blur/replacement?

---

*Generated by Layer 2 Verification | Status: DRAFT | Review required*
