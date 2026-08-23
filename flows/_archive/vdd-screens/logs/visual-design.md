# VDD: Logs Screen

## Screen Overview

**Purpose**: View and filter system logs in real-time  
**Type**: Monitoring / Logging  
**Users**: Administrators, support technicians  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  Логи 📝           👁️  🗑️  🔽  ⋮      │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ 🔍 Search logs...         [✕]    │ │  ← Search
│  └───────────────────────────────────┘ │
│                                         │
│  Showing 45 of 156 logs    [info ✕]   │  ← Stats Bar
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║ [INFO] [Gateway]        14:30:25  ║ │
│  ║ Gateway started successfully      ║ │  ← Log Card
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║ [ERROR] [SIP]           14:28:10  ║ │
│  ║ Registration failed: timeout      ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│            [↑] [↓]                      │  ← Scroll FABs
└─────────────────────────────────────────┘
```

### Color Palette

| Level | Color | Background |
|-------|-------|------------|
| Debug | `#9CA3AF` | Grey 20% |
| Info | `#3B82F6` | Blue 20% |
| Warning | `#F59E0B` | Orange 20% |
| Error | `#EF4444` | Red 20% |
| Success | `#10B981` | Green 20% |

### Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Level Badge | 10px | Bold | Colored |
| Source Badge | 10px | Bold | Grey |
| Timestamp | 11px | Regular | Grey |
| Message | 13px | Regular | Grey 900 |

---

## Component Specifications

### Search Bar

**Height**: 48px  
**Border Radius**: 8px  
**Background**: White  
**Border**: Grey 300

### Log Cards

**Border Radius**: 8px  
**Margin**: 8px horizontal, 2px vertical  
**Elevation**: 1  
**Left Border**: 4px colored by level

**Layout**:
```
[Level] [Source]     [Time]
[Message (2 lines max)]
```

### Filter Chip

**Height**: 24px  
**Background**: Level color with 20% opacity  
**Text**: 10px, Bold  
**Delete Icon**: Close icon

---

## Interaction Specifications

### AppBar Actions

| Icon | Action |
|------|--------|
| Auto-scroll | Toggle auto-scroll on new logs |
| Clear All | Clear all logs (confirm) |
| Filter | Select log level filter |

### Log Card Tap

**Action**: Show details dialog

### Details Dialog

**Content**:
- Full message (selectable)
- Timestamp
- Level
- Source
- **Actions**: Copy, Close

### Scroll FABs

| FAB | Action |
|-----|--------|
| Up (top) | Scroll to top |
| Down (bottom) | Scroll to bottom |

---

## Accessibility

### Text Scaling

- Support up to 200%
- Messages wrap properly
- Timestamps remain readable

### Screen Reader Support

- Level announced (INFO, ERROR, etc.)
- Source announced
- Full message read

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
