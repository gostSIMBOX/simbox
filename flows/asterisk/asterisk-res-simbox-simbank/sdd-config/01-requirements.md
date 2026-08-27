# Configuration Management - Requirements

> Spec-Driven Development: Конфигурация приложения

**Status**: DRAFT  
**Type**: SDD (Internal Service)  
**Generated**: 2026-03-04 via /legacy analysis  
**Source**: `internal/config/config.go`

---

## 1. Overview

### 1.1 Purpose

Система конфигурации приложения GOSTsimbox SimHub, обеспечивающая централизованное управление всеми параметрами сервиса через YAML файлы, environment variables и значения по умолчанию.

### 1.2 Scope

- Загрузка конфигурации из YAML файлов
- Переопределение через environment variables
- Валидация параметров перед использованием
- Helper методы для подключения к сервисам

### 1.3 Definitions

| Term | Definition |
|------|------------|
| viper | Go библиотека для управления конфигурацией |
| DSN | Data Source Name (строка подключения к БД) |
| SIMHUB_ | Префикс для environment variables |

---

## 2. Functional Requirements

### 2.1 Configuration Loading

**REQ-LOAD-001**: Система должна загружать конфигурацию из YAML файла

- **Priority**: MUST
- **Source**: `config.Load()`
- **Acceptance**:
  - Чтение из путей: `.`, `./config`, `/etc/gostsimbox/`
  - Поддержка формата YAML
  - Обработка ошибок чтения

**REQ-LOAD-002**: Система должна поддерживать переопределение через environment variables

- **Priority**: MUST
- **Source**: `viper.AutomaticEnv()`, `viper.SetEnvPrefix("SIMHUB")`
- **Acceptance**:
  - Все параметры могут быть переопределены через SIMHUB_*
  - Приоритет: env vars > YAML file > defaults

**REQ-LOAD-003**: Система должна предоставлять значения по умолчанию

- **Priority**: MUST
- **Source**: `setDefaults()` function
- **Acceptance**:
  - 8 секций с defaults (Server, Database, Redis, RabbitMQ, Logging, Metrics, SimBank, Hardware)
  - Defaults используются если не указаны в YAML или env

### 2.2 Configuration Structure

**REQ-STRUCT-001**: Конфигурация должна включать Server секцию

- **Priority**: MUST
- **Parameters**:
  - `port`: int (default: 8080)
  - `host`: string (default: "0.0.0.0")
  - `read_timeout`: duration (default: 30s)
  - `write_timeout`: duration (default: 30s)
  - `idle_timeout`: duration (default: 60s)

**REQ-STRUCT-002**: Конфигурация должна включать Database секцию

- **Priority**: MUST
- **Parameters**:
  - `host`: string (default: "localhost")
  - `port`: int (default: 5432)
  - `user`: string
  - `password`: string
  - `dbname`: string
  - `sslmode`: string (default: "disable")
  - `max_conns`: int (default: 10)

**REQ-STRUCT-003**: Конфигурация должна включать Redis секцию

- **Priority**: MUST
- **Parameters**:
  - `host`: string (default: "localhost")
  - `port`: int (default: 6379)
  - `password`: string
  - `db`: int (default: 0)

**REQ-STRUCT-004**: Конфигурация должна включать RabbitMQ секцию

- **Priority**: MUST
- **Parameters**:
  - `host`: string (default: "localhost")
  - `port`: int (default: 5672)
  - `user`: string (default: "guest")
  - `password`: string (default: "guest")
  - `vhost`: string (default: "/")

**REQ-STRUCT-005**: Конфигурация должна включать Logging секцию

- **Priority**: MUST
- **Parameters**:
  - `level`: string (default: "info")
  - `format`: string (default: "json")
  - `output`: string (default: "stdout")
  - `max_size`: int MB (default: 100)
  - `max_backups`: int (default: 3)
  - `max_age`: int days (default: 28)
  - `compress`: bool (default: true)

