# ADR-004: JSON Log Format for Production

**Status**: Accepted  
**Date**: 2026-03-04  
**Type**: Operational Decision  
**Source**: `/legacy` reverse engineering

## Context

The application generates logs for:
- Operational monitoring (health, performance)
- Debugging (error investigation)
- Audit trail (compliance)
- Security analysis (access patterns)

We need to decide on the log format to balance:
- Human readability during development
- Machine parseability for aggregation
- Performance (logging overhead)
- Integration with monitoring stack

### Requirements

- Support centralized log aggregation (ELK/Grafana)
- Include consistent metadata (service, version, timestamp)
- Support multiple log levels (debug, info, warn, error)
- Enable efficient querying and filtering

### Constraints

- Go application with logrus
- Lumberjack for log rotation
- Potential ELK/Grafana stack
- JSON and text format support available

## Decision

**Use JSON format as default for production, text format for development.**

### Implementation

```go
// internal/logger/logger.go
func Init(level, format, output string, ...) {
    Logger = logrus.New()
    
    // Format selection
    if format == "json" {
        Logger.SetFormatter(&logrus.JSONFormatter{
            TimestampFormat: time.RFC3339,
        })
    } else {
        Logger.SetFormatter(&logrus.TextFormatter{
            FullTimestamp:   true,
            TimestampFormat: time.RFC3339,
        })
    }
    
    // Add default fields to every log entry
    Logger.AddHook(&DefaultFieldsHook{
        Service: "simhub",
        Version: "1.0.0",
    })
}
```

### Default Configuration

```yaml
# config/config.yaml
logging:
  level: info
  format: json          # JSON for production
  output: stdout
  max_size: 100         # MB
  max_backups: 3
  max_age: 28           # days
  compress: true
```

### Log Entry Structure

**JSON Format**:
```json
{
  "level": "info",
  "msg": "Database connected successfully",
  "service": "simhub",
  "version": "1.0.0",
  "timestamp": 1709567890,
  "time": "2026-03-04T12:34:50Z"
}
```

**Text Format** (for development):
```
INFO[2026-03-04T12:34:50Z] Database connected successfully  service=simhub version=1.0.0 timestamp=1709567890
```

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Application Logs                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  DefaultFieldsHook                               │   │
│  │  Adds: service, version, timestamp               │   │
│  └──────────────────────────────────────────────────┘   │
│                       │                                  │
│                       ▼                                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Formatter (JSON or Text)                        │   │
│  │  - JSONFormatter (production)                    │   │
│  │  - TextFormatter (development)                   │   │
│  └──────────────────────────────────────────────────┘   │
│                       │                                  │
│         ┌─────────────┴─────────────┐                   │
│         │                           │                   │
│         ▼                           ▼                   │
│  ┌─────────────┐            ┌─────────────┐            │
│  │  stdout     │            │  File       │            │
│  │  (Docker)   │            │  (lumberjack)│           │
│  └──────┬──────┘            └──────┬──────┘            │
│         │                           │                   │
│         ▼                           ▼                   │
│  ┌─────────────┐            ┌─────────────┐            │
│  │  ELK/Grafana│            │  Rotation   │            │
│  │  (parse JSON)│           │  (100MB/3/28)│           │
│  └─────────────┘            └─────────────┘            │
└─────────────────────────────────────────────────────────┘
```

## Rationale

**JSON format was chosen because:**

1. **Machine parseable**: ELK/Grafana can parse without regex
2. **Structured data**: Easy to add custom fields
3. **Query efficiency**: Indexed field searches in Elasticsearch
4. **Standard practice**: Industry standard for log aggregation
5. **Type preservation**: Numbers stay numbers, not strings

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Text format** | Human readable, simple | Hard to parse, no structure | Doesn't scale for aggregation |
| **Logfmt** | Balanced readability/structure | Less common, tooling support | JSON has better ecosystem |
| **Protocol Buffers** | Compact, typed | Binary, needs schema | Overkill for logging |
| **Syslog** | Standard protocol | Limited structure, UDP issues | Application-level logging needed |

## Consequences

### Positive

- **Easy aggregation**: Logstash/Fluentd parse JSON natively
- **Efficient queries**: Field-based searches in Elasticsearch
- **Consistent metadata**: Every log has service/version/timestamp
- **Flexible**: Easy to add new fields without breaking parsers
- **Rotation built-in**: Lumberjack handles file management

### Negative

- **Human readability**: JSON harder to read in terminal
- **Verbosity**: More bytes than text format
- **Parsing overhead**: JSON parsing adds CPU cost (minimal)

### Mitigation Strategies

1. **Development mode**: Use text format locally (`LOGGING_FORMAT=text`)
2. **Pretty print**: Use `jq` for debugging JSON logs
3. **Log levels**: Use appropriate levels to reduce noise

## Configuration Examples

### Production (Docker/Kubernetes)

```yaml
# config/config.yaml
logging:
  level: info
  format: json
  output: stdout  # Docker captures stdout
```

```bash
# docker-compose.yml
services:
  simhub:
    environment:
      - SIMHUB_LOGGING_LEVEL=info
      - SIMHUB_LOGGING_FORMAT=json
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "3"
```

### Development

```yaml
# config/config.local.yaml
logging:
  level: debug
  format: text  # Human readable
  output: stdout
```

```bash
# Override for development
export SIMHUB_LOGGING_FORMAT=text
export SIMHUB_LOGGING_LEVEL=debug
```

## Query Examples

### ELK/Grafana Queries

```
# All errors for simhub service
service:simhub AND level:error

# Database connection issues
service:simhub AND message:*database* AND level:error

# Performance analysis (response time > 1s)
service:simhub AND duration_ms:>1000
```

## Compliance

**Compliant Flows**:
- `flows/sdd-logging-infrastructure/01-requirements.md` - Logger specification

**Default Fields** (added to every entry):
- `service`: "simhub"
- `version`: "1.0.0"
- `timestamp`: Unix timestamp (seconds)

## Notes

**When to use text format**:
- Local development
- Debugging sessions
- Small-scale deployments without log aggregation

**Log rotation defaults**:
- MaxSize: 100MB
- MaxBackups: 3 files
- MaxAge: 28 days
- Compress: true (gzip)

---

*Generated by /legacy reverse engineering - DRAFT for review*
