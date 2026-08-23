# VDD: Codecs Screen

## Screen Overview

**Purpose**: View and configure audio codecs for SIP calls  
**Type**: Technical Configuration  
**Users**: Administrators, technicians  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  Codecs Configuration                   │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Available Codecs                 ║ │
│  ║  ☑️ G.711 PCMU (0)        [≡]    ║ │
│  ║  ☑️ G.711 PCMA (8)        [≡]    ║ │
│  ║  ☑️ G.729 (18)            [≡]    ║ │  ← Codec List
│  ║  ☐ OPUS (123)             [≡]    ║ │
│  ║  ☐ G.722 (9)              [≡]    ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Codec Priority Order             ║ │
│  ║  1. G.711 PCMU                    ║ │
│  ║  2. G.711 PCMA                    ║ │  ← Priority
│  ║  3. G.729                         ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│         [Save Configuration]            │  ← Button
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Enabled | `#10B981` | Green (checkbox) |
| Disabled | `#9CA3AF` | Grey (checkbox) |
| Priority Badge | `#3B82F6` | Blue |
| Background | `#0A0A0A` | Dark theme |
| Card | `#1A1A1A` | Card background |

---

## Component Specifications

### Codec List Items

**Height**: 56px  
**Checkbox**: Leading  
**Name**: Primary text (16px)  
**ID**: Secondary text (12px, Grey)  
**Drag Handle**: Trailing icon

### Priority List

**Background**: `#1A1A1A`  
**Border Radius**: 12px  
**Padding**: 16px

**Item Layout**:
```
[Priority Number] [Codec Name]
```

---

## Interaction Specifications

### Codec Selection

- Toggle checkbox to enable/disable
- Drag to reorder priority
- Changes apply on Save

### Save Button

**Action**: Save codec configuration to settings

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
