# GoIP Integration - Spec-Driven Development

> Spec-Driven Development: Technical specifications for GoIP gateway integration.

## Overview

**Domain**: GoIP Integration  
**Type**: SDD (Spec-Driven Development)  
**Status**: DRAFT  
**Generated**: 2026-03-04  
**Source**: Legacy analysis (`legacy/www/goip/`, `legacy/access/DblTekGoIPPwn/`)

**Note**: This specification describes **legitimate** GoIP integration. Security exploitation tools from legacy system are **excluded** from modern implementation.

## Architecture

### Integration Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    SIM-Hub System                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              GoIP Integration Layer                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │  HTTP API   │  │  SMS        │  │  USSD       │      │  │
│  │  │  Client     │  │  Gateway    │  │  Processor  │      │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │  │
│  └─────────┼────────────────┼────────────────┼─────────────┘  │
└────────────┼────────────────┼────────────────┼────────────────┘
             │                │                │
             │ HTTP/JSON      │ SMPP/HTTP      │ USSD over HTTP
             ▼                ▼                ▼
    ┌─────────────────────────────────────────────────┐
    │              GoIP GSM Gateway                    │
    │  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
    │  │  GSM    │  │  GSM    │  │  GSM    │  ...    │
    │  │ Module  │  │ Module  │  │ Module  │         │
    │  │ (SIM 1) │  │ (SIM 2) │  │ (SIM N) │         │
    │  └─────────┘  └─────────┘  └─────────┘         │
    └─────────────────────────────────────────────────┘
```

### Security Note

**Legacy System Issues**:
- `legacy/access/DblTekGoIPPwn/` contains exploitation framework
- Vulnerability exploitation (CVE-2017-5521) for unauthorized access
- **NOT included** in modern implementation

**Modern Security**:
- Authenticated API access only
- No exploitation capabilities
- Compliance with telecommunications regulations
- Audit logging for all operations

## Component Specifications

### GoIP Client

**Package**: `internal/goip`

**Responsibilities**:
- HTTP API communication with GoIP devices
- SMS sending via GoIP gateway
- USSD command execution
- Status monitoring

**Configuration**:
```go
type GoIPConfig struct {
    BaseURL        string        `mapstructure:"base_url"`
    Username       string        `mapstructure:"username"`
    Password       string        `mapstructure:"password"`
    Timeout        time.Duration `mapstructure:"timeout"`
    RetryAttempts  int           `mapstructure:"retry_attempts"`
    RetryDelay     time.Duration `mapstructure:"retry_delay"`
}
```

**Methods**:

| Method | Signature | Purpose |
|--------|-----------|---------|
| GetStatus | `GetStatus() (*GoIPStatus, error)` | Get device status |
| SendSMS | `SendSMS(simSlot int, number string, message string) error` | Send SMS |
| SendUSSD | `SendUSSD(simSlot int, command string) (*USSDResponse, error)` | Execute USSD |
| GetSignal | `GetSignal(simSlot int) (int, error)` | Get signal strength |

### Data Structures

**GoIPStatus**:
```go
type GoIPStatus struct {
    DeviceName   string       `json:"device_name"`
    DeviceType   string       `json:"device_type"`  // GoIP-8, GoIP-16, etc.
    Firmware     string       `json:"firmware"`
    Uptime       int          `json:"uptime"`       // seconds
    SIMSlots     []SIMSlotStatus `json:"sim_slots"`
    Network      NetworkStatus   `json:"network"`
}
```

**SIMSlotStatus**:
```go
type SIMSlotStatus struct {
    SlotID     int    `json:"slot_id"`
    IMSI       string `json:"imsi"`
    ICCID      string `json:"iccid"`
    Operator   string `json:"operator"`
    Status     string `json:"status"`  // registered, unregistered, searching
    Signal     int    `json:"signal"`  // 0-100%
    Number     string `json:"number"`  // Phone number
}
```

**NetworkStatus**:
```go
type NetworkStatus struct {
    ExternalIP    string `json:"external_ip"`
    Connection    string `json:"connection"`  // connected, disconnected
    UploadSpeed   int    `json:"upload_speed"`
    DownloadSpeed int    `json:"download_speed"`
}
```

**USSDResponse**:
```go
type USSDResponse struct {
    Command    string `json:"command"`
    Response   string `json:"response"`
    Timestamp  time.Time `json:"timestamp"`
    SlotID     int    `json:"slot_id"`
}
```

## API Endpoints

### GoIP HTTP API (Device Side)

GoIP devices expose HTTP API for control:

**Base URL**: `http://{device-ip}:8080/`

