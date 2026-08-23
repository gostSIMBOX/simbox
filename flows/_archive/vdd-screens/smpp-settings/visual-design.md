# VDD: SMPP Settings Screen

## Screen Overview

**Purpose**: Configure SMPP connection parameters  
**Type**: Configuration / Technical  
**Users**: Administrators  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  SMPP Settings                          │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Connection                       ║ │
│  ║  Host: smpp.example.com           ║ │
│  ║  Port: 2775                       ║ │
│  ║  System ID: gateway               ║ │
│  ║  Password: ••••••••               ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Advanced                         ║ │
│  ║  System Type:                     ║ │
│  ║  Source TON: 0                    ║ │
│  ║  Source NPI: 0                    ║ │
│  ║  Address Range:                   ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│         [Test Connection]               │
│         [Save Settings]                 │
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Primary | `#1E88E5` | Buttons, accents |
| Success | `#10B981` | Test success |
| Error | `#EF4444` | Test failure |

---

## Component Specifications

### Input Fields

**Height**: 56px  
**Border Radius**: 8px  
**Password**: Obscured text

### Test Button

**Action**: Test SMPP connection  
**Result**: Show success/failure SnackBar

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
