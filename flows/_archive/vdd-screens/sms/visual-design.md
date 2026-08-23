# VDD: SMS Screen

## Screen Overview

**Purpose**: Compose, send, and view SMS messages  
**Type**: Communication / Messaging  
**Users**: Operators, administrators  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  SMS                    ⋮  ↻            │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Send SMS                         ║ │
│  ║  ┌─────────────────────────────┐  ║ │
│  ║  │ Recipient: +1234567890      │  ║ │  ← Compose
│  ║  └─────────────────────────────┘  ║ │
│  ║  ┌─────────────────────────────┐  ║ │
│  ║  │ Message: Hello...           │  ║ │
│  ║  │                    [160]    │  ║ │
│  ║  └─────────────────────────────┘  ║ │
│  ║  ☐ Use SMPP          [Send]       ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  SMS Statistics                   ║ │
│  ║  Total  Sent  Delivered  Failed   ║ │  ← Stats
│  ║   156     142     138       4     ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  💬 +1234567890        [delivered]║ │
│  ║  Hello World                      ║ │  ← Messages
│  ║  03/03/2026 14:30                 ║ │
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
| Pending | `#F59E0B` | Orange (pending) |
| Sent | `#3B82F6` | Blue (sent) |
| Delivered | `#10B981` | Green (delivered) |
| Failed | `#EF4444` | Red (failed) |
| Received | `#8B5CF6` | Purple (received) |

### Typography

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| App Bar Title | System | 20px | Bold | White |
| Card Title | System | 18px | Bold | Grey 900 |
| Phone Number | System | 16px | Bold | Grey 900 |
| Message Preview | System | 14px | Regular | Grey 700 |
| Timestamp | System | 12px | Regular | Grey 500 |
| Status Chip | System | 10px | Bold | Varies |

### Iconography

| Icon | Size | Color | Location |
|------|------|-------|----------|
| SMS | 24px | White | App bar |
| Person | 24px | Grey | Recipient prefix |
| Message | 24px | Grey | Message prefix |
| Send | 24px | White | Send button |
| Call Received | 24px | White | Incoming avatar |
| Call Made | 24px | White | Outgoing avatar |

---

## Component Specifications

### Compose Card

**Border Radius**: 12px  
**Padding**: 16px  
**Elevation**: 1

**Input Fields**:
- Recipient: Single line, phone keyboard
- Message: 3 lines max, 160 char counter

**SMPP Toggle**:
- Switch with "Use SMPP" label
- Default: OFF

**Send Button**:
- Elevated, icon + text
- Background: Primary Blue

### Statistics Card

**Border Radius**: 12px  
**Padding**: 16px  
**Elevation**: 1

**Stat Items**:
```
[Value: 20px, Bold, Blue]
[Label: 12px, Grey]
```

### Message Cards

**Border Radius**: 8px  
**Margin**: 8px bottom  
**Elevation**: 1

**Layout**:
```
[Avatar] [Number] [Status Chip]
         [Message preview (2 lines)]
         [Timestamp]
                  [⋮ popup menu]
```

**Status Chips**:
- Background: Color with 20% opacity
- Text: 10px, Bold, Color
- Border Radius: 4px

---

## Interaction Specifications

### Send SMS

**Flow**:
1. Enter recipient number
2. Enter message (max 160 chars)
3. Toggle "Use SMPP" if needed
4. Tap "Send" button
5. Message appears in list with "pending" status
6. Status updates: pending → sent → delivered

### Message Actions (Popup Menu)

| Action | Behavior |
|--------|----------|
| Copy | Copy message to clipboard |
| Reply | Pre-fill compose with sender |
| Delete | Remove message from list |

### AppBar Actions

| Action | Behavior |
|--------|----------|
| Refresh | Reload messages list |
| Clear Messages | Delete all messages |
| Send Test SMS | Send to +1234567890 |
| Simulate Incoming | Add mock incoming message |

---

## State Management

### Data Sources

| Data | Source | Update Frequency |
|------|--------|------------------|
| Messages | SmsService.messageStream | Real-time |
| Statistics | SmsService.getMessageStats() | On load |

### Message Status Flow

**Outgoing**:
```
pending → sent → delivered
          │
          └──→ failed
```

**Incoming**:
```
received (final state)
```

---

## Accessibility

### Text Scaling

- Support system font size up to 200%
- Message preview wraps properly
- Touch targets maintain 48x48px minimum

### Screen Reader Support

- Message direction announced (incoming/outgoing)
- Status announced
- Timestamp announced

### Color Contrast

- Status colors have icon backup
- Text on white: 7:1 (AAA)

---

## Testing Checklist

### Visual Tests

- [ ] Status colors render correctly
- [ ] Character counter works
- [ ] Message cards display properly
- [ ] Statistics show correct values

### Interaction Tests

- [ ] Send SMS works
- [ ] SMPP toggle functional
- [ ] Copy/Reply/Delete work
- [ ] Refresh reloads messages

### State Tests

- [ ] Real-time status updates
- [ ] Statistics update correctly
- [ ] Messages persist

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT - Pending review
