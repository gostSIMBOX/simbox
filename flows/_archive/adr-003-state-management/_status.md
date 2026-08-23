# ADR 003: State Management - Status

## Decision Summary

**Use Provider for UI state management with service-level streams**

## Status

- **Current**: DRAFT
- **Created**: 2026-03-03
- **Source**: Legacy analysis (/legacy command)

## Decision

| Aspect | Choice |
|--------|--------|
| UI State | Provider + ChangeNotifier |
| Service State | StreamController (broadcast) |
| Integration | MultiProvider at app root |
| Pattern | Service streams + Provider |

## Context

- Real-time state updates required
- Multiple state sources
- Widget integration needed
- Testability requirements

## Consequences

### Positive
- Simple and easy to understand
- Flutter integration
- Testability
- Flexibility (streams, ChangeNotifier, values)
- Performance

### Negative
- Provider boilerplate
- Context dependency
- Stream management overhead

## Alternatives Considered

| Alternative | Decision |
|-------------|----------|
| Riverpod | Overkill for current needs |
| Bloc | Too much boilerplate |
| GetX | Controversial, mixes concerns |
| Redux | Too complex |

## Compliance

- Services expose state via streams
- UI state uses ChangeNotifier
- StreamControllers closed on dispose
- MultiProvider at app root

## Related

- ADR 001: Clean Architecture
- ADR 002: Dependency Injection
- ADR 005: Service Orchestration

## Documents

- context.md - Full decision context

---

*Managed by /legacy flow*
