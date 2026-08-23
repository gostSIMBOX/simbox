# Specifications: Export App Screenshots to Figma

> Version: 2.0
> Status: DRAFT
> Last Updated: 2026-03-11
> Requirements: [01-requirements.md](01-requirements.md)

## Overview

This specification describes an **element-by-element reconstruction** approach for exporting all 37 app screens to Figma. Instead of raster screenshots, we analyze Flutter widget trees and document the structure for manual Figma rebuild with editable layers.

**Approach:** Code analysis → Design tokens extraction → Widget tree documentation → Figma layer structure guide

---

## Part 1: Design Tokens

### Color Palette

#### Primary Colors (Dark Theme)
| Token | Value | Usage |
|-------|-------|-------|
| `background.primary` | `#1A1A1A` | Main background |
| `background.surface` | `#2A2A2A` | Cards, input fields |
| `primary.main` | `#1E88E5` | Primary actions, accents |
| `primary.light` | `#42A5F5` | Primary hover states |
| `primary.dark` | `#1565C0` | Primary pressed states |

#### Semantic Colors
| Token | Value | Usage |
|-------|-------|-------|
| `success.main` | `#10B981` | Success states, connected |
| `warning.main` | `#F59E0B` | Warning states, connecting |
| `error.main` | `#EF4444` | Error states, disconnected |
| `info.main` | `#3B82F6` | Info states |
| `debug.main` | `#9CA3AF` | Debug states |

#### Text Colors
| Token | Value | Usage |
|-------|-------|-------|
| `text.primary` | `#FFFFFF` | Primary text |
| `text.secondary` | `#9CA3AF` | Secondary text, labels |
| `text.disabled` | `#6B7280` | Disabled text |

#### Border Colors
| Token | Value | Usage |
|-------|-------|-------|
| `border.default` | `#404040` | Default borders |
| `border.focused` | `#1E88E5` | Focused input borders |
| `border.error` | `#EF4444` | Error state borders |

### Typography

#### Font Family
- **Primary**: `Poppins` (Google Fonts)
- **Fallback**: `sans-serif`
- **Monospace**: For logs, code

#### Text Styles (Dark Theme)
| Token | Font Size | Weight | Line Height | Usage |
|-------|-----------|--------|-------------|-------|
| `display` | 28px | Bold (700) | 36px | Screen titles, logos |
| `headline.large` | 24px | Bold (700) | 32px | Section headers |
| `headline.medium` | 20px | SemiBold (600) | 28px | Card titles |
| `headline.small` | 18px | SemiBold (600) | 24px | Subsection headers |
| `body.large` | 16px | Normal (400) | 24px | Body text |
| `body.medium` | 14px | Normal (400) | 20px | Default body |
| `body.small` | 12px | Normal (400) | 16px | Captions, hints |
| `button.large` | 16px | SemiBold (600) | 24px | Large buttons |
| `button.medium` | 14px | SemiBold (600) | 20px | Default buttons |
| `label` | 12px | Medium (500) | 16px | Input labels |

### Spacing Scale
| Token | Value | Usage |
|-------|-------|-------|
| `space.xs` | 4px | Tight spacing |
| `space.sm` | 8px | Small gaps |
| `space.md` | 16px | Default padding |
| `space.lg` | 24px | Section spacing |
| `space.xl` | 32px | Large gaps |
| `space.xxl` | 40px | Section margins |

### Border Radius
| Token | Value | Usage |
|-------|-------|-------|
| `radius.sm` | 4px | Small badges, chips |
| `radius.md` | 8px | Buttons, cards |
| `radius.lg` | 12px | Input fields, large cards |
| `radius.xl` | 16px | Modals, dialogs |
| `radius.full` | 9999px | Circular buttons, FABs |

### Elevation (Shadows)
| Token | Value | Usage |
|-------|-------|-------|
| `shadow.sm` | 1dp | Subtle cards |
| `shadow.md` | 2dp | Default cards |
| `shadow.lg` | 4dp | Floating elements |
| `shadow.xl` | 8dp | Modals, dialogs |

---

## Part 2: Component Library

### Base Components

