# VDD: Dashboard Screen

## Screen Overview

**Purpose**: Main gateway control center with status overview and quick actions  
**Type**: Primary interface / Monitoring  
**Users**: System administrators, operators  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  GOSTsimbox Gateway 🚀          ⚙️     │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  📡  Gateway Status: Running      ║ │
│  ║      Всё работает как часы! 🕐    ║ │
│  ║                      Uptime: 02:15 ║ │
│  ╚═══════════════════════════════════╝ │  ← Status Card
│                                         │
│  ┌─────────┬─────────┬─────────┐       │
│  │  📞 SIP │  💬 SMS │  📞     │       │
│  │Connected│Connected│   2     │       │  ← Service Cards
│  │  Green  │  Green  │  Blue   │       │
│  └─────────┴─────────┴─────────┘       │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Device Information               ║ │
│  ║  Phone Number:    +1234567890     ║ │
│  ║  Network Operator: Verizon        ║ │
│  ║  Signal Strength: -65 dBm         ║ │
│  ║  Gateway Version: 3.0.0           ║ │
│  ╚═══════════════════════════════════╝ │  ← Device Info
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Quick Actions                    ║ │
│  ║  ┌───┐ ┌───┐ ┌───┐ ┌───┐        ║ │
│  ║  │ 📞│ │ 💬│ │ 📟│ │ 📋│        ║ │  ← Quick Actions
│  ║  └───┘ └───┘ └───┘ └───┘        ║ │
│  ║  Call  SMS  USSD  Logs           ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Statistics                       ║ │
│  ║  📞      💬       🎯              ║ │
│  ║  150     320     98.5%            ║ │
│  ║  Звонков  Сообщений  Успешность   ║ │
│  ║                                   ║ │
│  ║  😊 Вау! Вы настоящий мастер связи!║ │
│  ╚═══════════════════════════════════╝ │  ← Statistics
│                                         │
│            [ 🛑 Stop ]                  │  ← FAB
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Primary | `#1E88E5` (Blue 600) | App bar, accents |
| Background | `#FAFAFA` | Screen background |
| Card Background | `#FFFFFF` | Card backgrounds |
| Success | `#10B981` (Green) | Connected states |
| Warning | `#F59E0B` (Yellow) | Connecting states |
| Error | `#EF4444` (Red) | Disconnected/Error states |
| Info | `#3B82F6` (Blue) | Active calls, info |
| Text Primary | `#1F2937` | Main text |
| Text Secondary | `#6B7280` (Grey) | Labels, subtitles |

### Status Card Gradients

| State | Gradient Start | Gradient End |
|-------|---------------|--------------|
| Running | Green 400 | Green 600 |
| Stopped | Grey 400 | Grey 600 |
| Connecting | Orange 400 | Orange 600 |
| Error | Red 400 | Red 600 |

### Typography

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| App Bar Title | System | 20px | Bold | White |
| Card Title | System | 18px | Bold | Grey 900 |
| Card Value | System | 24px | Bold | Varies |
| Card Label | System | 12px | Regular | Grey |
| Status Title | System | 16px | Regular | White (on gradient) |
| Status Value | System | 24px | Bold | White (on gradient) |
| Funny Status | System | 12px | Italic | White 80% (on gradient) |
| Stat Label | System | 12px | Regular | Grey |
| Stat Value | System | 20px | Bold | Blue |

### Iconography

| Icon | Size | Color | Location |
|------|------|-------|----------|
| Router | 32px | White | Status card |
| Phone in Talk | 28px | Green/Grey | SIP card |
| SMS | 28px | Green/Grey | SMS card |
| Call | 28px | Blue/Grey | Calls card |
| Settings | 24px | White | App bar |
| Play/Stop | 24px | White | FAB |

---

## Component Specifications

### Status Overview Card

**Height**: 120px (minimum)  
**Border Radius**: 12px  
**Padding**: 20px  
**Elevation**: 2

