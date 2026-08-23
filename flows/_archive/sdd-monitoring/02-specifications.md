# Specifications: Connection Monitoring

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│               ConnectionMonitorService                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Periodic Monitoring                      │   │
│  │  Timer (5s interval)  _performMonitoringCycle()       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Connection Checks                        │   │
│  │  _checkSipConnection()  _checkSmppConnection()        │   │
│  │  TCP socket timing with Stopwatch                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Network Status                           │   │
│  │  connectivity_plus  signal strength  quality          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Speed Test                               │   │
│  │  performSpeedTest()  httpbin.org                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. ConnectionMonitorService (Singleton)

```dart
class ConnectionMonitorService {
  final Connectivity _connectivity = Connectivity();
  
  // State
  bool _isMonitoring = false;
  Timer? _monitoringTimer;
  StreamSubscription<ConnectivityResult>? _connectivitySubscription;
  
  ConnectionStats _sipStats = ConnectionStats.initial('SIP');
  ConnectionStats _smppStats = ConnectionStats.initial('SMPP');
  Map<String, dynamic> _networkStatus = {};
  
  // Streams
  final StreamController<ConnectionStats> _sipStatsController;
  final StreamController<ConnectionStats> _smppStatsController;
  final StreamController<Map<String, dynamic>> _networkStatusController;
}
```

### 2. ConnectionStats

```dart
class ConnectionStats {
  final String protocol;
  final bool isConnected;
  final double latency;
  final DateTime lastUpdate;
  final String? errorMessage;
  final int reconnectAttempts;
  
  ConnectionStats.initial(String protocol)
    : protocol = protocol,
      isConnected = false,
      latency = -1,
      lastUpdate = DateTime.now(),
      errorMessage = null,
      reconnectAttempts = 0;
  
  ConnectionStats copyWith({...});
}
```

## API Specifications

### Start Monitoring

```dart
Future<void> startMonitoring({
  String? sipServer,
  int? sipPort,
  String? smppServer,
  int? smppPort,
}) async {
  if (_isMonitoring) return;
  
  _isMonitoring = true;
  
  // Subscribe to connectivity changes
  _connectivitySubscription = _connectivity.onConnectivityChanged.listen(
    _handleConnectivityChange,
  );
  
  // Start periodic monitoring (5 second interval)
  _monitoringTimer = Timer.periodic(
    const Duration(seconds: 5),
    (_) => _performMonitoringCycle(sipServer, sipPort, smppServer, smppPort),
  );
  
  // First cycle immediately
  await _performMonitoringCycle(sipServer, sipPort, smppServer, smppPort);
}
```

### Stop Monitoring

```dart
Future<void> stopMonitoring() async {
  if (!_isMonitoring) return;
  
  _isMonitoring = false;
  _monitoringTimer?.cancel();
  await _connectivitySubscription?.cancel();
}
```

### Check SIP Connection

```dart
Future<void> _checkSipConnection(String server, int port) async {
  final stopwatch = Stopwatch()..start();
  
  try {
    final socket = await Socket.connect(
      server, port,
      timeout: const Duration(seconds: 5),
    );
    stopwatch.stop();
    await socket.close();
    
    _sipStats = _sipStats.copyWith(
      isConnected: true,
      latency: stopwatch.elapsedMilliseconds.toDouble(),
      lastUpdate: DateTime.now(),
      errorMessage: null,
      reconnectAttempts: 0,
    );
    
    _sipStatsController.add(_sipStats);
  } catch (e) {
    stopwatch.stop();
    
    _sipStats = _sipStats.copyWith(
      isConnected: false,
      latency: -1,
      lastUpdate: DateTime.now(),
      errorMessage: e.toString(),
      reconnectAttempts: _sipStats.reconnectAttempts + 1,
    );
    
    _sipStatsController.add(_sipStats);
  }
}
```

### Calculate Network Quality

```dart
String _calculateNetworkQuality() {
  final sipLatency = _sipStats.latency;
  final smppLatency = _smppStats.latency;
  
  if (sipLatency < 0 || smppLatency < 0) return 'Poor';
  
  final avgLatency = (sipLatency + smppLatency) / 2;
  
  if (avgLatency < 50) return 'Excellent';
  if (avgLatency < 100) return 'Good';
  if (avgLatency < 200) return 'Fair';
  return 'Poor';
}
```

### Speed Test

