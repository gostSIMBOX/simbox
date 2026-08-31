# Specifications: Voice Line Access

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-11
> **Requirements**: [01-requirements.md](01-requirements.md)
> **Visual**: [02-visual.md](02-visual.md)

---

## Overview

Спецификация системы выбора и управления методами доступа к голосовой линии (GSM radio) в GOSTsimbox Android Gateway.

Система автоматически определяет доступные методы доступа к линии и выбирает оптимальный, обеспечивая fallback цепочку от лучшего качества к худшему.

**4 метода доступа:**
1. **TTY Port** — последовательный порт (модель-специфичный)
2. **Telecom API** — стандартный Android API
3. **Enhanced Mode** — системный уровень (Magisk, скрыто из UI)
4. **Dongle** — внешний адаптер (USB-C / TRRS)

---

## Affected Systems

| System | Impact | Notes |
|--------|--------|-------|
| `lib/models/line_info.dart` | Modify | Добавить VoiceLineMethod enum и текущий метод |
| `lib/domain/entities/gateway_config_entity.dart` | Modify | Добавить конфигурацию выбора метода |
| `lib/domain/repositories/` | Create | VoiceLineRepository для управления методами |
| `lib/domain/usecases/` | Create | UseCase для обнаружения и выбора метода |
| `lib/data/repositories/` | Create | Implementation repository |
| `lib/data/sources/` | Create | Local data sources для TTY/Telecom/Dongle |
| `lib/presentation/providers/` | Create | VoiceLineProvider для state management |
| `lib/presentation/screens/` | Create | Экраны UI из visual.md |
| `android/app/src/main/kotlin/` | Modify | Platform channel для TTY/Enhanced mode |

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Voice Line Access Layer                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  VoiceLineManager (координация)                          │   │
│  │  - detectAvailableMethods()                              │   │
│  │  - selectBestMethod()                                    │   │
│  │  - setMethod(method)                                     │   │
│  │  - getMethodStatus()                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│           │           │           │                              │
│           │           │           │                              │
│    ┌──────┘    ┌──────┘    ┌──────┘                              │
│    ▼           ▼           ▼                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │   TTY    │ │ Telecom  │ │ Enhanced │ │  Dongle  │           │
│  │  Source  │ │  Source  │ │  Source  │ │  Source  │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Fallback Chain:
TTY Port → Enhanced Mode → Dongle → Telecom API → Acoustic
```

### Data Flow

```
App Start
    │
    ▼
Detect Available Methods (параллельно)
    │
    ├─► TTY Source ──────► Available? ──┐
    ├─► Enhanced Source ─► Available? ──┤
    ├─► Dongle Source ───► Available? ──┤
    ├─► Telecom Source ──► Available? ──┤
    └─► Acoustic ────────► Always       ┘
    │
    ▼
Select Best Method (по приоритету)
    │
    ▼
Store in VoiceLineState
    │
    ▼
Notify UI (VoiceLineProvider)
    │
    ▼
Update Main Screen
```

---

## Interfaces

### VoiceLineMethod Enum

```dart
enum VoiceLineMethod {
  ttyPort,           // TTY Port (serial)
  enhancedMode,      // Enhanced Mode (system-level)
  dongle,            // Dongle (USB-C/TRRS)
  telecomApi,        // Telecom API (standard Android)
  acoustic,          // Acoustic Coupling (fallback)
}
```

### VoiceLineMethodStatus

```dart
class VoiceLineMethodStatus {
  final VoiceLineMethod method;
  final bool available;
  final QualityLevel quality; // excellent/great/good/fair/poor
  final String? reasonUnavailable;
  final Map<String, dynamic>? details;

  const VoiceLineMethodStatus({
    required this.method,
    required this.available,
    required this.quality,
    this.reasonUnavailable,
    this.details,
  });
}
```

### VoiceLineRepository Interface

```dart
abstract class VoiceLineRepository {
  /// Получить все доступные методы
  Future<List<VoiceLineMethodStatus>> getAvailableMethods();

