# ADR-003: File-Based State Persistence

## Status
DRAFT

## Type
Enabling

## Context
The chan_dongle driver needs to persist state across restarts and between function calls:

1. **Device state**: Balance, limits, provider info
2. **Call statistics**: Call counts, duration
3. **Configuration**: Group assignments, settings
4. **Error tracking**: Error counters, last error

### Requirements
- Simple key-value storage
- Fast read/write operations
- Persistence across restarts
- Human-readable for debugging
- No external dependencies

### Constraints
- Must work on embedded Linux systems
- Minimal resource usage
- No database server available
- Must handle concurrent access

## Decision
Use **file-based key-value storage** with a simple directory structure.

### Storage Structure
```
/var/svistok/
├── imsi/
│   ├── {imsi}.balance
│   ├── {imsi}.number
│   ├── {imsi}.limits
│   └── {imsi}.state
├── device/
│   └── {device}.config
└── global/
    └── settings
```

### File Format
- Integer values: Plain text decimal
- String values: Plain text
- One value per file

## Consequences

### Positive
- **Simplicity**: No database setup required
- **Debugging**: Files can be read with standard tools
- **Portability**: Works on any POSIX system
- **Low overhead**: No external dependencies
- **Atomic operations**: File write is atomic on most filesystems

### Negative
- **Scalability**: Not suitable for large datasets
- **Concurrency**: Requires file locking for writes
- **Query limitations**: No search or filter capabilities
- **Performance**: Slower than in-memory storage

### Technical Impact
- ~600 lines of code for storage layer
- File path construction for each operation
- Mutex protection for concurrent access
- Error handling for missing/corrupt files

## Alternatives Considered

### SQLite Database
- **Pros**: Better concurrency, query support, transactions
- **Cons**: External dependency, more complex, overkill for simple key-value

### In-Memory Storage
- **Pros**: Fast access
- **Cons**: No persistence across restarts

### MySQL Database
- **Pros**: Full database features
- **Cons**: Heavy dependency, network overhead, not suitable for embedded

## Related Decisions
- AT command queue architecture (ADR-001)
- 8-state call machine (ADR-006)

## References
- `share.c` - Core storage functions
- `share_mysql.c` - File-based implementation (despite name)
- `share.h` - Storage API

## Notes
Despite the filename `share_mysql.c`, the implementation uses file I/O, not MySQL. The MySQL includes are present but not used.