```dart
Future<Map<String, double>> performSpeedTest() async {
  try {
    final stopwatch = Stopwatch()..start();
    final client = HttpClient();
    
    // Download 1KB test file
    final request = await client.getUrl(
      Uri.parse('https://httpbin.org/bytes/1024'),
    );
    final response = await request.close();
    await response.drain();
    
    stopwatch.stop();
    client.close();
    
    final downloadSpeed = (1024 * 8) / (stopwatch.elapsedMilliseconds / 1000);
    
    return {
      'download_speed_bps': downloadSpeed,
      'download_speed_kbps': downloadSpeed / 1024,
      'latency_ms': stopwatch.elapsedMilliseconds.toDouble(),
    };
  } catch (e) {
    return {
      'download_speed_bps': 0,
      'download_speed_kbps': 0,
      'latency_ms': -1,
    };
  }
}
```

### Get Detailed Statistics

```dart
Map<String, dynamic> getDetailedStats({Duration? period}) {
  final now = DateTime.now();
  final periodStart = period ?? now.subtract(const Duration(hours: 1));
  
  return {
    'period_start': periodStart.toIso8601String(),
    'period_end': now.toIso8601String(),
    'sip_stats': {
      'average_latency': _sipStats.latency,
      'connection_uptime': _sipStats.isConnected ? '100%' : '0%',
      'reconnect_attempts': _sipStats.reconnectAttempts,
      'last_error': _sipStats.errorMessage,
    },
    'smpp_stats': {
      'average_latency': _smppStats.latency,
      'connection_uptime': _smppStats.isConnected ? '100%' : '0%',
      'reconnect_attempts': _smppStats.reconnectAttempts,
      'last_error': _smppStats.errorMessage,
    },
    'network_quality': _calculateNetworkQuality(),
    'monitoring_active': _isMonitoring,
  };
}
```

## Monitoring Cycle Flow

```
_performMonitoringCycle()
       │
       ├─► _updateNetworkStatus()
       │    ├─► connectivity.checkConnectivity()
       │    ├─► _getSignalStrength()
       │    └─► Broadcast network status
       │
       ├─► _checkSipConnection(server, port)
       │    ├─► Socket.connect() with timeout
       │    ├─► Measure with Stopwatch
       │    └─► Update _sipStats, broadcast
       │
       └─► _checkSmppConnection(server, port)
            ├─► Socket.connect() with timeout
            ├─► Measure with Stopwatch
            └─► Update _smppStats, broadcast
```

## Network Change Handling

```dart
void _handleConnectivityChange(ConnectivityResult result) {
  _networkStatus = {
    ..._networkStatus,
    'connectivity_type': result.name,
    'is_connected': result != ConnectivityResult.none,
    'last_update': DateTime.now().toIso8601String(),
  };
  _networkStatusController.add(_networkStatus);
  
  // Reset connections on network loss
  if (result == ConnectivityResult.none) {
    _sipStats = _sipStats.copyWith(
      isConnected: false,
      errorMessage: 'Network disconnected',
    );
    _smppStats = _smppStats.copyWith(
      isConnected: false,
      errorMessage: 'Network disconnected',
    );
    _sipStatsController.add(_sipStats);
    _smppStatsController.add(_smppStats);
  }
}
```

## Testing Strategy

### Unit Tests

```dart
test('ConnectionMonitorService calculates network quality correctly', () {
  final service = ConnectionMonitorService();
  
  // Simulate excellent network (< 50ms)
  // Expected: 'Excellent'
  
  // Simulate good network (50-100ms)
  // Expected: 'Good'
  
  // Simulate fair network (100-200ms)
  // Expected: 'Fair'
  
  // Simulate poor network (> 200ms)
  // Expected: 'Poor'
});

test('Speed test returns valid results', () async {
  final service = ConnectionMonitorService();
  
  final results = await service.performSpeedTest();
  
  expect(results.containsKey('download_speed_bps'), true);
  expect(results.containsKey('download_speed_kbps'), true);
  expect(results.containsKey('latency_ms'), true);
});
```

## Dependencies

### External Dependencies

| Package | Purpose |
|---------|---------|
| connectivity_plus | Network connectivity detection |
| logger | Logging |

### Network Dependencies

| Endpoint | Purpose |
|----------|---------|
| httpbin.org/bytes/1024 | Speed test |

---

**Status**: DRAFT  
**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)  
**Related**: 01-requirements.md
