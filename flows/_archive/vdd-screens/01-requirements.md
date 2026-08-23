# Requirements: VDD Screens

## Overview

Visual-Driven Development (VDD) for the GOSTsimbox Gateway Android application screens. This document captures requirements for all 20 screens with visual specifications, user flows, and acceptance criteria.

## Stakeholders

- **Primary Users**: System administrators, operators, technical support staff
- **End Users**: Mobile app users interacting with gateway features
- **Dependencies**: ThemeService, SipService, GatewayService, SmsService, TelephonyService

---

## Business Requirements

### BR-1: Consistent Visual Design

All screens must follow a consistent visual design language based on Material 3 with technical/telecommunications aesthetics.

**Acceptance Criteria:**
- ✓ All screens use AppColors color palette
- ✓ Typography follows AppTextStyles
- ✓ Card elevation and border radius consistent
- ✓ Icon style consistent (Material Icons)

### BR-2: Theme Support

All screens must support Light, Dark, and System theme modes.

**Acceptance Criteria:**
- ✓ Theme switching works across all screens
- ✓ Colors adapt properly to theme changes
- ✓ Text remains readable in all themes
- ✓ Status colors maintain semantic meaning

### BR-3: Real-time Status Updates

Dashboard and monitoring screens must display real-time gateway status.

**Acceptance Criteria:**
- ✓ Gateway status updates in real-time
- ✓ Service status cards reflect current state
- ✓ Statistics update after operations
- ✓ Pull-to-refresh for manual refresh

### BR-4: Comprehensive Logging

Logs screen must provide comprehensive log viewing with filtering and search.

**Acceptance Criteria:**
- ✓ Real-time log streaming
- ✓ Search functionality
- ✓ Level filtering (Debug, Info, Warning, Error, Success)
- ✓ Log details with copy functionality
- ✓ Clear all logs with confirmation

### BR-5: SMS Management

SMS screen must provide message composition, sending, and viewing.

**Acceptance Criteria:**
- ✓ Compose new SMS with recipient and message
- ✓ Character counter (N/160)
- ✓ SMPP toggle for routing
- ✓ Message list with status indicators
- ✓ Message details with copy/reply/delete

### BR-6: Settings Management

Settings screen must provide configuration viewing and modification.

**Acceptance Criteria:**
- ✓ Theme selection (Light/Dark/System)
- ✓ SIP configuration display
- ✓ SMPP configuration display
- ✓ Gateway settings display
- ✓ Actions with confirm dialogs

### BR-7: Call Management

Call screen must provide full call control with animations.

**Acceptance Criteria:**
- ✓ Call state display with animations
- ✓ Call actions (mute, speaker, hold, DTMF, transfer)
- ✓ Multi-call handling
- ✓ Incoming call modal
- ✓ Call parallel info strip

---

## Functional Requirements

### FR-1: Dashboard Screen

**Purpose**: Main gateway control center with status overview and quick actions

**Inputs:**
- GatewayService.statusStream
- TelephonyService device info
- User interactions (FAB, quick actions)

**Process:**
1. Display gateway status overview card with gradient
2. Display service status cards (SIP, SMS, Calls)
3. Display device information
4. Display quick actions
5. Display statistics with funny messages
6. Handle Start/Stop via FAB

**Outputs:**
- Real-time status updates
- Navigation to quick actions
- Gateway start/stop

**Acceptance Criteria:**
- ✓ Status card shows gradient (green for running, grey for stopped)
- ✓ Service cards show connected/disconnected states
- ✓ Device info shows phone number, network, signal
- ✓ Quick actions navigate correctly
- ✓ Statistics update after calls/messages
- ✓ FAB toggles gateway state

---

### FR-2: Logs Screen

**Purpose**: View and filter system logs in real-time

**Inputs:**
- GatewayService.logStream
- SipService.logStream
- SmsService.logStream
- TelephonyService.logStream
- User search/filter interactions

**Process:**
1. Stream logs from all services
2. Display logs with level badges and source badges
3. Filter by level and search query
4. Show log details on tap
5. Support copy and clear operations

**Outputs:**
- Filtered log list
- Log details dialog
- Cleared logs

**Acceptance Criteria:**
- ✓ Search bar filters logs in real-time
- ✓ Level filter chip shows active filter
- ✓ Log cards have colored left border by level
- ✓ Stats bar shows "X of Y logs"
- ✓ Scroll FABs for navigation
- ✓ Details dialog with selectable text and copy

---

### FR-3: Settings Screen

**Purpose**: View and modify gateway configuration

**Inputs:**
- GatewayConfig from GatewayService
- ThemeService for theme selection
- User actions (reconfigure, restart, clear)

**Process:**
1. Display theme selector
2. Display SIP configuration
3. Display SMPP configuration
4. Display gateway settings
5. Handle actions with confirm dialogs

