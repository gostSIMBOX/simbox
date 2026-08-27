# ADR-007: Hardware Abstraction Layer Pattern

**Status**: Accepted  
**Date**: 2026-03-04  
**Type**: Architectural Decision  
**Source**: `/legacy` reverse engineering

## Context

The system must support multiple types of hardware devices:
- SMB128 SIM-banks (128 slots)
- SMB32 SIM-banks (32 slots)
- GoIP GSM gateways (8-32 SIM slots)
- Future hardware types

Each hardware type has:
- Different communication protocols (HTTP, UDP, SMPP)
- Different command structures
- Different status reporting formats
- Different capabilities (power control, USSD, SMS)

We need a design pattern that allows:
- Adding new hardware types without modifying existing code
- Uniform interface for business logic
- Hardware-specific error handling
- Testable abstraction

### Requirements

- Support multiple hardware vendors
- Uniform API for operations (status, power, USSD)
- Hardware-specific protocol handling
- Easy to add new device types
- Testable without physical hardware

### Constraints

- Legacy system had tightly coupled hardware code
- Physical hardware not always available for testing
- Protocol documentation varies by vendor
- Some protocols are proprietary

## Decision

**Use Hardware Abstraction Layer (HAL) pattern with adapter interfaces.**

### Implementation

```go
// internal/hardware/interface.go

// Device represents a generic hardware device
type Device interface {
    // GetStatus returns current device status
    GetStatus(ctx context.Context) (*DeviceStatus, error)
    
    // GetCapabilities returns supported operations
    GetCapabilities() *DeviceCapabilities
    
    // Health check
    IsHealthy() bool
}

// PowerControllable devices support power management
type PowerControllable interface {
    SetPower(ctx context.Context, slotID int, power bool) error
}

// USSDCapable devices support USSD commands
type USSDCapable interface {
    SendUSSD(ctx context.Context, slotID int, command string) (*USSDResponse, error)
}

// SMSCapable devices support SMS operations
type SMSCapable interface {
    SendSMS(ctx context.Context, slotID int, number string, message string) (string, error)
}
```

### Concrete Implementations

**SMB128 Adapter**:
```go
type SMB128Device struct {
    baseURL string
    client  *http.Client
    config  *SMB128Config
}

func (d *SMB128Device) GetStatus(ctx context.Context) (*DeviceStatus, error) {
    // HTTP GET /status
    // Parse SMB128-specific XML response
    // Convert to common DeviceStatus
}

func (d *SMB128Device) SetPower(ctx context.Context, slotID int, power bool) error {
    // HTTP POST /slot/power
    // SMB128-specific request format
}

// Implements: Device, PowerControllable, USSDCapable
```

**GoIP Adapter**:
```go
type GoIPDevice struct {
    baseURL string
    client  *http.Client
    config  *GoIPConfig
}

func (d *GoIPDevice) GetStatus(ctx context.Context) (*DeviceStatus, error) {
    // HTTP GET /status
    // Parse GoIP-specific JSON response
    // Convert to common DeviceStatus
}

func (d *GoIPDevice) SendSMS(ctx context.Context, slotID int, number string, message string) (string, error) {
    // HTTP POST /sms/send
    // GoIP-specific SMS API
    // Returns message ID
}

// Implements: Device, SMSCapable, USSDCapable
```

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Business Logic Layer                    │
│  (SimBank Manager, Task Scheduler, API Handlers)         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Hardware Abstraction Layer                │   │
│  │                                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │   │
│  │  │   Device    │  │    Power    │  │   USSD   │ │   │
│  │  │  Interface  │  │Controllable │ │ Capable  │ │   │
│  │  └──────┬──────┘  └──────┬──────┘  └────┬─────┘ │   │
│  └─────────┼────────────────┼────────────────┼──────┘   │
│            │                │                │           │
│  ┌─────────┴────────────────┴────────────────┴───────┐  │
│  │              Adapters (Concrete)                   │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │  │
│  │  │  SMB128  │ │  SMB32   │ │   GoIP   │  Future  │  │
│  │  │  Adapter │ │  Adapter │ │  Adapter │ Adapters │  │
│  │  └──────────┘ └──────────┘ └──────────┘          │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │  Physical Hardware Devices     │
         │  SMB128 │ SMB32 │ GoIP │ ...   │
         └────────────────────────────────┘
```

### Device Factory

```go
// DeviceFactory creates appropriate device based on type
type DeviceFactory struct{}

