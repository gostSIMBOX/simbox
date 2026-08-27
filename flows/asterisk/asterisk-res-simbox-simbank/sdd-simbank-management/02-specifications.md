# SIM-Bank Management - Specifications

> Spec-Driven Development: Technical specifications for SIM-bank management domain.

## Overview

**Domain**: SIM-Bank Management  
**Type**: SDD  
**Status**: DRAFT (Legacy Analysis Generated)  
**Generated**: 2026-03-04  

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     SimBank Manager                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Client #1  │  │  Client #2  │  │  Client #N  │         │
│  │ (HTTP API)  │  │ (HTTP API)  │  │ (HTTP API)  │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
└─────────┼────────────────┼────────────────┼─────────────────┘
          │                │                │
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ SIM-Bank │    │ SIM-Bank │    │ SIM-Bank │
    │   #1     │    │   #2     │    │   #N     │
    └──────────┘    └──────────┘    └──────────┘
```

### Data Flow

```
[Manager.Start()]
      │
      ▼
[loadSimBanks()] ────► [PostgreSQL: sim_banks table]
      │
      ▼
[monitorLoop()] ────► [ticker: 30s interval]
      │
      ▼
[updateAllSimBanks()] ────► [goroutine per device]
      │
      ├────► [Client.GetStatus()] ────► [HTTP GET /status]
      │                                      │
      │                                      ▼
      │                                [SIM-Bank Hardware]
      │                                      │
      │                                      ▼
      │                                [StatusResponse]
      │                                      │
      ▼                                      ▼
[updateSlots()] ◄──────────────────── [slots data]
      │
      ▼
[PostgreSQL: sim_slots table] ────► [upsert operation]
```

## Component Specifications

### SimBank Manager

**Package**: `internal/simbank`

**Responsibilities**:
- Device lifecycle management
- Polling coordination
- Database synchronization
- Operation delegation

**Fields**:
```go
type Manager struct {
    clients map[uint]*Client  // Device clients by ID
    config  *config.SimBankConfig
    mutex   sync.RWMutex
    ctx     context.Context
    cancel  context.CancelFunc
}
```

**Methods**:

| Method | Signature | Purpose |
|--------|-----------|---------|
| NewManager | `NewManager(cfg *SimBankConfig) *Manager` | Create manager instance |
| Start | `Start() error` | Load devices, start polling |
| Stop | `Stop()` | Graceful shutdown |
| SetPower | `SetPower(simBankID uint, slotID int, power bool) error` | Control slot power |
| SendUSSD | `SendUSSD(simBankID uint, slotID int, command string) (string, error)` | Send USSD command |
| GetSimBankStatus | `GetSimBankStatus(simBankID uint) (*StatusResponse, error)` | Get device status |

### SimBank Client

**Package**: `internal/simbank`

**Responsibilities**:
- HTTP communication with device API
- Request/response serialization
- Error handling

**Fields**:
```go
type Client struct {
    baseURL    string
    httpClient *http.Client
    timeout    time.Duration
}
```

**Methods**:

| Method | Signature | HTTP Request |
|--------|-----------|--------------|
| GetStatus | `GetStatus() (*StatusResponse, error)` | GET /status |
| SetPower | `SetPower(slotID int, power bool) error` | POST /slot/power |
| SendUSSD | `SendUSSD(slotID int, command string) (*USSDResponse, error)` | POST /ussd |
| Ping | `Ping() error` | GET /ping |

### Data Structures

**StatusResponse**:
```go
type StatusResponse struct {
    Status string     // "online" | "offline" | "error"
    Slots  []SlotInfo // List of slot states
    Error  string     // Error message if any
}
```

**SlotInfo**:
```go
type SlotInfo struct {
    SlotID   int    // Slot number (1-based)
    IMSI     string // International Mobile Subscriber Identity
    ICCID    string // Integrated Circuit Card Identifier
    Operator string // Mobile network operator
    Status   string // "online" | "offline" | "error" | "busy"
    Power    bool   // Power state
    Signal   int    // Signal strength (0-100)
}
```

**PowerRequest**:
```go
type PowerRequest struct {
    SlotID int  `json:"slot_id"`
    Power  bool `json:"power"`
}
```

**USSDRequest/USSDResponse**:
```go
type USSDRequest struct {
    SlotID  int    `json:"slot_id"`
    Command string `json:"command"`
}

