# SimBank Management - Requirements

> Spec-Driven Development: Управление SIM-банками

**Status**: DRAFT  
**Type**: SDD (Internal Service)  
**Generated**: 2026-03-04 via /legacy analysis  
**Source**: `internal/simbank/manager.go`, `internal/simbank/client.go`

---

## 1. Overview

### 1.1 Purpose

Система управления SIM-банками GOSTsimbox SimHub, обеспечивающая мониторинг состояния слотов, управление питанием и отправку USSD команд.

### 1.2 Scope

- Менеджер SIM-банков с periodic polling
- HTTP клиенты для общения с устройствами
- Database-backed состояние слотов
- Graceful shutdown

### 1.3 Definitions

| Term | Definition |
|------|------------|
| SIM-банк | Устройство SMB128/SMB32 для управления SIM-картами |
| Polling | Периодический опрос статуса банков (30s interval) |
| Slot | Слот для SIM-карты в SIM-банке |
| USSD | Unstructured Supplementary Service Data |

---

## 2. Functional Requirements

### 2.1 Manager Lifecycle

**REQ-MGR-001**: Система должна создавать менеджер SIM-банков

- **Priority**: MUST
- **Source**: `simbank.NewManager(cfg)`
- **Acceptance**:
  - Принимает SimBankConfig
  - Создает context для отмены
  - Инициализирует clients map
  - Возвращает *Manager

**REQ-MGR-002**: Система должна запускать менеджер

- **Priority**: MUST
- **Source**: `manager.Start()`
- **Acceptance**:
  - Загружает SIM-банки из БД (loadSimBanks)
  - Запускает monitorLoop в горутине
  - Возвращает error при неудаче

**REQ-MGR-003**: Система должна останавливать менеджер

- **Priority**: MUST
- **Source**: `manager.Stop()`
- **Acceptance**:
  - Вызывает context cancel
  - Останавливает polling loop
  - Логирует остановку

### 2.2 SIM-Bank Loading

**REQ-LOAD-001**: Система должна загружать SIM-банки из базы данных

- **Priority**: MUST
- **Source**: `loadSimBanks()`
- **Acceptance**:
  - Query: `WHERE is_active = true`
  - Создает Client для каждого банка
  - Сохраняет в clients map (ID → Client)
  - RWMutex lock для защиты map

**REQ-LOAD-002**: Система должна логировать загруженные банки

- **Priority**: SHOULD
- **Acceptance**:
  - `logger.Infof("Loaded SimBank: %s (ID: %d)", Name, ID)`

### 2.3 Polling & Monitoring

**REQ-POLL-001**: Система должна периодически опрашивать SIM-банки

- **Priority**: MUST
- **Source**: `monitorLoop()`
- **Acceptance**:
  - Interval: config.PollingInterval (default: 30s)
  - Использует time.Ticker
  - Работает в бесконечном цикле
  - Останавливается по context.Done()

**REQ-POLL-002**: Система должна обновлять все банки параллельно

- **Priority**: MUST
- **Source**: `updateAllSimBanks()`
- **Acceptance**:
  - Копирует clients map (RLock)
  - Создает goroutine per client
  - Использует WaitGroup для sync
  - Вызывает updateSimBank для каждого

**REQ-POLL-003**: Система должна обновлять статус каждого банка

- **Priority**: MUST
- **Source**: `updateSimBank()`
- **Acceptance**:
  - Вызывает client.GetStatus()
  - При error: логирует, записывает system event
  - Вызывает updateSlots(slots)
  - Логирует debug: "Updated SimBank %d: %d slots"

**REQ-POLL-004**: Система должна обновлять слоты в базе данных

- **Priority**: MUST
- **Source**: `updateSlots()`
- **Acceptance**:
  - Для каждого слота: Find or Create
  - Обновляет поля: IMSI, ICCID, Operator, Status, Power, Signal
  - Save или Create в БД
  - Возвращает error при неудаче

### 2.4 Power Control

**REQ-PWR-001**: Система должна управлять питанием слота

- **Priority**: MUST
- **Source**: `SetPower(simBankID, slotID, power)`
- **Acceptance**:
  - Находит client по simBankID (RLock)
  - Вызывает client.SetPower(slotID, power)
  - Обновляет power в БД
  - Логирует: `logger.Infof("Set power for SimBank %d, Slot %d: %v")`
  - Возвращает error

**REQ-PWR-002**: Система должна обрабатывать отсутствующий банк

- **Priority**: MUST
- **Acceptance**:
  - Возвращает error: "simbank %d not found"

### 2.5 USSD Commands

**REQ-USSD-001**: Система должна отправлять USSD команды

- **Priority**: MUST
- **Source**: `SendUSSD(simBankID, slotID, command)`
- **Acceptance**:
  - Находит client по simBankID (RLock)
  - Вызывает client.SendUSSD(slotID, command)
  - Логирует response
  - Возвращает (response string, error)

**REQ-USSD-002**: Система должна обрабатывать отсутствующий банк

- **Priority**: MUST
- **Acceptance**:
  - Возвращает error: "simbank %d not found", ""

### 2.6 Status Queries

**REQ-STATUS-001**: Система должна возвращать статус банка

- **Priority**: MUST
- **Source**: `GetSimBankStatus(simBankID)`
- **Acceptance**:
  - Находит client по simBankID (RLock)
  - Вызывает client.GetStatus()
  - Возвращает (*StatusResponse, error)

### 2.7 Client Operations

**REQ-CLIENT-001**: Клиент должен получать статус банка

- **Priority**: MUST
- **Source**: `client.GetStatus()`
- **Acceptance**:
  - GET {baseURL}/status
  - Парсит StatusResponse (Status, Slots[])
  - Возвращает error при != 200 OK

