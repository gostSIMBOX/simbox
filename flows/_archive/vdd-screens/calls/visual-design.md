# VDD: Calls Screen (History)

## Screen Overview

**Purpose**: View call history with filtering and actions  
**Type**: History / Communication  
**Users**: All users  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  Call History        🔄  🔽       ⋮     │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  📞 +1234567890              ⋮   ║ │
│  ║     Completed                     ║ │  ← Call Item
│  ║     5m ago                        ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  📤 +0987654321              ⋮   ║ │
│  ║     Missed                        ║ │
│  ║     2h ago                        ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│                    [📞]                 │  ← FAB
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Incoming | `#10B981` | Green avatar |
| Outgoing | `#3B82F6` | Blue avatar |
| Missed | `#EF4444` | Red |
| Completed | `#10B981` | Green |
| Background | `#0A0A0A` | Dark theme |
| Card | `#1A1A1A` | Card background |

### Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Phone Number | 16px | 500 | White |
| Status | 12px | Regular | Grey |
| Time | 12px | Regular | Grey |

---

## Component Specifications

### Call Cards

**Border Radius**: 8px  
**Margin**: 8px bottom  
**Background**: `#1A1A1A`

**Avatar**: 40px circle, color by direction

**Popup Menu**:
- Call (phone icon)
- Send SMS (sms icon)
- Call Info (info icon)

### FAB

**Size**: Standard (56px)  
**Color**: Green  
**Icon**: Call (white)

---

## Interaction Specifications

### Card Actions

| Popup Action | Behavior |
|--------------|----------|
| Call | Initiate call to number |
| Send SMS | Navigate to SMS with pre-filled number |
| Call Info | Show call details dialog |

### FAB

**Action**: Open dialer dialog

### Filter Dialog

**Options**:
- Incoming (checkbox)
- Outgoing (checkbox)
- Missed (checkbox)

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