**Content Layout:**
```
[Icon 32px]  [Status Text Column]           [Uptime Column]
             Title: "Gateway Status"         Label: "Uptime"
             Value: "Running"                Value: "02:15:30"
             Funny: "Всё работает..."
```

**Gradient Backgrounds:**
```dart
// Running
LinearGradient(colors: [Green.shade400, Green.shade600])

// Stopped
LinearGradient(colors: [Grey.shade400, Grey.shade600])
```

### Service Status Cards

**Width**: Equal thirds (minus spacing)  
**Height**: 100px  
**Border Radius**: 8px  
**Padding**: 16px  
**Elevation**: 1

**Layout:**
```
[Icon 28px]
[Title: 12px]
[Value: 16px, Bold, Colored]
```

### Device Information Card

**Border Radius**: 12px  
**Padding**: 16px  
**Elevation**: 1

**Info Row Layout:**
```
[Label: Grey]              [Value: Bold]
```

**Spacing:**
- Between rows: 8px vertical
- Title to first row: 16px

### Quick Actions Card

**Border Radius**: 12px  
**Padding**: 16px  
**Elevation**: 1

**Action Button:**
```
[Circle Button 52px diameter]
[Label: 12px, Center]
```

**Button Spacing:**
- Horizontal: Equal spacing
- Button to label: 8px

### Statistics Card

**Border Radius**: 12px  
**Padding**: 16px  
**Elevation**: 1

**Stat Item Layout:**
```
[Emoji: 24px]
[Value: 20px, Bold, Blue]
[Label: 12px, Grey, Center]
```

**Motivational Banner:**
```
Background: Blue.shade50
Border: Blue.shade200, 1px
Padding: 12px
Icon: 20px, Blue.shade600
Text: 12px, Italic, Blue.shade700
```

### Floating Action Button

**Size**: Extended FAB  
**Icon**: Play/Stop (24px)  
**Label**: "Start" / "Stop"  
**Background**: Green (start) / Red (stop)  
**Elevation**: 6

---

## Interaction Specifications

### Pull to Refresh

**Trigger**: Pull down from top  
**Indicator**: CircularProgressIndicator  
**Action**: Refresh device info (phone number, network, signal)

### Start/Stop Gateway

**Trigger**: FAB tap  
**Behavior**:
1. Call gatewayService.start() or stop()
2. Update status in real-time
3. Show loading during transition
4. Update FAB icon and color

### Quick Action Buttons

| Button | Action | Navigation |
|--------|--------|------------|
| Make Call | Navigate to CallScreen | Push |
| Send SMS | Navigate to SmsScreen | Push |
| USSD | Show dialog | Modal |
| Logs | Navigate to LogsScreen | Push |

### Service Status Tap

**Behavior**: Tap on service card shows detailed status  
**Future**: Expand to show connection details

---

## User Flow

### Normal Operation

```
1. User navigates to Dashboard
2. Status cards show current state
3. User monitors gateway status
4. User can:
   - Start/Stop gateway via FAB
   - Navigate to quick actions
   - View statistics
   - Pull to refresh device info
```

### Starting Gateway

```
1. User taps "Start" FAB
2. GatewayService.start() called
3. Status changes to "Starting..."
4. SIP registers
5. SMPP connects (if configured)
6. Status updates to "Running"
7. Uptime timer starts
8. FAB changes to "Stop" (red)
```

### Stopping Gateway

```
1. User taps "Stop" FAB
2. GatewayService.stop() called
3. Active calls ended
4. SIP unregisters
5. SMPP disconnects
6. Status updates to "Stopped"
7. Uptime resets
8. FAB changes to "Start" (green)
```

### Receiving Status Updates

```
GatewayService.statusStream
    │
    ├─► Update _gatewayStatus
    ├─► Rebuild status card
    ├─► Update service cards
    └─► Update statistics
```

---

## State Management

