# Specifications: VDD Screens

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
├─────────────────────────────────────────────────────────┤
│  Screens (20 total)                                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Core Screens (7 implemented)                    │   │
│  │  - DashboardScreen  - LogsScreen                 │   │
│  │  - SettingsScreen   - SmsScreen                  │   │
│  │  - CallScreen       - SetupScreen                │   │
│  │  - AuthScreen                                    │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Secondary Screens (13 visual specs)             │   │
│  │  - analytics, base_stations, calls, codecs       │   │
│  │  - info, language, lines, sims                   │   │
│  │  - smpp_logs, smpp_settings, theme_demo          │   │
│  │  - theme_settings, ussd, auth                    │   │
│  └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  Providers                                               │
│  - SipProvider      - GatewayProvider                   │
│  - ThemeProvider    - SmsProvider                       │
├─────────────────────────────────────────────────────────┤
│  Services                                                │
│  - SipService       - GatewayService                    │
│  - SmsService       - TelephonyService                  │
│  - ThemeService     - StorageService                    │
└─────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. DashboardScreen

**Purpose**: Main gateway control center

**State Management:**
```dart
class _DashboardScreenState extends State<DashboardScreen> {
  GatewayStatus? _gatewayStatus;
  String? _phoneNumber;
  String? _networkOperator;
  int? _signalStrength;
  
  // Listen to status stream
  gatewayService.statusStream.listen((status) {
    setState(() => _gatewayStatus = status);
  });
}
```

**Component Structure:**
```
DashboardScreen
├── StatusOverviewCard (gradient background)
│   ├── Icon (router)
│   ├── Status text (Running/Stopped)
│   ├── Funny status message
│   └── Uptime display
├── ServiceStatusCards (Row of 3)
│   ├── SIP Card (phone_in_talk icon)
│   ├── SMS Card (sms icon)
│   └── Calls Card (call icon, count)
├── DeviceInfoCard
│   ├── Phone Number
│   ├── Network Operator
│   ├── Signal Strength
│   └── Gateway Version
├── QuickActionsCard
│   ├── Make Call → CallScreen
│   ├── Send SMS → SmsScreen
│   ├── USSD → Dialog
│   └── Logs → LogsScreen
├── StatisticsCard
│   ├── Total calls
│   ├── Total messages
│   ├── Success rate
│   └── Motivational message
└── FloatingActionButton (Start/Stop)
```

**Color Specifications:**
```dart
// Status card gradient
Running:    LinearGradient([Green.shade400, Green.shade600])
Stopped:    LinearGradient([Grey.shade400, Grey.shade600])
Connecting: LinearGradient([Orange.shade400, Orange.shade600])
Error:      LinearGradient([Red.shade400, Red.shade600])

// Service cards
Connected:  Colors.green
Disconnected: Colors.grey
Active:     Colors.blue
```

---

### 2. LogsScreen

**Purpose**: View and filter system logs

**State Management:**
```dart
class _LogsScreenState extends State<LogsScreen> {
  final List<LogEntry> _logs = [];
  String _searchQuery = '';
  LogLevel _selectedLevel = LogLevel.all;
  bool _autoScroll = true;
  
  // Listen to all service log streams
  gatewayService.logStream.listen((log) => _addLog(log, LogLevel.info, 'Gateway'));
  sipService.logStream.listen((log) => _addLog(log, LogLevel.info, 'SIP'));
  // ... other services
}
```

**Component Structure:**
```
LogsScreen
├── AppBar (title, auto-scroll, filter, clear)
├── SearchBar
│   ├── Search icon
│   ├── Text field
│   └── Clear button (when query exists)
├── StatsBar
│   ├── "Showing X of Y logs"
│   └── Active filter chip (deletable)
├── LogList (ListView.builder)
│   └── LogCard (per entry)
│       ├── Level badge (colored)
│       ├── Source badge (grey)
│       ├── Timestamp
│       └── Message (2 lines max)
└── ScrollFABs (positioned)
    ├── Scroll to top
    └── Scroll to bottom
```

**Level Colors:**
```dart
Debug:   Color(0xFF9CA3AF)  // Grey
Info:    Color(0xFF3B82F6)  // Blue
Warning: Color(0xFFF59E0B)  // Yellow
Error:   Color(0xFFEF4444)  // Red
Success: Color(0xFF10B981)  // Green
```