| Endpoint | Method | Parameters | Response |
|----------|--------|------------|----------|
| `/status` | GET | - | Device status JSON |
| `/sms/send` | POST | `{slot, number, message}` | `{success, message_id}` |
| `/ussd/send` | POST | `{slot, command}` | `{success, response}` |
| `/signal` | GET | `{slot}` | `{signal_strength}` |

**Authentication**:
```http
Authorization: Basic base64(username:password)
```

**Example Request**:
```http
POST http://192.168.1.100:8080/sms/send HTTP/1.1
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
Content-Type: application/json

{
  "slot": 1,
  "number": "+79991234567",
  "message": "Test message"
}
```

**Example Response**:
```json
{
  "success": true,
  "message_id": "msg_12345",
  "status": "queued"
}
```

## SMS Gateway Integration

### SMPP Protocol (Optional)

For enterprise GoIP deployments with SMPP support:

**Configuration**:
```go
type SMPPConfig struct {
    Host          string        `mapstructure:"host"`
    Port          int           `mapstructure:"port"`  // Usually 2775
    SystemID      string        `mapstructure:"system_id"`
    Password      string        `mapstructure:"password"`
    SystemType    string        `mapstructure:"system_type"`
    AddressTON    int           `mapstructure:"address_ton"`
    AddressNPI    int           `mapstructure:"address_npi"`
    EnquireLink   time.Duration `mapstructure:"enquire_link"`
}
```

**SMPP Operations**:
- `bind_transmitter` - Session establishment
- `submit_sm` - SMS submission
- `deliver_sm` - SMS delivery receipt
- `enquire_link` - Connection keepalive
- `unbind` - Session termination

### SMS Queue Integration

Integration with message queue for high-volume SMS:

```go
type SMSQueue struct {
    QueueName    string `json:"queue_name"`
    BatchSize    int    `json:"batch_size"`
    RateLimit    int    `json:"rate_limit"`  // SMS per minute
    RetryAttempts int   `json:"retry_attempts"`
}
```

**Flow**:
```
1. Application publishes SMS request to queue
2. GoIP Gateway consumes from queue
3. Gateway sends via GoIP device
4. Delivery receipt published to response queue
5. Application correlates receipt with original request
```

## USSD Processing

### USSD Command Structure

```go
type USSDCommand struct {
    SlotID      int    `json:"slot_id"`
    Command     string `json:"command"`
    Timeout     time.Duration `json:"timeout"`
    Description string `json:"description"`  // For logging
}
```

**Common USSD Commands**:

| Command | Purpose | Example Response |
|---------|---------|------------------|
| `*100#` | Balance check | "Balance: $10.50. Valid until..." |
| `*111#` | Tariff info | "Your tariff: Premium. Monthly fee..." |
| `*102#` | Data balance | "Data remaining: 5.2 GB" |
| `*112#` | Service status | "Services: Voice=Active, Data=Active" |

### USSD Response Processing

```go
func (g *GoIPClient) ProcessUSSDResponse(response string) (*ParsedUSSDResponse, error) {
    // Parse common response patterns
    patterns := map[string]*regexp.Regexp{
        "balance": regexp.MustCompile(`Balance:\s*\$?([\d.]+)`),
        "data": regexp.MustCompile(`([\d.]+)\s*(GB|MB)`),
        "validity": regexp.MustCompile(`Valid until:\s*(\d{2}.\d{2}.\d{4})`),
    }
    
    result := &ParsedUSSDResponse{
        Raw: response,
    }
    
    // Extract balance
    if matches := patterns["balance"].FindStringSubmatch(response); matches != nil {
        result.Balance, _ = strconv.ParseFloat(matches[1], 64)
    }
    
    // Extract data
    if matches := patterns["data"].FindStringSubmatch(response); matches != nil {
        result.DataRemaining, _ = strconv.ParseFloat(matches[1], 64)
        result.DataUnit = matches[2]
    }
    
    return result, nil
}
```

## Database Integration

### GoIP Device Table

```sql
CREATE TABLE goip_devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL,  -- GoIP-8, GoIP-16, GoIP-32
    ip_address INET NOT NULL,
    port INTEGER DEFAULT 8080,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_seen TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_goip_devices_active ON goip_devices(is_active);
CREATE INDEX idx_goip_devices_last_seen ON goip_devices(last_seen);
```

### SIM Slot Table (GoIP-specific)

