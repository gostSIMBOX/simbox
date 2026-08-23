# ADR 004: Error Handling

## Status

**PROPOSED** → DRAFT

## Context

The GOSTsimbox Gateway requires comprehensive error handling for:

- Network errors (SIP, SMPP, HTTP)
- Platform channel errors (Android telephony)
- Permission errors
- Configuration errors
- Service initialization failures
- Call routing failures

### Requirements

1. **Centralized handling** - Single point for error processing
2. **User-friendly messages** - Clear messages for end users
3. **Logging** - All errors must be logged for debugging
4. **Analytics integration** - Track errors for monitoring
5. **Graceful degradation** - App should continue on non-critical errors
6. **Error persistence** - Store critical errors for later analysis

## Decision

We WILL implement a **centralized ErrorHandler** class with the following capabilities:

### Architecture

```dart
// lib/core/error/error_handler.dart

class ErrorHandler {
  static final Logger _logger = Logger();
  static const String _errorLogKey = 'error_logs';
  static const int _maxErrorLogs = 100;
  
  /// Handle all application errors
  static void handleError(dynamic error, StackTrace? stackTrace) {
    _logger.e('Application error occurred', error: error, stackTrace: stackTrace);
    _saveErrorToLog(error, stackTrace);
    _sendErrorToAnalytics(error, stackTrace);
    _showUserFriendlyError(error);
  }
  
  /// Handle network-specific errors
  static void handleNetworkError(dynamic error, String endpoint) {
    _logger.w('Network error for endpoint: $endpoint', error: error);
    final message = _getNetworkErrorMessage(error);
    _showSnackBar(message);
  }
  
  /// Handle authentication errors
  static void handleAuthError(dynamic error) {
    _logger.w('Authentication error', error: error);
    _navigateToLogin();
  }
  
  /// Handle permission errors
  static void handlePermissionError(String permission) {
    _logger.w('Permission denied: $permission');
    _showSnackBar('Permission required: $permission');
  }
}
```

### Error Categories

| Category | Handler | Behavior |
|----------|---------|----------|
| Application | `handleError()` | Log, analytics, user message |
| Network | `handleNetworkError()` | Log, endpoint-specific message |
| Validation | `handleValidationError()` | Log, field-specific message |
| Authentication | `handleAuthError()` | Log, redirect to login |
| Permission | `handlePermissionError()` | Log, permission message |

### Error Storage

```dart
static Future<void> _saveErrorToLog(dynamic error, StackTrace? stackTrace) async {
  final prefs = await SharedPreferences.getInstance();
  final errorLogs = prefs.getStringList(_errorLogKey) ?? [];
  
  final errorEntry = {
    'timestamp': DateTime.now().toIso8601String(),
    'error': error.toString(),
    'stackTrace': stackTrace?.toString() ?? '',
  };
  
  errorLogs.add(errorEntry.toString());
  
  // Limit to 100 entries
  if (errorLogs.length > _maxErrorLogs) {
    errorLogs.removeRange(0, errorLogs.length - _maxErrorLogs);
  }
  
  await prefs.setStringList(_errorLogKey, errorLogs);
}
```

### UI Integration

**ErrorBoundary Widget:**
```dart
class ErrorBoundary extends StatefulWidget {
  final Widget child;
  final Widget Function(dynamic error)? errorBuilder;
  
  @override
  State<ErrorBoundary> createState() => _ErrorBoundaryState();
}

class _ErrorBoundaryState extends State<ErrorBoundary> {
  dynamic _error;
  
  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return widget.errorBuilder?.call(_error) ?? _defaultErrorWidget();
    }
    return widget.child;
  }
  
  Widget _defaultErrorWidget() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 48, color: Colors.red),
          const SizedBox(height: 16),
          const Text('Something went wrong',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text(_error.toString()),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => setState(() => _error = null),
            child: const Text('Try Again'),
          ),
        ],
      ),
    );
  }
}
```

### Global Error Capture

```dart
// In main.dart or ErrorBoundary
FlutterError.onError = (FlutterErrorDetails details) {
  ErrorHandler.handleError(details.exception, details.stack);
};
```

### User-Friendly Messages

```dart
static String _getUserFriendlyMessage(dynamic error) {
  if (error.toString().contains('network')) {
    return 'Network connection error. Please check your internet connection.';
  } else if (error.toString().contains('timeout')) {
    return 'Request timeout. Please try again.';
  } else if (error.toString().contains('permission')) {
    return 'Permission denied. Please grant required permissions.';
  } else if (error.toString().contains('validation')) {
    return 'Invalid data provided. Please check your input.';
  } else {
    return 'An unexpected error occurred. Please try again.';
  }
}
```

## Consequences

### Positive

1. **Consistency** - All errors handled uniformly
2. **User experience** - Clear, actionable error messages
3. **Debugging** - Comprehensive logging and analytics
4. **Monitoring** - Error tracking for production issues
5. **Graceful degradation** - App continues on non-critical errors
6. **Error persistence** - Critical errors stored for analysis

### Negative

1. **Global state** - ErrorHandler is a static class
2. **Analytics dependency** - Error handling depends on analytics availability
3. **Storage overhead** - Error logs consume SharedPreferences space
4. **Complexity** - Multiple error handling paths to maintain

### Alternatives Considered

**dartz Either type:**
- Pros: Type-safe error handling, functional approach
- Cons: Learning curve, verbose for simple cases
- Decision: Use for domain layer, centralized handler for UI

**Zone-based error handling:**
- Pros: Catches all async errors automatically
- Cons: Less control, harder to customize per error type
- Decision: Use Zone for uncaught errors, ErrorHandler for known errors

**Try-catch everywhere:**
- Pros: Explicit, local handling
- Cons: Repetitive, inconsistent, easy to forget
- Decision: Centralized handler with specific methods per category

## Compliance

- All errors MUST be caught and handled
- Critical errors MUST be logged and sent to analytics
- User-facing errors MUST show friendly messages
- Errors MUST be categorized by type
- ErrorBoundary MUST wrap major UI sections

## Related Decisions

- ADR 001: Clean Architecture (error layer in core)
- ADR 002: Dependency Injection (Logger registration)
- ADR 003: State Management (error state in streams)

## References

- Flutter error handling best practices
- Logger package: https://pub.dev/packages/logger
- dartz package: https://pub.dev/packages/dartz

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)  
**Status**: DRAFT - Pending review
