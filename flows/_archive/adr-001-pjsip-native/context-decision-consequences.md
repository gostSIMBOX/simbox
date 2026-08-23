# ADR-001: PjSIP Native Integration

## Status

DRAFT

## Date

2026-03-04

## Authors

- react-native-sip2 maintainers
- telefon-one team

## Tags

architecture, native-bridge, pjsip, webrtc, sip

## Context

We need to provide SIP/VoIP functionality for React Native applications. The core challenge is choosing the right approach for SIP protocol implementation.

### Requirements

- Support for iOS and Android platforms
- Audio and video calling capabilities
- CallKit integration (iOS)
- Push notification support
- Reliable connection management
- Low latency communication

### Options Considered

1. **Pure JavaScript SIP Library**
   - Implement SIP protocol entirely in JavaScript
   - Use WebRTC for media handling
   - Example: SIP.js, JsSIP

2. **Native PjSIP Integration**
   - Wrap PjSIP (C library) via React Native bridge
   - Use native platform implementations
   - Example: Vialer-pjsip-iOS, pjsip-android

3. **Hybrid Approach**
   - SIP signaling in JavaScript
   - Native media handling only
   - Custom bridge for media operations

## Decision

**Chosen: Native PjSIP Integration**

We chose to wrap the PjSIP native library (C implementation) via React Native's NativeModules bridge system.

### Rationale

**Advantages of Native PjSIP:**

1. **Maturity**: PjSIP is a well-established, production-tested library with 15+ years of development
2. **Performance**: Native C code provides optimal performance for SIP stack operations
3. **Feature Complete**: Full SIP RFC compliance, supports all major SIP extensions
4. **Platform Integration**: Direct access to CallKit (iOS) and ConnectionService (Android)
5. **Codec Support**: Built-in support for wide range of audio/video codecs
6. **NAT Traversal**: Built-in STUN/TURN support with ICE
7. **Battery Efficiency**: Native implementation is more power-efficient than JS alternatives

**Disadvantages Accepted:**

1. **Build Complexity**: Requires native build configuration (Xcode, Gradle)
2. **Platform-Specific Code**: Separate iOS/Android native modules
3. **Debugging Difficulty**: Cross-platform debugging is more complex
4. **Binary Size**: Native libraries increase app size (~5-10MB)

**Why Not Pure JavaScript:**

1. WebRTC integration complexity on mobile platforms
2. Background execution limitations in React Native
3. CallKit/ConnectionService integration not possible from JS
4. Performance overhead for real-time communication
5. Limited codec support in JavaScript implementations

**Why Not Hybrid:**

1. Increased complexity in synchronization
2. No significant benefits over full native implementation
3. More surface area for bugs

## Consequences

### Positive

- ✅ Full SIP feature parity with native applications
- ✅ CallKit integration works seamlessly
- ✅ Background call handling supported
- ✅ Optimal performance and battery life
- ✅ Wide device compatibility
- ✅ Production-ready stability

### Negative

- ⚠️ More complex setup process for developers
- ⚠️ Requires native development knowledge for debugging
- ⚠️ Larger application binary size
- ⚠️ Platform-specific issues require native debugging
- ⚠️ Dependency on PjSIP release cycle for updates

### Technical Implications

1. **Bridge Architecture**: JavaScript layer is pure orchestration (no business logic)
2. **Data Models**: Immutable wrappers around native data structures
3. **Event System**: Native events bridged to JavaScript via DeviceEventEmitter
4. **Initialization**: Must call `start()` to initialize native module before any operations
5. **Error Handling**: `(successful, data)` callback pattern from native

## Compliance

### Code Patterns

All SIP operations follow this pattern:

```javascript
// JavaScript layer - orchestration only
makeCall(account, destination, settings) {
  return new Promise((resolve, reject) => {
    NativeModules.PjSipModule.makeCall(
      account.getId(),
      destination,
      settings,
      (successful, data) => {
        if (successful) {
          resolve(new Call(data)); // Wrap native data
        } else {
          reject(data);
        }
      }
    );
  });
}
```

### Native Module Interface

**iOS**: `RTCPjSip/PjSipModule.m`
- Implements `RCTBridgeModule` protocol
- Exposes methods via `RCT_EXPORT_METHOD`
- Uses `RCTEventEmitter` for event bridging

**Android**: `android/src/main/java/.../PjSipModule.java`
- Implements `ReactMethod` annotated methods
- Uses `DeviceEventManagerModule` for events
- Runs on dedicated thread pool

## Related Decisions

- ADR-002: EventEmitter Pattern for State Management
- ADR-003: Promise Wrapper Around Native Callbacks
- ADR-004: Immutable Data Models
- ADR-005: Native Video Component Architecture

## References

- [PjSIP Official Site](https://www.pjsip.org/)
- [Vialer-pjsip-iOS](https://github.com/VoIPGRID/Vialer-pjsip-iOS)
- [react-native-sip2-builder](https://github.com/telefon-one/react-native-sip2-builder)
- [React Native Native Modules](https://reactnative.dev/docs/native-modules-intro)
- [SIP RFC 3261](https://tools.ietf.org/html/rfc3261)

## Notes

**Legacy Analysis Discovery** (2026-03-04):

From code analysis:
- All methods in `Endpoint.js` delegate to `NativeModules.PjSipModule`
- JavaScript layer has zero SIP business logic
- Data models (`Account`, `Call`, `Message`) are immutable wrappers
- Event subscription happens in constructor via `DeviceEventEmitter`
- Native module must be initialized via `start()` before any operations

**Example from Endpoint.js**:
```javascript
constructor() {
  super();
  // Subscribe to ALL native events automatically
  DeviceEventEmitter.addListener('pjSipRegistrationChanged', ...);
  DeviceEventEmitter.addListener('pjSipCallReceived', ...);
  // ... 5 more event subscriptions
}
```

---

*This ADR was generated by /legacy analysis of existing codebase*
