# VDD: Lines Screen

## Screen Overview

**Purpose**: Configure SIP lines and GSM channels  
**Type**: Configuration / Technical  
**Users**: Administrators  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  Lines Configuration                    │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  SIP Lines                        ║ │
│  ║  ┌─────────────────────────────┐  ║ │
│  ║  │ Line 1  🟢 Active     [≡]  │  ║ │
│  ║  │ admin@sip.example.com       │  ║ │
│  ║  └─────────────────────────────┘  ║ │
│  ║  ┌─────────────────────────────┐  ║ │
│  ║  │ Line 2  🔴 Inactive   [≡]  │  ║ │
│  ║  │ user2@sip.example.com       │  ║ │
│  ║  └─────────────────────────────┘  ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  GSM Channels                     ║ │
│  ║  ┌─────────────────────────────┐  ║ │
│  ║  │ SIM 1  🟢 Active      [+44]│  ║ │
│  ║  │ +1234567890                 │  ║ │
│  ║  └─────────────────────────────┘  ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│              [+ Add Line]               │  ← FAB
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Active | `#10B981` | Green status |
| Inactive | `#EF4444` | Red status |
| Primary | `#1E88E5` | App bar, FAB |
| Background | `#FAFAFA` | Screen bg |

---

## Component Specifications

### Line Cards

**Border Radius**: 8px  
**Margin**: 8px bottom  
**Elevation**: 1

**Status Indicator**: 8px circle  
**Drag Handle**: Trailing icon

---

## Interaction Specifications

### Line Actions

- Tap to edit
- Drag to reorder
- FAB to add new line

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