**Log Card Specification:**
```dart
Card(
  margin: EdgeInsets.symmetric(horizontal: 4, vertical: 2),
  elevation: 1,
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(8),
    side: BorderSide(
      color: levelColor.withOpacity(0.3),
      width: 4,  // Left border color by level
    ),
  ),
  child: ListTile(
    title: Row(
      children: [
        LevelBadge(level),    // Colored badge
        SourceBadge(source),  // Grey badge
        Spacer(),
        Timestamp(time),
      ],
    ),
    subtitle: Message(maxLines: 2),
  ),
)
```

---

### 3. SettingsScreen

**Purpose**: View and modify gateway configuration

**State Management:**
```dart
class _SettingsScreenState extends State<SettingsScreen> {
  GatewayConfig? _config;
  ThemeMode? _currentThemeMode;
  
  // Load config and theme on init
  _loadConfig();
  _loadTheme();
}
```

**Component Structure:**
```
SettingsScreen
├── ThemeSection
│   ├── Title with palette icon
│   └── Theme Options (Row of 3)
│       ├── Light (sun icon)
│       ├── Dark (moon icon)
│       └── System (auto icon)
├── SipConfigCard
│   ├── Username
│   ├── Domain
│   ├── Proxy (if exists)
│   ├── Port
│   └── Secure (Yes/No)
├── SmppConfigCard
│   ├── Host
│   ├── Port
│   └── System ID
├── GatewaySettingsCard
│   ├── Auto Answer
│   ├── Enable Logging
│   ├── Route SIP→GSM
│   ├── Route GSM→SIP
│   ├── Route SMS→SMPP
│   ├── Route SMPP→SMS
│   └── Max Concurrent Calls
└── ActionsCard
    ├── Reconfigure Gateway → SetupScreen
    ├── Restart Services → Confirm → Restart
    ├── Clear Logs → Confirm → Clear
    ├── Divider
    └── About → Dialog
```

**Theme Option Specification:**
```dart
Container(
  decoration: BoxDecoration(
    color: isSelected ? primary.withOpacity(0.1) : null,
    borderRadius: BorderRadius.circular(8),
    border: Border.all(
      color: isSelected ? primary : Colors.grey.shade300,
      width: isSelected ? 2 : 1,
    ),
  ),
  child: Column(
    children: [
      Icon(icon, color: isSelected ? primary : Colors.grey),
      Text(label, style: isSelected ? bold : normal),
    ],
  ),
)
```

---

### 4. SmsScreen

**Purpose**: Compose, send, and view SMS messages

**State Management:**
```dart
class _SmsScreenState extends State<SmsScreen> {
  final TextEditingController _recipientController = TextEditingController();
  final TextEditingController _messageController = TextEditingController();
  List<SmsMessage> _messages = [];
  bool _useSmpp = false;
  int _charCount = 0;
  
  // Listen to message stream
  smsService.messageStream.listen((message) {
    setState(() {
      _messages.insert(0, message);
    });
  });
}
```

**Component Structure:**
```
SmsScreen
├── AppBar (title, refresh, menu)
│   ├── Refresh
│   ├── Clear Messages
│   ├── Send Test SMS
│   └── Simulate Incoming
├── ComposeCard
│   ├── Recipient field (phone keyboard)
│   ├── Message field (maxLines: 3)
│   ├── Character counter (N/160, color changes at 140)
│   ├── SMPP toggle switch
│   └── Send button (icon + label)
├── StatisticsCard
│   ├── Total
│   ├── Sent
│   ├── Delivered
│   └── Failed
└── MessagesList
    └── MessageCard (per message)
        ├── Avatar (direction icon)
        ├── Phone number/name
        ├── Status chip (colored)
        ├── Message preview (2 lines)
        ├── Timestamp
        └── Popup menu (Copy, Reply, Delete)
```

**Character Counter Logic:**
```dart
int remaining = 160 - _messageController.text.length;
Color counterColor = remaining < 20 
    ? (remaining < 10 ? Colors.red : Colors.orange)
    : Colors.grey;

Text('${_messageController.text.length}/160',
  style: TextStyle(color: counterColor),
)
```

