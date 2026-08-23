# VDD: Analytics Screen

## Screen Overview

**Purpose**: View call analytics, quality metrics, and usage statistics  
**Type**: Analytics / Monitoring  
**Users**: Administrators, managers  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  Analytics           📊 [Period ▼]     │  ← AppBar
│  Calls │ Quality │ Usage               │  ← Tabs
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  📅 Period: Today                 ║ │  ← Period Selector
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ┌─────────┬─────────┬─────────┐       │
│  │ 📞 Total│ 📥 Inc  │ 📤 Out  │       │
│  │   156   │   89    │   67    │       │  ← Stats Cards
│  │ Calls   │Incoming │Outgoing │       │
│  └─────────┴─────────┴─────────┘       │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  📊 Call Volume                   ║ │
│  ║  [Chart Placeholder]              ║ │  ← Chart
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  📋 Recent Calls                  ║ │
│  ║  📞 +1234567890  Incoming  2m ago ║ │  ← History
│  ║  📤 +0987654321  Outgoing  5m ago ║ │
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
| Success Green | `#10B981` | Incoming calls |
| Info Blue | `#3B82F6` | Total/Outgoing |
| Warning Orange | `#F59E0B` | Metrics |
| Purple | `#8B5CF6` | Quality metrics |

### Typography

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| App Bar Title | Poppins | 20px | 600 | White |
| Tab Labels | System | 14px | Medium | White/Grey |
| Card Title | Poppins | 18px | Bold | White |
| Stat Value | Poppins | 18px | Bold | White |
| Stat Label | Poppins | 12px | Regular | Grey 400 |

### Iconography

| Icon | Size | Color | Location |
|------|------|-------|----------|
| Filter List | 24px | White | App bar |
| Call | 24px | Blue | Stats card |
| Call Received | 24px | Green | Incoming |
| Call Made | 24px | Orange | Outgoing |
| Signal Cellular | 24px | Green | Quality |
| Speed | 24px | Blue | Latency |

---

## Component Specifications

### Period Selector Card

**Border Radius**: 16px  
**Padding**: 16px  
**Background**: `#1A1A1A`  
**Border**: Grey 600, 1px

**Content**:
- Icon: Calendar (20px, Blue)
- Text: "Period: Today" (16px, Bold, White)

### Stats Cards

**Border Radius**: 12px  
**Padding**: 16px  
**Background**: `#1A1A1A`  
**Border**: Color with 30% opacity, 1px

**Layout**:
```
[Icon 24px, Colored]
[Value: 18px, Bold, White]
[Label: 12px, Grey 400, Center]
```

### Chart Card

**Border Radius**: 16px  
**Padding**: 20px  
**Background**: `#1A1A1A`  
**Border**: Color with 30% opacity, 1px

**Title**: 18px, Bold, White  
**Chart Area**: 200px height

### History Card

**Border Radius**: 16px  
**Padding**: 20px  
**Background**: `#1A1A1A`  
**Border**: Green with 30% opacity, 1px

**History Item**:
```
[Icon] [Number]    [Type]
       [Time]
```

---

## Interaction Specifications

### Tab Navigation

| Tab | Content |
|-----|---------|
| Calls | Call statistics, volume chart, history |
| Quality | MOS scores, latency, packet loss |
| Usage | Data usage, SMS count, balance |

### Period Filter

**Options**: Today, Week, Month, Year  
**Action**: Updates all statistics for selected period

### Tooltips

All stat cards have tooltips with explanations:
- Total Calls: "Total number of calls processed"
- MOS: "Mean Opinion Score - Audio quality 1-5"
- Latency: "Network delay time (lower is better)"

---

## Accessibility

### Text Scaling

- Support system font size up to 200%
- Charts remain readable
- Stats cards expand vertically

### Screen Reader Support

- Tab labels announced
- Stat values and labels announced
- Tooltip text available

### Color Contrast

- White text on dark bg: 7:1 (AAA)
- Colored borders distinguishable
- Icons supplement color coding

---

## Testing Checklist

### Visual Tests

- [ ] Tabs render correctly
- [ ] Stats cards show correct colors
- [ ] Chart placeholder displays
- [ ] History items formatted properly

### Interaction Tests

- [ ] Tab switching works
- [ ] Period filter updates data
- [ ] Tooltips display on long press

### State Tests

- [ ] Statistics update on refresh
- [ ] Period filtering works
- [ ] Charts update with data

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT - Pending review
