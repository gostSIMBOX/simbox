# Configuration Management - Specifications

> Spec-Driven Development: Техническая спецификация

**Status**: DRAFT  
**Type**: SDD  
**Generated**: 2026-03-04 via /legacy analysis  
**Source**: `internal/config/config.go`

---

## 1. Architecture

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────┐
│                  config.Load()                       │
│                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   YAML      │  │  Env Vars    │  │  Defaults  │ │
│  │   File      │  │  SIMHUB_*    │  │  setDefaults│ │
│  └──────┬──────┘  └──────┬───────┘  └─────┬──────┘ │
│         │                │                 │        │
│         └────────────────┼─────────────────┘        │
│                          │                          │
│                 ┌────────▼────────┐                 │
│                 │     viper       │                 │
│                 │   Unmarshal     │                 │
│                 └────────┬────────┘                 │
│                          │                          │
│                 ┌────────▼────────┐                 │
│                 │  validateConfig │                 │
│                 └────────┬────────┘                 │
│                          │                          │
│                 ┌────────▼────────┐                 │
│                 │   Config Struct │                 │
│                 └─────────────────┘                 │
└─────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
Application Start
       │
       ▼
  config.Load()
       │
       ├──► Set defaults (setDefaults())
       │
       ├──► Read YAML file
       │    └─► ./config.yaml
       │    └─► ./config/config.yaml
       │    └─► /etc/gostsimbox/config.yaml
       │
       ├──► Read env vars (SIMHUB_*)
       │
       ├──► Unmarshal to Config struct
       │
       ├──► validateConfig()
       │    └─► Validate ports (1-65535)
       │
       └──► Return Config or Error
```

---

## 2. Data Structures

### 2.1 Main Config Struct

```go
type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
    Redis    RedisConfig    `mapstructure:"redis"`
    RabbitMQ RabbitMQConfig `mapstructure:"rabbitmq"`
    Logging  LoggingConfig  `mapstructure:"logging"`
    Metrics  MetricsConfig  `mapstructure:"metrics"`
    SimBank  SimBankConfig  `mapstructure:"simbank"`
    Hardware HardwareConfig `mapstructure:"hardware"`
}
```

### 2.2 ServerConfig

```go
type ServerConfig struct {
    Port         int           `mapstructure:"port"`         // default: 8080
    Host         string        `mapstructure:"host"`         // default: "0.0.0.0"
    ReadTimeout  time.Duration `mapstructure:"read_timeout"` // default: 30s
    WriteTimeout time.Duration `mapstructure:"write_timeout"`// default: 30s
    IdleTimeout  time.Duration `mapstructure:"idle_timeout"` // default: 60s
}
```

### 2.3 DatabaseConfig

```go
type DatabaseConfig struct {
    Host     string `mapstructure:"host"`     // default: "localhost"
    Port     int    `mapstructure:"port"`     // default: 5432
    User     string `mapstructure:"user"`
    Password string `mapstructure:"password"`
    DBName   string `mapstructure:"dbname"`
    SSLMode  string `mapstructure:"sslmode"`  // default: "disable"
    MaxConns int    `mapstructure:"max_conns"`// default: 10
}

// Method: GetDSN() string
// Returns: "host=X port=Y user=Z password=W dbname=V sslmode=U"
```

### 2.4 RedisConfig

```go
type RedisConfig struct {
    Host     string `mapstructure:"host"` // default: "localhost"
    Port     int    `mapstructure:"port"` // default: 6379
    Password string `mapstructure:"password"`
    DB       int    `mapstructure:"db"`   // default: 0
}

// Method: GetRedisAddr() string
// Returns: "host:port"
```

### 2.5 RabbitMQConfig

```go
type RabbitMQConfig struct {
    Host     string `mapstructure:"host"` // default: "localhost"
    Port     int    `mapstructure:"port"` // default: 5672
    User     string `mapstructure:"user"` // default: "guest"
    Password string `mapstructure:"password"`
    VHost    string `mapstructure:"vhost"`// default: "/"
}

