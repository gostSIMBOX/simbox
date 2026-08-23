# ADR-005: Native Video Component Architecture

## Status

DRAFT

## Date

2026-03-04

## Authors

- react-native-sip2 maintainers

## Tags

architecture, video, native-components, ui, react-native

## Context

The library needs to display video streams for video calls:
- Local camera preview (self-view)
- Remote participant video

Video rendering requires direct access to native media surfaces for performance.

### Requirements

- Display local camera preview
- Display remote video streams
- Low latency rendering
- Support iOS and Android
- React Native integration
- Minimal JavaScript overhead

### Options Considered

1. **JavaScript Video Rendering**
   - Render video frames in JS
   - Use React Native Image or View
   - Transfer frames from native

2. **Native Component Wrapper (Chosen)**
   - Native UI components (UIView/SurfaceView)
   - Thin JavaScript wrapper
   - Direct native rendering

3. **WebRTC View Component**
   - Use WebRTC library view
   - Wrap in React Native component
   - Additional dependency

## Decision

**Chosen: Native Component Wrapper Pattern**

Create minimal JavaScript wrappers around native video components using `requireNativeComponent`:

```javascript
// PreviewVideoView.js
import { requireNativeComponent } from 'react-native';
import PropTypes from 'prop-types';

const PreviewVideoView = {
  name: 'PjSipPreviewVideoView',
  propTypes: {
    deviceId: PropTypes.number.isRequired,
    objectFit: PropTypes.oneOf(['contain', 'cover'])
  },
};

export default requireNativeComponent('PjSipPreviewVideoView', null);
```

```javascript
// RemoteVideoView.js
import { requireNativeComponent } from 'react-native';
import PropTypes from 'prop-types';

const RemoteVideoView = {
  name: 'PjSipRemoteVideoView',
  propTypes: {
    windowId: PropTypes.string.isRequired,
    objectFit: PropTypes.oneOf(['contain', 'cover'])
  },
};

export default requireNativeComponent('PjSipRemoteVideoView', null);
```

### Usage

```javascript
import { PreviewVideoView, RemoteVideoView } from 'react-native-sip2';

<View style={{ flex: 1 }}>
  {/* Remote video (full screen) */}
  <RemoteVideoView 
    windowId={call.getMedia().windowId}
    objectFit="cover"
    style={{ flex: 1 }}
  />
  
  {/* Local preview (picture-in-picture) */}
  <PreviewVideoView
    deviceId={cameraDeviceId}
    objectFit="contain"
    style={{ position: 'absolute', top: 20, right: 20, width: 120, height: 160 }}
  />
</View>
```

## Rationale

### Why Native Components

1. **Performance**: Direct native rendering, no JavaScript overhead
2. **Zero Copy**: Video frames rendered directly to native surface
3. **Platform Optimization**: Uses platform-specific video rendering APIs
4. **Minimal JS**: Only 10 lines of JavaScript per component
5. **React Native Integration**: Works like any React Native component

### Why Not JavaScript Rendering

**JavaScript Approach:**
```javascript
// ❌ Terrible performance
class VideoView extends Component {
  componentDidMount() {
    // Request frames from native
    this.frameInterval = setInterval(() => {
      NativeModules.VideoModule.getNextFrame((frame) => {
        // Render frame to Image component
        this.setState({ frame }); // 60 FPS = disaster!
      });
    }, 16); // 60 FPS
  }
}
```

**Problems:**
- ❌ Bridge overhead for every frame (60 FPS = 60 messages/sec)
- ❌ Memory copies (native → JS → native)
- ❌ JavaScript thread contention
- ❌ Dropped frames, stuttering video
- ❌ Battery drain

### Why Not WebRTC View

- ✅ Good performance
- ❌ Additional dependency (~5MB)
- ❌ Different API than PjSIP
- ❌ Codec compatibility issues
- ❌ Overkill for PjSIP integration

## Consequences

### Positive

- ✅ Optimal performance (native rendering)
- ✅ Zero JavaScript overhead
- ✅ Direct platform API access
- ✅ Minimal code (10 LOC each)
- ✅ Simple API (2 props each)
- ✅ Works with React Native layout system

### Negative

- ⚠️ **No JavaScript Control**: Cannot manipulate video frames in JS
- ⚠️ **Platform-Specific**: Native implementation required for iOS and Android
- ⚠️ **Limited Props**: Only `deviceId`/`windowId` and `objectFit`
- ⚠️ **No Customization**: Cannot add JavaScript overlays/effects
- ⚠️ **Testing**: Cannot unit test in JavaScript (requires native)

### Technical Implications

1. **Props Interface**: Only two props supported
   - `deviceId` (number): Local camera identifier
   - `windowId` (string): Remote video window identifier
   - `objectFit` ('contain' | 'cover'): Video scaling mode

