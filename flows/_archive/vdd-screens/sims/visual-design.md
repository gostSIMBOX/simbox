# VDD: SIMs Screen

## Screen Overview

**Purpose**: View SIM card information and status  
**Type**: Hardware / Information  
**Users**: Administrators, technicians  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  SIM Cards                              │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  SIM 1  🟢 Active                 ║ │
│  ║  ───────────────────────────────── ║ │
│  ║  Operator: MTS                    ║ │
│  ║  Number: +1234567890              ║ │
│  ║  Signal: 📶📶📶📶 (85%)           ║ │
│  ║  ICCID: 8970101...                ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  SIM 2  🔴 No SIM                 ║ │
│  ║  ───────────────────────────────── ║ │
│  ║  No SIM card inserted             ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Active | `#10B981` | Green |
| No SIM | `#9CA3AF` | Grey |
| Signal | `#10B981` | Green bars |
| Background | `#FAFAFA` | Screen bg |

---

## Component Specifications

### SIM Cards

**Border Radius**: 12px  
**Padding**: 16px  
**Elevation**: 1

**Signal Indicator**: 4-5 bars

---

## Interaction Specifications

### Refresh

**Action**: Pull to refresh SIM status

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
