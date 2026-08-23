# ADR-006: Real-Time Call Duration Calculation

> Enabling architectural decision: Accurate duration tracking without native polling

## Status

DRAFT

## Type

Enabling - This decision enables accurate call duration display without continuous native queries.

## Context

The SIP plugin needs to track and display call duration:

- Total duration (since call creation)
- Connected duration (since call was answered)
- Formatted display (MM:SS format)
- Real-time updates for UI

**Requirements:**
1. Duration must be accurate to within 1 second
2. Duration must update in real-time (every second)
3. Must work when app is in background
4. Must survive serialization/deserialization
5. Should not require polling native layer

**Constraints:**
- Native PJSIP tracks duration internally
- Polling native layer for duration is expensive
- Call objects are immutable snapshots
- Duration needs to increase even when Call object is unchanged

## Decision

We will use **construction time offset** for real-time duration calculation:

### Architecture Pattern

```
┌─────────────────┐
│  Call Object    │
│  Created        │
│  t = 0          │
└────────┬────────┘
         │ Store _constructionTime
         ▼
┌─────────────────┐
│  Duration       │
│  Calculation    │  ← getDuration()
│                 │  ← now - _constructionTime
└────────┬────────┘
         ▼
┌─────────────────┐
│  Real-Time      │
│  Duration       │  ← Increases automatically
└─────────────────┘
```

### Implementation Details

1. **Store creation timestamp** (`_constructionTime`) in Call constructor
2. **Calculate duration dynamically** using current time minus construction time
3. **Add native duration** (connectDuration, totalDuration) as base offset
4. **Format on-demand** with MM:SS formatting
5. **Handle disconnected calls** (stop duration at termination)

### Code Pattern

```dart
// call.dart
class Call {
  final int id;
  final int callId;
  final int accountId;
  final String state;
  final int connectDuration;  // Duration from native when connected
  final int totalDuration;    // Duration from native at snapshot
  
  // Internal tracking - set at construction
  final int _constructionTime;  // Unix timestamp in seconds

  Call({
    required this.id,
    required this.callId,
    required this.accountId,
    required this.state,
    required this.connectDuration,
    required this.totalDuration,
    // ... other fields
  }) : _constructionTime = DateTime.now().millisecondsSinceEpoch ~/ 1000;

  /// Get up-to-date call duration in seconds
  int getTotalDuration() {
    final time = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    final offset = time - _constructionTime;
    return totalDuration + offset;
  }

  /// Get up-to-date connected duration
  int getConnectDuration() {
    // Handle terminated calls
    if (connectDuration < 0 || state == "PJSIP_INV_STATE_DISCONNECTED") {
      return connectDuration;
    }
    final time = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    final offset = time - _constructionTime;
    return connectDuration + offset;
  }

  /// Get formatted total duration in "MM:SS" format
  String getFormattedTotalDuration() => _formatTime(getTotalDuration());

  /// Get formatted connected duration in "MM:SS" format
  String getFormattedConnectDuration() => _formatTime(getConnectDuration());

  /// Format time in MM:SS format
  String _formatTime(int seconds) {
    if (seconds < 0) return "00:00";

    final minutes = seconds ~/ 60;
    final remainingSeconds = seconds % 60;

    return "${minutes.toString().padLeft(2, '0')}:${remainingSeconds.toString().padLeft(2, '0')}";
  }
}
```

### Usage Pattern

```dart
// Flutter UI - Duration updates automatically
class CallDurationWidget extends StatelessWidget {
  final Call call;

  CallDurationWidget({required this.call});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder(
      // Rebuild on call state changes
      stream: FlutterSip2.eventStream.where((e) => e['call_id'] == call.id),
      builder: (context, snapshot) {
        // Duration calculated in real-time
        final duration = call.getFormattedConnectDuration();
        return Text(duration);  // "05:23"
      },
    );
  }
}
```

## Consequences

### Positive

1. **No Native Polling**: Duration calculated without querying native layer:
   - Reduces platform channel overhead
   - No IPC for simple duration queries
   - Better performance

2. **Real-Time Accuracy**: Duration updates every time it's accessed:
   - Always shows current duration
   - No staleness between updates
   - Accurate to within milliseconds

3. **Memory Efficient**: No timers or intervals running:
   - Calculation on-demand only
   - No background tasks needed
   - Minimal memory footprint

4. **Serialization Safe**: _constructionTime survives serialization:
   - Works across platform boundaries
   - Duration accurate after deserialization
   - Survives app state restoration

5. **Immutability Compatible**: Works with immutable Call objects:
   - No mutation needed for duration updates
   - Consistent with ADR-005 (immutable models)
   - Pure function calculation

6. **Disconnected Call Handling**: Stops at termination:
   - Checks call state before calculating
   - Returns final duration for ended calls
   - Doesn't continue counting after hangup

### Negative

1. **Clock Dependency**: Relies on system clock accuracy:
   - Clock changes affect duration
   - DST transitions may cause issues
   - NTP adjustments could skew time

2. **Calculation Overhead**: Duration calculated on every access:
   - Small CPU cost per calculation
   - Multiple accesses = multiple calculations
   - Could be cached if needed

3. **Time Zone Sensitivity**: Uses local time (DateTime.now()):
   - Should use UTC for consistency
   - Time zone changes during call could affect
   - Minor issue for typical call durations

4. **Snapshot Inconsistency**: Call object may have stale state:
   - Other fields (state, held, muted) may be outdated
   - Duration accurate but state may not match
   - Must rely on events for state updates

### Trade-offs

**Rejected Alternative: Native Polling**

We considered polling native layer for duration:

```dart
// Rejected: Polling native
static Future<int> getCallDuration(int callId) async {
  return await _channel.invokeMethod('getCallDuration', callId);
}

// Usage with timer
Timer.periodic(Duration(seconds: 1), (_) {
  final duration = await getCallDuration(callId);
  updateUI(duration);
});
```

**Why Rejected:**
- High overhead (platform channel per second)
- Blocks async execution
- Wastes battery on polling
- Doesn't work in background

**Rejected Alternative: Dart Timer Tracking**

We considered using Dart timers to track duration:

```dart
// Rejected: Timer-based
class Call {
  int _duration = 0;
  Timer? _timer;

  Call() {
    _timer = Timer.periodic(Duration(seconds: 1), (_) {
      _duration++;
      notifyListeners();  // For UI update
    });
  }
}
```

**Why Rejected:**
- Requires mutable state
- Timer management overhead
- Must cancel timers on disposal
- Doesn't survive serialization
- Memory leak risk

**Rejected Alternative: Stream-Based Duration**

We considered emitting duration in events:

```dart
// Rejected: Duration in events
eventStream.listen((event) {
  if (event['type'] == 'call_duration') {
    setState(() => duration = event['duration']);
  }
});
```

**Why Rejected:**
- Event overhead for simple duration
- Service must track and emit duration
- Wakes Flutter every second
- Battery impact

**Accepted Trade-off:** Calculation overhead for simplicity - Small CPU cost accepted for no polling, no timers, no native calls.

## Related Decisions

- **ADR-005**: Immutable Dart models (_constructionTime is final)

## References

- [Call.dart](../lib/src/call.dart) - Duration calculation implementation
- [DateTime Documentation](https://api.flutter.dev/flutter/dart-core/DateTime-class.html)
- [PJSIP Call Duration API](https://www.pjsip.org/pjsip-doc/html/group__group__call__control.htm) (native reference)

---

*Generated by /legacy analysis | 2026-03-04*
