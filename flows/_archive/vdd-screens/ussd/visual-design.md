# VDD: USSD Screen

## Screen Overview

**Purpose**: Send USSD codes and view responses  
**Type**: Utility / Communication  
**Users**: Operators, administrators  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  USSD                                   │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Send USSD Code                   ║ │
│  ║  ┌─────────────────────────────┐  ║ │
│  ║  │ *123#                       │  ║ │  ← Input
│  ║  └─────────────────────────────┘  ║ │
│  ║          [Send]                   ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Quick Codes                      ║ │
│  ║  [*100#] [*101#] [*111#]         ║ │  ← Quick Codes
│  ║  Balance  Numbers  Data           ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  History                          ║ │
│  ║  *123# - Response text...        ║ │  ← History
│  ║  03/03/2026 14:30                 ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Primary | `#1E88E5` | App bar, buttons |
| Quick Code | `#3B82F6` | Blue chips |
| Background | `#FAFAFA` | Screen bg |

---

## Component Specifications

### Input Field

**Height**: 56px  
**Border Radius**: 8px  
**Hint**: "*123#"

### Quick Code Chips

**Height**: 32px  
**Background**: Blue 20%  
**Text**: 14px, Blue

### History Items

**Padding**: 12px  
**Border Bottom**: Grey 200, 1px

---

## Interaction Specifications

### Send USSD

**Flow**:
1. Enter USSD code (must start with *)
2. Tap Send
3. Show loading dialog
4. Display response in SnackBar

### Quick Codes

**Action**: Tap to fill input field

### History

**Action**: Tap to re-send code

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
