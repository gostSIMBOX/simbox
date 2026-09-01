# ADR-001: Platform Interface Pattern

## Decision

Use Flutter's **Platform Interface Pattern** with token-based verification.

**Type**: Enabling

**Status**: DRAFT

## Summary

Adopted Flutter's standard platform interface pattern using the `plugin_platform_interface` package to enable cross-platform SMS functionality with proper abstraction, testability, and extensibility.

## Key Points

- **Abstract Base**: `FlutterSmsussdPlatform` extends `PlatformInterface`
- **Token Verification**: Prevents unauthorized platform implementations
- **Default Implementation**: Method channel version
- **Data Models**: `SmsMessage` and `SmsType` in platform interface
- **6 Platform Methods**: All operations defined in abstract class

## Consequences

**Positive**:
- Single API across platforms
- Testable without native dependencies
- Follows Flutter best practices
- Easy to add new platforms

**Negative**:
- Added complexity and boilerplate
- Runtime errors for unsupported platforms

---

*See context.md for full details*
