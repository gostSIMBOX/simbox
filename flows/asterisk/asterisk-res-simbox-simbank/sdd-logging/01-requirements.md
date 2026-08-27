# Logging Infrastructure - Requirements

> Spec-Driven Development: Logging System

**Status**: DRAFT  
**Type**: SDD (Internal Service)  
**Generated**: 2026-03-04 via /legacy analysis  
**Source**: `internal/logger/logger.go`

---

## 1. Overview

### 1.1 Purpose

Централизованная система логирования приложения GOSTsimbox SimHub на базе logrus с поддержкой различных форматов, уровней, и ротации логов.

### 1.2 Scope

- Глобальный логгер для всего приложения
- Настройка уровня, формата, вывода
- Ротация логов через lumberjack
- Кастомный hook для default полей

### 1.3 Definitions

| Term | Definition |
|------|------------|
| logrus | Structured logging library for Go |
| lumberjack | Log rotation library |
| Hook | Extension point для модификации log entry |

---

## 2. Functional Requirements

### 2.1 Logger Initialization

**REQ-INIT-001**: Система должна инициализировать глобальный логгер

- **Priority**: MUST
- **Source**: `logger.Init()`
- **Acceptance**:
  - Создает новый实例 logrus.Logger
  - Настраивает уровень логирования
  - Настраивает формат вывода
  - Настраивает output destination
  - Добавляет DefaultFieldsHook

**REQ-INIT-002**: Система должна поддерживать настройку уровня логирования

- **Priority**: MUST
- **Parameters**: level string (debug, info, warn, error, fatal, panic)
- **Default**: info
- **Acceptance**:
  - Парсит строку в logrus.Level
  - Возвращает info level при ошибке парсинга

**REQ-INIT-003**: Система должна поддерживать настройку формата

- **Priority**: MUST
- **Parameters**: format string (json, text)
- **Default**: json
- **Acceptance**:
  - JSON: logrus.JSONFormatter с RFC3339 timestamp
  - Text: logrus.TextFormatter с FullTimestamp

### 2.2 Output Configuration

**REQ-OUT-001**: Система должна поддерживать вывод в stdout

- **Priority**: MUST
- **Parameters**: output = "stdout"
- **Acceptance**:
  - Устанавливает os.Stdout как output
  - Используется для development

**REQ-OUT-002**: Система должна поддерживать вывод в файл

- **Priority**: MUST
- **Parameters**: output = file path
- **Acceptance**:
  - Создает директорию для логов (0755 permissions)
  - Использует lumberjack.Logger для rotation
  - Возвращает error при создании директории

**REQ-OUT-003**: Система должна настраивать ротацию логов

- **Priority**: MUST
- **Parameters**:
  - MaxSize: int MB (default: 100)
  - MaxBackups: int count (default: 3)
  - MaxAge: int days (default: 28)
  - Compress: bool (default: true)
- **Acceptance**:
  - lumberjack.Logger с указанными параметрами

### 2.3 Default Fields Hook

**REQ-HOOK-001**: Hook должен добавлять service поле

- **Priority**: MUST
- **Value**: "simhub"
- **Acceptance**: Все log entry содержат field "service"

**REQ-HOOK-002**: Hook должен добавлять version поле

- **Priority**: MUST
- **Value**: "1.0.0"
- **Acceptance**: Все log entry содержат field "version"

**REQ-HOOK-003**: Hook должен добавлять timestamp поле

- **Priority**: MUST
- **Value**: Unix timestamp (int64)
- **Acceptance**: Все log entry содержат field "timestamp"

**REQ-HOOK-004**: Hook должен срабатывать на всех уровнях

- **Priority**: MUST
- **Acceptance**:
  - Levels() возвращает logrus.AllLevels
  - Fire() вызывается для каждого log entry

### 2.4 Logging Methods

**REQ-LOG-001**: Поддержка всех уровней логирования

- **Priority**: MUST
- **Levels**:
  - Debug() - отладочная информация
  - Info() - информационные сообщения
  - Warn() - предупреждения
  - Error() - ошибки
  - Fatal() - критические ошибки с exit
  - Panic() - логирование с panic

**REQ-LOG-002**: Поддержка structured logging

- **Priority**: MUST
- **Acceptance**:
  - `logger.Infof("User %s logged in", username)`
  - `logger.WithField("user_id", id).Info("User action")`
  - `logger.WithError(err).Error("Operation failed")`

---

## 3. Non-Functional Requirements

### 3.1 Performance

**REQ-NF-PERF-001**: Минимальное влияние на производительность

- **Priority**: MUST
- **Acceptance**:
  - Асинхронная запись (если поддерживается)
  - Буферизация вывода

### 3.2 Thread Safety

**REQ-NF-SAFE-001**: Thread-safe логирование

- **Priority**: MUST
- **Acceptance**:
  - logrus является thread-safe по умолчанию
  - Concurrent log вызовы не вызывают race conditions

### 3.3 Disk Space Management

**REQ-NF-DISK-001**: Автоматическая ротация предотвращает переполнение

- **Priority**: MUST
- **Acceptance**:
  - MaxSize ограничивает размер файла
  - MaxBackups ограничивает количество backup файлов
  - MaxAge удаляет старые логи

---

## 4. Configuration Example

### 4.1 YAML Configuration

```yaml
logging:
  level: "info"
  format: "json"
  output: "stdout"
  max_size: 100
  max_backups: 3
  max_age: 28
  compress: true
```

### 4.2 Usage Examples

```go
// Basic logging
logger.Logger.Info("Server starting")
logger.Logger.Errorf("Database connection failed: %v", err)

// With fields
logger.Logger.WithField("simbank_id", id).Info("Loaded SimBank")

// With error
if err != nil {
    logger.Logger.WithError(err).Error("Operation failed")
}

// Different levels
logger.Logger.Debug("Debug info")
logger.Logger.Warn("Warning message")
logger.Logger.Fatal("Critical error")
```

### 4.3 JSON Output Example

```json
{
  "level": "info",
  "msg": "Server starting",
  "service": "simhub",
  "version": "1.0.0",
  "timestamp": 1709567890,
  "time": "2026-03-04T12:00:00Z"
}
```

---

## 5. Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| github.com/sirupsen/logrus | v1.9.3 | Structured logging |
| gopkg.in/natefinch/lumberjack.v2 | latest | Log rotation |
| os | stdlib | Stdout, file operations |
| filepath | stdlib | Path manipulation |
| time | stdlib | Timestamp formatting |

---

## 6. Open Questions

- [ ] Асинхронное логирование для производительности
- [ ] Поддержка дополнительных hook'ов (Sentry, Slack alerts)
- [ ] Context-aware логирование (trace ID, request ID)
- [ ] Тестовое покрытие (не обнаружено в коде)

---

*Generated via /legacy analysis on 2026-03-04*
