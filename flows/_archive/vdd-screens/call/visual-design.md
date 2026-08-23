# VDD: Call Screen

## Screen Overview

**Purpose**: Make and manage calls (SIP, GSM, routings)  
**Type**: Communication / Call Management  
**Users**: Operators, administrators  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  Calls                            ⋮     │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Make Call                        ║ │
│  ║  ┌──────────────┐ [Call]          ║ │  ← Dialer
│  ║  │ +1234567890  │                 ║ │
│  ║  └──────────────┘                 ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Quick Actions                    ║ │
│  ║  [📞]    [📥]    [📴]             ║ │  ← Quick Actions
│  ║  Test   Incoming  End All         ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ SIP Calls │ GSM Calls │ Routings │ │  ← TabBar
│  └───────────────────────────────────┘ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  📞 +1234567890              📴   ║ │
│  ║     State: active                 ║ │  ← Call List
│  ║     Duration: 05:30               ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Primary | `#1E88E5` | App bar, accents |
| Background | `#FAFAFA` | Screen background |
| Card Background | `#FFFFFF` | Card backgrounds |
| Connecting | `#F59E0B` | Orange (connecting state) |
| Ringing | `#3B82F6` | Blue (ringing state) |
| Active | `#10B981` | Green (active calls) |
| Hold | `#8B5CF6` | Purple (hold state) |
| Ended | `#9CA3AF` | Grey (ended calls) |
| Failed | `#EF4444` | Red (failed calls) |

### Typography

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| App Bar Title | System | 20px | Bold | White |
| Card Title | System | 18px | Bold | Grey 900 |
| Phone Number | System | 16px | Bold | Grey 900 |
| State Label | System | 14px | Regular | Grey 600 |
| Duration | System | 14px | Regular | Grey 600 |

### Iconography

| Icon | Size | Color | Location |
|------|------|-------|----------|
| Phone | 24px | White | App bar |
| Call (outgoing) | 24px | White | Avatar |
| Call Received (incoming) | 24px | White | Avatar |
| Call End | 24px | Red | Action button |
| Pause (hold) | 24px | Orange | Action button |
| Play Arrow (resume) | 24px | Blue | Action button |

---

## Component Specifications

### Dialer Card

**Border Radius**: 12px  
**Padding**: 16px  
**Elevation**: 1

**Input Field**:
- Height: 56px
- Border Radius: 8px
- Prefix Icon: phone (24px)

**Call Button**:
- Background: Primary Blue
- Text: "Call"
- Icon: call

### Quick Actions Card

**Border Radius**: 12px  
**Padding**: 16px  
**Elevation**: 1

**Action Buttons**:
- Size: Circle, 48px diameter
- Background: White with elevation
- Icon: 24px
- Label: 12px below

### Call Cards

**Border Radius**: 8px  
**Margin**: 8px bottom  
**Elevation**: 1

**Avatar**:
- Size: 40px circle
- Color: State-based

**Content Layout**:
```
[Avatar] [Number]           [Actions...]
         [State]
         [Duration]
```

### TabBar

**Height**: 48px  
**Indicator**: Primary Blue (2px bottom)  
**Label Color**: Active = Primary, Inactive = Grey

---

## Interaction Specifications

### Make Call

**Flow**:
1. Enter number in text field
2. Tap "Call" button
3. GatewayService.makeCallViaSip() called
4. Call appears in SIP Calls tab
5. State transitions: connecting → ringing → active

### Quick Actions

| Button | Action |
|--------|--------|
| Test Call | Dials +1234567890 |
| Incoming | Simulates incoming call from +0987654321 |
| End All | Ends all active calls |

### Call Actions (per call)

| State | Available Actions |
|-------|-------------------|
| Ringing (incoming) | Answer (green phone), End (red) |
| Active | Hold (orange pause), End (red) |
| Hold | Resume (blue play), End (red) |

### Tab Navigation

| Tab | Content |
|-----|---------|
| SIP Calls | List of SipCall objects |
| GSM Calls | List of TelephonyCall objects |
| Routings | List of CallRouting objects |

---

## State Management

### Data Sources

| Data | Source | Update Frequency |
|------|--------|------------------|
| SIP Calls | SipService.callStateStream | Real-time |
| GSM Calls | TelephonyService.callStateStream | Real-time |
| Routings | GatewayService.routingStream | Real-time |

### State Transitions

**SipCallState**:
```
connecting → ringing → active → hold → active → ended
                                    │
                                    └──→ ended
```

**TelephonyCallState**:
```
idle → ringing → offhook → active → ended
```

**CallRoutingState**:
```
connecting → active → ended
                 │
                 └──→ failed
```

---

## Accessibility

### Text Scaling

- Support system font size up to 200%
- Phone numbers remain readable
- Action buttons maintain touch targets

### Screen Reader Support

- Call direction announced (incoming/outgoing)
- State announced (active, ringing, etc.)
- Duration announced

### Color Contrast

- State colors distinguishable for colorblind users
- Icons supplement color coding
- Text on white: 7:1 (AAA)

---

## Testing Checklist

### Visual Tests

- [ ] State colors render correctly
- [ ] TabBar displays properly
- [ ] Call cards show all information
- [ ] Quick action buttons aligned

### Interaction Tests

- [ ] Make call works
- [ ] Quick actions functional
- [ ] Answer/hold/resume/end work
- [ ] Tabs switch correctly

### State Tests

- [ ] Real-time updates work
- [ ] Calls removed after ending
- [ ] State transitions smooth

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT - Pending review