**REQ-STRUCT-006**: Конфигурация должна включать Metrics секцию

- **Priority**: MUST
- **Parameters**:
  - `enabled`: bool (default: true)
  - `port`: int (default: 9092)
  - `path`: string (default: "/metrics")

**REQ-STRUCT-007**: Конфигурация должна включать SimBank секцию

- **Priority**: MUST
- **Parameters**:
  - `polling_interval`: duration (default: 30s)
  - `timeout`: duration (default: 10s)
  - `retry_attempts`: int (default: 3)
  - `retry_delay`: duration (default: 5s)

**REQ-STRUCT-008**: Конфигурация должна включать Hardware секцию

- **Priority**: MUST
- **Parameters**:
  - `enabled`: bool (default: false)
  - `usb_control_path`: string (default: "/usr/bin/hub-ctrl")
  - `power_cycle_delay`: duration (default: 5s)
  - `max_retries`: int (default: 3)

### 2.3 Validation

**REQ-VAL-001**: Система должна валидировать порты

- **Priority**: MUST
- **Source**: `validateConfig()`
- **Acceptance**:
  - Server port: 1-65535
  - Database port: 1-65535
  - Redis port: 1-65535
  - RabbitMQ port: 1-65535
  - Metrics port (если enabled): 1-65535
  - Возврат ошибки при invalid port

**REQ-VAL-002**: Система должна возвращать ошибку при невалидной конфигурации

- **Priority**: MUST
- **Acceptance**:
  - `config.Load()` возвращает error
  - Приложение не запускается с невалидной конфигурацией

### 2.4 Helper Methods

**REQ-HELPER-001**: Система должна предоставлять метод для получения DSN

- **Priority**: MUST
- **Source**: `DatabaseConfig.GetDSN()`
- **Acceptance**:
  - Формат: `host=X port=Y user=Z password=W dbname=V sslmode=U`

**REQ-HELPER-002**: Система должна предоставлять метод для получения Redis адреса

- **Priority**: MUST
- **Source**: `RedisConfig.GetRedisAddr()`
- **Acceptance**:
  - Формат: `host:port`

**REQ-HELPER-003**: Система должна предоставлять метод для получения RabbitMQ URL

- **Priority**: MUST
- **Source**: `RabbitMQConfig.GetRabbitMQURL()`
- **Acceptance**:
  - Формат: `amqp://user:pass@host:port/vhost`

**REQ-HELPER-004**: Система должна предоставлять методы для проверки окружения

- **Priority**: SHOULD
- **Source**: `IsDevelopment()`, `IsProduction()`
- **Acceptance**:
  - Проверка ENV=development/dev или ENV=production/prod

---

## 3. Non-Functional Requirements

### 3.1 Type Safety

**REQ-NF-TYPE-001**: Все параметры должны быть строго типизированы

- **Priority**: MUST
- **Implementation**: Go structs с mapstructure tags

### 3.2 Error Handling

**REQ-NF-ERR-001**: Ошибки конфигурации должны быть информативны

- **Priority**: MUST
- **Acceptance**:
  - fmt.Errorf с контекстом ("invalid server port: %d")
  - Обёртка ошибок: fmt.Errorf("...: %w", err)

### 3.3 Deployment Flexibility

**REQ-NF-DEPLOY-001**: Поддержка различных путей развертывания

- **Priority**: MUST
- **Acceptance**:
  - Local: `./config.yaml`
  - Project: `./config/config.yaml`
  - System: `/etc/gostsimbox/config.yaml`

---

## 4. Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| github.com/spf13/viper | v1.17.0 | Configuration management |
| strconv | stdlib | String conversion for env vars |
| os | stdlib | Environment variable access |

---

## 5. Open Questions

- [ ] Тестовое покрытие конфигурации (не обнаружено в коде)
- [ ] Поддержка hot-reload конфигурации (не реализовано)
- [ ] Шифрование чувствительных параметров (passwords в plain text)

---

*Generated via /legacy analysis on 2026-03-04*
