# Implementation Plan: Voice Line Access

> **Version**: 1.0
> **Status**: DRAFT
> **Last Updated**: 2026-03-11
> **Specifications**: [03-specifications.md](03-specifications.md)

---

## Summary

План реализации системы выбора и управления методами доступа к голосовой линии.

**Подход:**
1. Начать с domain layer (интерфейсы, модели)
2. Реализовать data layer (источники данных, repository)
3. Добавить presentation layer (providers, UI)
4. Интегрировать с vdd-dongles и существующими компонентами

**Ключевые решения:**
- Domain-driven design (repository pattern)
- State management через ChangeNotifier
- Platform channels для Android TTY/Enhanced
- Интеграция с vdd-dongles через общий интерфейс

---

## Task Breakdown

### Phase 1: Domain Layer (Foundation)

#### Task 1.1: VoiceLineMethod Enum и Models

- **Description**: Базовые модели и enum для методов доступа
- **Files**:
  - `lib/domain/models/voice_line_method.dart` — Create
  - `lib/domain/models/voice_line_method_status.dart` — Create
  - `lib/domain/models/quality_level.dart` — Create
  - `lib/domain/models/test_method_result.dart` — Create
- **Dependencies**: None
- **Verification**: Models compile, enums defined
- **Complexity**: Low

#### Task 1.2: VoiceLineConfig Entity

- **Description**: Конфигурация voice line в GatewayConfig
- **Files**:
  - `lib/domain/entities/voice_line_config.dart` — Create
  - `lib/domain/entities/gateway_config_entity.dart` — Modify (добавить voiceLineConfig)
- **Dependencies**: Task 1.1
- **Verification**: GatewayConfig включает VoiceLineConfig
- **Complexity**: Low

#### Task 1.3: VoiceLineRepository Interface

- **Description**: Repository interface для управления методами
- **Files**:
  - `lib/domain/repositories/voice_line_repository.dart` — Create
- **Dependencies**: Task 1.1, 1.2
- **Verification**: Interface defined с методами из spec
- **Complexity**: Low

#### Task 1.4: Update LineInfo

- **Description**: Добавить поля для voice line capabilities
- **Files**:
  - `lib/models/line_info.dart` — Modify (добавить currentMethod, availableMethods)
- **Dependencies**: Task 1.1
- **Verification**: LineInfo сериализуется с новыми полями
- **Complexity**: Low

---

### Phase 2: Data Layer (Sources & Repository)

#### Task 2.1: TtyPortSource

- **Description**: Источник для TTY портов (сканирование, тест)
- **Files**:
  - `lib/data/sources/voice_line/tty_port_source.dart` — Create
  - `android/app/src/main/kotlin/.../voice_line/TtyPortScanner.kt` — Create
- **Dependencies**: Task 1.1
- **Verification**: Сканит /dev/tty*, возвращает список
- **Complexity**: Medium

#### Task 2.2: EnhancedModeSource

- **Description**: Проверка доступности Enhanced Mode (Magisk)
- **Files**:
  - `lib/data/sources/voice_line/enhanced_mode_source.dart` — Create
  - `android/app/src/main/kotlin/.../voice_line/EnhancedModeChecker.kt` — Create
- **Dependencies**: Task 1.1
- **Verification**: Возвращает true/false для доступности
- **Complexity**: Medium

#### Task 2.3: DongleSource (интеграция с vdd-dongles)

- **Description**: Получение статуса dongle из vdd-dongles
- **Files**:
  - `lib/data/sources/voice_line/dongle_source.dart` — Create
  - `lib/data/sources/dongles/dongle_detector.dart` — Create (shared)
- **Dependencies**: Task 1.1, vdd-dongles status
- **Verification**: Возвращает DongleStatus из spec
- **Complexity**: Medium

#### Task 2.4: TelecomApiSource

- **Description**: Проверка Telecom API (всегда available)
- **Files**:
  - `lib/data/sources/voice_line/telecom_api_source.dart` — Create
- **Dependencies**: Task 1.1
- **Verification**: Всегда возвращает available
- **Complexity**: Low

#### Task 2.5: VoiceLineRepository Implementation

- **Description**: Основная логика detection и fallback
- **Files**:
  - `lib/data/repositories/voice_line_repository_impl.dart` — Create
- **Dependencies**: Task 2.1-2.4
- **Verification**: Correct fallback chain, auto-selection
- **Complexity**: High

#### Task 2.6: Platform Channels (Android)

