# Database Layer - Specifications

> Spec-Driven Development: Technical specifications for database layer domain.

## Overview

**Domain**: Database Layer  
**Type**: SDD  
**Status**: DRAFT (Legacy Analysis Generated)  
**Generated**: 2026-03-04  

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Global DB Instance                      │    │
│  │              (*gorm.DB)                              │    │
│  └─────────────────────────────────────────────────────┘    │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │  SimBank    │     │  SimSlot    │     │ Scheduler-  │   │
│  │  Model      │     │  Model      │     │ Task Model  │   │
│  └─────────────┘     └─────────────┘     └─────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SystemEvent Model                       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │  PostgreSQL   │
                  │   Database    │
                  └───────────────┘
```

## Component Specifications

### Database Connection

**Package**: `internal/database`

**Global Instance**:
```go
var DB *gorm.DB
```

**Functions**:

| Function | Signature | Purpose |
|----------|-----------|---------|
| Connect | `Connect(cfg *DatabaseConfig) error` | Initialize connection |
| Close | `Close() error` | Close connection |
| AutoMigrate | `AutoMigrate() error` | Migrate schema |

### Connection Configuration

```go
func Connect(cfg *DatabaseConfig) error {
    dsn := cfg.GetDSN()
    
    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
        NamingStrategy: schema.NamingStrategy{
            SingularTable: true,  // sim_banks, not sim_bankss
        },
        Logger: gormlogger.Default.LogMode(gormlogger.Info),
    })
    
    sqlDB, _ := db.DB()
    sqlDB.SetMaxIdleConns(5)
    sqlDB.SetMaxOpenConns(cfg.MaxConns)
    sqlDB.SetConnMaxLifetime(time.Hour)
    
    DB = db
}
```

### Connection Pool Settings

| Setting | Value | Description |
|---------|-------|-------------|
| MaxIdleConns | 5 | Minimum idle connections |
| MaxOpenConns | 10 (configurable) | Maximum open connections |
| ConnMaxLifetime | 1 hour | Connection reuse duration |

## Data Models

### SimBank

**Table**: `sim_banks`

**Purpose**: Registry of SIM-bank devices.

```go
type SimBank struct {
    ID        uint           `gorm:"primarykey"`
    Name      string         `gorm:"size:100;not null"`
    Type      string         `gorm:"size:50;not null"`  // SMB128, SMB32
    URL       string         `gorm:"size:255;not null"`
    IsActive  bool           `gorm:"default:true"`
    CreatedAt time.Time
    UpdatedAt time.Time
    DeletedAt gorm.DeletedAt `gorm:"index"`
    
    Slots []SimSlot `gorm:"foreignKey:SimBankID"`
}
```

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| ID | uint | PRIMARY KEY | Auto-increment |
| Name | string(100) | NOT NULL | Device name |
| Type | string(50) | NOT NULL | Device model |
| URL | string(255) | NOT NULL | HTTP API URL |
| IsActive | bool | DEFAULT true | Active status |
| CreatedAt | time | | Creation timestamp |
| UpdatedAt | time | | Update timestamp |
| DeletedAt | gorm.DeletedAt | INDEX | Soft delete |

### SimSlot

**Table**: `sim_slots`

**Purpose**: State of individual SIM slots.

```go
type SimSlot struct {
    ID        uint           `gorm:"primarykey"`
    SimBankID uint           `gorm:"not null"`
    SlotID    int            `gorm:"not null"`
    IMSI      string         `gorm:"size:15;index"`
    ICCID     string         `gorm:"size:20"`
    Operator  string         `gorm:"size:50"`
    Status    string         `gorm:"size:20;default:'offline'"`
    Power     bool           `gorm:"default:false"`
    Signal    int            `gorm:"default:0"`
    Mode      string         `gorm:"size:20"`
    IsActive  bool           `gorm:"default:true"`
    CreatedAt time.Time
    UpdatedAt time.Time
    DeletedAt gorm.DeletedAt `gorm:"index"`
    
    SimBank SimBank `gorm:"foreignKey:SimBankID"`
}
```

**Status Values**: `online`, `offline`, `error`, `busy`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| ID | uint | PRIMARY KEY | Auto-increment |
| SimBankID | uint | FOREIGN KEY | Reference to sim_banks |
| SlotID | int | NOT NULL | Slot number |
| IMSI | string(15) | INDEX | SIM identifier |
| ICCID | string(20) | | Card identifier |
| Operator | string(50) | | Network operator |
| Status | string(20) | DEFAULT 'offline' | Slot status |
| Power | bool | DEFAULT false | Power state |
| Signal | int | DEFAULT 0 | Signal strength |
| Mode | string(20) | | Operation mode |
| IsActive | bool | DEFAULT true | Active flag |

### SchedulerTask

**Table**: `scheduler_tasks`

**Purpose**: Scheduled task definitions.

```go
type SchedulerTask struct {
    ID         uint           `gorm:"primarykey"`
    Name       string         `gorm:"size:100;not null"`
    Type       string         `gorm:"size:50;not null"`
    Status     string         `gorm:"size:20;default:'pending'"`
    Schedule   string         `gorm:"size:100"`  // cron expression
    Parameters string         `gorm:"type:text"`  // JSON
    LastRun    *time.Time
    NextRun    *time.Time
    RetryCount int            `gorm:"default:0"`
    MaxRetries int            `gorm:"default:3"`
    IsActive   bool           `gorm:"default:true"`
    CreatedAt  time.Time
    UpdatedAt  time.Time
    DeletedAt  gorm.DeletedAt `gorm:"index"`
}
```

**Type Values**: `power_cycle`, `sync`, `maintenance`

**Status Values**: `pending`, `running`, `completed`, `failed`

### SystemEvent

**Table**: `system_events`

**Purpose**: Event audit trail.

```go
type SystemEvent struct {
    ID        uint           `gorm:"primarykey"`
    Type      string         `gorm:"size:50;not null"`
    Source    string         `gorm:"size:100;not null"`
    Message   string         `gorm:"type:text;not null"`
    Data      string         `gorm:"type:text"`  // JSON
    Level     string         `gorm:"size:20;default:'info'"`
    IsRead    bool           `gorm:"default:false"`
    CreatedAt time.Time
    UpdatedAt time.Time
    DeletedAt gorm.DeletedAt `gorm:"index"`
}
```

**Type Values**: `info`, `warning`, `error`, `critical`

**Source Values**: `simbank`, `scheduler`, `hardware`

## Database Schema

### Table Relationships

```
sim_banks (1) ──────< (N) sim_slots
```

### Indexes

| Table | Column | Type | Purpose |
|-------|--------|------|---------|
| sim_slots | imsi | INDEX | Fast IMSI lookups |
| sim_banks | deleted_at | INDEX | Soft delete queries |
| sim_slots | deleted_at | INDEX | Soft delete queries |
| scheduler_tasks | deleted_at | INDEX | Soft delete queries |
| system_events | deleted_at | INDEX | Soft delete queries |

## Operations

### Connect

```go
func Connect(cfg *DatabaseConfig) error
```

**Steps**:
1. Build DSN from config
2. Open GORM connection
3. Configure connection pool
4. Store in global variable
5. Log success

### Close

```go
func Close() error
```

**Steps**:
1. Get underlying sql.DB
2. Close connection
3. Log closure

### AutoMigrate

```go
func AutoMigrate() error
```

**Models**: SimBank, SimSlot, SchedulerTask, SystemEvent

**Steps**:
1. Check DB connected
2. Call GORM AutoMigrate
3. Log completion

## Configuration

### DatabaseConfig

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| Host | string | localhost | Database host |
| Port | int | 5432 | Database port |
| User | string | | Database user |
| Password | string | | Database password |
| DBName | string | | Database name |
| SSLMode | string | disable | SSL mode |
| MaxConns | int | 10 | Max connections |

### GetDSN

```go
func (c *DatabaseConfig) GetDSN() string
```

**Returns**: `host={host} port={port} user={user} password={password} dbname={dbname} sslmode={sslmode}`

---

*Generated by /legacy reverse engineering - DRAFT for review*
