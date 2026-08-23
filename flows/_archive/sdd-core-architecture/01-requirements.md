# Requirements: Core Architecture

## Overview

The GOSTsimbox Gateway requires a robust, maintainable architecture to support bidirectional GSM↔SIP/SMPP bridging with clear separation of concerns and testability.

## Functional Requirements

### FR-1: Clean Architecture Implementation

The system SHALL implement Clean Architecture with four distinct layers:

| Layer | Responsibility |
|-------|----------------|
| **Presentation** | UI rendering, user input handling, state management |
| **Domain** | Business logic, use cases, domain entities |
| **Data** | Data access, external APIs, local storage |
| **Core** | Cross-cutting concerns (DI, error handling, utilities) |

### FR-2: Dependency Injection

The system SHALL provide a centralized dependency injection system:

- Use get_it as the DI container
- Support singleton and lazy singleton patterns
- Register external dependencies (SharedPreferences, HTTP Client, Logger)
- Register services, repositories, and use cases
- Support dependency lifecycle management (initialize/dispose)

### FR-3: Error Handling

The system SHALL provide centralized error handling:

- Global error capture via FlutterError.onError
- Error logging to local storage (max 100 entries, 24-hour retention)
- Integration with analytics for error tracking
- User-friendly error messages
- UI error boundaries for graceful degradation

### FR-4: State Management

The system SHALL provide state management via Provider pattern:

- MultiProvider setup for core services
- Real-time state updates for gateway status
- Persistent configuration storage

### FR-5: Service Architecture

The system SHALL provide the following core services:

| Service | Purpose |
|---------|---------|
| GatewayService | Core gateway logic (GSM↔SIP bridging) |
| SipService | SIP protocol handling |
| SmsService | SMS message handling |
| TelephonyService | GSM telephony integration |
| SmppService | SMPP protocol for SMS |
| StorageService | Local data persistence |
| ThemeService | Theme management |
| LocalizationService | i18n support |

## Non-Functional Requirements

### NFR-1: Maintainability

- Each class SHALL have a single responsibility (SRP)
- Dependencies SHALL point toward abstractions (DIP)
- Components SHALL be open for extension, closed for modification (OCP)

### NFR-2: Testability

- Business logic SHALL be isolated in domain layer
- External dependencies SHALL be injectable for mocking
- Use cases SHALL be independently testable

### NFR-3: Performance

- DI initialization SHALL complete within 2 seconds
- Error logging SHALL not block UI thread
- State updates SHALL be efficient (no unnecessary rebuilds)

### NFR-4: Reliability

- Critical errors SHALL be logged and reported
- Service health checks SHALL be available
- Graceful degradation on service failures

## Architecture Principles

1. **Dependency Inversion** - High-level modules don't depend on low-level modules; both depend on abstractions
2. **Single Responsibility** - Each class has one reason to change
3. **Open/Closed** - Open for extension, closed for modification
4. **Interface Segregation** - Clients don't depend on unused interfaces
5. **Dependency Injection** - Dependencies are provided from outside

## Constraints

- Flutter SDK 3.8.1 or higher
- Android API level 21+ minimum
- Material Design 3 for UI components

---

**Status**: DRAFT  
**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)