```sql
CREATE TABLE goip_sim_slots (
    id SERIAL PRIMARY KEY,
    goip_device_id INTEGER REFERENCES goip_devices(id),
    slot_id INTEGER NOT NULL,
    imsi VARCHAR(15) UNIQUE,
    iccid VARCHAR(20),
    phone_number VARCHAR(20),
    operator VARCHAR(50),
    status VARCHAR(20) DEFAULT 'unknown',  -- registered, unregistered, searching
    signal_strength INTEGER DEFAULT 0,
    last_ussd_response TEXT,
    last_ussd_time TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(goip_device_id, slot_id)
);

CREATE INDEX idx_goip_sim_slots_imsi ON goip_sim_slots(imsi);
CREATE INDEX idx_goip_sim_slots_status ON goip_sim_slots(status);
```

### SMS Log Table

```sql
CREATE TABLE sms_logs (
    id SERIAL PRIMARY KEY,
    goip_device_id INTEGER REFERENCES goip_devices(id),
    slot_id INTEGER,
    from_number VARCHAR(20),
    to_number VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, sent, delivered, failed
    error_message TEXT,
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sms_logs_status ON sms_logs(status);
CREATE INDEX idx_sms_logs_to_number ON sms_logs(to_number);
CREATE INDEX idx_sms_logs_created ON sms_logs(created_at);
```

## Error Handling

### Error Categories

| Category | Handling | Retry | Alert |
|----------|----------|-------|-------|
| **Network Timeout** | Log, retry up to 3 times | Yes | On 3rd failure |
| **Authentication Failed** | Log error, disable device | No | Immediate |
| **SIM Not Registered** | Log, mark slot as error | No | On first occurrence |
| **USSD Timeout** | Log partial response | Yes (once) | On repeated failures |
| **SMS Queue Full** | Backpressure, wait | Yes | On sustained full |

### Error Response Format

```json
{
  "error": {
    "code": "GOIP_ERR_SIM_NOT_REGISTERED",
    "message": "SIM in slot 5 is not registered to network",
    "details": {
      "slot_id": 5,
      "imsi": "123456789012345",
      "last_attempt": "2026-03-04T12:34:50Z"
    },
    "recoverable": false,
    "suggested_action": "Check SIM card physical connection"
  }
}
```

## Monitoring & Metrics

### Prometheus Metrics

```go
// Device status
goip_device_online{device="goip-1"} 1|0
goip_device_uptime_seconds{device="goip-1"} 86400

// SIM slots
goip_slot_registered{device="goip-1",slot="1"} 1|0
goip_slot_signal_strength{device="goip-1",slot="1"} 85

// SMS operations
goip_sms_sent_total{device="goip-1"} 1234
goip_sms_failed_total{device="goip-1"} 5
goip_sms_queue_depth 12

// USSD operations
goip_ussd_sent_total{device="goip-1"} 567
goip_ussd_failed_total{device="goip-1"} 2
goip_ussd_response_time_seconds{device="goip-1"} 2.5
```

### Health Checks

```go
type GoIPHealth struct {
    DeviceReachable bool          `json:"device_reachable"`
    AuthValid       bool          `json:"auth_valid"`
    SIMSlotsOnline  int           `json:"sim_slots_online"`
    SIMSlotsTotal   int           `json:"sim_slots_total"`
    LastPoll        time.Time     `json:"last_poll"`
    Errors          []HealthError `json:"errors"`
}
```

## Legacy vs Modern Comparison

| Aspect | Legacy (PHP) | Modern (Go) |
|--------|-------------|-------------|
| **Protocol** | UDP + HTTP | HTTP/JSON (primary) |
| **Authentication** | Plain text | Hashed passwords |
| **Error Handling** | Minimal | Comprehensive with retry |
| **Logging** | File-based | Structured JSON logs |
| **Security** | Exploitation tools included | Security-first, no exploits |
| **Monitoring** | Manual checks | Prometheus metrics |

## Security Considerations

### Legacy Security Issues (NOT Replicated)

⚠️ **The following legacy capabilities are intentionally excluded**:

1. **DblTekGoIPPwn Exploitation**
   - Challenge-response vulnerability exploitation
   - Unauthorized root shell access
   - Firmware modification
   
2. **Plain Text Credentials**
   - Passwords stored in config files
   - No encryption for network communication

3. **No Access Control**
   - Any user could send SMS/USSD
   - No audit trail

### Modern Security Features

✅ **Modern implementation includes**:

1. **Authenticated Access**
   - JWT tokens for API access
   - Role-based permissions

2. **Encrypted Storage**
   - Password hashing (bcrypt)
   - Sensitive data encryption

3. **Audit Logging**
   - All operations logged
   - Compliance reporting

4. **Rate Limiting**
   - SMS rate limits per device
   - API request throttling

---

*Generated by /legacy reverse engineering - SDD for GoIP integration (security-compliant)*
