# VDD: Theme Settings Screen

## Screen Overview

**Purpose**: Select application theme  
**Type**: Settings / Visual  
**Users**: All users  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  Theme Settings                         │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  🌞 Light                  [○]   ║ │
│  ║  Light theme for daytime use      ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  🌙 Dark                   [●]   ║ │
│  ║  Dark theme for technical mon.    ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  ⚙️ System                [○]   ║ │
│  ║  Auto-switch based on system      ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Selected | `#1E88E5` | Radio button |
| Icon Light | `#F59E0B` | Sun (yellow) |
| Icon Dark | `#8B5CF6` | Moon (purple) |
| Icon System | `#6B7280` | Gear (grey) |

---

## Component Specifications

### Theme Cards

**Border Radius**: 12px  
**Padding**: 16px  
**Elevation**: 1

**Radio Button**: Trailing  
**Icon**: Leading (24px)  
**Description**: 12px Grey

---

## Interaction Specifications

### Selection

**Action**: Tap card → Select theme → Save to preferences

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
