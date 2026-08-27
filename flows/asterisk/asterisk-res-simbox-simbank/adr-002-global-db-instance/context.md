# ADR-002: Global Database Instance Pattern

**Date**: 2026-03-04  
**Status**: Accepted  
**Type**: Constraining  
**Source**: Legacy analysis via `/legacy` command

---

## Context

The application requires a centralized way to access the PostgreSQL database across multiple modules (simbank management, API handlers, event logging, scheduler). Each module needs to perform CRUD operations on shared data models while maintaining consistency and avoiding connection proliferation.

Key requirements:
- Single source of truth for database connection
- Connection pooling for performance
- Shared access from multiple goroutines
- Simple API for common operations
- Graceful connection management

---

## Decision

**Use a global `var DB *gorm.DB` instance for all database operations.**

All modules access the database through this global variable, which is initialized once at application startup and closed on shutdown.

Implementation details:
```go
// From database/database.go
var DB *gorm.DB

func Connect(cfg *config.DatabaseConfig) error {
    dsn := cfg.GetDSN()
    
    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
        NamingStrategy: schema.NamingStrategy{
            SingularTable: true,
        },
        Logger: gormlogger.Default.LogMode(gormlogger.Info),
    })
    
    if err != nil {
        return fmt.Errorf("failed to connect to database: %w", err)
    }
    
    // Connection pooling configuration
    sqlDB, err := db.DB()
    if err != nil {
        return fmt.Errorf("failed to get underlying sql.DB: %w", err)
    }
    
    sqlDB.SetMaxIdleConns(5)
    sqlDB.SetMaxOpenConns(cfg.MaxConns) // default: 10
    sqlDB.SetConnMaxLifetime(time.Hour)
    
    DB = db
    logger.Logger.Info("Database connected successfully")
    return nil
}

func Close() error {
    if DB != nil {
        sqlDB, err := DB.DB()
        if err != nil {
            return fmt.Errorf("failed to get underlying sql.DB: %w", err)
        }
        if err := sqlDB.Close(); err != nil {
            return fmt.Errorf("failed to close database: %w", err)
        }
        logger.Logger.Info("Database connection closed")
    }
    return nil
}
```

Usage pattern across modules:
```go
// From simbank/manager.go
err := database.DB.Where("is_active = ?", true).Find(&simBanks).Error

// From api/handlers/simbank.go
err := database.DB.Preload("Slots").First(&simBank, id).Error
```

---

## Consequences

### Positive

1. **Simplicity**: No dependency injection or context passing required
2. **Consistency**: All modules use the same connection with identical settings
3. **Performance**: Connection pooling (5 idle, 10 max open, 1h lifetime) reduces connection overhead
4. **Easy testing**: Can be mocked by reassigning the global variable
5. **Clear lifecycle**: Initialized once in `main.go`, closed on shutdown

### Negative

1. **Hidden dependency**: Modules implicitly depend on global state, making dependencies less explicit
2. **Testing complexity**: Tests must ensure proper initialization and cleanup to avoid cross-test contamination
3. **Single point of failure**: If the global DB instance becomes invalid, all database operations fail
4. **Limited flexibility**: Cannot easily support multiple database connections or per-request connection customization
5. **Concurrency concerns**: Requires careful handling of transactions to avoid conflicts

### Trade-offs

| Alternative | Pros | Cons | Why Not Chosen |
|-------------|------|------|----------------|
| **Dependency Injection** | Explicit dependencies, easier unit testing, multiple DB support | More boilerplate, requires passing DB through all function calls | Simplicity preferred for single-DB application |
| **Context-based DB** | Per-request customization, better tracing | More complex, requires context propagation everywhere | Not needed for current use case |
| **Repository Pattern** | Abstraction layer, easier to swap ORM | Additional layer of indirection, more code | GORM provides sufficient abstraction |
| **Global with Interface** | Mockable via interface, explicit contract | Still has global state issues | Added complexity not justified |

---

## Compliance

### Requirements Met
- REQ-NF-CONC-001: Thread-safe access (GORM is concurrent-safe)
- REQ-NF-PERF-001: Connection pooling configured
- Database layer SDD: Global instance with pooling

### Related SDDs
- `flows/sdd-database-layer/01-requirements.md` - Section 2.1 Connection Management
- `flows/sdd-database-layer/02-specifications.md` - Section 2.1 Connect()

---

## Notes

**Legacy Analysis Addition (2026-03-04)**:  
This ADR was reverse-engineered from existing code during `/legacy` BFS analysis. The global DB pattern is used consistently across all modules that require database access.

**Observed Usage**:
- `simbank/manager.go`: 12 usages of `database.DB`
- `api/handlers/simbank.go`: 9 usages of `database.DB`
- `database/database.go`: Connection management
- `database/models.go`: Model definitions (no direct DB usage)

**Connection Pool Settings** (from config):
- `MaxIdleConns`: Hardcoded to 5
- `MaxOpenConns`: Configurable via `database.max_conns` (default: 10)
- `ConnMaxLifetime`: Hardcoded to 1 hour

---

*Generated via /legacy analysis on 2026-03-04*
