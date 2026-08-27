# ADR-002: Global Database Instance Pattern

**Status**: Accepted  
**Date**: 2026-03-04  
**Type**: Architectural Decision  
**Source**: `/legacy` reverse engineering

## Context

The application requires database access from multiple components:
- SIM-Bank Manager (read/write slot state)
- API Handlers (CRUD operations)
- Event Logger (write system events)
- Scheduler (read/write tasks)

We need to decide how to provide database access throughout the application.

### Requirements

- Single connection pool (avoid connection exhaustion)
- Consistent configuration across components
- Simple access pattern (minimal boilerplate)
- Support for GORM ORM

### Constraints

- Go application (single process, single binary)
- PostgreSQL database
- GORM ORM for data access
- Moderate concurrency (10-100 requests/second)

## Decision

**Use a package-level global variable for the database instance.**

### Implementation

```go
// internal/database/database.go
package database

import "gorm.io/gorm"

// DB is the global database instance
var DB *gorm.DB

// Connect initializes the database connection
func Connect(cfg *config.DatabaseConfig) error {
    dsn := cfg.GetDSN()
    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{...})
    if err != nil {
        return err
    }
    
    sqlDB, err := db.DB()
    if err != nil {
        return err
    }
    
    // Configure connection pool
    sqlDB.SetMaxIdleConns(5)
    sqlDB.SetMaxOpenConns(cfg.MaxConns)
    sqlDB.SetConnMaxLifetime(time.Hour)
    
    DB = db  // Store in global variable
    return nil
}
```

### Usage Pattern

```go
// Any component can access the database
import "github.com/gostsimbox/simhub/internal/database"

func GetSimBank(id uint) (*database.SimBank, error) {
    var simBank database.SimBank
    err := database.DB.First(&simBank, id).Error
    return &simBank, err
}
```

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Application                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ SimBank      │  │ API Handlers │  │ Logger       │  │
│  │ Manager      │  │              │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│         └─────────────────┼─────────────────┘           │
│                           │                             │
│                           ▼                             │
│              ┌────────────────────────┐                 │
│              │  database.DB           │                 │
│              │  (*gorm.DB)            │                 │
│              │  [Global Singleton]    │                 │
│              └───────────┬────────────┘                 │
└──────────────────────────┼─────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  PostgreSQL  │
                    │  Connection  │
                    │  Pool        │
                    └──────────────┘
```

## Rationale

**Global instance was chosen because:**

1. **Simplicity**: No dependency injection boilerplate
2. **Single process**: Go application runs as single binary (no multi-process concerns)
3. **GORM pattern**: GORM is designed for global instance usage
4. **Consistent configuration**: All components use same connection pool
5. **Low complexity**: Easy to understand and maintain

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Dependency Injection** | Testable, explicit dependencies | Boilerplate, complexity | Over-engineering for single-process app |
| **Context-based** | Clean cancellation, request-scoped | More complex, GORM doesn't require | Unnecessary for this use case |
| **Interface abstraction** | Mockable for tests | Extra layer, GORM already abstracts | GORM provides sufficient abstraction |
| **Per-component instances** | Isolation | Multiple pools, connection exhaustion | Defeats purpose of connection pooling |

## Consequences

### Positive

- **Simple access**: `database.DB` from anywhere
- **Single pool**: All components share connection pool
- **Easy initialization**: One `Connect()` call at startup
- **GORM conventions**: Follows GORM community patterns

### Negative

- **Testing complexity**: Global state harder to mock
- **Hidden dependency**: Database access not explicit in function signatures
- **Tight coupling**: Components depend on global variable

### Mitigation Strategies

1. **Test setup**: Initialize test database in test setup functions
2. **Integration tests**: Use real database for integration tests
3. **Clear ownership**: `internal/database` package owns the global variable

## Testing Approach

```go
// Test setup
func TestMain(m *testing.M) {
    // Connect to test database
    cfg := &config.DatabaseConfig{
        Host: "localhost",
        DBName: "simhub_test",
        // ...
    }
    database.Connect(cfg)
    
    // Run migrations
    database.AutoMigrate()
    
    // Run tests
    code := m.Run()
    
    // Cleanup
    database.Close()
    os.Exit(code)
}
```

## Compliance

**Compliant Flows**:
- `flows/sdd-database-layer/02-specifications.md` - Global DB instance specification

**Usage Examples**:
```go
// simbank/manager.go
database.DB.Where("is_active = ?", true).Find(&simBanks)

// api/handlers/simbank.go
database.DB.First(&simBank, id)
database.DB.Create(&simBank)
```

## Notes

This decision is appropriate for:
- Single-process Go applications
- Moderate concurrency workloads
- Teams comfortable with global state

Reconsider if:
- Application becomes multi-process
- Need fine-grained connection control
- Testing requirements become more stringent

---

*Generated by /legacy reverse engineering - DRAFT for review*
