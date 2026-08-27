# ADR-004: JSON Log Format for Production

**Date**: 2026-03-04  
**Status**: Accepted  
**Type**: Constraining  
**Source**: Legacy analysis via `/legacy` command

---

## Context

The application requires structured logging for debugging, monitoring, and alerting. Logs need to be consumed by automated systems (ELK stack, Grafana Loki, or similar) for aggregation, searching, and alerting. Human readability during development is also important.

Key requirements:
- Machine-parseable format for log aggregation
- Consistent structure across all log entries
- Support for structured fields (service, version, timestamp)
- Configurable output (stdout for development, file for production)
- Log rotation to prevent disk space issues

---

## Decision

**Use JSON format as the default log format for production deployments.**

The logging system uses logrus with configurable format (JSON or text), with JSON as the production default. All log entries include mandatory fields: `service`, `version`, `timestamp`.

Implementation details:
```go
// From logger/logger.go
func Init(level, format, output string, maxSize, maxBackups, maxAge int, compress bool) {
    Logger = logrus.New()
    
    // Set log level
    logLevel, err := logrus.ParseLevel(level)
    if err != nil {
        logLevel = logrus.InfoLevel
    }
    Logger.SetLevel(logLevel)
    
    // Set formatter
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
    
    // Add default fields hook
    Logger.AddHook(&DefaultFieldsHook{
        Service: "simhub",
        Version: "1.0.0",
    })
}

// DefaultFieldsHook adds context to all logs
type DefaultFieldsHook struct {
    Service string
    Version string
}

func (h *DefaultFieldsHook) Fire(entry *logrus.Entry) error {
    entry.Data["service"] = h.Service
    entry.Data["version"] = h.Version
    entry.Data["timestamp"] = time.Now().Unix()
    return nil
}
```

Configuration:
```yaml
# config/config.yaml
logging:
  level: "info"
  format: "json"  # JSON for production, "text" for development
  output: "stdout"  # or file path
  max_size: 100  # MB
  max_backups: 3
  max_age: 28  # days
  compress: true
```

Example JSON output:
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

## Consequences

### Positive

1. **Machine-parseable**: JSON format is easily consumed by log aggregation systems (ELK, Loki, Splunk)
2. **Structured data**: Fields are typed and queryable (e.g., `level=error AND service=simhub`)
3. **Consistent schema**: All logs follow the same structure with mandatory fields
4. **Context enrichment**: DefaultFieldsHook ensures every log has service identification
5. **Flexibility**: Can switch to text format for local development
6. **Rotation support**: Lumberjack integration prevents disk space issues

### Negative

1. **Human readability**: JSON is harder to read in terminal during development
2. **Verbosity**: JSON format is more verbose than text, increasing storage requirements
3. **Performance**: JSON marshaling has slight overhead compared to text formatting
4. **Nested data**: Complex structured data in log fields can make JSON deeply nested

### Trade-offs

| Alternative | Pros | Cons | Why Not Chosen |
|-------------|------|------|----------------|
| **Text format** | Human-readable, concise | Hard to parse automatically, inconsistent structure | Not suitable for automated log processing |
| **Logfmt** | Balanced readability/parsability | Less common, not all tools support it | JSON has broader ecosystem support |
| **Binary formats (protobuf)** | Compact, fast to parse | Not human-readable at all, requires schema | Overkill for logging use case |
| **Custom format** | Full control | Reinventing the wheel, tooling incompatibility | Standard formats have mature tooling |

---

## Compliance

### Requirements Met
- REQ-INIT-003: JSON formatter with RFC3339 timestamps
- REQ-HOOK-001/002/003: Default fields (service, version, timestamp)
- REQ-NF-DISK-001: Log rotation via lumberjack

### Related SDDs
- `flows/sdd-logging-infrastructure/01-requirements.md` - Section 2.2 Output Configuration
- `flows/sdd-logging-infrastructure/01-requirements.md` - Section 2.3 Default Fields Hook

---

## Notes

**Legacy Analysis Addition (2026-03-04)**:  
This ADR was reverse-engineered from existing code during `/legacy` BFS analysis. JSON format is configured as default in `config/config.yaml`.

**Configuration in Production**:
- Format: `json`
- Output: `stdout` (for Docker/container deployments)
- Rotation: 100MB max, 3 backups, 28 days retention

**Default Fields Added to Every Log**:
- `service`: "simhub" (identifies the service)
- `version`: "1.0.0" (application version)
- `timestamp`: Unix timestamp (for correlation)
- `time`: RFC3339 formatted (from logrus)
- `level`: Log level (info, error, etc.)
- `msg`: Log message

---

*Generated via /legacy analysis on 2026-03-04*
