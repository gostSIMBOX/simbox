# Implementation Plan: Dongle Configuration UI

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-11
> **Specifications**: [03-specifications.md](03-specifications.md)

---

## Summary

План реализации системы обнаружения, конфигурации и мониторинга донглов.

**Подход:**
1. Начать с domain layer (модели, интерфейсы)
2. Реализовать data layer (detection sources, repository)
3. Добавить presentation layer (providers, UI screens)
4. Интегрировать с vdd-voiceline и audio path

**Ключевые решения:**
- Domain-driven design (repository pattern)
- State management через ChangeNotifier
- Platform channels для Android USB/TRRS detection
- Resistance measurement через HID interface

---

## Task Breakdown

### Phase 1: Domain Layer (Foundation)

#### Task 1.1: Dongle Enums and Models

- **Description**: Базовые enum и модели для донглов
- **Files**:
  - `lib/domain/models/dongle_interface_type.dart` — Create
  - `lib/domain/models/dongle_type.dart` — Create
  - `lib/domain/models/dongle_status.dart` — Create
  - `lib/domain/models/resistance_measurements.dart` — Create
- **Dependencies**: None
- **Verification**: Models compile, enums defined
- **Complexity**: Low

#### Task 1.2: DongleConfig Entity

- **Description**: Конфигурация донгла
- **Files**:
  - `lib/domain/entities/dongle_config.dart` — Create
- **Dependencies**: Task 1.1
- **Verification**: DongleConfig compiles with copyWith, toJson
- **Complexity**: Low

#### Task 1.3: DongleRepository Interface

- **Description**: Repository interface для управления донглами
- **Files**:
  - `lib/domain/repositories/dongle_repository.dart` — Create
- **Dependencies**: Task 1.1, 1.2
- **Verification**: Interface defined с методами из spec
- **Complexity**: Low

#### Task 1.4: Update LineInfo

- **Description**: Добавить dongle status в LineInfo
- **Files**:
  - `lib/models/line_info.dart` — Modify (добавить dongleStatus)
- **Dependencies**: Task 1.1
- **Verification**: LineInfo сериализуется с новыми полями
- **Complexity**: Low

---

### Phase 2: Data Layer (Detection & Repository)

#### Task 2.1: USB Dongle Source

- **Description**: Обнаружение USB-C донглов
- **Files**:
  - `lib/data/sources/dongle/usb_dongle_source.dart` — Create
  - `android/app/src/main/kotlin/.../dongle/UsbDongleDetector.kt` — Create
- **Dependencies**: Task 1.1
- **Verification**: Detects USB-C with DAC and Accessory
- **Complexity**: Medium

#### Task 2.2: TRRS Dongle Source

- **Description**: Обнаружение TRRS донглов
- **Files**:
  - `lib/data/sources/dongle/trrs_dongle_source.dart` — Create
- **Dependencies**: Task 1.1
- **Verification**: Detects headset jack insertion
- **Complexity**: Low

#### Task 2.3: Resistance Meter Source

- **Description**: Измерение сопротивлений
- **Files**:
  - `lib/data/sources/dongle/resistance_meter.dart` — Create
  - `android/app/src/main/kotlin/.../dongle/ResistanceMeter.kt` — Create
- **Dependencies**: Task 1.1
- **Verification**: Measures GND→MIC, L→GND, R→GND
- **Complexity**: High

#### Task 2.4: DongleType Detector

- **Description**: Алгоритм определения типа по сопротивлению
- **Files**:
  - `lib/data/sources/dongle/dongle_type_detector.dart` — Create
- **Dependencies**: Task 1.1, 2.3
- **Verification**: Correctly identifies all 4 types
- **Complexity**: Medium

#### Task 2.5: DongleRepository Implementation

- **Description**: Основная логика detection и конфигурации
- **Files**:
  - `lib/data/repositories/dongle_repository_impl.dart` — Create
- **Dependencies**: Task 2.1-2.4
- **Verification**: Detection works, config saves
- **Complexity**: High

#### Task 2.6: Platform Channels (Android)

- **Description**: Platform channel interface для USB/TRRS
- **Files**:
  - `lib/platform/dongle_platform.dart` — Create
  - `android/app/src/main/kotlin/.../dongle/DonglePlatformChannel.kt` — Create
- **Dependencies**: Task 1.1
- **Verification**: Platform calls work
- **Complexity**: High

---

### Phase 3: Presentation Layer (State & UI)

#### Task 3.1: DongleProvider

- **Description**: State management для донглов
- **Files**:
  - `lib/presentation/providers/dongle_provider.dart` — Create