**Message Card Specification:**
```dart
Card(
  margin: EdgeInsets.only(bottom: 8),
  child: ListTile(
    leading: CircleAvatar(
      backgroundColor: _getMessageStatusColor(message.status),
      child: Icon(
        isIncoming ? Icons.call_received : Icons.call_made,
        color: Colors.white,
      ),
    ),
    title: Row(
      children: [
        Expanded(child: Text(phoneNumber)),
        Chip(
          label: Text(status.name.toUpperCase(), style: TextStyle(fontSize: 10)),
          backgroundColor: statusColor.withOpacity(0.2),
        ),
      ],
    ),
    subtitle: Column(
      children: [
        Text(message.content, maxLines: 2, overflow: ellipsis),
        Text(timestamp, style: TextStyle(fontSize: 12, color: Colors.grey)),
      ],
    ),
    trailing: PopupMenuButton(items: [
      PopupMenuItem(child: Text('Copy'), onTap: () => _copyMessage(message)),
      PopupMenuItem(child: Text('Reply'), onTap: () => _replyToMessage(message)),
      PopupMenuItem(child: Text('Delete'), onTap: () => _deleteMessage(message)),
    ]),
  ),
)
```

---

### 5. CallScreen

**Purpose**: Manage active calls with full control

**State Management:**
```dart
class _CallScreenState extends State<CallScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _infoOffsetAnimation;
  late Animation<double> _avatarOpacityAnimation;
  // ... more animations
  
  SipCall? _activeCall;
  CallRouting? _activeRouting;
  CallState _callState = CallState.initiated;
  bool _isMuted = false;
  bool _isSpeaker = false;
  bool _isOnHold = false;
  List<SipCall> _otherCalls = [];
  bool _showIncomingCallModal = false;
}
```

**Animation Specifications:**
```dart
// Animation setup
_animationController = AnimationController(
  vsync: this,
  duration: Duration(milliseconds: 300),
);

_infoOffsetAnimation = Tween<double>(begin: 0, end: -50).animate(
  CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
);

_avatarOpacityAnimation = Tween<double>(begin: 1, end: 0).animate(
  CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
);

// State-based animation trigger
void _updateAnimation() {
  if (_callState == CallState.active || _callState == CallState.held) {
    _animationController.forward();  // Incoming → Active
  } else {
    _animationController.reverse();  // Active → Incoming
  }
}
```

**Component Structure:**
```
CallScreen
├── Container (gradient background)
│   ├── CallParallelInfo (if other calls)
│   │   └── ListView (horizontal strips)
│   ├── Stack
│   │   └── Column
│   │       ├── CallInfo (animated offset)
│   │       │   ├── Caller name (24px bold)
│   │       │   └── Caller number (18px)
│   │       ├── Avatar (animated opacity + offset)
│   │       │   └── CircleAvatar (30% screen height)
│   │       ├── CallState (animated offset)
│   │       │   └── Text (Calling/Connected/On Hold)
│   │       ├── CallActions (animated opacity + offset)
│   │       │   ├── Page indicators (2 dots)
│   │       │   └── PageView (2 pages)
│   │       │       ├── Page 1: Mute, Speaker, Hold, Add, Transfer, DTMF
│   │       │       └── Page 2: Park, Merge, Record, Chat
│   │       ├── Spacer
│   │       └── CallControls
│   │           ├── Hangup (red)
│   │           ├── Answer (green, incoming only)
│   │           └── Redirect (orange, incoming only)
│   └── IncomingCallModal (overlay, if second call)
│       ├── ModalBarrier (transparent)
│       └── Card (centered)
│           ├── Icon (64px green)
│           ├── Caller info
│           ├── "is calling" text
│           └── Action buttons (Decline, Answer)
```

**Gradient Background:**
```dart
Container(
  decoration: BoxDecoration(
    gradient: LinearGradient(
      begin: Alignment.topCenter,
      end: Alignment.bottomCenter,
      colors: [
        Color(0xFF2a5743),  // Teal green
        Color(0xFF14456f),  // Deep blue
      ],
    ),
  ),
)
```

---

### 6. SetupScreen

**Purpose**: Initial gateway configuration wizard

**Component Structure:**
```
SetupScreen
├── AppBar (title, no back button)
├── ProgressIndicator (3 segments)
│   ├── Segment 1: SIP (filled if page >= 0)
│   ├── Segment 2: SMPP (filled if page >= 1)
│   └── Segment 3: Settings (filled if page >= 2)
├── PageView (3 pages)
│   ├── Page 1: SIP Configuration
│   │   ├── Username (required)
│   │   ├── Password (required)
│   │   ├── Domain (required)
│   │   ├── Proxy (optional)
│   │   ├── Port (default: 5060)
│   │   └── Secure toggle
│   ├── Page 2: SMPP Configuration
│   │   ├── Enable SMPP toggle
│   │   ├── Host
│   │   ├── Port (default: 2775)
│   │   ├── System ID
│   │   └── Password
│   └── Page 3: Gateway Settings
│       ├── Auto Answer toggle
│       ├── Enable Logging toggle
│       ├── Route SIP→GSM toggle
│       ├── Route GSM→SIP toggle
│       ├── Route SMS→SMPP toggle
│       └── Route SMPP→SMS toggle
└── NavigationButtons
    ├── Back (if page > 0)
    └── Next/Finish (loading state supported)
```