#### 1. Button - Primary
```
Frame: "Button/Primary"
- Rectangle: fill=#1E88E5, radius=8
- Text: "Connect", style=button.large, color=#FFFFFF
- Padding: 24×12
States:
  - Default: fill=#1E88E5
  - Hover: fill=#42A5F5
  - Disabled: fill=#404040, text=#6B7280
  - Loading: CircularProgressIndicator (white, stroke=2)
```

#### 2. Button - FAB
```
Frame: "Button/FAB"
- Circle: fill=#1E88E5 or dynamic, radius=28
- Icon: Icons.play_arrow or Icons.stop, size=24, color=#FFFFFF
- Extended: + Text label, padding=16×16
```

#### 3. Input Field
```
Frame: "Input/TextField"
- Rectangle: fill=#2A2A2A, stroke=#404040, radius=12
- Prefix Icon: Icons.person, size=24, color=#9CA3AF
- Label: "SIP Username", style=label, color=#9CA3AF
- Text: style=body.large, color=#FFFFFF
- Padding: 16×16
States:
  - Default: stroke=#404040
  - Focused: stroke=#1E88E5
  - Error: stroke=#EF4444
  - Disabled: fill=#2A2A2A40, text=#6B7280
```

#### 4. Card
```
Frame: "Container/Card"
- Rectangle: fill=#2A2A2A, radius=12, elevation=2
- Padding: 16
Children: [Content]
```

#### 5. Status Badge
```
Frame: "Status/Badge"
- Rectangle: fill=[color]20, radius=4
- Text: "CONNECTED", style=label, color=[color]
- Padding: 6×2
Colors:
  - Success: fill=#10B98120, text=#10B981
  - Warning: fill=#F59E0B20, text=#F59E0B
  - Error: fill=#EF444420, text=#EF4444
  - Info: fill=#3B82F620, text=#3B82F6
```

#### 6. Status Card
```
Frame: "Status/Card"
- Rectangle: fill=#2A2A2A, radius=8, elevation=1
- Icon: [icon], size=28, color=[status color]
- Title: "SIP", style=label, color=#9CA3AF
- Value: "Connected", style=headline.small, color=[status color]
- Padding: 16
```

#### 7. Info Row
```
Frame: "Layout/InfoRow"
- Auto Layout (horizontal)
- Label: "Phone Number", style=body.medium, color=#9CA3AF
- Spacer
- Value: "+1234567890", style=body.medium, color=#FFFFFF
- Padding: 4 vertical
```

#### 8. Dialog
```
Frame: "Overlay/Dialog"
- Rectangle: fill=#2A2A2A, radius=16, elevation=8
- Title: style=headline.medium
- Content: style=body.medium
- Actions: [Button]
- Padding: 24
```

---

## Part 3: Screen Specifications

### Screen Category 1: Core Gateway (5 screens)

#### 1.1 Auth Screen
**File**: `lib/screens/auth_screen.dart`

**Structure:**
```
Frame: "01 Auth Screen" (390×844 - iPhone 13)
├─ Background: fill=#1A1A1A
├─ SafeArea top
├─ Padding: 24
│  ├─ Spacer: 40
│  ├─ Icon: Icons.router, size=80, color=#42A5F5
│  ├─ Spacer: 24
│  ├─ Text: "GOSTsimbox Gateway", style=display
│  ├─ Spacer: 8
│  ├─ Text: "Configure your SIP credentials", style=body.large, color=#9CA3AF
│  ├─ Spacer: 40
│  ├─ Input: "SIP Username" [Icons.person]
│  ├─ Spacer: 16
│  ├─ Input: "SIP Password" [Icons.lock, password=true]
│  ├─ Spacer: 16
│  ├─ Input: "SIP Server" [Icons.dns]
│  ├─ Spacer: 16
│  ├─ Input: "SIP Port" [Icons.settings_ethernet, keyboard=number]
│  ├─ Spacer: 24
│  ├─ Checkbox Row
│  │  ├─ Checkbox: checked=false, activeColor=#42A5F5
│  │  ├─ Spacer: 8
│  │  └─ Text: "Remember credentials...", style=body.medium, color=#FFFFFF
│  ├─ Spacer: 32
│  └─ Button: Primary "Connect"
└─ SafeArea bottom
```

