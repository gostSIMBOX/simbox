# SIM-Hub Dashboard - Visual Design Document

> Visual-Driven Development: Dashboard and UI/UX specifications.

## Overview

**Domain**: SIM-Hub Dashboard  
**Type**: VDD (Visual-Driven Development)  
**Status**: DRAFT  
**Generated**: 2026-03-04  
**Source**: Legacy PHP UI (`legacy/www/smb_scheduler/`, `legacy/www/goip/`) → Modern React/Material Design

## Design System

### Technology Stack

- **Framework**: React 18+ with TypeScript
- **UI Library**: Material-UI (MUI) v5
- **Icons**: Material Design Icons
- **Charts**: Recharts / Chart.js
- **Real-time**: WebSocket for live updates
- **Theme**: Custom SIM-Hub brand (blue/teal primary)

### Color Palette

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary | Deep Blue | `#1976D2` | Navigation, primary actions |
| Secondary | Teal | `#00897B` | Success states, SIM active |
| Error | Red | `#D32F2F` | Errors, SIM offline |
| Warning | Orange | `#F57C00` | Warnings, SIM busy |
| Info | Blue | `#1976D2` | Information, tooltips |
| Success | Green | `#388E3C` | Success messages, online status |
| Background | Light Gray | `#F5F5F5` | Page background |
| Surface | White | `#FFFFFF` | Cards, panels |

### Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| H1 (Page Title) | Roboto | 32px | 700 |
| H2 (Section) | Roboto | 24px | 600 |
| H3 (Subsection) | Roboto | 20px | 600 |
| Body | Roboto | 14px | 400 |
| Caption | Roboto | 12px | 400 |
| Code | Roboto Mono | 13px | 400 |

## Dashboard Layouts

### 1. Main Dashboard (Home)

**Purpose**: Overview of entire SIM-bank infrastructure

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  SIM-Hub Dashboard                              [User] [Settings]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐│
│  │ SIM-Banks   │  │ Total Slots │  │ Active SIMs │  │ Errors  ││
│  │    12       │  │    1,536    │  │   1,421     │  │    3    ││
│  │   +2 today  │  │  92% used   │  │   93%       │  │  -1 vs  ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘│
│                                                                  │
│  ┌────────────────────────────┐  ┌─────────────────────────────┐│
│  │  SIM-Bank Status Map       │  │  Signal Strength Trend      ││
│  │  [Map with markers]        │  │  [Line chart: 24h]          ││
│  │                            │  │                             ││
│  │  🟢 🟢 🟢 🟡 🔴           │  │  Avg: -67dBm                ││
│  │  🟢 🟢 🟢 🟢 🟢           │  │  Peak: -45dBm               ││
│  └────────────────────────────┘  └─────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Recent Activity                                             ││
│  │  ─────────────────────────────────────────────────────────  ││
│  │  [12:34] SIM-Bank #5 slot 12 status changed: online → off  ││
│  │  [12:33] USSD command sent to SIM-Bank #3 slot 5           ││
│  │  [12:30] Scheduled task completed: Power cycle Bank #7     ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

**Components**:
- **Stats Cards**: 4 summary metrics with trends
- **Status Map**: Geographic distribution of SIM-banks
- **Signal Chart**: 24-hour signal strength trend
- **Activity Feed**: Real-time event stream

### 2. SIM-Bank Detail View

**Purpose**: Detailed view of individual SIM-bank

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  < Back to Dashboard    SIM-Bank #5 - SMB128    [Edit] [Actions]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Status: 🟢 Online    Location: Data Center A                  │
│  URL: http://192.168.1.105:8080    Last Poll: 12:34:50 (30s ago)│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Slot Grid (128 slots)                                      ││
│  │  ┌───┬───┬───┬───┬───┬───┬───┬───┐                        ││
│  │  │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ ... (16 rows x 8 cols) ││
│  │  ├───┼───┼───┼───┼───┼───┼───┼───┤                        ││
│  │  │ 🟢│ 🟢│ 🟡│ 🟢│ 🔴│ 🟢│ 🟢│ 🟢│ 🟢=Online 🟡=Busy       ││
│  │  │IMS│IMS│IMS│IMS│IMS│IMS│IMS│IMS│ 🔴=Offline ⚫=Empty    ││
│  │  │123│456│789│012│345│678│901│234│                        ││
│  │  └───┴───┴───┴───┴───┴───┴───┴───┘                        ││
│  │  [Show all 128 slots in scrollable grid]                   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌────────────────────┐  ┌────────────────────┐                │
│  │  Signal Quality    │  │  Operator Dist.    │                │
│  │  [Pie chart]       │  │  [Bar chart]       │                │
│  │  Excellent: 45%    │  │  MTS: 32           │                │
│  │  Good: 38%         │  │  Beeline: 28       │                │
│  │  Fair: 12%         │  │  Megafon: 25       │                │
│  │  Poor: 5%          │  │  Tele2: 18         │                │
│  └────────────────────┘  └────────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

