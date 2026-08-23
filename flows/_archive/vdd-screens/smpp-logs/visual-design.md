# VDD: SMPP Logs Screen

## Screen Overview

**Purpose**: View SMPP protocol logs  
**Type**: Logging / Technical  
**Users**: Administrators, developers  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  SMPP Logs         ↻  🗑️  🔍           │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║ [BIND] [TX]           14:30:25    ║ │
│  ║ BIND_TRANSCEIVER sent             ║ │
│  ║ Response: BIND_OK                 ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║ [SUBMIT_SM] [TX]      14:30:30    ║ │
│  ║ Submit to: +1234567890            ║ │
│  ║ Message ID: 12345                 ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
└─────────────────────────────────────────┘
```

### Color Palette

| Type | Color | Usage |
|------|-------|-------|
| TX (Transmit) | `#3B82F6` | Blue |
| RX (Receive) | `#10B981` | Green |
| Error | `#EF4444` | Red |

---

## Component Specifications

### Log Cards

**Border Radius**: 8px  
**Margin**: 8px bottom  
**Left Border**: 4px colored

**Badges**:
- Type: [BIND], [SUBMIT_SM], etc.
- Direction: [TX], [RX]

---

## Interaction Specifications

### Filter

**Options**: All, TX, RX, Errors

### Tap

**Action**: Show full SMPP PDU details

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
