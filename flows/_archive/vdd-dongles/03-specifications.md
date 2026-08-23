# Specifications: Dongle Configuration UI

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-11
> **Requirements**: From sdd-dongle-* flows
> **Visual**: [02-visual.md](02-visual.md)

---

## Overview

Спецификация системы обнаружения, конфигурации и мониторинга донглов (адаптеров) для GOSTsimbox Android Gateway.

Система автоматически определяет:
1. Тип интерфейса (USB-C with DAC, USB-C Accessory, TRRS)
2. Тип схемы донгла (по сопротивлению)
3. Предлагает конфигурацию и тестирование

**4 типа схем:**
- Differential (4R+1C) — дифференциальный выход
- Mono Loopback — монофонический loopback
- Stereo Loopback — стерео loopback
- Earphone-to-Mic — акустическое сопряжение

---

## Affected Systems

| System | Impact | Notes |
|--------|--------|-------|
| `lib/models/line_info.dart` | Modify | Добавить dongle status |
| `lib/domain/entities/` | Create | Dongle entities |
| `lib/domain/repositories/` | Create | DongleRepository |
| `lib/data/sources/` | Create | Dongle detection sources |
| `lib/presentation/providers/` | Create | DongleProvider |
| `lib/presentation/screens/` | Create | Dongle UI screens |
| `android/` | Modify | Platform channels для USB/TRRS |

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dongle Detection Layer                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  DongleDetector (координация)                            │   │
│  │  - detectInterface()                                     │   │
│  │  - detectDongleType()                                    │   │
│  │  - measureResistance()                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│           │           │           │                              │
│           │           │           │                              │
│    ┌──────┘    ┌──────┘    ┌──────┘                              │
│    ▼           ▼           ▼                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│  │  USB-C   │ │  TRRS    │ │Resistance│                        │
│  │  Source  │ │  Source  │ │  Meter   │                        │
│  └──────────┘ └──────────┘ └──────────┘                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Dongle Type Detection (by resistance):
┌──────────────────────────────────────────────────────────────────┐
│  Measurement    | Diff   | Mono   | Stereo | Ear-Mic            │
│  ---------------+--------+--------+--------+------------         │
│  GND → MIC      | ~10k   | ~1.8k  | ~1.8k  | ~10k               │
│  L → GND        | ~10-20k| ~100k  | ∞      | ∞                  │
│  R → GND        | ~10-20k| ~100k  | ∞      | ∞                  │
│  L → MIC        | ~47k   | ~100k  | ∞      | ∞                  │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
App Start / Dongle Connected
    │
    ▼
Detect Interface Type
    │
    ├─► USB-C with DAC ──► Digital (UAC) ──┐
    ├─► USB-C Accessory ──► Analog (SBU) ──┤
    └─► TRRS ─────────────► Analog ────────┤
    │                                       │
    ▼                                       │
For analog: Measure Resistance              │
    │                                       │
    ├─► GND→MIC ~10k + L→GND ~15k ──► Differential │
    ├─► GND→MIC ~1.8k + L→GND ~100k ──► Mono     │
    ├─► GND→MIC ~1.8k + L→GND ∞   ──► Stereo     │
    └─► GND→MIC ~10k + L→GND ∞    ──► Ear-Mic    │
    │                                       │
    ▼                                       │
Show Dongle Status                          │
    │                                       │
    ▼                                       │
User can: Configure / Test / Monitor ◄─────┘
```

---

## Interfaces

### DongleInterfaceType Enum

```dart
enum DongleInterfaceType {
  /// USB-C с внешним DAC (цифровой)
  usbCWithDac,
  
  /// USB-C Audio Accessory (аналоговый через SBU)
  usbCAudioAccessory,
  
  /// TRRS 3.5mm (аналоговый)
  trrs,
  
  /// Нет донгла
  none,
}
```

### DongleType Enum

```dart
enum DongleType {
  /// Differential (4R+1C)
  differential,
  
  /// Mono Loopback
  monoLoopback,
  
  /// Stereo Loopback
  stereoLoopback,
  
