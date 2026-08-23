# ADR 005: Service Orchestration - Status

## Decision Summary

**Implement GatewayService as central orchestrator with bidirectional routing**

## Status

- **Current**: DRAFT
- **Created**: 2026-03-03
- **Source**: Legacy analysis (/legacy command)

## Decision

| Aspect | Choice |
|--------|--------|
| Pattern | Central Orchestrator (GatewayService) |
| Routing | Bidirectional (SIP↔GSM) |
| Events | Stream-based coordination |
| Initialization | Ordered (Telephony → SIP → SMPP) |

## Context

- Multiple services to coordinate
- Bidirectional call routing required
- Event coordination needed
- Error isolation required

## Consequences

### Positive
- Centralized orchestration
- Clear responsibilities
- Event coordination
- Bidirectional routing
- Error isolation
- State consistency

### Negative
- Coupling to sub-services
- Complex routing logic
- Single point of failure
- Testing complexity

## Alternatives Considered

| Alternative | Decision |
|-------------|----------|
| Event Bus | Direct listeners for clarity |
| Mediator | GatewayService acts as mediator |
| Microservices | Overkill for mobile app |

## Compliance

- GatewayService orchestrates all sub-services
- Services expose state via streams
- Event listeners set up during initialization
- Bidirectional routing supported
- Service errors contained

## Related

- ADR 001: Clean Architecture
- ADR 002: Dependency Injection
- ADR 003: State Management

## Documents

- context.md - Full decision context

---

*Managed by /legacy flow*
