# ADR-005: Viper for Configuration Management

**Status**: Accepted  
**Date**: 2026-03-04  
**Type**: Technology Selection  
**Source**: `/legacy` reverse engineering

## Context

The application requires configuration for:
- Server settings (port, timeouts)
- Database connection (host, port, credentials)
- Redis, RabbitMQ connections
- Logging settings
- Metrics endpoint
- SIM-bank polling parameters
- Hardware control options

We need to decide on configuration management approach to balance:
- Flexibility (multiple sources, overrides)
- Type safety (compile-time checking)
- Ease of use (simple API)
- Deployment flexibility (containers, bare metal)

### Requirements

- Support YAML configuration files
- Support environment variable overrides
- Provide sensible defaults
- Validate configuration at startup
- Support multiple environments (dev, prod)

### Constraints

- Go application
- Container deployment (Docker/Kubernetes)
- 12-factor app principles (config in environment)
- Multiple configuration sections (8+)

## Decision

**Use Viper library for configuration management with hierarchical config sources.**

### Implementation

```go
// internal/config/config.go
import "github.com/spf13/viper"

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

func Load() (*Config, error) {
    // Configuration file search paths
    viper.SetConfigName("config")
    viper.SetConfigType("yaml")
    viper.AddConfigPath(".")
    viper.AddConfigPath("./config")
    viper.AddConfigPath("/etc/gostsimbox/")
    
    // Set defaults (25+ default values)
    setDefaults()
    
    // Environment variable overrides
    viper.AutomaticEnv()
    viper.SetEnvPrefix("SIMHUB")
    
    // Read config file
    viper.ReadInConfig()
    
    // Unmarshal into typed struct
    var config Config
    viper.Unmarshal(&config)
    
    // Validate
    validateConfig(&config)
    
    return &config, nil
}
```

### Configuration Sources (Priority: High → Low)

1. **Environment variables** (`SIMHUB_*`)
2. **Config file** (`config.yaml`)
3. **Default values** (hardcoded)

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Configuration Loading                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  1. Environment Variables (SIMHUB_*)             │   │
│  │     SIMHUB_SERVER_PORT=9000                      │   │
│  │     SIMHUB_DATABASE_HOST=db.example.com          │   │
│  └──────────────────────────────────────────────────┘   │
│                       ▲                                  │
│                       │ (overrides)                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  2. Config File (config.yaml)                    │   │
│  │     server:                                      │   │
│  │       port: 8080                                 │   │
│  │     database:                                    │   │
│  │       host: localhost                            │   │
│  └──────────────────────────────────────────────────┘   │
│                       ▲                                  │
│                       │ (overrides)                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  3. Default Values (25+ defaults)                │   │
│  │     server.port = 8080                           │   │
│  │     database.host = localhost                    │   │
│  │     logging.level = info                         │   │
│  └──────────────────────────────────────────────────┘   │
│                       │                                  │
│                       ▼                                  │
│              ┌─────────────────┐                        │
│              │  viper.Unmarshal() │                    │
│              │  → Config struct  │                    │
│              └─────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

### Environment Variable Mapping

**Pattern**: `SIMHUB_{SECTION}_{FIELD}`

| Config Path | Environment Variable | Example |
|-------------|---------------------|---------|
| `server.port` | `SIMHUB_SERVER_PORT` | `SIMHUB_SERVER_PORT=9000` |
| `database.host` | `SIMHUB_DATABASE_HOST` | `SIMHUB_DATABASE_HOST=db` |
| `logging.level` | `SIMHUB_LOGGING_LEVEL` | `SIMHUB_LOGGING_LEVEL=debug` |
| `simbank.polling_interval` | `SIMHUB_SIMBANK_POLLING_INTERVAL` | `SIMHUB_SIMBANK_POLLING_INTERVAL=30s` |

## Rationale

**Viper was chosen because:**