**Interactive Features**:
- Click slot → Detail modal (IMSI, ICCID, operator, signal)
- Right-click → Context menu (Power cycle, Send USSD, Disable)
- Filter: Show by status (online/offline/busy/error)
- Search: By IMSI, ICCID, slot number

### 3. Task Scheduler View

**Purpose**: Manage scheduled tasks

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  Task Scheduler                        [+ New Task] [Run Now]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Filters: [All Status ▼] [Type ▼] [Date Range]  [Search 🔍]    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Task Name          │ Type        │ Schedule   │ Status │ ⚙️ ││
│  │────────────────────│─────────────│────────────│────────│────││
│  │ Daily Power Cycle  │ power_cycle │ 0 2 * * *  │ 🟢 Active│ ⚙️││
│  │ SIM Activation #42 │ activation  │ Once       │ 🟡 Running│⚙️││
│  │ Weekly Sync        │ sync        │ 0 3 * * 0  │ 🟢 Active│ ⚙️││
│  │ Maintenance Check  │ maintenance │ 0 4 1 * *  │ 🔴 Failed│ ⚙️││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Task Execution History (Last 10 runs)                       ││
│  │ ──────────────────────────────────────────────────────────  ││
│  │ [12:00] Daily Power Cycle → ✅ Completed (45s)             ││
│  │ [Yesterday] Weekly Sync → ✅ Completed (2m 13s)            ││
│  │ [Mon] Maintenance Check → ❌ Failed: Timeout               ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 4. USSD Command Center

