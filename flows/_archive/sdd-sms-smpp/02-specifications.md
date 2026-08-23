# Specifications: SMS/SMPP Service

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      SmsService                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              SMPP Connection Management               │   │
│  │  SmppConfig  connectSmpp()  disconnectSmpp()          │   │
│  │  SmppConnectionState tracking                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  SMS Operations                       │   │
│  │  sendSmsViaSmpp()  sendSmsLocal()                     │   │
│  │  Message lifecycle tracking                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Message History & Stats                  │   │
│  │  getMessageHistory()  getMessageStats()               │   │
│  │  Filtering by sender, recipient, type, date           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. SmsService (Singleton)

```dart
class SmsService {
  // State
  SmppConfig? _smppConfig;
  SmppConnectionState _smppConnectionState = SmppConnectionState.disconnected;
  final Map<String, SmsMessage> _messages = {};
  int _messageCounter = 0;
  
  // Streams
  final StreamController<SmppConnectionState> _connectionStateController;
  final StreamController<SmsMessage> _messageController;
  final StreamController<String> _logController;
}
```

### 2. SmppConfig

```dart
class SmppConfig {
  final String host;
  final int port;
  final String systemId;
  final String password;
  final String systemType;
  final String sourceAddrTon;
  final String sourceAddrNpi;
  final String addressRange;
  
  // JSON serialization
  Map<String, dynamic> toJson();
  factory SmppConfig.fromJson(Map<String, dynamic>);
}
```

### 3. SmsMessage

```dart
class SmsMessage {
  final String id;
  final String sender;
  final String recipient;
  final String content;
  final DateTime timestamp;
  final SmsMessageType type;
  final SmsMessageStatus status;
  
  // JSON serialization
  Map<String, dynamic> toJson();
  factory SmsMessage.fromJson(Map<String, dynamic>);
}

enum SmsMessageType { incoming, outgoing }
enum SmsMessageStatus { pending, sent, delivered, failed, received }
```

## API Specifications

### Initialize SMPP

```dart
Future<bool> initializeSmpp(SmppConfig config) async {
  _smppConfig = config;
  _updateConnectionState(SmppConnectionState.connecting);
  
  // Simulate connection (2 second delay)
  await Future.delayed(const Duration(seconds: 2));
  
  _updateConnectionState(SmppConnectionState.bound);
  return true;
}
```

### Connect SMPP

```dart
Future<bool> connectSmpp() async {
  if (_smppConfig == null) return false;
  
  _updateConnectionState(SmppConnectionState.connecting);
  
  // Simulate connection (1 second delay)
  await Future.delayed(const Duration(seconds: 1));
  
  _updateConnectionState(SmppConnectionState.bound);
  return true;
}
```

### Send SMS via SMPP

```dart
Future<String?> sendSmsViaSmpp(String recipient, String content) async {
  if (_smppConnectionState != SmppConnectionState.bound) return null;
  
  final messageId = 'smpp_${++_messageCounter}_${DateTime.now().millisecondsSinceEpoch}';
  
  final message = SmsMessage(
    id: messageId,
    sender: _smppConfig?.systemId ?? 'SMPP',
    recipient: recipient,
    content: content,
    timestamp: DateTime.now(),
    type: SmsMessageType.outgoing,
    status: SmsMessageStatus.pending,
  );
  
  _messages[messageId] = message;
  _messageController.add(message);
  
  // Simulate delivery
  _simulateMessageDelivery(messageId);
  
  return messageId;
}
```

### Send SMS Local

```dart
Future<String?> sendSmsLocal(String recipient, String content) async {
  final messageId = 'local_${++_messageCounter}_${DateTime.now().millisecondsSinceEpoch}';
  
  final message = SmsMessage(
    id: messageId,
    sender: 'Local',
    recipient: recipient,
    content: content,
    timestamp: DateTime.now(),
    type: SmsMessageType.outgoing,
    status: SmsMessageStatus.pending,
  );
  
  _messages[messageId] = message;
  _messageController.add(message);
  
  // Simulate local SMS sending
  Timer(const Duration(seconds: 1), () {
    _updateMessageStatus(messageId, SmsMessageStatus.sent);
    Timer(const Duration(seconds: 2), () {
      _updateMessageStatus(messageId, SmsMessageStatus.delivered);
    });
  });
  
  return messageId;
}
```

