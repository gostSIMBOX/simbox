# ADR-003: Soft Deletes for All Entities

**Status**: Accepted  
**Date**: 2026-03-04  
**Type**: Data Design Decision  
**Source**: `/legacy` reverse engineering

## Context

The application manages critical infrastructure data:
- SIM-Bank devices (hardware inventory)
- SIM Slots (active SIM cards)
- Scheduler Tasks (automated operations)
- System Events (audit trail)

We need to decide how to handle record deletion to balance:
- Data integrity and audit requirements
- Storage efficiency
- Query simplicity

### Requirements

- Maintain audit trail for compliance
- Support data recovery (accidental deletions)
- Track entity history
- Support "active" filtering in queries

### Constraints

- PostgreSQL database
- GORM ORM
- Regulatory requirements for telecom data retention
- Operator need to see historical configurations

## Decision

**Use soft deletes for all entity tables via GORM's `gorm.DeletedAt` field.**

### Implementation

```go
// All models include DeletedAt field
type SimBank struct {
    ID        uint           `gorm:"primarykey"`
    Name      string         `gorm:"size:100;not null"`
    // ... other fields ...
    DeletedAt gorm.DeletedAt `gorm:"index"`  // Soft delete field
}

type SimSlot struct {
    ID        uint           `gorm:"primarykey"`
    // ... other fields ...
    DeletedAt gorm.DeletedAt `gorm:"index"`
}

type SchedulerTask struct {
    ID         uint           `gorm:"primarykey"`
    // ... other fields ...
    DeletedAt  gorm.DeletedAt `gorm:"index"`
}

type SystemEvent struct {
    ID        uint           `gorm:"primarykey"`
    // ... other fields ...
    DeletedAt gorm.DeletedAt `gorm:"index"`
}
```

### Behavior

```go
// Soft delete (default GORM behavior with DeletedAt field)
database.DB.Delete(&simBank)
// SQL: UPDATE sim_banks SET deleted_at = '2026-03-04 12:00:00' WHERE id = 1

// Query automatically excludes deleted records
database.DB.First(&simBank, 1)
// SQL: SELECT * FROM sim_banks WHERE id = 1 AND deleted_at IS NULL

// Include deleted records explicitly
database.DB.Unscoped().First(&simBank, 1)
// SQL: SELECT * FROM sim_banks WHERE id = 1

// Permanently delete
database.DB.Unscoped().Delete(&simBank)
// SQL: DELETE FROM sim_banks WHERE id = 1
```

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GORM ORM Layer                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Default Queries (exclude deleted)               │   │
│  │  WHERE ... AND deleted_at IS NULL                │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Unscoped Queries (include deleted)              │   │
│  │  WHERE ... (no deleted_at filter)                │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Delete Operation (soft)                         │   │
│  │  UPDATE ... SET deleted_at = NOW()               │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Rationale

**Soft deletes were chosen because:**

1. **Audit trail**: Deleted entities remain in database for compliance
2. **Data recovery**: Accidental deletions can be undone
3. **Historical analysis**: Track entity lifecycle over time
4. **Referential integrity**: Foreign keys remain valid (no orphaned records)
5. **GORM support**: Built-in feature, well-tested pattern

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Hard deletes** | Clean tables, simple queries | No audit trail, no recovery | Violates compliance requirements |
| **Audit table** | Separates current/historical | Complex queries, dual writes | More complex than soft deletes |
| **is_deleted flag** | Simple, explicit | No timestamp, manual filtering | DeletedAt provides more information |
| **Event sourcing** | Complete history | Complex implementation | Over-engineering for this use case |

## Consequences

### Positive

- **Audit compliance**: All deletions tracked with timestamp
- **Recovery possible**: Undelete by setting `deleted_at = NULL`
- **Automatic filtering**: GORM excludes deleted by default
- **Historical queries**: Can query deleted records with `Unscoped()`
- **Foreign key safety**: Related records remain valid

### Negative

- **Storage growth**: Deleted records consume disk space
- **Query complexity**: Must remember `Unscoped()` for historical queries
- **Unique constraints**: Deleted records still count toward uniqueness
- **Performance**: Indexes include deleted records

### Mitigation Strategies

1. **Periodic cleanup**: Archive old deleted records to cold storage
2. **Clear documentation**: Document when to use `Unscoped()`
3. **Monitoring**: Track table growth, alert on unusual deletion patterns

## Query Patterns

### Standard Queries (exclude deleted)
```go
// Get active SIM-banks
database.DB.Where("is_active = ?", true).Find(&simBanks)

// Get specific slot
database.DB.First(&slot, id)
```

### Historical Queries (include deleted)
```go
// Get all SIM-banks (including deleted)
database.DB.Unscoped().Find(&simBanks)

// Get deletion history
database.DB.Unscoped().
    Where("deleted_at IS NOT NULL").
    Find(&deletedBanks)
```

### Recovery
```go
// Undelete a SIM-bank
database.DB.Unscoped().
    Model(&simBank).
    Update("deleted_at", nil)
```

## Compliance

**Compliant Flows**:
- `flows/sdd-database-layer/02-specifications.md` - Data model specifications

**Database Schema**:
```sql
-- All tables include deleted_at column
CREATE TABLE sim_banks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    -- ... other columns ...
    deleted_at TIMESTAMPTZ  -- Soft delete timestamp
);

CREATE INDEX idx_sim_banks_deleted_at ON sim_banks(deleted_at);
```

## Notes

**When to use hard deletes** (via `Unscoped().Delete()`):
- GDPR "right to be forgotten" requests
- Data retention policy expiration
- Sensitive data removal

**Retention policy recommendation**:
- Keep deleted records for 90 days minimum
- Archive to cold storage after 1 year
- Permanent deletion after 7 years (compliance dependent)

---

*Generated by /legacy reverse engineering - DRAFT for review*