**Purpose**: Send and manage USSD commands

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  USSD Command Center                          [History] [Templates]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Select SIM Cards                                            ││
│  │ [x] Select All  [ ] Bank #5  [ ] Bank #6  [ ] Bank #7      ││
│  │                                                              ││
│  │ Selected: 12 SIM cards from 3 banks                         ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ USSD Command                                                ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ *100#                                                    │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │                                                              ││
│  │ [Quick Commands]                                             ││
│  │ [Balance *100#] [Tariff *111#] [Data *102#] [Custom...]    ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ [Send to Selected (12)]  [Schedule...]  [Save Template]     ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Recent Responses                                            ││
│  │ ──────────────────────────────────────────────────────────  ││
│  │ [12:34] Bank #5 Slot 3: "Balance: $10.50. Valid until..."  ││
│  │ [12:33] Bank #5 Slot 7: "Your tariff: Premium. Monthly..." ││
│  │ [12:30] Bank #6 Slot 1: ERROR: Network timeout             ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 5. Mobile Responsive Design

**Breakpoints**:
- **Desktop**: ≥1200px (full layout)
- **Tablet**: 768px-1199px (condensed, collapsible sidebar)
- **Mobile**: <768px (single column, bottom navigation)

**Mobile Adaptations**:
- Stats cards → Horizontal scroll
- Slot grid → List view with filters
- Sidebar → Hamburger menu
- Tables → Card layout with expandable rows

## Component Specifications

### Status Indicator

```tsx
interface StatusIndicator {
  status: 'online' | 'offline' | 'busy' | 'error';
  showLabel?: boolean;
  size?: 'small' | 'medium' | 'large';
}

// Visual mapping:
// online  → 🟢 Green circle (#4CAF50)
// offline → 🔴 Red circle (#F44336)
// busy    → 🟡 Yellow circle (#FFC107)
// error   → 🟠 Orange circle (#FF5722)
```

### SIM Slot Card

```tsx
interface SimSlotCard {
  slotId: number;
  imsi: string;
  iccid: string;
  operator: string;
  status: 'online' | 'offline' | 'busy' | 'error';
  signal: number; // 0-100
  power: boolean;
  onClick: (slotId: number) => void;
}

// Layout:
// ┌─────────────┐
// │ 🟢 Slot #12 │
// │ MTS         │
// │ IMSI: 12345 │
// │ Signal: ████░ 80% │
// └─────────────┘
```

### Signal Strength Meter

```tsx
interface SignalMeter {
  value: number; // dBm (-113 to -51)
  showLabel?: boolean;
}

// Visual mapping:
// -51 to -73 dBm  → 🟢 Excellent (5 bars)
// -74 to -83 dBm  → 🟢 Good (4 bars)
// -84 to -93 dBm  → 🟡 Fair (3 bars)
// -94 to -103 dBm → 🟠 Poor (2 bars)
// -104 to -113 dBm → 🔴 None (1 bar)
```

## Interaction Patterns

### Real-time Updates

**WebSocket Events**:
```typescript
// Slot status change
{
  type: 'SLOT_STATUS_UPDATE',
  payload: {
    simBankId: 5,
    slotId: 12,
    status: 'offline',
    signal: 0,
    timestamp: '2026-03-04T12:34:50Z'
  }
}

// New system event
{
  type: 'NEW_EVENT',
  payload: {
    level: 'error',
    message: 'SIM-Bank #5 connection lost',
    timestamp: '2026-03-04T12:34:50Z'
  }
}
```

### User Actions

**Power Control**:
1. Click slot → Context menu
2. Select "Power Cycle"
3. Confirmation dialog: "Power cycle slot #12?"
4. Optimistic UI update (show spinner)
5. WebSocket confirmation → Update status
6. Toast notification: "Power cycle successful"

**USSD Command**:
1. Select multiple slots (checkboxes)
2. Enter USSD command
3. Click "Send"
4. Progress indicator: "Sending to 12 SIMs..."
5. Real-time responses stream in
6. Summary: "10/12 successful, 2 failed"

## Accessibility

### WCAG 2.1 AA Compliance

- **Color Contrast**: Minimum 4.5:1 for text
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: ARIA labels for all interactive elements
- **Focus Indicators**: Visible focus rings
- **Error Messages**: Clear, descriptive error text

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `g` then `d` | Go to Dashboard |
| `g` then `s` | Go to SIM-Banks |
| `g` then `t` | Go to Tasks |
| `/` | Focus search |
| `?` | Show keyboard shortcuts |
| `Esc` | Close modal/cancel |

## Responsive Breakpoints

```css
/* Mobile first approach */
.sim-slot-grid {
  display: grid;
  grid-template-columns: 1fr; /* Mobile: 1 column */
  gap: 8px;
}

@media (min-width: 600px) {
  .sim-slot-grid {
    grid-template-columns: repeat(2, 1fr); /* Tablet: 2 columns */
  }
}

@media (min-width: 1200px) {
  .sim-slot-grid {
    grid-template-columns: repeat(8, 1fr); /* Desktop: 8 columns */
  }
}
```

## Legacy UI Comparison

| Legacy (PHP) | Modern (React) | Improvement |
|--------------|----------------|-------------|
| Static HTML pages | SPA with React Router | No page reloads |
| Table-based layout | Material-UI Grid | Responsive, accessible |
| jQuery AJAX | WebSocket + Redux | Real-time updates |
| Fixed width (1024px) | Fluid responsive | Mobile-friendly |
| Browser refresh | Optimistic UI updates | Better UX |
| No keyboard nav | Full keyboard support | Accessibility |

## Design Assets

### Icons (Material Design)

- **SIM-Bank**: `dns` (DNS icon)
- **Slot**: `sim-card`
- **Online**: `check_circle` (green)
- **Offline**: `cancel` (red)
- **Busy**: `schedule` (yellow)
- **Error**: `error` (orange)
- **Signal**: `signal_cellular_4_bar` to `signal_cellular_null`
- **Task**: `tasks` or `calendar_today`
- **USSD**: `chat` or `message`

### Logo

**SIM-Hub Logo**: 
- Concept: Hub/spoke pattern with SIM card icon
- Colors: Deep blue (#1976D2) + Teal accent (#00897B)
- Variants: Full (horizontal), Icon (square), Monochrome

---

*Generated by /legacy reverse engineering - VDD for stakeholder review*