// Method: GetRabbitMQURL() string
// Returns: "amqp://user:pass@host:port/vhost"
```

### 2.6 LoggingConfig

```go
type LoggingConfig struct {
    Level      string `mapstructure:"level"`      // default: "info"
    Format     string `mapstructure:"format"`     // default: "json"
    Output     string `mapstructure:"output"`     // default: "stdout"
    MaxSize    int    `mapstructure:"max_size"`   // default: 100 (MB)
    MaxBackups int    `mapstructure:"max_backups"`// default: 3
    MaxAge     int    `mapstructure:"max_age"`    // default: 28 (days)
    Compress   bool   `mapstructure:"compress"`   // default: true
}
```

### 2.7 MetricsConfig

```go
type MetricsConfig struct {
    Enabled bool   `mapstructure:"enabled"` // default: true
    Port    int    `mapstructure:"port"`    // default: 9092
    Path    string `mapstructure:"path"`    // default: "/metrics"
}
```

### 2.8 SimBankConfig

```go
type SimBankConfig struct {
    PollingInterval time.Duration `mapstructure:"polling_interval"` // default: 30s
    Timeout         time.Duration `mapstructure:"timeout"`          // default: 10s
    RetryAttempts   int           `mapstructure:"retry_attempts"`   // default: 3
    RetryDelay      time.Duration `mapstructure:"retry_delay"`      // default: 5s
}
```

### 2.9 HardwareConfig

```go
type HardwareConfig struct {
    Enabled         bool          `mapstructure:"enabled"`          // default: false
    USBControlPath  string        `mapstructure:"usb_control_path"` // default: "/usr/bin/hub-ctrl"
    PowerCycleDelay time.Duration `mapstructure:"power_cycle_delay"`// default: 5s
    MaxRetries      int           `mapstructure:"max_retries"`      // default: 3
}
```

---

## 3. API Specification

### 3.1 Load()

**Signature**: `func Load() (*Config, error)`

**Behavior**:
1. Set config file name and type (YAML)
2. Add search paths: `.`, `./config`, `/etc/gostsimbox/`
3. Call `setDefaults()`
4. Enable automatic env reading with prefix `SIMHUB`
5. Read config file
6. Unmarshal to Config struct
7. Call `validateConfig()`
8. Return Config or error

**Errors**:
- `viper.ConfigFileNotFoundError` - file not found (не критично)
- `error` - error reading file
- `error` - error unmarshaling
- `error` - validation error

### 3.2 setDefaults()

**Signature**: `func setDefaults()`

**Behavior**: Устанавливает значения по умолчанию через viper.SetDefault()

**Defaults**:
| Section | Parameter | Default |
|---------|-----------|---------|
| server | port | 8080 |
| server | host | "0.0.0.0" |
| server | read_timeout | 30s |
| server | write_timeout | 30s |
| server | idle_timeout | 60s |
| database | host | "localhost" |
| database | port | 5432 |
| database | sslmode | "disable" |
| database | max_conns | 10 |
| redis | host | "localhost" |
| redis | port | 6379 |
| redis | db | 0 |
| rabbitmq | host | "localhost" |
| rabbitmq | port | 5672 |
| rabbitmq | vhost | "/" |
| logging | level | "info" |
| logging | format | "json" |
| logging | output | "stdout" |
| logging | max_size | 100 |
| logging | max_backups | 3 |
| logging | max_age | 28 |
| logging | compress | true |
| metrics | enabled | true |
| metrics | port | 9092 |
| metrics | path | "/metrics" |
| simbank | polling_interval | 30s |
| simbank | timeout | 10s |
| simbank | retry_attempts | 3 |
| simbank | retry_delay | 5s |
| hardware | enabled | false |
| hardware | usb_control_path | "/usr/bin/hub-ctrl" |
| hardware | power_cycle_delay | 5s |
| hardware | max_retries | 3 |

### 3.3 validateConfig()

**Signature**: `func validateConfig(config *Config) error`

**Validation Rules**:

```go
// Server port
if config.Server.Port <= 0 || config.Server.Port > 65535 {
    return fmt.Errorf("invalid server port: %d", config.Server.Port)
}

// Database port
if config.Database.Port <= 0 || config.Database.Port > 65535 {
    return fmt.Errorf("invalid database port: %d", config.Database.Port)
}

// Redis port
if config.Redis.Port <= 0 || config.Redis.Port > 65535 {
    return fmt.Errorf("invalid redis port: %d", config.Redis.Port)
}

// RabbitMQ port
if config.RabbitMQ.Port <= 0 || config.RabbitMQ.Port > 65535 {
    return fmt.Errorf("invalid rabbitmq port: %d", config.RabbitMQ.Port)
}