### Message Delivery Simulation

```dart
void _simulateMessageDelivery(String messageId) {
  // After 1 second: sent
  Timer(const Duration(seconds: 1), () {
    _updateMessageStatus(messageId, SmsMessageStatus.sent);
    
    // After 3 more seconds: delivered (95% success) or failed (5%)
    Timer(const Duration(seconds: 3), () {
      final delivered = DateTime.now().millisecond % 100 < 95;
      _updateMessageStatus(
        messageId,
        delivered ? SmsMessageStatus.delivered : SmsMessageStatus.failed
      );
    });
  });
}
```

### Get Message History

```dart
List<SmsMessage> getMessageHistory({
  String? sender,
  String? recipient,
  SmsMessageType? type,
  DateTime? fromDate,
  DateTime? toDate,
}) {
  return _messages.values.where((message) {
    if (sender != null && message.sender != sender) return false;
    if (recipient != null && message.recipient != recipient) return false;
    if (type != null && message.type != type) return false;
    if (fromDate != null && message.timestamp.isBefore(fromDate)) return false;
    if (toDate != null && message.timestamp.isAfter(toDate)) return false;
    return true;
  }).toList()
    ..sort((a, b) => b.timestamp.compareTo(a.timestamp));
}
```

### Get Message Statistics

```dart
Map<String, int> getMessageStats() {
  final stats = <String, int>{
    'total': _messages.length,
    'incoming': 0,
    'outgoing': 0,
    'sent': 0,
    'delivered': 0,
    'failed': 0,
  };
  
  for (final message in _messages.values) {
    stats[message.type.name] = (stats[message.type.name] ?? 0) + 1;
    stats[message.status.name] = (stats[message.status.name] ?? 0) + 1;
  }
  
  return stats;
}
```

## State Transitions

### SMPP Connection Flow

```
disconnected
     │
     ▼
connecting ──► bound ──► disconnected
     │
     ▼
   error
```

### Message Status Flow (Outgoing)

```
pending ──► sent ──► delivered
          │
          └──► failed
```

### Message Status Flow (Incoming)

```
received
```

## Testing Support

### Simulate Incoming SMS

```dart
void simulateIncomingSms(String sender, String content) {
  final messageId = 'incoming_${++_messageCounter}_${DateTime.now().millisecondsSinceEpoch}';
  
  final message = SmsMessage(
    id: messageId,
    sender: sender,
    recipient: 'Local',
    content: content,
    timestamp: DateTime.now(),
    type: SmsMessageType.incoming,
    status: SmsMessageStatus.received,
  );
  
  _messages[messageId] = message;
  _messageController.add(message);
}
```

## Testing Strategy

### Unit Tests

```dart
test('SmsService.initializeSmpp returns true on success', () async {
  final service = SmsService();
  final config = SmppConfig(
    host: 'smpp.example.com',
    port: 2775,
    systemId: 'test',
    password: 'pass',
  );
  
  final result = await service.initializeSmpp(config);
  
  expect(result, true);
  expect(service.connectionState, SmppConnectionState.bound);
});

test('sendSmsViaSmpp returns message ID when bound', () async {
  final service = SmsService();
  await service.initializeSmpp(testConfig);
  
  final messageId = await service.sendSmsViaSmpp('+1234567890', 'Hello');
  
  expect(messageId, isNotNull);
  expect(service.messages.length, 1);
});
```

## Dependencies

### External Dependencies

| Package | Purpose |
|---------|---------|
| logger | Logging |

### Future Native Dependencies

| Platform | Component |
|----------|-----------|
| Android | SMPP client library |
| Android | SMS Manager |

---

**Status**: DRAFT  
**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)  
**Related**: 01-requirements.md
