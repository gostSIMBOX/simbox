# VDD: Info Screen (Device Info)

## Screen Overview

**Purpose**: Display application and device information  
**Type**: Information / About  
**Users**: All users, support technicians  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  Device Info                            │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  📡 GOSTsimbox Gateway            ║ │
│  ║     Version 2.0.4                 ║ │  ← App Info
│  ║  Bidirectional bridge GSM ↔ SIP   ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  📱 Device Information            ║ │
│  ║  Device Model    Pixel 7          ║ │
│  ║  Manufacturer    Google           ║ │  ← Device Info
│  ║  Android Version 14               ║ │
│  ║  SDK Level       34               ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  ℹ️ System Information            ║ │
│  ║  Platform        android          ║ │
│  ║  Theme           Dark             ║ │  ← System Info
│  ║  Locale          en_US            ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  💻 About                         ║ │
│  ║  Features:                        ║ │
│  ║  • Bidirectional call routing     ║ │  ← About
│  ║  • Real-time monitoring           ║ │
│  ╚═══════════════════════════════════╝ │
└─────────────────────────────────────────┘
```

### Color Palette

| Section | Border Color | Icon Color |
|---------|--------------|------------|
| App Info | Blue 30% | Blue 400 |
| Device Info | Green 30% | Green 400 |
| System Info | Orange 30% | Orange 400 |
| About | Purple 30% | Purple 400 |

### Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Section Title | 18px | Bold | White |
| Label | 14px | 500 | Grey 400 |
| Value | 14px | 600 | White |
| Description | 14px | Regular | Grey 300 |

---

## Component Specifications

### Info Cards

**Border Radius**: 16px  
**Padding**: 20px  
**Background**: `#1A1A1A`  
**Border**: Colored with 30% opacity, 1px

**Icon Container**:
- Size: 44px (12px padding + 28px icon)
- Background: Color with 20% opacity
- Border Radius: 12px

### Info Rows

**Layout**:
```
[Label (2 flex)]     [Value (3 flex)]
```

**Spacing**: 12px bottom margin

---

## Interaction Specifications

### Copy to Clipboard

**Action**: Long press on any value to copy

### Refresh

**Action**: Pull to refresh device info

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