- **Dependencies**: Task 1.3, 2.5
- **Verification**: Provider обновляется при изменении статуса
- **Complexity**: Medium

#### Task 3.2: Dongle Status Screen (Screen 1)

- **Description**: Главный экран статуса донгла
- **Files**:
  - `lib/presentation/screens/dongle/dongle_status_screen.dart` — Create
  - `lib/presentation/widgets/dongle/interface_status_card.dart` — Create
  - `lib/presentation/widgets/dongle/dongle_type_card.dart` — Create
  - `lib/presentation/widgets/dongle/signal_level_bars.dart` — Create
- **Dependencies**: Task 3.1
- **Verification**: UI matches visual.md mockups
- **Complexity**: Medium

#### Task 3.3: Detect Dongle Type Screen (Screen 2)

- **Description**: Экран автоопределения типа
- **Files**:
  - `lib/presentation/screens/dongle/detect_type_screen.dart` — Create
  - `lib/presentation/widgets/dongle/resistance_display.dart` — Create
- **Dependencies**: Task 3.1, 2.4
- **Verification**: Shows measurements, detected type
- **Complexity**: Medium

#### Task 3.4: TRRS Config Screen (Screen 3a)

- **Description**: Настройка TRRS донгла
- **Files**:
  - `lib/presentation/screens/dongle/trrs_config_screen.dart` — Create
- **Dependencies**: Task 3.1
- **Verification**: Config saves, inversion toggle works
- **Complexity**: Low

#### Task 3.5: USB Accessory Config Screen (Screen 3b)

- **Description**: Настройка USB-C Accessory донгла
- **Files**:
  - `lib/presentation/screens/dongle/usb_accessory_config_screen.dart` — Create
- **Dependencies**: Task 3.1
- **Verification**: Config saves, volume control works
- **Complexity**: Low

#### Task 3.6: USB DAC Config Screen (Screen 3c)

- **Description**: Настройка USB-C с DAC
- **Files**:
  - `lib/presentation/screens/dongle/usb_dac_config_screen.dart` — Create
- **Dependencies**: Task 3.1
- **Verification**: Config saves, DAC info displays
- **Complexity**: Low

#### Task 3.7: Test Dongle Screens (Screen 4, 4a-4d)

- **Description**: Экраны тестирования
- **Files**:
  - `lib/presentation/screens/dongle/test_menu_screen.dart` — Create
  - `lib/presentation/screens/dongle/loopback_test_screen.dart` — Create
  - `lib/presentation/screens/dongle/tone_generator_screen.dart` — Create
  - `lib/presentation/screens/dongle/line_echo_test_screen.dart` — Create
  - `lib/presentation/screens/dongle/call_test_screen.dart` — Create
- **Dependencies**: Task 3.1
- **Verification**: Tests run, results display
- **Complexity**: Medium

#### Task 3.8: Dongle Monitor Screen (Screen 5)

- **Description**: Мониторинг во время звонка
- **Files**:
  - `lib/presentation/screens/dongle/dongle_monitor_screen.dart` — Create
  - `lib/presentation/widgets/dongle/call_stats_card.dart` — Create
- **Dependencies**: Task 3.1
- **Verification**: Real-time updates during call
- **Complexity**: Medium

#### Task 3.9: Schematic Viewer (Screen 6)

- **Description**: Просмотр схемы донгла
- **Files**:
  - `lib/presentation/screens/dongle/schematic_viewer_screen.dart` — Create
  - `lib/presentation/widgets/dongle/circuit_diagram.dart` — Create
- **Dependencies**: Task 3.1
- **Verification**: Diagram displays correctly
- **Complexity**: Low

---

### Phase 4: Integration & Polish

#### Task 4.1: Integrate with vdd-voiceline

- **Description**: Интеграция с VoiceLineMethod.dongle
- **Files**:
  - `lib/data/sources/voice_line/dongle_source.dart` — Modify (integrate)
- **Dependencies**: Task 2.5, vdd-voiceline
- **Verification**: Dongle appears in voice line methods
- **Complexity**: Medium

#### Task 4.2: Integrate with Dashboard

- **Description**: Dongle card на главном экране
- **Files**:
  - `lib/presentation/screens/dashboard_screen.dart` — Modify
  - `lib/presentation/widgets/dongle/dongle_dashboard_card.dart` — Create
- **Dependencies**: Task 3.2
- **Verification**: Card shows dongle status
- **Complexity**: Low

#### Task 4.3: Integrate with Call Routing

- **Description**: Использование донгла при звонках
- **Files**:
  - `lib/domain/usecases/start_call.dart` — Modify
  - `lib/services/call_service.dart` — Modify
