# ADR-003: Soft Deletes for All Data Models

**Date**: 2026-03-04  
**Status**: Accepted  
**Type**: Constraining  
**Source**: Legacy analysis via `/legacy` command

---

## Context

The system manages critical infrastructure data including SIM-banks, SIM slots, scheduler tasks, and system events. Business requirements dictate that data should never be permanently deleted to maintain an audit trail, support compliance requirements, and enable recovery from accidental deletions.

Key requirements:
- Maintain historical records for audit purposes
- Support data recovery after "deletion"
- Preserve referential integrity
- Track when records were deleted
- Filter out deleted records in normal queries

---

## Decision

**Use GORM's soft delete feature (`gorm.DeletedAt`) for all data models.**

All four data models (SimBank, SimSlot, SchedulerTask, SystemEvent) include a `DeletedAt` field that GORM uses to implement soft deletes automatically.

Implementation details:
```go
// From database/models.go
type SimBank struct {
    ID        uint           `gorm:"primarykey"`
    Name      string         `gorm:"size:100;not null"`
    // ... other fields ...
    DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
    // ... relations ...
}

type SimSlot struct {
    ID        uint           `gorm:"primarykey"`
    SimBankID uint           `gorm:"not null"`
    // ... other fields ...
    DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
    // ... relations ...
}

type SchedulerTask struct {
    ID        uint           `gorm:"primarykey"`
    Name      string         `gorm:"size:100;not null"`
    // ... other fields ...
    DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

type SystemEvent struct {
    ID        uint           `gorm:"primarykey"`
    Type      string         `gorm:"size:50;not null"`
    // ... other fields ...
    DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}
```

GORM behavior with soft deletes:
- `DB.Delete(&model)` → Sets `DeletedAt` to current timestamp instead of deleting row
- `DB.First(&model)` → Automatically adds `WHERE deleted_at IS NULL`
- `DB.Unscoped().Delete(&model)` → Forces hard delete (permanent)
- `DB.Unscoped().First(&model)` → Includes deleted records in query

---

## Consequences

### Positive

1. **Audit trail**: All deletions are tracked with timestamp
2. **Data recovery**: "Deleted" records can be restored by setting `DeletedAt` to nil
3. **Referential integrity**: Foreign key relationships remain valid after "deletion"
4. **Automatic filtering**: GORM automatically excludes deleted records from normal queries
5. **Compliance**: Meets regulatory requirements for data retention
6. **Accidental deletion protection**: Easy to recover from mistakes

### Negative

1. **Storage growth**: Database size increases over time as records are never truly deleted
2. **Query complexity**: Must use `Unscoped()` to include deleted records when needed
3. **Unique constraints**: Deleted records still count toward unique constraints, may cause conflicts
4. **Performance**: Index on `DeletedAt` required for efficient filtering
5. **Data export**: Must explicitly filter out deleted records when exporting data

### Trade-offs

| Alternative | Pros | Cons | Why Not Chosen |
|-------------|------|------|----------------|
| **Hard deletes** | Simpler queries, no storage growth | No audit trail, no recovery, compliance violations | Unacceptable for critical infrastructure data |
| **Manual soft deletes** | Full control over implementation | Error-prone, inconsistent across models | GORM provides built-in solution |
| **Audit log table** | Centralized audit trail, detailed history | Complex queries, separate from data | Soft deletes simpler for basic requirements |
| **Temporal tables** | Full history, point-in-time queries | Database-specific feature, complex | Overkill for current requirements |

---

## Compliance

### Requirements Met
- Audit trail requirement: Deletions tracked via `DeletedAt` timestamp
- Data retention: Records preserved indefinitely
- Referential integrity: Foreign keys remain valid

### Related SDDs
- `flows/sdd-database-layer/01-requirements.md` - Section 4.1-4.4 (all models include DeletedAt)
- `flows/sdd-database-layer/02-specifications.md` - Section 2 (all model structs)

---

## Notes

**Legacy Analysis Addition (2026-03-04)**:  
This ADR was reverse-engineered from existing code during `/legacy` BFS analysis. All four data models consistently use `gorm.DeletedAt` field with index annotation.

**Model Coverage**:
- ✅ `SimBank` - Has `DeletedAt gorm.DeletedAt`
- ✅ `SimSlot` - Has `DeletedAt gorm.DeletedAt`
- ✅ `SchedulerTask` - Has `DeletedAt gorm.DeletedAt`
- ✅ `SystemEvent` - Has `DeletedAt gorm.DeletedAt`

**Database Migration**:
```go
// AutoMigrate automatically creates soft delete indexes
// Index name: idx_{table}_deleted_at
```

---

*Generated via /legacy analysis on 2026-03-04*