**Figma Layers:**
- Create frame: 390×844
- Add auto layout (vertical, spacing=16)
- Use components: Input, Button, Checkbox
- Icon library: Material Icons

---

#### 1.2 Dashboard Screen
**File**: `lib/screens/dashboard_screen.dart`

**Structure:**
```
Frame: "02 Dashboard Screen" (390×844)
├─ AppBar
│  ├─ Title: "GOSTsimbox Gateway 🚀", style=headline.medium
│  └─ Action: Icons.settings
├─ RefreshIndicator
├─ Padding: 16
│  ├─ Status Overview Card [Gradient Banner]
│  │  ├─ Gradient: linear (#4CAF50 → #2E7D32) if running
│  │  ├─ Icon: Icons.router, size=32
│  │  ├─ Text: "Gateway Status", style=body.large, color=#FFFFFF99
│  │  ├─ Text: "Running", style=display, color=#FFFFFF
│  │  ├─ Text: "Всё работает как часы! 🕐", style=body.small, italic, color=#FFFFFFCC
│  │  └─ Text: "Uptime 01:23:45", style=headline.small
│  ├─ Spacer: 16
│  ├─ Service Status Cards (Row ×3)
│  │  ├─ Card: "SIP" [Icons.phone_in_talk]
│  │  ├─ Card: "SMS" [Icons.sms]
│  │  └─ Card: "Calls" [Icons.call]
│  ├─ Spacer: 16
│  ├─ Device Info Card
│  │  ├─ Title: "Device Information", style=headline.medium
│  │  ├─ InfoRow: "Phone Number" → "+123..."
│  │  ├─ InfoRow: "Network Operator" → "MTS"
│  │  ├─ InfoRow: "Signal Strength" → "-85 dBm"
│  │  └─ InfoRow: "Gateway Version" → "3.0.0"
│  ├─ Spacer: 16
│  ├─ Quick Actions Card
│  │  ├─ Title: "Quick Actions"
│  │  └─ Action Buttons (Row ×4)
│  │     ├─ Button: "Make Call" [Icons.call]
│  │     ├─ Button: "Send SMS" [Icons.sms]
│  │     ├─ Button: "USSD" [Icons.dialpad]
│  │     └─ Button: "Logs" [Icons.list_alt]
│  ├─ Spacer: 16
│  └─ Statistics Card
│     ├─ Title: "Statistics"
│     ├─ Stat Items (Row ×3)
│     │  ├─ "📞" / "150" / "Звонков"
│     │  ├─ "💬" / "300" / "Сообщений"
│     │  └─ "🎯" / "98.5%" / "Успешность"
│     └─ Motivational Banner
└─ FAB: "Start/Stop" [Icons.play_arrow/Icons.stop]
```

---

#### 1.3 Settings Screen
**File**: `lib/screens/settings_screen.dart`

**Structure:**
```
Frame: "03 Settings Screen" (390×844)
├─ AppBar: "Settings"
└─ ListView [Padding: 16]
   ├─ Theme Card
   │  ├─ Header: [Icons.palette] "Theme"
   │  └─ Theme Options (Row ×3)
   │     ├─ Option: "Light" [Icons.wb_sunny]
   │     ├─ Option: "Dark" [Icons.nightlight_round] (selected)
   │     └─ Option: "System" [Icons.settings_system_daydream]
   ├─ Spacer: 16
   ├─ SIP Configuration Card
   │  ├─ Title: "SIP Configuration"
   │  └─ InfoRows: Username, Domain, Proxy, Port, Secure
   ├─ Spacer: 16
   ├─ SMPP Configuration Card
   │  ├─ Title: "SMPP Configuration"
   │  └─ InfoRows: Host, Port, System ID
   ├─ Spacer: 16
   ├─ Gateway Settings Card
   │  ├─ Title: "Gateway Settings"
   │  └─ InfoRows: Auto Answer, Enable Logging, Routes...
   ├─ Spacer: 16
   └─ Actions Card
      ├─ Title: "Actions"
      └─ ListTiles ×4
         ├─ "Reconfigure Gateway" [Icons.edit]
         ├─ "Restart Services" [Icons.refresh]
         ├─ "Clear Logs" [Icons.delete_sweep]
         └─ Divider
         └─ "About" [Icons.info]
```

