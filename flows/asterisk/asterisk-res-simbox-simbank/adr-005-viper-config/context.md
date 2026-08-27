# ADR-005: Viper for Configuration Management

**Date**: 2026-03-04  
**Status**: Accepted  
**Type**: Enabling  
**Source**: Legacy analysis via `/legacy` command

---

## Context

The application requires flexible configuration management to support multiple deployment environments (development, staging, production), containerized deployments (Docker, Kubernetes), and system-level installations. Configuration must support hierarchical overrides, environment-specific values, and validation.

Key requirements:
- Support multiple configuration sources (file, environment variables, defaults)
- Hierarchical configuration with clear precedence
- Type-safe configuration access
- Environment variable overrides for container deployments
- Configuration validation before application startup
- Support for multiple deployment paths (local, project, system)

---

## Decision

**Use Viper library for configuration management with hierarchical loading.**

The system uses Viper to load configuration from YAML files with automatic environment variable overrides and sensible defaults. Configuration is organized into 8 typed sections with clear precedence: YAML file → Environment variables → Defaults.

Implementation details:
```go
// From config/config.go
func Load() (*Config, error) {
    viper.SetConfigName("config")
    viper.SetConfigType("yaml")
    viper.AddConfigPath(".")
    viper.AddConfigPath("./config")
    viper.AddConfigPath("/etc/gostsimbox/")
    
    setDefaults()
    
    viper.AutomaticEnv()
    viper.SetEnvPrefix("SIMHUB")
    
    if err := viper.ReadInConfig(); err != nil {
        if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
            return nil, fmt.Errorf("error reading config file: %w", err)
        }
    }
    
    var config Config
    if err := viper.Unmarshal(&config); err != nil {
        return nil, fmt.Errorf("error unmarshaling config: %w", err)
    }
    
    if err := validateConfig(&config); err != nil {
        return nil, fmt.Errorf("config validation error: %w", err)
    }
    
    return &config, nil
}
```

Configuration structure (8 sections):
1. **ServerConfig** - HTTP server settings (port, host, timeouts)
2. **DatabaseConfig** - PostgreSQL connection (host, port, credentials, pooling)
3. **RedisConfig** - Redis connection (host, port, credentials)
4. **RabbitMQConfig** - RabbitMQ connection (host, port, credentials, vhost)
5. **LoggingConfig** - Logging settings (level, format, output, rotation)
6. **MetricsConfig** - Prometheus metrics (enabled, port, path)
7. **SimBankConfig** - SIM-bank polling (interval, timeout, retry)
8. **HardwareConfig** - Hardware control (enabled, USB path, delays)

Environment variable precedence:
```bash
# All env vars use SIMHUB_ prefix
export SIMHUB_SERVER_PORT=9090
export SIMHUB_DATABASE_HOST=prod-db.example.com
export SIMHUB_LOGGING_LEVEL=debug
```

---

## Consequences

### Positive

1. **Flexibility**: Supports multiple deployment scenarios (local dev, containers, system install)
2. **Clear precedence**: YAML → Env → Defaults is easy to understand and predict
3. **Type safety**: Configuration is strongly typed via Go structs with mapstructure tags
4. **Validation**: Config validation prevents invalid startup
5. **Industry standard**: Viper is widely adopted in Go ecosystem with good documentation
6. **Environment overrides**: Perfect for Docker/Kubernetes deployments
7. **Multiple paths**: Supports `./config.yaml`, `./config/config.yaml`, `/etc/gostsimbox/config.yaml`

### Negative

1. **Dependency**: Adds external dependency (viper, fsnotify) to the project
2. **Startup time**: Viper initialization adds minimal overhead (~1-5ms)
3. **Magic behavior**: Automatic env mapping can be confusing for new developers
4. **No hot reload**: Configuration is loaded once at startup, changes require restart
5. **Plain text secrets**: Passwords stored in YAML or env vars (not encrypted)

### Trade-offs

| Alternative | Pros | Cons | Why Not Chosen |
|-------------|------|------|----------------|
| **Manual YAML parsing** | No dependencies, full control | More code, no env overrides, no validation | Viper provides all features out-of-box |
| **Environment variables only** | Simple, container-native | No defaults, no structure, hard to manage many vars | Need defaults and structure |
| **Configuration management tools (Consul, etcd)** | Centralized config, hot reload | Operational complexity, external dependencies | Overkill for single-service application |
| **Flags only** | Simple for CLI tools | Not suitable for complex configuration | Need hierarchical structure |

---

## Compliance

### Requirements Met
- REQ-LOAD-001: YAML file loading
- REQ-LOAD-002: Environment variable overrides
- REQ-LOAD-003: Default values
- REQ-STRUCT-001 to REQ-STRUCT-008: All 8 configuration sections
- REQ-VAL-001/002: Port validation

### Related SDDs
- `flows/sdd-config-management/01-requirements.md` - Complete requirements specification
- `flows/sdd-config-management/01-requirements.md` - Section 2.1 Configuration Loading

---

## Notes

**Legacy Analysis Addition (2026-03-04)**:  
This ADR was reverse-engineered from existing code during `/legacy` BFS analysis. Viper is properly configured with all best practices.

**Configuration Defaults** (25+ defaults set):
- Server: port 8080, host 0.0.0.0, timeouts 30s/30s/60s
- Database: localhost:5432, max_conns 10
- Redis: localhost:6379, db 0
- RabbitMQ: localhost:5672, vhost /
- Logging: level info, format json, output stdout
- Metrics: enabled, port 9092, path /metrics
- SimBank: polling 30s, timeout 10s, retry 3 times
- Hardware: disabled, usb_control_path /usr/bin/hub-ctrl

**Environment Variable Mapping**:
- All variables use `SIMHUB_` prefix
- Nested fields use underscore: `SIMHUB_SERVER_PORT`, `SIMHUB_DATABASE_HOST`
- Case-insensitive matching

---

*Generated via /legacy analysis on 2026-03-04*