- **Description**: Platform channel interface для TTY/Enhanced
- **Files**:
  - `lib/platform/voice_line_platform.dart` — Create
  - `android/app/src/main/kotlin/.../voice_line/VoiceLinePlatformChannel.kt` — Create
  - `android/app/src/main/kotlin/.../voice_line/VoiceLineMethod.kt` — Create (enum)
- **Dependencies**: Task 1.1
- **Verification**: Platform calls work
- **Complexity**: High

---

### Phase 3: Presentation Layer (State & UI)

#### Task 3.1: VoiceLineProvider

- **Description**: State management для voice line
- **Files**:
  - `lib/presentation/providers/voice_line_provider.dart` — Create
- **Dependencies**: Task 1.3, 2.5
- **Verification**: Provider обновляется при изменении метода
- **Complexity**: Medium

#### Task 3.2: Voice Line Status Screen

- **Description**: Главный экран (Screen 1 из visual.md)
- **Files**:
  - `lib/presentation/screens/voice_line/voice_line_status_screen.dart` — Create
  - `lib/presentation/widgets/voice_line/method_status_card.dart` — Create
  - `lib/presentation/widgets/voice_line/signal_path_diagram.dart` — Create
- **Dependencies**: Task 3.1
- **Verification**: UI matches visual.md mockups
- **Complexity**: Medium

#### Task 3.3: Select Method Screen

- **Description**: Экран выбора метода (Screen 2 из visual.md)
- **Files**:
  - `lib/presentation/screens/voice_line/select_method_screen.dart` — Create
  - `lib/presentation/widgets/voice_line/method_list_item.dart` — Create
  - `lib/presentation/widgets/voice_line/why_unavailable_dialog.dart` — Create
- **Dependencies**: Task 3.1
- **Verification**: UI matches visual.md, navigation works
- **Complexity**: Medium

#### Task 3.4: TTY Configuration Screen

- **Description**: Настройка TTY порта (Screen 3a из visual.md)
- **Files**:
  - `lib/presentation/screens/voice_line/tty_config_screen.dart` — Create
  - `lib/presentation/widgets/voice_line/port_path_selector.dart` — Create
  - `lib/presentation/widgets/voice_line/tty_test_result_dialog.dart` — Create
- **Dependencies**: Task 3.1, 2.1
- **Verification**: Configuration saves, test works
- **Complexity**: Medium

#### Task 3.5: Enhanced Mode Setup Screen

- **Description**: Настройка Enhanced Mode (Screen 3b из visual.md)
- **Files**:
  - `lib/presentation/screens/voice_line/enhanced_mode_screen.dart` — Create
  - `lib/presentation/widgets/voice_line/enhanced_mode_status.dart` — Create
- **Dependencies**: Task 3.1, 2.2
- **Verification**: UI matches visual.md
- **Complexity**: Low

#### Task 3.6: Test Voice Line Screen

- **Description**: Тестирование метода (Screen 4 из visual.md)
- **Files**:
  - `lib/presentation/screens/voice_line/test_voice_line_screen.dart` — Create
  - `lib/presentation/widgets/voice_line/test_progress.dart` — Create
  - `lib/presentation/widgets/voice_line/test_result_card.dart` — Create
- **Dependencies**: Task 3.1, 2.5
- **Verification**: Test runs, shows results
- **Complexity**: Medium

#### Task 3.7: Voice Line Settings Screen

- **Description**: Расширенные настройки (Screen 5 из visual.md)
- **Files**:
  - `lib/presentation/screens/voice_line/voice_line_settings_screen.dart` — Create
- **Dependencies**: Task 3.1
- **Verification**: Settings save and apply
- **Complexity**: Low

---

### Phase 4: Integration & Polish

#### Task 4.1: Integrate with Main Dashboard

- **Description**: Добавить Voice Line card на главный экран
- **Files**:
  - `lib/presentation/screens/dashboard_screen.dart` — Modify
  - `lib/presentation/widgets/voice_line/voice_line_dashboard_card.dart` — Create
- **Dependencies**: Task 3.2
- **Verification**: Card shows current method status
- **Complexity**: Low

#### Task 4.2: Integrate with GatewayConfig Storage

- **Description**: Сохранение/загрузка VoiceLineConfig
- **Files**:
  - `lib/data/storage/gateway_config_storage.dart` — Modify
- **Dependencies**: Task 1.2, 2.5
- **Verification**: Config persists across restarts
- **Complexity**: Medium

#### Task 4.3: Update Call Routing

- **Description**: Интеграция выбора метода с routing вызовов
- **Files**:
  - `lib/domain/usecases/start_call.dart` — Modify
  - `lib/services/call_service.dart` — Modify