  /// Earphone-to-Mic
  earphoneToMic,
}
```

### DongleStatus Model

```dart
class DongleStatus {
  final bool connected;
  final DongleInterfaceType interfaceType;
  final DongleType? dongleType;
  final int? measuredResistanceMic;
  final int? measuredResistanceLeft;
  final int? measuredResistanceRight;
  final QualityLevel quality;
  
  // Методы для определения типа по сопротивлениям
  static DongleType detectType({
    required int? gndToMic,
    required int? leftToGnd,
    required int? rightToGnd,
  });
}
```

### DongleRepository Interface

```dart
abstract class DongleRepository {
  /// Получить статус донгла
  Future<DongleStatus> getStatus();
  
  /// Определить тип интерфейса
  Future<DongleInterfaceType> detectInterface();
  
  /// Измерить сопротивления
  Future<ResistanceMeasurements> measureResistance();
  
  /// Определить тип донгла
  Future<DongleType?> detectDongleType();
  
  /// Сохранить конфигурацию донгла
  Future<void> saveConfig(DongleConfig config);
  
  /// Загрузить конфигурацию донгла
  Future<DongleConfig?> loadConfig();
  
  /// Тестировать донгл
  Future<TestMethodResult> testDongle(DongleTestType testType);
}
```

---

## Data Models

### ResistanceMeasurements

```dart
class ResistanceMeasurements {
  /// GND → MIC (омы)
  final int? gndToMic;
  
  /// L → GND (омы)
  final int? leftToGnd;
  
  /// R → GND (омы)
  final int? rightToGnd;
  
  /// L → MIC (омы)
  final int? leftToMic;
  
  /// Точность измерений
  final double accuracy;
  
  /// Определить тип донгла
  DongleType? detectType() {
    return DongleTypeDetector.detect(
      gndToMic: gndToMic,
      leftToGnd: leftToGnd,
      rightToGnd: rightToGnd,
      leftToMic: leftToMic,
    );
  }
}
```

### DongleConfig

```dart
class DongleConfig extends Equatable {
  final DongleInterfaceType interfaceType;
  final DongleType? dongleType;
  final bool enableInversion;
  final int? outputVolume;
  final int? sampleRate;
  
  const DongleConfig({
    required this.interfaceType,
    this.dongleType,
    this.enableInversion = true,
    this.outputVolume,
    this.sampleRate,
  });
  
  // copyWith, toJson, fromJson...
}
```

### DongleTestType

```dart
enum DongleTestType {
  /// Loopback test (TX → RX)
  loopback,
  
  /// Tone generator
  toneGenerator,
  
  /// Line echo test
  lineEcho,
  
  /// Call test
  callTest,
}
```

---

## Behavior Specifications

### Happy Path: Dongle Detection

1. **Dongle Connected** → USB/Headset broadcast received
2. **Detect Interface**:
   - USB-C: Check VID:PID, UAC class
   - USB-C Accessory: Check Ra on CC pins
   - TRRS: Check headset jack inserted
3. **For Analog**: Measure resistance (GND→MIC, L→GND, R→GND)
4. **Detect Type**: Match resistance signature
5. **Show Status**: Update UI with detected info
6. **User can**: Configure, Test, or Monitor

### Dongle Type Detection Algorithm

```
IF GND→MIC ~1.8k:
  IF L→GND ~100k:
    → Mono Loopback
  ELSE IF L→GND ∞:
    → Stereo Loopback
ELSE IF GND→MIC ~10k:
  IF L→GND ~15k AND R→GND ~15k:
    → Differential (4R+1C)
  ELSE IF L→GND ∞ AND R→GND ∞:
    → Earphone-to-Mic
ELSE:
  → Unknown (manual selection required)