func (f *DeviceFactory) CreateDevice(
    deviceType string,
    config DeviceConfig,
) (Device, error) {
    switch deviceType {
    case "SMB128":
        return &SMB128Device{
            baseURL: config.URL,
            client:  &http.Client{Timeout: config.Timeout},
        }, nil
    case "SMB32":
        return &SMB32Device{
            baseURL: config.URL,
            client:  &http.Client{Timeout: config.Timeout},
        }, nil
    case "GoIP":
        return &GoIPDevice{
            baseURL: config.URL,
            client:  &http.Client{Timeout: config.Timeout},
        }, nil
    default:
        return nil, fmt.Errorf("unsupported device type: %s", deviceType)
    }
}
```

### Capability Checking

```go
// Manager checks capabilities before operations
func (m *Manager) SendUSSD(simBankID uint, slotID int, command string) (string, error) {
    device, exists := m.devices[simBankID]
    if !exists {
        return "", fmt.Errorf("device %d not found", simBankID)
    }
    
    // Check if device supports USSD
    ussdDevice, ok := device.(USSDCapable)
    if !ok {
        return "", fmt.Errorf("device does not support USSD")
    }
    
    return ussdDevice.SendUSSD(context.Background(), slotID, command)
}
```

## Rationale

**HAL pattern was chosen because:**

1. **Open/Closed Principle**: Open for extension (new devices), closed for modification
2. **Dependency Inversion**: Business logic depends on abstractions, not concrete devices
3. **Testability**: Mock devices for testing without hardware
4. **Vendor Isolation**: Protocol changes only affect specific adapter
5. **Capability Discovery**: Runtime checking of supported operations

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Direct coupling** | Simple, no abstraction layer | Tight coupling, hard to extend | Violates SOLID principles |
| **Plugin architecture** | Dynamic loading, runtime discovery | Complex, over-engineered | Static typing benefits outweigh |
| **Code generation** | Type-safe, less boilerplate | Build complexity, tooling | Manual adapters more maintainable |
| **Unified protocol** | Single implementation | Requires hardware standardization | Not feasible with mixed vendors |

## Consequences

### Positive

- **Easy extension**: Add new device type by creating new adapter
- **Isolated changes**: Protocol updates only affect one adapter
- **Testable**: Mock implementations for unit tests
- **Type-safe**: Go interfaces provide compile-time checking
- **Capability discovery**: Runtime checking prevents invalid operations

### Negative

- **Boilerplate code**: Each adapter needs similar structure
- **Interface evolution**: Adding methods requires updating all adapters
- **Abstraction overhead**: Slight performance cost
- **Learning curve**: Team must understand pattern

### Mitigation Strategies

1. **Base classes**: Provide partial implementations for common functionality
2. **Interface segregation**: Small, focused interfaces (not god interface)
3. **Code templates**: Generate boilerplate for new adapters
4. **Documentation**: Clear examples for implementing adapters

## Testing Strategy

### Mock Device for Testing

```go
type MockDevice struct {
    mock.Mock
}

func (m *MockDevice) GetStatus(ctx context.Context) (*DeviceStatus, error) {
    args := m.Called(ctx)
    return args.Get(0).(*DeviceStatus), args.Error(1)
}

func (m *MockDevice) GetCapabilities() *DeviceCapabilities {
    args := m.Called()
    return args.Get(0).(*DeviceCapabilities)
}

// Test using mock
func TestManagerSendUSSD(t *testing.T) {
    mockDevice := new(MockDevice)
    mockDevice.On("SendUSSD", mock.Anything, 1, "*100#").
        Return("Balance: $10.50", nil)
    
    manager := NewManager()
    manager.devices[1] = mockDevice
    
    response, err := manager.SendUSSD(1, 1, "*100#")
    assert.NoError(t, err)
    assert.Equal(t, "Balance: $10.50", response)
}
```

## Compliance

**Compliant Flows**:
- `flows/sdd-simbank-management/02-specifications.md` - Device management
- `flows/sdd-goip-integration/01-specifications.md` - GoIP integration

**Legacy Reference**:
- `legacy/www/smb_scheduler/` - Original SMB adapter logic
- `legacy/www/goip/` - Original GoIP adapter logic

## Future Considerations

### Planned Extensions

1. **WebSocket Devices**: Real-time status updates
2. **MQTT Integration**: IoT-style device communication
3. **gRPC Protocol**: Type-safe RPC for new devices
4. **Auto-discovery**: Network scanning for device detection

### Interface Evolution

Process for adding interface methods:
1. Add optional interface (e.g., `PowerControllableV2`)
2. Implement in new adapters
3. Deprecate old method
4. Remove after migration period

---

*Generated by /legacy reverse engineering - ADR for hardware abstraction*