// Metrics port (if enabled)
if config.Metrics.Enabled && (config.Metrics.Port <= 0 || config.Metrics.Port > 65535) {
    return fmt.Errorf("invalid metrics port: %d", config.Metrics.Port)
}
```

### 3.4 Helper Methods

**DatabaseConfig.GetDSN()**:
```go
func (c *DatabaseConfig) GetDSN() string {
    return fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
        c.Host, c.Port, c.User, c.Password, c.DBName, c.SSLMode)
}
```

**RedisConfig.GetRedisAddr()**:
```go
func (c *RedisConfig) GetRedisAddr() string {
    return fmt.Sprintf("%s:%d", c.Host, c.Port)
}
```

**RabbitMQConfig.GetRabbitMQURL()**:
```go
func (c *RabbitMQConfig) GetRabbitMQURL() string {
    return fmt.Sprintf("amqp://%s:%s@%s:%d%s",
        c.User, c.Password, c.Host, c.Port, c.VHost)
}
```

**IsDevelopment()**:
```go
func IsDevelopment() bool {
    return os.Getenv("ENV") == "development" || os.Getenv("ENV") == "dev"
}
```

**IsProduction()**:
```go
func IsProduction() bool {
    return os.Getenv("ENV") == "production" || os.Getenv("ENV") == "prod"
}
```

---

## 4. Configuration Example

### 4.1 YAML Configuration File

```yaml
server:
  port: 8080
  host: "0.0.0.0"
  read_timeout: "30s"
  write_timeout: "30s"
  idle_timeout: "60s"

database:
  host: "localhost"
  port: 5432
  user: "postgres"
  password: "password"
  dbname: "gostsimbox_simhub"
  sslmode: "disable"
  max_conns: 10

redis:
  host: "localhost"
  port: 6379
  password: ""
  db: 0

rabbitmq:
  host: "localhost"
  port: 5672
  user: "guest"
  password: "guest"
  vhost: "/"

logging:
  level: "info"
  format: "json"
  output: "stdout"
  max_size: 100
  max_backups: 3
  max_age: 28
  compress: true

metrics:
  enabled: true
  port: 9092
  path: "/metrics"

simbank:
  polling_interval: "30s"
  timeout: "10s"
  retry_attempts: 3
  retry_delay: "5s"

hardware:
  enabled: false
  usb_control_path: "/usr/bin/hub-ctrl"
  power_cycle_delay: "5s"
  max_retries: 3
```

### 4.2 Environment Variable Overrides

```bash
export SIMHUB_SERVER_PORT=9090
export SIMHUB_DATABASE_HOST=prod-db.example.com
export SIMHUB_DATABASE_PASSWORD=supersecret
export SIMHUB_LOGGING_LEVEL=debug
export SIMHUB_METRICS_ENABLED=false
```

---

## 5. Error Handling

### 5.1 Error Types

| Error | Condition | Severity |
|-------|-----------|----------|
| Config file not found | No YAML file in search paths | LOW (uses defaults) |
| Unmarshal error | Invalid YAML structure | CRITICAL |
| Validation error | Invalid port range | CRITICAL |

### 5.2 Error Propagation

```
config.Load()
    │
    ├─► viper.ReadInConfig()
    │   └─► ConfigFileNotFoundError (не критично)
    │
    ├─► viper.Unmarshal()
    │   └─► error: "error unmarshaling config: %w"
    │
    └─► validateConfig()
        └─► error: "config validation error: %w"
```

---

## 6. Testing Considerations

### 6.1 Unit Test Cases

**Test Load()**:
- [ ] Valid YAML file
- [ ] Missing YAML file (uses defaults)
- [ ] Invalid YAML syntax
- [ ] Environment variable override
- [ ] Invalid port validation

**Test validateConfig()**:
- [ ] Port = 0 (invalid)
- [ ] Port = 65536 (invalid)
- [ ] Port = 8080 (valid)
- [ ] Port = 1 (valid edge case)
- [ ] Port = 65535 (valid edge case)
- [ ] Metrics disabled (port validation skipped)

**Test Helper Methods**:
- [ ] GetDSN() format
- [ ] GetRedisAddr() format
- [ ] GetRabbitMQURL() format

### 6.2 Integration Test Cases

- [ ] Application starts with valid config
- [ ] Application fails with invalid port
- [ ] Environment variables override YAML
- [ ] Defaults used when config missing

---

## 7. Security Considerations

### 7.1 Sensitive Data

| Parameter | Sensitivity | Current State | Recommendation |
|-----------|-------------|---------------|----------------|
| database.password | HIGH | Plain text in YAML | Use env vars or secrets manager |
| redis.password | MEDIUM | Plain text in YAML | Use env vars |
| rabbitmq.password | MEDIUM | Plain text in YAML | Use env vars |

### 7.2 Best Practices

- **DO**: Store passwords in environment variables, not in YAML
- **DO**: Use secrets management in production (HashiCorp Vault, AWS Secrets Manager)
- **DON'T**: Commit YAML files with passwords to version control

---

## 8. Performance Considerations

### 8.1 Load Time

- Config loading происходит один раз при старте приложения
- Viper unmarshal: <1ms для типичной конфигурации
- Validation: <0.1ms

### 8.2 Memory

- Config struct: ~500 bytes
- Viper internal state: ~50KB
- Negligible impact на runtime memory

---

*Generated via /legacy analysis on 2026-03-04*