```

### Edge Cases

| Case | Trigger | Expected Behavior |
|------|---------|-------------------|
| USB-C DAC not recognized | Unknown VID:PID | Show "Unknown DAC", use defaults |
| TRRS partially inserted | Jack detect fluctuates | Show "Check connection" warning |
| Resistance out of range | Custom dongle | Show "Unknown type", allow manual |
| Dongle disconnected during call | USB unplugged | Continue call, show warning |
| Multiple dongles | 2+ USB devices | Use first, notify user |

### Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| Resistance measurement failed | Hardware issue | Show "Cannot measure", suggest manual |
| USB permission denied | User denied | Show "Grant USB permission" dialog |
| TRRS detect failed | No jack detect | Poll periodically, notify on change |
| Test failed | Dongle fault | Show test result, suggestions |

---

## Dependencies

### Requires

- **vdd-voiceline** — Voice line access methods
- **PJSIP audio endpoint** — для test tone generation
- **Android USB Host API** — для USB dongle detection
- **Android AudioManager** — для TRRS detection
- **Platform channels** — для resistance measurement

### Blocks

- **Call routing** — не может начать вызов без донгла
- **Audio path configuration** — зависит от типа донгла

---

## Integration Points

### External Systems

| System | Integration | Purpose |
|--------|-------------|---------|
| Android USB Host API | BroadcastReceiver | Dongle connect/disconnect |
| Android AudioManager | HEADSET_PLUG | TRRS jack detect |
| Android HID | USB HID | Resistance measurement |

### Internal Systems

| System | Integration Point |
|--------|-------------------|
| vdd-voiceline | VoiceLineMethod.dongle |
| PJSIP | Test tone generation |
| GatewayConfig | DongleConfig storage |
| LineInfo | Dongle status |

---

## Platform Channels (Android)

### Dongle Detection

```kotlin
// Platform channel: com.gostsimbox/dongle
interface DonglePlatform {
    // Interface Detection
    fun detectInterface(): DongleInterfaceType
    fun getUsbDeviceInfo(): UsbDeviceInfo?
    
    // Resistance Measurement
    fun measureResistance(): ResistanceMeasurements?
    fun measureGndToMic(): Int?
    fun measureLeftToGnd(): Int?
    fun measureRightToGnd(): Int?
    
    // TRRS Detection
    fun isTrrsJackInserted(): Boolean
    fun getTrrsState(): Int // 0=removed, 1=inserted
}
```

### USB Device Info

```kotlin
data class UsbDeviceInfo(
    val vendorId: Int,
    val productId: Int,
    val productName: String?,
    val manufacturerName: String?,
    val audioClass: Int, // USB_CLASS_AUDIO
    val audioSubclass: Int, // AUDIO_SUBCLASS_AUDIOSTREAMING
)
```

---

## Testing Strategy

### Unit Tests

- [ ] `DongleTypeDetector.detect()` — correct type for each signature
- [ ] `ResistanceMeasurements.detectType()` — matches expected type
- [ ] `DongleRepository.getStatus()` — returns correct status
- [ ] `DongleInterfaceDetector.detect()` — correct interface type

### Integration Tests

- [ ] USB dongle detection works on real hardware
- [ ] TRRS detection works on real hardware
- [ ] Resistance measurement accurate (±10%)
- [ ] Dongle disconnect detected within 1s

### Manual Verification

- [ ] UI shows correct dongle type
- [ ] Configuration saves and applies
- [ ] Test screens show accurate results
- [ ] Monitor updates in real-time during call

---

## Migration / Rollout

### Data Migration

- Добавить `DongleConfig` в существующий `GatewayConfig`
- Default: `enableInversion = true` (для differential)
- Старые настройки `audioOutput` → migrate в `DongleConfig`

### Rollout

1. **Phase 1**: USB-C with DAC detection
2. **Phase 2**: USB-C Accessory detection
3. **Phase 3**: TRRS detection
4. **Phase 4**: Resistance measurement
5. **Phase 5**: Full UI integration

---

## Open Design Questions

- [ ] **Resistance Tolerance**: Какой допуск для matching? (предложение: ±20%)
- [ ] **Measurement Frequency**: Как часто обновлять измерения? (предложение: on-demand only)
- [ ] **USB Permissions**: Запрашивать при старте или on-demand?
- [ ] **TRRS Polling**: Poll или interrupt-based detection?

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /vdd - Dongle Configuration specifications*
