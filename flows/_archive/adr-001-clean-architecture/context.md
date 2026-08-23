# ADR 001: Clean Architecture

## Status

**PROPOSED** → DRAFT

## Context

The GOSTsimbox Gateway requires a maintainable, testable architecture for a bidirectional GSM↔SIP/SMPP bridge application. The system must handle:

- Complex service orchestration (Gateway, SIP, SMS, Telephony)
- Multiple protocol implementations (SIP, SMPP, GSM)
- Platform-specific integrations (Android telephony via MethodChannel)
- Real-time state management and monitoring
- Extensive error handling and logging

### Requirements

1. **Separation of concerns** - Business logic must be isolated from UI and data access
2. **Testability** - Core logic must be testable without platform dependencies
3. **Maintainability** - Changes in one layer should not affect others
4. **Dependency management** - Clear dependency direction and inversion
5. **Scalability** - Support for future features and protocols

## Decision

We WILL implement **Clean Architecture** with four distinct layers:

### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  - screens/ (UI screens)                                    │
│  - widgets/ (Reusable components)                           │
│  - providers/ (State providers)                             │
│  - theme/ (Theming)                                         │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                            │
│  - entities/ (Business entities)                            │
│  - repositories/ (Repository interfaces)                    │
│  - usecases/ (Business use cases)                           │
│  - exceptions/ (Domain exceptions)                          │
├─────────────────────────────────────────────────────────────┤
│                       Data Layer                             │
│  - datasources/ (Local/Remote data sources)                 │
│  - repositories/ (Repository implementations)               │
│  - models/ (Data models/DTOs)                               │
│  - services/ (External service integrations)                │
├─────────────────────────────────────────────────────────────┤
│                        Core Layer                            │
│  - di/ (Dependency Injection)                               │
│  - error/ (Error handling)                                  │
│  - utils/ (Utilities)                                       │
│  - constants/ (Constants)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Rule

Dependencies point **inward only**:
- Presentation → Domain (and Core)
- Data → Domain (and Core)
- Domain → Core only
- Core → No internal dependencies

### Architecture Principles

1. **Dependency Inversion** - High-level modules don't depend on low-level modules; both depend on abstractions
2. **Single Responsibility** - Each class has one reason to change
3. **Open/Closed** - Open for extension, closed for modification
4. **Interface Segregation** - Clients don't depend on unused interfaces
5. **Dependency Injection** - Dependencies are provided from outside

## Consequences

### Positive

1. **Testability** - Domain layer can be tested without Flutter or platform dependencies
2. **Maintainability** - Clear boundaries make changes localized
3. **Reusability** - Domain logic is framework-independent
4. **Parallel development** - Teams can work on different layers simultaneously
5. **Clear responsibilities** - Each layer has well-defined concerns

### Negative

1. **Complexity** - More files and abstractions than simple architectures
2. **Learning curve** - Team must understand Clean Architecture patterns
3. **Boilerplate** - Repository interfaces, use cases, entities add code volume
4. **Over-engineering risk** - May be excessive for simple features

### Implementation Notes

- Repository pattern for data access abstraction
- Use Case pattern for business logic encapsulation
- Dependency Injection via get_it
- Error handling via centralized ErrorHandler
- State management via Provider pattern

## Compliance

- All new code MUST follow layer structure
- Domain layer MUST NOT import presentation or data layers
- Dependencies MUST point inward
- Repository interfaces MUST be in domain layer
- Use cases MUST encapsulate business logic

## Related Decisions

- ADR 002: Dependency Injection (get_it selection)
- ADR 003: State Management (Provider pattern)
- ADR 004: Error Handling (Centralized approach)

## References

- Clean Architecture by Robert C. Martin
- Flutter Clean Architecture examples
- Repository pattern documentation
- Use Case pattern documentation

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)  
**Status**: DRAFT - Pending review