1. **Industry standard**: Widely used in Go ecosystem
2. **Multiple formats**: YAML, JSON, TOML support
3. **Hierarchical config**: Nested sections with mapstructure tags
4. **Environment overrides**: Built-in support with prefix
5. **Live reload**: Can watch config file changes (not used currently)
6. **Validation**: Manual validation after unmarshal

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Standard library (flag)** | No dependencies | Limited, no nested config | Too basic for requirements |
| **koanf** | Modern, type-safe | Less mature, smaller community | Viper has more adoption |
| **config** | Simple, lightweight | No env override built-in | Missing key feature |
| **Custom solution** | Full control | Maintenance burden | Reinventing the wheel |

## Consequences

### Positive

- **Flexible deployment**: Same config works in containers and bare metal
- **Type safety**: Typed struct with mapstructure tags
- **Sensible defaults**: 25+ defaults for zero-config startup
- **Environment overrides**: Container-friendly (12-factor)
- **Validation**: Catch config errors at startup

### Negative

- **Dependency**: External library (well-maintained)
- **Reflection**: Unmarshal uses reflection (minor performance cost)
- **Magic**: mapstructure tags are runtime-checked, not compile-time

### Mitigation Strategies

1. **Pinned version**: Pin viper version in go.mod
2. **Validation**: Comprehensive validateConfig() function
3. **Documentation**: Document all config options and env vars

## Configuration Examples

### Full Configuration File

```yaml
# config/config.yaml
server:
  port: 8080
  host: 0.0.0.0
  read_timeout: 30s
  write_timeout: 30s
  idle_timeout: 60s

database:
  host: localhost
  port: 5432
  user: simhub
  password: secret
  dbname: simhub
  sslmode: disable
  max_conns: 10

redis:
  host: localhost
  port: 6379
  password: ""
  db: 0

rabbitmq:
  host: localhost
  port: 5672
  user: guest
  password: guest
  vhost: /

logging:
  level: info
  format: json
  output: stdout
  max_size: 100
  max_backups: 3
  max_age: 28
  compress: true

metrics:
  enabled: true
  port: 9092
  path: /metrics

simbank:
  polling_interval: 30s
  timeout: 10s
  retry_attempts: 3
  retry_delay: 5s

hardware:
  enabled: false
  usb_control_path: /usr/bin/hub-ctrl
  power_cycle_delay: 5s
  max_retries: 3
```

### Docker Compose

```yaml
# docker-compose.yml
services:
  simhub:
    image: gostsimbox/simhub:latest
    environment:
      - SIMHUB_DATABASE_HOST=postgres
      - SIMHUB_REDIS_HOST=redis
      - SIMHUB_RABBITMQ_HOST=rabbitmq
      - SIMHUB_LOGGING_FORMAT=json
    ports:
      - "8080:8080"
```

### Kubernetes ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: simhub-config
data:
  SIMHUB_SERVER_PORT: "8080"
  SIMHUB_DATABASE_HOST: "postgres.default.svc"
  SIMHUB_LOGGING_LEVEL: "info"
  SIMHUB_LOGGING_FORMAT: "json"
```

## Compliance

**Compliant Flows**:
- `flows/sdd-config-management/01-requirements.md` - Configuration specification

**Default Values** (25+ total):
- Server: port, host, timeouts (5 defaults)
- Database: host, port, sslmode, max_conns (4 defaults)
- Redis: host, port, db (3 defaults)
- RabbitMQ: host, port, vhost (3 defaults)
- Logging: level, format, output, rotation (6 defaults)
- Metrics: enabled, port, path (3 defaults)
- SimBank: polling_interval, timeout, retry (4 defaults)
- Hardware: enabled, paths, delays (4 defaults)

## Notes

**Config file search order**:
1. `./config.yaml`
2. `./config/config.yaml`
3. `/etc/gostsimbox/config.yaml`

**Environment variable prefix**: `SIMHUB_`

**Validation rules**:
- All ports must be 1-65535
- Required fields checked
- Format validation (time durations, URLs)

---

*Generated by /legacy reverse engineering - DRAFT for review*