---

#### 1.4 Logs Screen
**File**: `lib/screens/logs_screen.dart`

**Structure:**
```
Frame: "04 Logs Screen" (390×844)
├─ AppBar: "Логи 📝"
│  ├─ Action: Icons.keyboard_arrow_down (auto-scroll)
│  ├─ Action: Icons.filter_list
│  └─ Action: Icons.delete_outline
├─ Search Bar
│  ├─ TextField: "Search logs..." [Icons.search]
│  └─ Border: radius=8, fill=#FFFFFF
├─ Stats Bar
│  ├─ Text: "Showing 50 of 500 logs"
│  └─ Chip: "ERROR" [close icon]
└─ Logs List [Expanded]
   └─ Log Card (repeating)
      ├─ Border left: 4px [color by level]
      ├─ Header Row
      │  ├─ Badge: "ERROR" [fill=#EF444420, text=#EF4444]
      │  ├─ Badge: "Gateway" [fill=#FFFFFF20, text=#9CA3AF]
      │  ├─ Spacer
      │  └─ Text: "14:30:25", style=caption
      └─ Message: style=body.medium, maxLines=2
```

**Log Level Colors:**
- DEBUG: `#9CA3AF`
- INFO: `#3B82F6`
- WARNING: `#F59E0B`
- ERROR: `#EF4444`
- SUCCESS: `#10B981`

---

### Screen Category 2: Call Management (3 screens)

#### 2.1 Call Screen
**File**: `lib/screens/call_screen.dart`

**Structure:**
```
Frame: "05 Call Screen" (390×844)
├─ AppBar: "Active Call"
├─ Padding: 24
│  ├─ Contact Info
│  │  ├─ Avatar: Circle, size=120
│  │  ├─ Text: "+1234567890", style=headline.large
│  │  └─ Text: "02:34", style=display
│  ├─ Spacer: 40
│  ├─ Call Options (Grid 2×2)
│  │  ├─ Button: "Mute" [Icons.mic]
│  │  ├─ Button: "Speaker" [Icons.volume_up]
│  │  ├─ Button: "Keypad" [Icons.dialpad]
│  │  └─ Button: "Hold" [Icons.pause]
│  ├─ Spacer: 40
│  └─ End Call Button
│     └─ Button: FAB large, fill=#EF4444, "End" [Icons.call_end]
```

---

### Screen Category 3: SMS & Messaging (4 screens)

#### 3.1 SMS Screen
**File**: `lib/screens/sms_screen.dart`

**Structure:**
```
Frame: "06 SMS Screen" (390×844)
├─ AppBar: "SMS 💬"
├─ Message List [Expanded]
│  └─ Message Bubble (repeating)
│     ├─ Incoming: fill=#404040, radius=16 (top-left)
│     └─ Outgoing: fill=#1E88E5, radius=16 (bottom-right)
├─ Input Row
│  ├─ TextField: "Message..."
│  └─ Button: "Send" [Icons.send]
```

---

### Screen Category 4: Voice Line (6 screens)

#### 4.1 Voice Line Status Screen
**File**: `lib/presentation/screens/voice_line/voice_line_status_screen.dart`

**Structure:**
```
Frame: "07 Voice Line Status" (390×844)
├─ AppBar: "Voice Line"
├─ Status Card
│  ├─ Method: "TRRS", style=headline.medium
│  ├─ Status: "Connected" [badge]
│  └─ Signal Path Diagram
├─ Config Card
│  └─ InfoRows: Port, Baud Rate, Interface
└─ Action Buttons
   ├─ "Test" [Icons.test]
   └─ "Configure" [Icons.settings]
```

---

### Screen Category 5: Dongle (8 screens)

#### 5.1 Dongle Status Screen
**File**: `lib/presentation/screens/dongle/dongle_status_screen.dart`

**Structure:**
```
Frame: "08 Dongle Status" (390×844)
├─ AppBar: "Dongle"
├─ Type Card
│  ├─ Icon: Icons.usb
│  └─ Text: "USB Dongle Detected"
├─ Interface Status
│  ├─ TRRS: [connected/disconnected]
│  └─ USB: [connected/disconnected]
├─ Signal Level
│  └─ Bar indicator (5 segments)
└─ Actions
   ├─ "Detect Type"
   ├─ "Test Menu"
   └─ "Configure"
```

