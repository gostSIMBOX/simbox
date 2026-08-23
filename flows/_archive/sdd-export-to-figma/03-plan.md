# Plan: Export App Screenshots to Figma

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-03-11
> Specifications: [02-specifications.md](02-specifications.md)

## Overview

This plan breaks down the element-by-element Figma reconstruction into actionable tasks. The work is organized in phases: Design System → Components → Screens (by category) → Organization.

**Total Estimated Time:** 8-12 hours (manual work in Figma)
**Total Screens:** 37 across 8 categories
**Total Components:** 8 base components with variants

---

## Phase 1: Design System Setup

### Task 1.1: Create Color Styles
**File:** Figma File
**Estimate:** 30 minutes

**Steps:**
1. Open Figma file: https://www.figma.com/design/FUBZIOMUleEqSDgQiuibXD/Telon
2. Create "📱 GOSTsimbox Gateway" page if not exists
3. Create frame "Colors" for reference
4. Add Color Styles (Local):

| Style Name | Value |
|------------|-------|
| `GOSTsimbox/Background/Primary` | `#1A1A1A` |
| `GOSTsimbox/Background/Surface` | `#2A2A2A` |
| `GOSTsimbox/Primary/Main` | `#1E88E5` |
| `GOSTsimbox/Primary/Light` | `#42A5F5` |
| `GOSTsimbox/Primary/Dark` | `#1565C0` |
| `GOSTsimbox/Success/Main` | `#10B981` |
| `GOSTsimbox/Warning/Main` | `#F59E0B` |
| `GOSTsimbox/Error/Main` | `#EF4444` |
| `GOSTsimbox/Info/Main` | `#3B82F6` |
| `GOSTsimbox/Debug/Main` | `#9CA3AF` |
| `GOSTsimbox/Text/Primary` | `#FFFFFF` |
| `GOSTsimbox/Text/Secondary` | `#9CA3AF` |
| `GOSTsimbox/Text/Disabled` | `#6B7280` |
| `GOSTsimbox/Border/Default` | `#404040` |
| `GOSTsimbox/Border/Focused` | `#1E88E5` |
| `GOSTsimbox/Border/Error` | `#EF4444` |

**Output:** 16 Color Styles created

---

### Task 1.2: Create Text Styles
**File:** Figma File
**Estimate:** 30 minutes

**Steps:**
1. Create frame "Typography" for reference
2. Add Text Styles (Local) with font family "Poppins":

| Style Name | Size | Weight | Line Height | Color |
|------------|------|--------|-------------|-------|
| `GOSTsimbox/Display` | 28 | Bold | 36 | `#FFFFFF` |
| `GOSTsimbox/Headline/Large` | 24 | Bold | 32 | `#FFFFFF` |
| `GOSTsimbox/Headline/Medium` | 20 | SemiBold | 28 | `#FFFFFF` |
| `GOSTsimbox/Headline/Small` | 18 | SemiBold | 24 | `#FFFFFF` |
| `GOSTsimbox/Body/Large` | 16 | Regular | 24 | `#FFFFFF` |
| `GOSTsimbox/Body/Medium` | 14 | Regular | 20 | `#FFFFFF` |
| `GOSTsimbox/Body/Small` | 12 | Regular | 16 | `#FFFFFF` |
| `GOSTsimbox/Button/Large` | 16 | SemiBold | 24 | `#FFFFFF` |
| `GOSTsimbox/Button/Medium` | 14 | SemiBold | 20 | `#FFFFFF` |
| `GOSTsimbox/Label` | 12 | Medium | 16 | `#9CA3AF` |

**Output:** 10 Text Styles created

---

### Task 1.3: Create Effect Styles (Shadows)
**File:** Figma File
**Estimate:** 15 minutes

**Steps:**
1. Add Effect Styles:

| Style Name | Effect |
|------------|--------|
| `GOSTsimbox/Shadow/Small` | Drop shadow: Y=1, Blur=2, Spread=0, `#000000` 10% |
| `GOSTsimbox/Shadow/Medium` | Drop shadow: Y=2, Blur=4, Spread=0, `#000000` 15% |
| `GOSTsimbox/Shadow/Large` | Drop shadow: Y=4, Blur=8, Spread=0, `#000000` 20% |
| `GOSTsimbox/Shadow/XL` | Drop shadow: Y=8, Blur=16, Spread=0, `#000000` 25% |

**Output:** 4 Effect Styles created

---

## Phase 2: Component Library

### Task 2.1: Button Components
**File:** Figma File
**Estimate:** 45 minutes

**Steps:**
1. Create frame "Components/Buttons"
2. Build Primary Button component with variants:
   - Properties: `State` (Default, Hover, Disabled, Loading)
   - Default: fill=`#1E88E5`, text="Connect"
   - Hover: fill=`#42A5F5`
   - Disabled: fill=`#404040`, text=`#6B7280`
   - Loading: add CircularProgressIndicator
3. Build FAB (Floating Action Button) component:
   - Properties: `Type` (Regular, Extended), `Icon`, `State`
   - Circle: diameter=56, fill=`#1E88E5`
   - Icon: size=24, color=`#FFFFFF`
   - Extended: add text label, padding=16×16

**Output:** 2 component sets with variants

---

### Task 2.2: Input Component
**File:** Figma File
**Estimate:** 45 minutes

**Steps:**
1. Create frame "Components/Inputs"
2. Build TextField component with variants:
   - Properties: `State` (Default, Focused, Error, Disabled), `Has Icon`, `Has Label`
   - Frame: 358×56 (iPhone 13 width minus padding)
   - Background: fill=`#2A2A2A`
   - Border: radius=12, stroke=1
   - Default: stroke=`#404040`
   - Focused: stroke=`#1E88E5`
   - Error: stroke=`#EF4444`
   - Icon slot: 24×24, left padding=16
   - Label: style=Label, top margin=4
   - Text input: style=Body/Large, left padding=16
3. Create variants with/without prefix icon
4. Create password variant (obscure text)

**Output:** 1 component set with 12+ variants

---

### Task 2.3: Container Components
**File:** Figma File
**Estimate:** 30 minutes

**Steps:**
1. Create frame "Components/Containers"
2. Build Card component:
   - Frame: variable width, min 358
   - Background: fill=`#2A2A2A`
   - Border: radius=12
   - Effect: Shadow/Medium
   - Padding: 16 (auto layout)
3. Build Dialog component:
   - Frame: 327×auto
   - Background: fill=`#2A2A2A`
   - Border: radius=16
   - Effect: Shadow/XL
   - Padding: 24
   - Slots: Title, Content, Actions

**Output:** 2 container components

---

### Task 2.4: Status Components
**File:** Figma File
**Estimate:** 30 minutes

**Steps:**
1. Create frame "Components/Status"
2. Build Badge component:
   - Properties: `Level` (Success, Warning, Error, Info, Debug)
   - Frame: auto width×20
   - Background: fill=[color]20
   - Text: style=Label, color=[color]
   - Padding: 6×2
   - Border radius: 4
3. Build Status Card component:
   - Frame: 114×96
   - Background: fill=`#2A2A2A`
   - Icon: 28×28, color by state
   - Title: style=Label
   - Value: style=Headline/Small, color by state
   - Padding: 16

**Output:** 2 status components with variants

---

### Task 2.5: Layout Components
**File:** Figma File
**Estimate:** 30 minutes

**Steps:**
1. Create frame "Components/Layout"
2. Build InfoRow component:
   - Auto layout: horizontal
   - Label: style=Body/Medium, color=`#9CA3AF`
   - Spacer (flex)
   - Value: style=Body/Medium, color=`#FFFFFF`
   - Padding: 4 vertical
3. Build AppBar component:
   - Frame: 390×56
   - Background: fill=`#1A1A1A` or transparent
   - Title: style=Headline/Medium
   - Action icons slot (right)