type USSDResponse struct {
    Response string `json:"response"`
    Error    string `json:"error,omitempty"`
}
```

## Database Schema

### sim_banks Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uint | PRIMARY KEY | Auto-increment ID |
| name | string(100) | NOT NULL | Device name |
| type | string(50) | NOT NULL | Device type (SMB128, SMB32) |
| url | string(255) | NOT NULL | HTTP API base URL |
| is_active | bool | DEFAULT true | Active flag |
| created_at | time | | Creation timestamp |
| updated_at | time | | Last update timestamp |
| deleted_at | gorm.DeletedAt | INDEX | Soft delete timestamp |

### sim_slots Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uint | PRIMARY KEY | Auto-increment ID |
| simbank_id | uint | FOREIGN KEY | Reference to sim_banks.id |
| slot_id | int | NOT NULL | Slot number |
| imsi | string(15) | INDEX | SIM IMSI |
| iccid | string(20) | | SIM ICCID |
| operator | string(50) | | Network operator |
| status | string(20) | DEFAULT 'offline' | online/offline/error/busy |
| power | bool | DEFAULT false | Power state |
| signal | int | DEFAULT 0 | Signal strength |
| mode | string(20) | | Operation mode |
| is_active | bool | DEFAULT true | Active flag |
| created_at | time | | Creation timestamp |
| updated_at | time | | Last update timestamp |
| deleted_at | gorm.DeletedAt | INDEX | Soft delete timestamp |

## Concurrency Model

### Polling Loop

```go
func (m *Manager) monitorLoop() {
    ticker := time.NewTicker(m.config.PollingInterval)
    defer ticker.Stop()

    for {
        select {
        case <-m.ctx.Done():
            return  // Graceful shutdown
        case <-ticker.C:
            m.updateAllSimBanks()  // Parallel update
        }
    }
}
```

### Parallel Device Updates

```go
func (m *Manager) updateAllSimBanks() {
    // Snapshot clients map (read-lock)
    m.mutex.RLock()
    clients := make(map[uint]*Client)
    for id, client := range m.clients {
        clients[id] = client
    }
    m.mutex.RUnlock()

    // Launch goroutine per device
    var wg sync.WaitGroup
    for simBankID, client := range clients {
        wg.Add(1)
        go func(id uint, c *Client) {
            defer wg.Done()
            m.updateSimBank(id, c)
        }(simBankID, client)
    }
    wg.Wait()  // Wait for all updates
}
```

### Thread-Safe Client Access

```go
func (m *Manager) SetPower(simBankID uint, slotID int, power bool) error {
    m.mutex.RLock()
    client, exists := m.clients[simBankID]
    m.mutex.RUnlock()

    if !exists {
        return fmt.Errorf("simbank %d not found", simBankID)
    }

    return client.SetPower(slotID, power)
}
```

## Error Handling

### Error Categories

| Category | Handling | Logging |
|----------|----------|---------|
| HTTP timeout | Retry on next poll | ERROR level |
| Device not found | Return 404 to API | INFO level |
| Database error | Log and continue | ERROR level |
| Invalid request | Return 400 to API | WARN level |

### Event Recording

```go
func (m *Manager) recordSystemEvent(eventType, source, message string, simBankID uint) {
    event := database.SystemEvent{
        Type:    eventType,  // "info" | "warning" | "error" | "critical"
        Source:  source,     // "simbank" | "scheduler" | "hardware"
        Message: message,
        Data:    fmt.Sprintf(`{"simbank_id": %d}`, simBankID),
        Level:   eventType,
    }
    database.DB.Create(&event)
}
```

## Configuration

### SimBankConfig

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| PollingInterval | time.Duration | 30s | Status polling interval |
| Timeout | time.Duration | 10s | HTTP client timeout |
| RetryAttempts | int | 3 | Number of retry attempts |
| RetryDelay | time.Duration | 5s | Delay between retries |

## API Endpoints

See: `flows/sdd-api-handlers/` for complete API specification.

---

*Generated by /legacy reverse engineering - DRAFT for review*
