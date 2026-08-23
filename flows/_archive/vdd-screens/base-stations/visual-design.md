# VDD: Base Stations Screen

## Screen Overview

**Purpose**: Monitor cellular base stations and signal quality  
**Type**: Network Monitoring / Technical  
**Users**: Network administrators, technicians  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  📡 Base Stations           ↻          │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────┬─────────┬─────────┐       │
│  │ 📡 Active│ 📞 Lines│ 📶 Avg  │       │
│  │    3    │   10    │ -65dBm  │       │  ← Stats
│  └─────────┴─────────┴─────────┘       │
│                                         │
│  [All] [Active] [Weak] [Inactive]      │  ← Filter Chips
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  📡 LAC:12345 • CELL:67890   [Active]║ │
│  ║     MTS                           ║ │
│  ║     📶 -65dBm  📞 3 lines  ⏰ 2min ║ │  ← Station Card
│  ║  ───────────────────────────────── ║ │
│  ║  Location: Moscow, Russia         ║ │
│  ║  [View Metrics] [Connected Lines] ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Primary | `#1E88E5` | App bar, accents |
| Background | `#0A0A0A` | Dark theme bg |
| Card Background | `#1A1A1A` | Card backgrounds |
| Active | `#10B981` | Green (active stations) |
| Weak | `#F59E0B` | Orange (weak signal) |
| Inactive | `#EF4444` | Red (inactive) |

### Typography

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| App Bar Title | Poppins | 20px | Bold | White |
| Card Title | Poppins | 14px | 600 | White |
| Operator | Poppins | 12px | Regular | Grey 400 |
| Status Chip | Poppins | 10px | 600 | Colored |
| Info Labels | Poppins | 10px | Regular | Grey 400 |

---

## Component Specifications

### Stats Cards

**Border Radius**: 12px  
**Padding**: 16px  
**Background**: `#1A1A1A`  
**Border**: Grey 800, 1px

### Filter Chips

**Height**: 50px  
**Background**: `#2A2A2A` (unselected)  
**Selected**: Blue 600  
**Text**: 12px, 600 when selected

### Station Cards

**Border Radius**: 12px  
**Margin**: 12px bottom  
**Background**: `#1A1A1A`  
**Border**: Grey 800, 1px

**Status Badge**:
- Padding: 8px horizontal, 4px vertical
- Background: Status color with 20% opacity
- Text: 10px, Bold, Status color

**Info Chips**:
- Background: Grey 800
- Icon: 12px
- Text: 10px, Grey 400

---

## Interaction Specifications

### Filter Chips

| Filter | Shows |
|--------|-------|
| All | All stations |
| Active | Active stations only |
| Weak | Weak signal stations |
| Inactive | Inactive stations |

### Card Expansion

**Collapsed**: Summary info (LAC, CELL, operator, status)  
**Expanded**: Full details + action buttons

### Action Buttons

| Button | Action |
|--------|--------|
| View Metrics | Show detailed signal metrics dialog |
| Connected Lines | Show connected lines dialog |

---

## Accessibility

### Text Scaling

- Support up to 200%
- Cards expand vertically
- Info chips remain readable

### Screen Reader Support

- Station status announced
- Signal strength announced
- Connected lines count announced

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