4. Build SearchBar component:
   - Frame: 358×48
   - Background: fill=`#FFFFFF` (light) or `#2A2A2A` (dark)
   - Icon: search, left
   - Placeholder text
   - Border radius: 8

**Output:** 3 layout components

---

## Phase 3: Screen Reconstruction

### Task 3.1: Core Gateway Screens (5 screens)
**File:** Figma File
**Estimate:** 90 minutes

**Screens:**
1. **01 Auth Screen** (390×844)
   - Background: `#1A1A1A`
   - Logo icon: 80×80
   - Title + subtitle
   - 4 Input fields (Username, Password, Server, Port)
   - Checkbox row
   - Primary button: "Connect"

2. **02 Dashboard Screen** (390×844)
   - AppBar with settings icon
   - Status overview card (gradient banner)
   - 3 service status cards (row)
   - Device info card (4 info rows)
   - Quick actions card (4 circular buttons)
   - Statistics card (3 stat items + banner)
   - FAB: Start/Stop

3. **03 Settings Screen** (390×844)
   - AppBar: "Settings"
   - Theme card (3 theme options)
   - SIP config card (5 info rows)
   - SMPP config card
   - Gateway settings card (7 info rows)
   - Actions card (4 list tiles)

4. **04 Logs Screen** (390×844)
   - AppBar with 3 actions
   - Search bar
   - Stats bar with chip
   - Log list (repeatable log cards)

5. **05 Setup Screen** (390×844)
   - Similar to Auth screen
   - Additional welcome content

**Output:** 5 complete screen frames

---

### Task 3.2: Call Management Screens (3 screens)
**File:** Figma File
**Estimate:** 45 minutes

**Screens:**
1. **06 Call Screen** (390×844)
   - Contact avatar (120×120)
   - Phone number + timer
   - 4 call option buttons (2×2 grid)
   - End call button (large red FAB)

2. **07 Calls Screen** (390×844)
   - Call history list
   - Call log cards with icons

3. **08 Incoming Video Call Screen** (390×844)
   - Full screen video placeholder
   - Answer/decline buttons

**Output:** 3 complete screen frames

---

### Task 3.3: SMS & Messaging Screens (4 screens)
**File:** Figma File
**Estimate:** 60 minutes

**Screens:**
1. **09 SMS Screen** (390×844)
   - Message bubbles (incoming/outgoing)
   - Input row

2. **10 USSD Screen** (390×844)
   - Dialpad
   - Response display

3. **11 SMPP Logs Screen** (390×844)
   - Similar to Logs screen
   - SMPP-specific content

4. **12 SMPP Settings Screen** (390×844)
   - SMPP config form

**Output:** 4 complete screen frames

---

### Task 3.4: Voice Line Screens (6 screens)
**File:** Figma File
**Estimate:** 90 minutes

**Screens:**
1. **13 Voice Line Status Screen**
2. **14 Voice Line Settings Screen**
3. **15 Select Method Screen**
4. **16 Test Voice Line Screen**
5. **17 Enhanced Mode Screen**
6. **18 TTY Config Screen**

**Note:** Read actual Flutter files for exact structure:
- `lib/presentation/screens/voice_line/*.dart`

**Output:** 6 complete screen frames

---

### Task 3.5: Dongle Screens (8 screens)
**File:** Figma File
**Estimate:** 120 minutes

**Screens:**
1. **19 Dongle Status Screen**
2. **20 Dongle Monitor Screen**
3. **21 Detect Type Screen**
4. **22 Test Menu Screen**
5. **23 TRRS Config Screen**
6. **24 USB Accessory Config Screen**
7. **25 USB DAC Config Screen**
8. **26 Schematic Viewer Screen**

**Note:** Read actual Flutter files for exact structure:
- `lib/presentation/screens/dongle/*.dart`

**Output:** 8 complete screen frames

---