  /// Получить текущий выбранный метод
  Future<VoiceLineMethod?> getCurrentMethod();

  /// Установить метод вручную
  Future<void> setMethod(VoiceLineMethod method);

  /// Автоматически выбрать лучший метод
  Future<VoiceLineMethod> selectBestMethod();

  /// Проверить доступность конкретного метода
  Future<bool> isMethodAvailable(VoiceLineMethod method);

  /// Получить информацию о методе
  Future<VoiceLineMethodStatus> getMethodStatus(VoiceLineMethod method);

  /// Тестировать метод
  Future<TestMethodResult> testMethod(VoiceLineMethod method);
}
```

### TestMethodResult

```dart
class TestMethodResult {
  final bool success;
  final String? error;
  final Map<String, dynamic> measurements;
  final QualityLevel quality;

  const TestMethodResult({
    required this.success,
    this.error,
    required this.measurements,
    required this.quality,
  });
}
```

---

## Data Models

### VoiceLineConfig (в GatewayConfig)

```dart
class VoiceLineConfig extends Equatable {
  final VoiceLineMethod? selectedMethod;
  final bool autoSelect;
  final String? ttyPortPath;
  final int ttyBaudRate;
  final bool enableInversion;
  final bool enableEchoCancellation;

  const VoiceLineConfig({
    this.selectedMethod,
    this.autoSelect = true,
    this.ttyPortPath,
    this.ttyBaudRate = 115200,
    this.enableInversion = true,
    this.enableEchoCancellation = true,
  });

  // copyWith, props...
}
```

### TtyPortInfo

```dart
class TtyPortInfo {
  final String path;
  final String? name;
  final String? manufacturer;
  final List<int> supportedBaudRates;
  final bool requiresPermissions;

  const TtyPortInfo({
    required this.path,
    this.name,
    this.manufacturer,
    this.supportedBaudRates = const [9600, 19200, 115200],
    this.requiresPermissions = false,
  });
}
```

### DongleStatus (интеграция с vdd-dongles)

```dart
class DongleStatus {
  final bool connected;
  final DongleInterfaceType interfaceType;
  final DongleType? dongleType;
  final int? measuredResistanceMic;
  final int? measuredResistanceLeft;

  enum DongleInterfaceType {
    usbCWithDac,
    usbCAudioAccessory,
    trrs,
    none,
  }