**Outputs:**
- Theme changes
- Configuration updates
- Service restarts
- Cleared logs

**Acceptance Criteria:**
- ✓ Theme section with 3 visual options
- ✓ SIP config shows username, domain, port, secure
- ✓ SMPP config shows host, port, system ID
- ✓ Gateway settings show routing flags
- ✓ Actions have confirm dialogs
- ✓ Reconfigure navigates to Setup

---

### FR-4: SMS Screen

**Purpose**: Compose, send, and view SMS messages

**Inputs:**
- SmsService.messageStream
- User composition (recipient, message)
- SMPP toggle state

**Process:**
1. Display compose section with character counter
2. Display statistics
3. Display message list
4. Handle send via SMS or SMPP
5. Show message details on tap

**Outputs:**
- Sent messages
- Updated statistics
- Message actions (copy, reply, delete)

**Acceptance Criteria:**
- ✓ Character counter updates (N/160)
- ✓ Counter changes color at 140 chars
- ✓ SMPP toggle switches routing
- ✓ Statistics show total/sent/delivered/failed
- ✓ Message cards show direction, status, preview
- ✓ Popup menu with copy/reply/delete
- ✓ Details dialog with full message

---

### FR-5: Call Screen

**Purpose**: Manage active calls with full control

**Inputs:**
- SipService.callStateStream
- TelephonyService.callStateStream
- GatewayService.routingStream
- User actions (answer, hangup, actions)

**Process:**
1. Display call info (name/number)
2. Display avatar with animations
3. Display call state
4. Display actions ViewPager (2 pages)
5. Display call controls
6. Handle multi-call scenarios

**Outputs:**
- Call state changes
- Action executions (mute, speaker, hold, DTMF, transfer)
- Multi-call handling

**Acceptance Criteria:**
- ✓ Gradient background (teal → blue)
- ✓ Avatar opacity animation on state change
- ✓ Actions ViewPager with page indicators
- ✓ Call controls (Answer/Hangup/Redirect)
- ✓ Toggle actions (mute, speaker, hold)
- ✓ DTMF/Transfer/Add Call dialogs
- ✓ IncomingCallModal for second call
- ✓ CallParallelInfo strip for active calls

---

### FR-6: Setup Screen

**Purpose**: Initial gateway configuration wizard

**Inputs:**
- User configuration input
- Form validation
- Page navigation

**Process:**
1. Display 3-page wizard
2. Page 1: SIP configuration
3. Page 2: SMPP configuration (optional)
4. Page 3: Gateway settings
5. Validate and save configuration

**Outputs:**
- Saved GatewayConfig
- Navigation to Dashboard

**Acceptance Criteria:**
- ✓ Progress indicator shows current page
- ✓ Back/Next navigation works
- ✓ Form validation on each page
- ✓ SMPP can be skipped
- ✓ Finish saves config and navigates

---

### FR-7: Auth Screen

**Purpose**: User authentication and credential management

**Inputs:**
- User credentials (username, password, server)
- Remember me toggle
- Saved credentials

**Process:**
1. Display credential form
2. Load saved credentials if available
3. Handle auto-login
4. Save credentials on success

**Outputs:**
- Authentication success/failure
- Saved credentials

**Acceptance Criteria:**
- ✓ Form validation
- ✓ Remember me toggle
- ✓ Auto-login if enabled
- ✓ First run detection
- ✓ Error handling

---

## Non-Functional Requirements

### NFR-1: Performance

- Screen transitions: < 300ms
- Real-time updates: < 100ms latency
- List scrolling: 60 FPS

### NFR-2: Accessibility

- Text scaling: Support up to 200%
- Color contrast: WCAG AA minimum
- Screen reader: All elements announced

### NFR-3: Responsiveness

- Screen sizes: 360px - 800px width
- Orientation: Portrait primary, landscape supported
- Layout: Adaptive for tablets

### NFR-4: Maintainability

- Code organization: One screen per file
- State management: Provider pattern
- Theme integration: ThemeService

---

## Constraints

### C-1: Existing Services

All screens must integrate with existing services:
- GatewayService
- SipService
- SmsService
- TelephonyService
- ThemeService

### C-2: Material 3

All screens must follow Material 3 design guidelines.

### C-3: Existing Visual Specs

All screens must adhere to VDD visual specifications in `flows/vdd-screens/*/visual-design.md`.

---

## Open Questions

1. **Call Park/Merge**: Actions exist but not implemented - intentional?
2. **Call Recording**: Placeholder action - planned feature?
3. **Chat Integration**: What chat functionality expected?
4. **Landscape Mode**: Should landscape layout be optimized?

---

**Status**: APPROVED  
**Created**: 2026-03-03  
**Updated**: 2026-03-07  
**Source**: Legacy analysis (/legacy command) + Implementation review
