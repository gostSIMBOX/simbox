# ADR 002: Dependency Injection - Status

## Decision Summary

**Use get_it as dependency injection framework**

## Status

- **Current**: DRAFT
- **Created**: 2026-03-03
- **Source**: Legacy analysis (/legacy command)

## Decision

| Aspect | Choice |
|--------|--------|
| DI Framework | get_it |
| Pattern | Service Locator + DI |
| Registration | Singleton, Lazy Singleton, Factory |
| Lifecycle | Managed via DependencyLifecycleManager |

## Context

- Multiple services with dependencies
- Need for lazy initialization
- Test support with mocks
- Type safety requirements

## Consequences

### Positive
- Simple API
- No code generation
- Type safety
- Lazy initialization
- Test-friendly

### Negative
- Service locator anti-pattern concerns
- Global state
- Runtime errors on missing registrations

## Alternatives Considered

| Alternative | Decision |
|-------------|----------|
| injectable + get_it | Too complex |
| Provider/Riverpod | For UI state only |
| Manual DI | Too verbose |

## Compliance

- All services registered in DependencyInjection
- External dependencies registered first
- Use cases depend on repository interfaces

## Related

- ADR 001: Clean Architecture
- ADR 003: State Management
- ADR 005: Service Orchestration

## Documents

- context.md - Full decision context

---

*Managed by /legacy flow*
