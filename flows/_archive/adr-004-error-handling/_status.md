# ADR 004: Error Handling - Status

## Decision Summary

**Implement centralized ErrorHandler class with categorized handling**

## Status

- **Current**: DRAFT
- **Created**: 2026-03-03
- **Source**: Legacy analysis (/legacy command)

## Decision

| Aspect | Choice |
|--------|--------|
| Pattern | Centralized ErrorHandler |
| Categories | Application, Network, Validation, Auth, Permission |
| Storage | SharedPreferences (100 entries max) |
| UI | ErrorBoundary widget |
| Analytics | Integrated error tracking |

## Context

- Multiple error sources (network, platform, permissions)
- Need for user-friendly messages
- Logging and analytics requirements
- Graceful degradation needed

## Consequences

### Positive
- Consistent error handling
- User-friendly messages
- Comprehensive logging
- Error tracking for production
- Error persistence

### Negative
- Global state
- Analytics dependency
- Storage overhead
- Multiple handling paths

## Alternatives Considered

| Alternative | Decision |
|-------------|----------|
| dartz Either | Use for domain layer only |
| Zone-based | For uncaught errors only |
| Try-catch everywhere | Too repetitive |

## Compliance

- All errors caught and handled
- Critical errors logged and tracked
- User-friendly messages required
- Errors categorized by type
- ErrorBoundary wraps major UI sections

## Related

- ADR 001: Clean Architecture
- ADR 002: Dependency Injection
- ADR 003: State Management

## Documents

- context.md - Full decision context

---

*Managed by /legacy flow*