---

### Screen Category 6: SIP & Network (3 screens)
### Screen Category 7: Configuration (5 screens)
### Screen Category 8: Other (3 screens)

[Similar detailed structure for remaining 25 screens...]

---

## Part 4: Figma File Structure

### Recommended Organization

```
Telon (Figma File)
├─ Page: "📱 GOSTsimbox Gateway"
│  ├─ Section: "🎨 Design System"
│  │  ├─ Frame: "Colors"
│  │  ├─ Frame: "Typography"
│  │  ├─ Frame: "Components"
│  │  │  ├─ Buttons
│  │  │  ├─ Inputs
│  │  │  ├─ Cards
│  │  │  ├─ Badges
│  │  │  └─ Dialogs
│  │  └─ Frame: "Icons"
│  │  ├─ Section: "Core Gateway"
│  │  │  ├─ Frame: "01 Auth Screen"
│  │  │  ├─ Frame: "02 Dashboard Screen"
│  │  │  ├─ Frame: "03 Settings Screen"
│  │  │  └─ Frame: "04 Logs Screen"
│  │  ├─ Section: "Call Management"
│  │  │  ├─ Frame: "05 Call Screen"
│  │  │  ├─ Frame: "06 Calls Screen"
│  │  │  └─ Frame: "07 Incoming Video Call"
│  │  ├─ Section: "SMS & Messaging"
│  │  │  ├─ Frame: "08 SMS Screen"
│  │  │  ├─ Frame: "09 USSD Screen"
│  │  │  ├─ Frame: "10 SMPP Logs"
│  │  │  └─ Frame: "11 SMPP Settings"
│  │  ├─ Section: "Voice Line"
│  │  │  ├─ Frame: "12 Voice Line Status"
│  │  │  ├─ Frame: "13 Voice Line Settings"
│  │  │  ├─ Frame: "14 Select Method"
│  │  │  ├─ Frame: "15 Test Voice Line"
│  │  │  ├─ Frame: "16 Enhanced Mode"
│  │  │  └─ Frame: "17 TTY Config"
│  │  ├─ Section: "Dongle"
│  │  │  ├─ Frame: "18 Dongle Status"
│  │  │  ├─ Frame: "19 Dongle Monitor"
│  │  │  ├─ Frame: "20 Detect Type"
│  │  │  ├─ Frame: "21 Test Menu"
│  │  │  ├─ Frame: "22 TRRS Config"
│  │  │  ├─ Frame: "23 USB Accessory Config"
│  │  │  ├─ Frame: "24 USB DAC Config"
│  │  │  └─ Frame: "25 Schematic Viewer"
│  │  └─ Section: "Other"
│  │     ├─ Frame: "26 Lines Screen"
│  │     └─ Frame: "27 SIMs Screen"
```

---

## Part 5: Implementation Guide

### Step 1: Set Up Design System

1. **Create Color Styles**
   - Add all colors from Part 1 as Figma Color Styles
   - Naming: `GOSTsimbox/Background/Primary`, `GOSTsimbox/Primary/Main`, etc.

2. **Create Text Styles**
   - Add all text styles as Figma Text Styles
   - Naming: `GOSTsimbox/Display`, `GOSTsimbox/Body/Medium`, etc.

3. **Create Components**
   - Build all components from Part 2
   - Set up variants for states (default, hover, disabled)

### Step 2: Build Screens

For each screen:
1. Create frame (390×844 for iPhone 13)
2. Apply auto layout (vertical)
3. Use components from Design System
4. Follow structure from Part 3
5. Name layers clearly

### Step 3: Organize

1. Group screens by category (Sections)
2. Use consistent naming: "XX Screen Name"
3. Add cover frame with index

---

## Open Design Questions

- [ ] Device frame size: iPhone 13 (390×844) or Android (360×800)?
- [ ] Include device frame mockup or bare screens?
- [ ] Add interaction prototypes between screens?
- [ ] Create separate light theme variant?

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]