  enum DongleType {
    differential,      // 4R+1C
    monoLoopback,
    stereoLoopback,
    earphoneToMic,
  }
}
```

---

## Behavior Specifications

### Happy Path: Auto-Detection

1. **App Start** → VoiceLineManager.init()
2. **Parallel Detection**:
   - TTY Source сканирует `/dev/tty*`, `/sys/class/tty/*`
   - Enhanced Source проверяет system permissions
   - Dongle Source проверяет USB/Headset state
   - Telecom Source всегда available
3. **Select Best** → по приоритету: TTY > Enhanced > Dongle > Telecom > Acoustic
4. **Store & Notify** → VoiceLineState обновляется, UI обновляется
5. **User sees** → "Current Method: Dongle (USB-C Audio Accessory) ★★★★☆"

### Fallback Logic

| Если метод недоступен | Fallback к |
|----------------------|------------|
| TTY Port | Enhanced Mode |
| Enhanced Mode | Dongle |
| Dongle | Telecom API |
| Telecom API | Acoustic Coupling |

### Edge Cases

| Case | Trigger | Expected Behavior |
|------|---------|-------------------|
| TTY port busy | Port opened by another app | Mark unavailable, fallback |
| Dongle disconnected | USB unplugged during call | Continue with current, mark unavailable for next call |
| Enhanced Mode revoked | System permission revoked | Detect on next check, notify user |
| Multiple dongles | 2+ USB devices | Use first detected, allow manual selection |

### Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| TTY permission denied | No read access to /dev/tty* | Show "Why unavailable", suggest manual config |
| Enhanced Mode install failed | Magisk not rooted | Show alternative methods |
| Dongle detection failed | USB host mode disabled | Show recommendation to enable |
| Test failed | Hardware issue | Show suggestions, retry option |

---

## Dependencies

### Requires

- **vdd-dongles** — Dongle detection и UI integration
- **PJSIP audio endpoint** — для test tone generation
- **Android USB Host API** — для dongle detection
- **Android Telecom API** — для telecom method
- **Platform channels** — для TTY port access

### Blocks

- **Call routing** — не может начать вызов без выбранного метода
- **Audio path configuration** — зависит от выбранного метода

---

## Integration Points

### External Systems

| System | Integration | Purpose |
|--------|-------------|---------|
| Android USB Host API | BroadcastReceiver | Dongle connect/disconnect |
| Android Telecom API | ConnectionService | Telecom method |
| Android File System | File I/O | TTY port access |

### Internal Systems

| System | Integration Point |
|--------|-------------------|
| vdd-dongles | DongleSource.getStatus() |
| PJSIP | Test tone generation |
| GatewayConfig | VoiceLineConfig storage |
| LineInfo | canRecordVoiceToRadio и др. |

---

## Platform Channels (Android)

### TTY Port Access

```kotlin
// Platform channel: com.gostsimbox/voice_line
interface VoiceLinePlatform {
    // TTY Port
    fun scanTtyPorts(): List<TtyPortInfo>
    fun testTtyPort(path: String, baudRate: Int): TtyTestResult
    fun openTtyPort(path: String, baudRate: Int): Boolean
    
    // Enhanced Mode
    fun checkEnhancedModeAvailable(): Boolean
    fun getEnhancedModeStatus(): EnhancedModeStatus
    
    // Dongle (интеграция с vdd-dongles)
    fun getDongleStatus(): DongleStatus
}
```

### TTY Port Paths (device-specific)

```kotlin
val commonTtyPaths = listOf(
    "/dev/ttyUSB0",  // USB serial (most common)
    "/dev/ttyHS0",   // Qualcomm high-speed
    "/dev/ttyGS0",   // GSM serial
    "/dev/ttyMSM0",  // MSM serial
)
```

---

## Testing Strategy

### Unit Tests

- [ ] `VoiceLineManager.selectBestMethod()` — correct priority order
- [ ] `VoiceLineManager.fallbackChain()` — correct fallback sequence
- [ ] `TtySource.scanPorts()` — correct path detection
- [ ] `EnhancedSource.checkAvailable()` — permission detection
- [ ] `DongleSource.getStatus()` — USB state detection

### Integration Tests

- [ ] Auto-detection returns at least one method
- [ ] Fallback works when preferred method unavailable
- [ ] Manual method selection persists
- [ ] Test method returns accurate measurements

### Manual Verification

- [ ] UI shows correct quality indicators
- [ ] "Why unavailable?" shows accurate reasons
- [ ] TTY configuration saves and applies
- [ ] Dongle detection works on real hardware

---

## Migration / Rollout

### Data Migration

- Добавить `VoiceLineConfig` в существующий `GatewayConfig`
- Default: `autoSelect = true`, `selectedMethod = null`
- Старые настройки `enableCallRecording` → migrate в `VoiceLineConfig`

### Rollout

1. **Phase 1**: Telecom API + Acoustic (baseline)
2. **Phase 2**: Dongle integration (vdd-dongles)
3. **Phase 3**: TTY Port support (device database)
4. **Phase 4**: Enhanced Mode (Magisk, скрыто)

---

## Open Design Questions

- [ ] **TTY Database**: Где хранить базу device-specific TTY paths? (assets/network)
- [ ] **Enhanced Mode Naming**: "Enhanced Mode" или "Advanced Audio Access"?
- [ ] **Dongle Priority**: Dongle выше или ниже Enhanced Mode в приоритете?
- [ ] **Test Duration**: Как долго тестировать метод перед результатом?

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /vdd - Voice Line Access specifications*