- **Dependencies**: Task 2.5
- **Verification**: Call uses selected method
- **Complexity**: High

#### Task 4.4: Error Handling & Notifications

- **Description**: Обработка ошибок, уведомления пользователя
- **Files**:
  - `lib/presentation/widgets/common/error_banner.dart` — Create (shared)
  - `lib/domain/exceptions/voice_line_exceptions.dart` — Create
- **Dependencies**: Task 2.5
- **Verification**: Errors shown clearly
- **Complexity**: Medium

#### Task 4.5: Documentation & Help

- **Description**: Help screens, tooltips
- **Files**:
  - `lib/presentation/widgets/voice_line/help_tooltip.dart` — Create
  - `assets/help/voice_line_methods.md` — Create
- **Dependencies**: Task 3.2-3.7
- **Verification**: Help accessible from UI
- **Complexity**: Low

---

## Dependency Graph

```
Phase 1: Domain Layer
┌────────────────────────────────────────┐
│  1.1 Models ──┬── 1.2 Config ── 1.4   │
│               │                        │
│               └── 1.3 Repository       │
└────────────────────────────────────────┘
                │
                ▼
Phase 2: Data Layer
┌────────────────────────────────────────┐
│  2.1 TTY      2.2 Enhanced             │
│  2.3 Dongle   2.4 Telecom              │
│       │            │                   │
│       └──── 2.5 Repository_impl ────── │
│                │                       │
│       2.6 Platform Channels            │
└────────────────────────────────────────┘
                │
                ▼
Phase 3: Presentation Layer
┌────────────────────────────────────────┐
│         3.1 VoiceLineProvider          │
│    │         │         │         │     │
│  3.2      3.3      3.4      3.5      3.6
│ Status   Select   TTY    Enhanced  Test
│          │                          │
│          └──────── 3.7 Settings ────┘│
└────────────────────────────────────────┘
                │
                ▼
Phase 4: Integration
┌────────────────────────────────────────┐
│  4.1 Dashboard  4.2 Storage            │
│  4.3 Call Routing  4.4 Errors  4.5 Help│
└────────────────────────────────────────┘
```

---

## File Change Summary

| Directory | Create | Modify | Total |
|-----------|--------|--------|-------|
| `lib/domain/` | 6 | 2 | 8 |
| `lib/data/` | 8 | 2 | 10 |
| `lib/presentation/` | 12 | 3 | 15 |
| `lib/platform/` | 1 | 0 | 1 |
| `android/` | 4 | 0 | 4 |
| **Total** | **31** | **7** | **38** |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| TTY paths device-specific | High | Medium | Device database, manual config option |
| Enhanced Mode detection fails | Medium | High | Fallback to other methods |
| Dongle integration conflicts | Medium | Medium | Clear interface contract with vdd-dongles |
| Platform channel errors | Medium | High | Error handling, graceful degradation |
| Call routing integration complex | High | High | Incremental testing, rollback plan |

---

## Rollback Strategy

Если реализация требует отката:

1. **Domain Layer**: Удалить новые файлы моделей, вернуть LineInfo к оригиналу
2. **Data Layer**: Удалить repository impl, platform channels
3. **Presentation**: Удалить screens, provider
4. **Integration**: Revert изменения в Call Service и Dashboard
5. **Config**: VoiceLineConfig опционален — старая конфигурация работает

**Git strategy**: Каждый phase в отдельном commit для easy revert.

---

## Checkpoints

### После Phase 1 (Domain)
- [ ] Все модели компилируются
- [ ] Repository interface определён
- [ ] LineInfo обновлён

### После Phase 2 (Data)
- [ ] Все sources возвращают данные
- [ ] Fallback логика работает
- [ ] Platform channels вызываются

### После Phase 3 (Presentation)
- [ ] Все экраны из visual.md реализованы
- [ ] Provider обновляет UI
- [ ] Навигация работает

### После Phase 4 (Integration)
- [ ] Dashboard показывает статус
- [ ] Call routing использует метод
- [ ] Конфигурация сохраняется
- [ ] Errors обрабатываются

---

## Open Implementation Questions

- [ ] **TTY Database**: Формат хранения device-specific paths? (JSON в assets)
- [ ] **Test Duration**: Сколько секунд тестировать метод? (предложение: 5s)
- [ ] **Dongle Priority**: Приоритет Dongle vs Enhanced? (предложение: Enhanced выше)

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /vdd - Voice Line Access implementation plan*