---

### 7. AuthScreen

**Purpose**: User authentication and credential management

**Component Structure:**
```
AuthScreen
├── Container (dark background #1A1A1A)
└── Form
    ├── Logo (80px router icon)
    ├── Title (28px bold)
    ├── Subtitle (16px grey)
    ├── Username field (person icon)
    ├── Password field (lock icon)
    ├── Server field (dns icon)
    ├── Port field (default: 5060)
    ├── Remember me checkbox
    └── Login button (loading state)
```

---

## Data Flow Diagrams

### Dashboard Status Updates

```
GatewayService.statusStream
       │
       ▼
DashboardScreen (listen in initState)
       │
       ▼
setState(() => _gatewayStatus = status)
       │
       ▼
Rebuild:
  - StatusOverviewCard
  - ServiceStatusCards
  - StatisticsCard
```

### Logs Streaming

```
Service.logStream (multiple)
       │
       ├─► GatewayService ──► _addLog()
       ├─► SipService ──────► _addLog()
       ├─► SmsService ──────► _addLog()
       └─► TelephonyService ─► _addLog()
              │
              ▼
       setState(() => _logs.insert(0, entry))
              │
              ▼
       ListView.builder rebuilds
```

### Call State Animations

```
SipService.callStateStream
       │
       ▼
CallScreen._handleCallStateChange()
       │
       ▼
setState(() => _callState = newState)
       │
       ▼
_updateAnimation()
       │
       ├─► forward() if active/held
       └─► reverse() if incoming/initiated
       │
       ▼
AnimatedBuilder widgets update
```

---

## Error Handling

### Network/Connection Errors

```dart
try {
  await gatewayService.start();
} catch (e) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text('Failed to start: $e'),
      backgroundColor: Colors.red,
    ),
  );
}
```

### Validation Errors

```dart
Form(
  key: _formKey,
  child: Column(
    children: [
      TextFormField(
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Required field';
          }
          return null;
        },
      ),
    ],
  ),
)
```

---

## Testing Strategy

### Widget Tests

```dart
testWidgets('Dashboard shows running status', (tester) async {
  final mockService = MockGatewayService();
  when(mockService.statusStream).thenAnswer((_) => Stream.value(
    GatewayStatus(isRunning: true),
  ));

  await tester.pumpWidget(
    ChangeNotifierProvider.value(
      value: mockService,
      child: DashboardScreen(),
    ),
  );

  expect(find.text('Running'), findsOneWidget);
});
```

### Integration Tests

```dart
testWidgets('LogsScreen filters by level', (tester) async {
  await tester.pumpWidget(LogsScreen());
  
  // Tap filter button
  await tester.tap(find.byIcon(Icons.filter_list));
  await tester.pumpAndSettle();
  
  // Select Error level
  await tester.tap(find.text('ERROR'));
  await tester.pumpAndSettle();
  
  // Verify only error logs shown
  expect(find.byType(LogCard), findsNWidgets(errorLogs.length));
});
```

---

## Performance Considerations

### List Optimization

- Use `ListView.builder` for lazy loading
- Keep item widgets stateless where possible
- Use `const` constructors

### Animation Performance

- Use `vsync` for AnimationController
- Prefer `Transform` over rebuilding widgets
- Use `AnimatedBuilder` for complex animations

### Stream Management

- Cancel subscriptions in `dispose()`
- Use `broadcast` for multi-listener streams
- Debounce rapid updates

---

## Security Considerations

### Credential Storage

- Passwords stored encrypted
- Remember me opt-in only
- Auto-login requires explicit enable

### Input Validation

- All user input sanitized
- SQL injection prevention
- XSS prevention in selectable text

---

**Status**: APPROVED  
**Created**: 2026-03-03  
**Updated**: 2026-03-07  
**Source**: Legacy analysis + Implementation review