### Data Sources

| Data | Source | Update Frequency |
|------|--------|------------------|
| Gateway Status | GatewayService.statusStream | Real-time |
| Phone Number | TelephonyService.getPhoneNumber() | On load/refresh |
| Network Operator | TelephonyService.getNetworkOperatorName() | On load/refresh |
| Signal Strength | TelephonyService.getSignalStrength() | On load/refresh |

### Stream Subscriptions

```dart
// In initState
gatewayService.statusStream.listen((status) {
  setState(() {
    _gatewayStatus = status;
  });
});
```

---

## Funny Messages System

### Status Messages by Category

**Connected (Running):**
- "Всё работает как часы! 🕐"
- "Связь налажена, можно звонить! 📞"
- "Готов к бою! ⚔️"
- "Всё под контролем! 🎯"

**Connecting:**
- "Подключаемся к матрице... 🔌"
- "Ищем сигнал в космосе... 🛸"
- "Настраиваем антенны... 📡"

**Disconnected:**
- "Связь потеряна в космосе... 🚀"
- "Сервер ушёл на обед... 🍕"
- "Интернет решил отдохнуть... 😴"

**Error:**
- "Что-то пошло не так... 🤔"
- "Сервер в плохом настроении... 😤"
- "Кто-то забыл заплатить за интернет... 💸"

### Motivational Messages (Statistics)

| Condition | Message |
|-----------|---------|
| 0 calls, 0 messages | "Пока тихо, но мы готовы к бою! ⚔️" |
| >100 calls OR >100 messages | "Вау! Вы настоящий мастер связи! 🚀" |
| Other | Random from FunnyMessages.getMotivationalMessage() |

---

## Accessibility

### Text Scaling

- Support system font size up to 200%
- Cards expand vertically
- Text wraps appropriately
- Icons maintain size

### Screen Reader Support

- All status values announced
- Service states announced
- Button labels descriptive
- Statistics announced clearly

### Color Contrast

- Text on white: 7:1 (AAA)
- White text on gradients: 4.5:1 (AA)
- Service status colors: Distinguishable for colorblind users

---

## Responsive Design

### Layout Breakpoints

| Screen Width | Behavior |
|--------------|----------|
| < 360px | Stack service cards vertically |
| 360-600px | 3 service cards in row |
| > 600px | Center content, max-width 800px |

### Orientation

- **Portrait**: Default layout
- **Landscape**: Same layout, scrollable

---

## Animation Specifications

### Status Change

**Gradient Transition**: Crossfade 300ms  
**Icon**: Scale 1.0 → 1.1 → 1.0 (200ms)

### FAB State Change

**Icon**: RotateTransition 180° (300ms)  
**Color**: Crossfade 300ms  
**Label**: Fade in/out 200ms

### Pull to Refresh

**Indicator**: Standard Material  
**Overscroll**: 100px max

### Card Entry

**Initial Load**: Fade in + slide up (20px), 300ms staggered

---

## Testing Checklist

### Visual Tests

- [ ] Status card gradient renders correctly
- [ ] Service cards show correct colors
- [ ] Typography matches specifications
- [ ] Icons properly aligned
- [ ] Statistics display correctly

### Interaction Tests

- [ ] Pull to refresh works
- [ ] FAB toggles gateway state
- [ ] Quick actions navigate correctly
- [ ] Status updates in real-time
- [ ] Funny messages rotate

### State Tests

- [ ] Status stream updates UI
- [ ] Device info loads correctly
- [ ] Statistics update after calls
- [ ] Uptime calculates correctly

---

## Related Screens

| Screen | Relationship |
|--------|--------------|
| Auth | Entry point before dashboard |
| Settings | Access via app bar |
| CallScreen | Quick action navigation |
| SmsScreen | Quick action navigation |
| LogsScreen | Quick action navigation |

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - Detailed VDD  
**Status**: DRAFT - Pending review