- **Dependencies**: Task 2.5
- **Verification**: Call uses dongle audio path
- **Complexity**: High

#### Task 4.4: Error Handling & Notifications

- **Description**: Обработка ошибок, уведомления
- **Files**:
  - `lib/domain/exceptions/dongle_exceptions.dart` — Create
  - `lib/presentation/widgets/dongle/dongle_error_banner.dart` — Create
- **Dependencies**: Task 2.5
- **Verification**: Errors shown clearly
- **Complexity**: Medium

#### Task 4.5: Help Documentation

- **Description**: Help screens, tooltips
- **Files**:
  - `lib/presentation/widgets/dongle/help_tooltip.dart` — Create
  - `assets/help/dongle_types.md` — Create
- **Dependencies**: Task 3.2-3.9
- **Verification**: Help accessible from UI
- **Complexity**: Low

---

## Dependency Graph

```
Phase 1: Domain Layer
┌────────────────────────────────────────┐
│  1.1 Models ──┬── 1.2 Config          │
│               │                        │
│               └── 1.3 Repository ── 1.4 LineInfo
└────────────────────────────────────────┘
                │
                ▼
Phase 2: Data Layer
┌────────────────────────────────────────┐
│  2.1 USB      2.2 TRRS                 │
│  2.3 Resistance Meter                  │
│       │            │                   │
│       └──── 2.4 Type Detector ──────── │
│                │                       │
│       2.5 Repository_impl              │
│                │                       │
│       2.6 Platform Channels            │
└────────────────────────────────────────┘
                │
                ▼
Phase 3: Presentation Layer
┌────────────────────────────────────────┐
│         3.1 DongleProvider             │
│    │         │         │         │     │
│  3.2      3.3      3.4-3.6   3.7     3.8
│ Status   Detect   Config    Test   Monitor
│          │                          │
│          └──────── 3.9 Schematic ────┘
└────────────────────────────────────────┘
                │
                ▼
Phase 4: Integration
┌────────────────────────────────────────┐
│  4.1 vdd-voiceline  4.2 Dashboard     │
│  4.3 Call Routing   4.4 Errors  4.5 Help
└────────────────────────────────────────┘
```

---

## File Change Summary

| Directory | Create | Modify | Total |
|-----------|--------|--------|-------|
| `lib/domain/` | 6 | 1 | 7 |
| `lib/data/` | 8 | 1 | 9 |
| `lib/presentation/` | 15 | 2 | 17 |
| `lib/platform/` | 1 | 0 | 1 |
| `android/` | 3 | 0 | 3 |
| **Total** | **33** | **4** | **37** |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| USB detection fails on some devices | Medium | High | Fallback to manual selection |
| Resistance measurement inaccurate | High | Medium | Calibration, tolerance ±20% |
| TRRS jack detect unreliable | Medium | Medium | Poll periodically, debounce |
| Platform channel complexity | High | High | Incremental testing |
| Call routing integration complex | High | High | Test with mock audio path first |

---

## Rollback Strategy

Если реализация требует отката:

1. **Domain Layer**: Удалить новые файлы моделей, вернуть LineInfo к оригиналу
2. **Data Layer**: Удалить repository impl, platform channels
3. **Presentation**: Удалить screens, provider
4. **Integration**: Revert изменения в Call Service и Dashboard
5. **Config**: DongleConfig опционален — старая конфигурация работает

**Git strategy**: Каждый phase в отдельном commit для easy revert.

---

## Checkpoints

### После Phase 1 (Domain)
- [ ] Все модели компилируются
- [ ] Repository interface определён
- [ ] LineInfo обновлён

### После Phase 2 (Data)
- [ ] USB detection работает на устройстве
- [ ] TRRS detection работает
- [ ] Resistance measurement accurate
- [ ] Type detector correct

### После Phase 3 (Presentation)
- [ ] Все экраны из visual.md реализованы
- [ ] Provider обновляет UI
- [ ] Навигация работает

### После Phase 4 (Integration)
- [ ] Dongle в voice line methods
- [ ] Dashboard показывает статус
- [ ] Call routing использует донгл
- [ ] Errors обрабатываются

---

## Open Implementation Questions

- [ ] **USB Permissions**: Запрашивать при старте или при первом использовании?
- [ ] **Resistance Tolerance**: Какой допуск для matching? (предложение: ±20%)
- [ ] **TRRS Polling**: Как часто проверять jack state? (предложение: 1s)
- [ ] **DAC Info**: Какие данные показывать для USB DAC?

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /vdd - Dongle Configuration implementation plan*
