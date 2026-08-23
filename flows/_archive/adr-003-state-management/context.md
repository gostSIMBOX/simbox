# ADR 003: State Management

## Status

**PROPOSED** → DRAFT

## Context

The GOSTsimbox Gateway requires state management for:

- Gateway status (running, stopped, connection states)
- Call routing state (active calls, call states)
- SMS message state (message history, delivery status)
- Theme state (light, dark, system)
- Connection monitoring (latency, network quality)
- Settings and configuration

### Requirements

1. **Real-time updates** - UI must reflect state changes immediately
2. **Multiple state sources** - Different services produce state
3. **Widget integration** - Must work seamlessly with Flutter widgets
4. **Testability** - State must be mockable for tests
5. **Simplicity** - Team must understand and maintain easily

## Decision

We WILL use **Provider** for UI state management with service-level state streams.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   MultiProvider                       │   │
│  │  ┌────────────────────────────────────────────────┐   │   │
│  │  │  Provider<GatewayService>.value(value: ...)    │   │   │
│  │  │  Provider<SipService>.value(value: ...)        │   │   │
│  │  │  Provider<SmsService>.value(value: ...)        │   │   │
│  │  │  Provider<TelephonyService>.value(value: ...)  │   │   │
│  │  │  ChangeNotifierProvider<ThemeService>          │   │   │
│  │  └────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Service-Level State (Streams)

Services maintain internal state and broadcast changes:

```dart
class GatewayService {
  final StreamController<GatewayStatus> _statusController =
      StreamController<GatewayStatus>.broadcast();
  
  Stream<GatewayStatus> get statusStream => _statusController.stream;
  
  void _updateStatus() {
    _statusController.add(getStatus());
  }
}
```

### UI State (ChangeNotifier)

For UI-specific state, use ChangeNotifier:

```dart
class ThemeService extends ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.dark;
  
  ThemeMode get themeMode => _themeMode;
  
  Future<void> setDarkTheme() async {
    if (_themeMode != ThemeMode.dark) {
      _themeMode = ThemeMode.dark;
      notifyListeners();  // Notify UI
    }
  }
}
```

### Widget Integration

```dart
// In main.dart
MultiProvider(
  providers: [
    Provider<GatewayService>.value(value: GatewayService()),
    Provider<SipService>.value(value: SipService()),
    ChangeNotifierProvider<ThemeService>(
      create: (_) => ThemeService(),
    ),
  ],
  child: MaterialApp(...),
);

// In widgets
class DashboardWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final gatewayService = context.watch<GatewayService>();
    
    return StreamBuilder<GatewayStatus>(
      stream: gatewayService.statusStream,
      builder: (context, snapshot) {
        final status = snapshot.data;
        return Text('Status: ${status?.isRunning}');
      },
    );
  }
}
```

## Consequences

### Positive

1. **Simplicity** - Provider is easy to understand and use
2. **Flutter integration** - Works seamlessly with widget tree
3. **Testability** - Easy to provide mock services
4. **Flexibility** - Can use streams, ChangeNotifier, or values
5. **Performance** - Efficient rebuilds with proper usage
6. **Community support** - Widely used, well-documented

### Negative

1. **Boilerplate** - Requires Provider wrappers
2. **Context dependency** - Must have BuildContext for access
3. **Not global** - Services tied to widget tree location
4. **Stream management** - Must manually close StreamControllers

### Alternatives Considered

**Riverpod:**
- Pros: Compile-time safety, no context needed, better testing
- Cons: Learning curve, migration complexity
- Decision: Provider is sufficient for current needs

**Bloc:**
- Pros: Clear state management, event-driven
- Cons: More boilerplate, steeper learning curve
- Decision: Overkill for current state complexity

**GetX:**
- Pros: Simple API, many features
- Cons: Controversial, mixes concerns
- Decision: Provider is more aligned with Flutter best practices

**Redux:**
- Pros: Predictable state, time-travel debugging
- Cons: Significant boilerplate, complexity
- Decision: Too much for current needs

## Compliance

- Services MUST expose state via streams
- UI state MUST use ChangeNotifier with Provider
- StreamControllers MUST be closed on dispose
- Services MUST be provided via MultiProvider at app root
- Widgets MUST use context.watch() or StreamBuilder

## Related Decisions

- ADR 001: Clean Architecture (layer separation)
- ADR 002: Dependency Injection (get_it for services)
- ADR 005: Service Orchestration (GatewayService streams)

## References

- Provider package: https://pub.dev/packages/provider
- Provider documentation
- Flutter state management best practices

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)  
**Status**: DRAFT - Pending review