### Task 3.6: SIP & Network Screens (3 screens)
**File:** Figma File
**Estimate:** 45 minutes

**Screens:**
1. **27 Codecs Screen**
2. **28 Base Stations Screen**
3. **29 Info Screen**

**Output:** 3 complete screen frames

---

### Task 3.7: Configuration Screens (5 screens)
**File:** Figma File
**Estimate:** 75 minutes

**Screens:**
1. **30 Language Screen**
2. **31 Language Selection Screen**
3. **32 Theme Settings Screen**
4. **33 Theme Demo Screen**
5. **34 Analytics Screen**

**Output:** 5 complete screen frames

---

### Task 3.8: Other Screens (3 screens)
**File:** Figma File
**Estimate:** 45 minutes

**Screens:**
1. **35 Lines Screen**
2. **36 SIMs Screen**
3. **37 Dashboard Screen** (alternate state)

**Output:** 3 complete screen frames

---

## Phase 4: Organization & Polish

### Task 4.1: Create Sections & Organization
**File:** Figma File
**Estimate:** 30 minutes

**Steps:**
1. Create Sections for each category:
   - 🎨 Design System
   - 📱 Core Gateway (5 screens)
   - 📞 Call Management (3 screens)
   - 💬 SMS & Messaging (4 screens)
   - 🎤 Voice Line (6 screens)
   - 🔌 Dongle (8 screens)
   - 🌐 SIP & Network (3 screens)
   - ⚙️ Configuration (5 screens)
   - 📁 Other (3 screens)

2. Organize all frames into sections
3. Add cover frame with screen index

**Output:** Organized Figma file with sections

---

### Task 4.2: Add Prototyping (Optional)
**File:** Figma File
**Estimate:** 60 minutes

**Steps:**
1. Link screens based on navigation flow:
   - Auth → Dashboard
   - Dashboard → Settings
   - Dashboard → Logs
   - Dashboard → Call/SMS screens
2. Add interactive components (buttons with hover states)
3. Create prototype preview

**Output:** Clickable prototype (optional)

---

### Task 4.3: Final Review
**File:** Figma File
**Estimate:** 30 minutes

**Checklist:**
- [ ] All 37 screens created
- [ ] All 8 component sets created
- [ ] All 16 color styles created
- [ ] All 10 text styles created
- [ ] Layers named consistently
- [ ] Auto layout applied correctly
- [ ] Sections organized
- [ ] Cover/index frame added
- [ ] Share link generated

**Output:** Complete, polished Figma file

---

## Dependencies

| Task | Depends On |
|------|------------|
| 1.1 Color Styles | None |
| 1.2 Text Styles | None |
| 1.3 Effect Styles | None |
| 2.1 Button Components | 1.1, 1.2 |
| 2.2 Input Component | 1.1, 1.2 |
| 2.3 Container Components | 1.1, 1.2, 1.3 |
| 2.4 Status Components | 1.1, 1.2 |
| 2.5 Layout Components | 1.1, 1.2, 2.1, 2.2 |
| 3.1 Core Gateway Screens | All Phase 2 |
| 3.2-3.8 Other Screens | All Phase 2 |
| 4.1 Organization | All Phase 3 |
| 4.2 Prototyping | 4.1 |
| 4.3 Review | All tasks |

---

## Rollback Considerations

- Figma has version history - can revert to any previous state
- Duplicate the page before starting major work
- Export component specs as backup

---

## Testing Strategy

### Manual Verification

- [ ] Open Figma file and verify all screens present
- [ ] Check color styles match specification
- [ ] Check text styles match specification
- [ ] Verify component variants work correctly
- [ ] Test auto layout on screen resize
- [ ] Verify all layers are properly named
- [ ] Check section organization

---

## Open Plan Questions

- [ ] Should we create separate pages for light/dark themes?
- [ ] Should we add Android-specific frames (different dimensions)?
- [ ] Priority: which screens are most important if time is limited?

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]