**REQ-CLIENT-002**: Клиент должен управлять питанием

- **Priority**: MUST
- **Source**: `client.SetPower(slotID, power)`
- **Acceptance**:
  - POST {baseURL}/slot/power
  - Body: {"slot_id": N, "power": bool}
  - Возвращает error при != 200 OK

**REQ-CLIENT-003**: Клиент должен отправлять USSD

- **Priority**: MUST
- **Source**: `client.SendUSSD(slotID, command)`
- **Acceptance**:
  - POST {baseURL}/ussd
  - Body: {"slot_id": N, "command": "string"}
  - Парсит USSDResponse (Response, Error)
  - Возвращает error при != 200 OK

**REQ-CLIENT-004**: Клиент должен проверять доступность

- **Priority**: SHOULD
- **Source**: `client.Ping()`
- **Acceptance**:
  - GET {baseURL}/ping
  - Возвращает error при != 200 OK

### 2.8 Event Logging

**REQ-EVT-001**: Система должна записывать системные события

- **Priority**: MUST
- **Source**: `recordSystemEvent()`
- **Acceptance**:
  - Создает SystemEvent (Type, Source, Message, Data, Level)
  - Data: JSON с simbank_id
  - Сохраняет в БД
  - Логирует error при неудаче

---

## 3. Non-Functional Requirements

### 3.1 Concurrency

**REQ-NF-CONC-001**: Thread-safe доступ к clients map

- **Priority**: MUST
- **Implementation**: sync.RWMutex
- **Acceptance**:
  - RLock для чтения (updateAllSimBanks, SetPower, SendUSSD)
  - Lock для записи (loadSimBanks)

**REQ-NF-CONC-002**: Параллельное обновление банков

- **Priority**: MUST
- **Implementation**: Goroutine per client + WaitGroup
- **Acceptance**:
  - Каждый банк обновляется в отдельной горутине
  - WaitGroup.Wait() для ожидания всех

### 3.2 Graceful Shutdown

**REQ-NF-SHUTDOWN-001**: Корректная остановка polling

- **Priority**: MUST
- **Implementation**: context.Context с cancel
- **Acceptance**:
  - monitorLoop проверяет ctx.Done()
  - Stop() вызывает cancel()
  - Горотины завершаются корректно

### 3.3 Error Handling

**REQ-NF-ERR-001**: Логирование ошибок polling

- **Priority**: MUST
- **Acceptance**:
  - `logger.Errorf("Failed to get status for SimBank %d: %v")`
  - Запись system event при error

**REQ-NF-ERR-002**: Обработка ошибок БД

- **Priority**: MUST
- **Acceptance**:
  - Логирование: `logger.Errorf("Failed to update slots: %v")`
  - Возврат error caller'у

### 3.4 Performance

**REQ-NF-PERF-001**: Polling interval настраивается

- **Priority**: MUST
- **Default**: 30s
- **Acceptance**: Из config.SimBankConfig.PollingInterval

**REQ-NF-PERF-002**: HTTP timeout настраивается

- **Priority**: MUST
- **Default**: 10s
- **Acceptance**: Из config.SimBankConfig.Timeout

---

## 4. Data Models

### 4.1 SimBank

| Field | Type | Description |
|-------|------|-------------|
| ID | uint | Primary key |
| Name | string (100) | Имя банка |
| Type | string (50) | SMB128, SMB32 |
| URL | string (255) | HTTP baseURL |
| IsActive | bool | Активен ли |
| CreatedAt | time.Time | |
| UpdatedAt | time.Time | |
| DeletedAt | gorm.DeletedAt | Soft delete |
| Slots | []SimSlot | Has-many relation |

### 4.2 SimSlot

| Field | Type | Description |
|-------|------|-------------|
| ID | uint | Primary key |
| SimBankID | uint | Foreign key |
| SlotID | int | Номер слота |
| IMSI | string (15) | IMSI SIM-карты |
| ICCID | string (20) | ICCID SIM-карты |
| Operator | string (50) | Оператор |
| Status | string (20) | online/offline/error/busy |
| Power | bool | Питание включено |
| Signal | int | Уровень сигнала |
| Mode | string (20) | Режим работы |
| IsActive | bool | Активен ли |
| CreatedAt | time.Time | |
| UpdatedAt | time.Time | |
| DeletedAt | gorm.DeletedAt | Soft delete |
| SimBank | SimBank | Belongs-to relation |

### 4.3 StatusResponse (HTTP)

```json
{
  "status": "ok",
  "slots": [
    {
      "slot_id": 1,
      "imsi": "123456789012345",
      "iccid": "89701234567890123456",
      "operator": "MTS",
      "status": "online",
      "power": true,
      "signal": 85
    }
  ],
  "error": ""
}
```

### 4.4 PowerRequest (HTTP)

```json
{
  "slot_id": 1,
  "power": true
}
```

### 4.5 USSDRequest (HTTP)

```json
{
  "slot_id": 1,
  "command": "*100#"
}
```

### 4.6 USSDResponse (HTTP)

```json
{
  "response": "Balance: 100 RUB",
  "error": ""
}
```

---

## 5. Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| database.DB | GORM | PostgreSQL access |
| logger.Logger | logrus | Logging |
| config.SimBankConfig | viper | Configuration |
| context | stdlib | Cancellation |
| sync | stdlib | Mutex, WaitGroup |
| net/http | stdlib | HTTP client |
| encoding/json | stdlib | JSON marshaling |

---

## 6. Open Questions

- [ ] Тестовое покрытие (не обнаружено в коде)
- [ ] Retry logic для failed polling requests
- [ ] Rate limiting для USSD команд
- [ ] Поддержка разных протоколов SIM-банков (не только HTTP/JSON)

---

*Generated via /legacy analysis on 2026-03-04*