2. **Native Implementation Required**:
   
   **iOS** (`RTCPjSip/PjSipPreviewVideoView.m`):
   ```objective-c
   @implementation PjSipPreviewVideoView
   - (instancetype)initWithFrame:(CGRect)frame {
     self = [super initWithFrame:frame];
     if (self) {
       // Create PJSIP video preview
       _videoPreview = pjsua_vid_win_create(...);
     }
     return self;
   }
   
   - (void)setDeviceId:(NSNumber *)deviceId {
     // Update video capture device
     pjsua_vid_dev_set_param([deviceId intValue], ...);
   }
   @end
   ```
   
   **Android** (`PjSipPreviewVideoView.java`):
   ```java
   public class PjSipPreviewVideoView extends SurfaceView {
     public PjSipPreviewVideoView(Context context) {
       super(context);
       // Initialize PJSIP video
       pjsua_vid_win_create(...);
     }
     
     public void setDeviceId(int deviceId) {
       // Update video capture device
       pjsua_vid_dev_set_param(deviceId, ...);
     }
   }
   ```

3. **No JavaScript Logic**: Components are pure pass-through
   - No state management
   - No event handlers
   - No lifecycle methods
   - No business logic

## Compliance

### Component Specification

**PreviewVideoView**:
- **Purpose**: Display local camera preview
- **Props**:
  - `deviceId` (number, required): Camera device identifier
  - `objectFit` ('contain' | 'cover', optional): Video scaling
- **Native Component**: `PjSipPreviewVideoView`
- **JavaScript Logic**: None

**RemoteVideoView**:
- **Purpose**: Display remote participant video
- **Props**:
  - `windowId` (string, required): Remote video window ID from call media
  - `objectFit` ('contain' | 'cover', optional): Video scaling
- **Native Component**: `PjSipRemoteVideoView`
- **JavaScript Logic**: None

### Usage Pattern

```javascript
import { PreviewVideoView, RemoteVideoView } from 'react-native-sip2';

// In call screen component
render() {
  return (
    <View style={styles.container}>
      {/* Remote video */}
      <RemoteVideoView
        windowId={this.state.call.getMedia().remoteWindowId}
        objectFit="cover"
        style={styles.remoteVideo}
      />
      
      {/* Local preview */}
      <PreviewVideoView
        deviceId={this.state.cameraDeviceId}
        objectFit="contain"
        style={styles.localPreview}
      />
    </View>
  );
}
```

## Related Decisions

- ADR-001: PjSIP Native Integration
- ADR-002: EventEmitter Pattern for State Management

## Migration Path

### If Adding JavaScript Processing

```javascript
// Hybrid approach - native rendering + JS processing
class ProcessedVideoView extends Component {
  componentDidMount() {
    // Subscribe to video frame events
    NativeModules.VideoModule.onFrame((frame) => {
      // Process frame in JS (filter, overlay, etc.)
      const processed = this.applyFilter(frame);
      NativeModules.VideoModule.setFrame(processed);
    });
  }
  
  render() {
    return <RemoteVideoView {...this.props} />;
  }
}
```

**Warning**: This approach has significant performance overhead and should only be used for non-real-time processing.

## References

- [React Native Native Components](https://reactnative.dev/docs/native-components-ios)
- [requireNativeComponent](https://reactnative.dev/docs/0.72/requirenativecomponent)
- [PjSIP Video API](https://www.pjsip.org/docs/latest/video.htm)

## Notes

**Legacy Analysis Discovery** (2026-03-04):

From code analysis:

**PreviewVideoView.js** (10 lines):
```javascript
import {DeviceEventEmitter, NativeModules, requireNativeComponent} from 'react-native';
import PropTypes from 'prop-types';

const PreviewVideoView = {
  name: 'PjSipPreviewVideoView',
  propTypes: {
    deviceId: PropTypes.number.isRequired,
    objectFit: PropTypes.oneOf(['contain', 'cover'])
  },
};

const View = requireNativeComponent('PjSipPreviewVideoView', null);
export default View;
```

**RemoteVideoView.js** (10 lines):
```javascript
import {DeviceEventEmitter, NativeModules, requireNativeComponent} from 'react-native';
import PropTypes from 'prop-types';

const RemoteVideoView = {
  name: 'PjSipRemoteVideoView',
  propTypes: {
    windowId: PropTypes.string.isRequired,
    objectFit: PropTypes.oneOf(['contain', 'cover'])
  },
};

const View = requireNativeComponent('PjSipRemoteVideoView', null);
export default View;
```

**Key Observations**:
1. Both components are identical in structure (10 LOC each)
2. Zero JavaScript business logic
3. Only PropTypes validation
4. Pure native component wrappers
5. No event handlers
6. No state management
7. Unused imports (`DeviceEventEmitter`, `NativeModules` imported but not used)

**Identified Issues**:
1. Unused imports should be removed
2. No TypeScript types (only PropTypes)
3. No documentation for native implementation requirements
4. No example usage in code comments

**Recommendation**: These components are too simple to warrant separate VDD flow. Document in main SDD instead.

---

*This ADR was generated by /legacy analysis of existing codebase*
