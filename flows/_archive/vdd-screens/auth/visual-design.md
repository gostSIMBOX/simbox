# VDD: Auth Screen

## Screen Overview

**Purpose**: Initial authentication and SIP credentials configuration  
**Type**: Entry point / Authentication  
**Users**: System administrators, operators  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│                                         │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  │         📡 Router Icon          │   │
│  │         (80px, Blue 400)        │   │
│  │                                 │   │
│  │    GOSTsimbox Gateway           │   │
│  │    (28px, Bold, White)          │   │
│  │                                 │   │
│  │  Configure your SIP credentials │   │
│  │  (16px, Grey 400)               │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 👤 SIP Username                 │   │
│  │ [________________]              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 🔒 SIP Password                 │   │
│  │ [________________]              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 📡 SIP Server                   │   │
│  │ [________________]              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ ⚙️ SIP Port                     │   │
│  │ [________________]              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ☐ Remember credentials and auto-login │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │         CONNECT                 │   │
│  │     (or loading spinner)        │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Background | `#1A1A1A` | Main screen background |
| Card Background | `#2A2A2A` | Input field backgrounds |
| Primary Blue | `#60A5FA` (Blue 400) | Icon, button, focused borders |
| Text Primary | `#FFFFFF` (White) | Titles, input text |
| Text Secondary | `#9CA3AF` (Grey 400) | Labels, subtitles |
| Border Default | `#4B5563` (Grey 600) | Input borders |
| Border Focused | `#60A5FA` (Blue 400) | Active input border |
| Border Error | `#F87171` (Red 400) | Validation errors |
| Success | `#10B981` (Green) | Success states |
| Error | `#EF4444` (Red) | Error states |

### Typography

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| App Title | Poppins | 28px | Bold | White |
| Subtitle | Poppins | 16px | Regular | Grey 400 |
| Label | Poppins | 14px | Regular | Grey 400 |
| Input Text | Poppins | 16px | Regular | White |
| Button Text | Poppins | 16px | SemiBold (600) | White |
| Helper Text | Poppins | 12px | Regular | Grey 300 |

### Iconography

| Icon | Size | Color | Location |
|------|------|-------|----------|
| Router | 80px | Blue 400 | Header |
| Person | 24px | Grey 400 | Username prefix |
| Lock | 24px | Grey 400 | Password prefix |
| DNS | 24px | Grey 400 | Server prefix |
| Settings Ethernet | 24px | Grey 400 | Port prefix |
| Loading Spinner | 20x20px | White | Button (loading) |

---

## Component Specifications

### Input Fields

**Border Radius**: 12px  
**Padding**: 16px horizontal, 16px vertical  
**Height**: 56px (standard)  
**Background**: `#2A2A2A`  
**Border Width**: 1px

**States:**

```dart
// Default
border: BorderSide(color: Colors.grey[600])
fillColor: #2A2A2A
labelColor: Colors.grey[400]
iconColor: Colors.grey[400]

// Focused
border: BorderSide(color: Colors.blue[400], width: 2)
fillColor: #2A2A2A
labelColor: Colors.blue[400]
iconColor: Colors.blue[400]

// Error
border: BorderSide(color: Colors.red[400])
fillColor: #2A2A2A
labelColor: Colors.grey[400]
errorColor: Colors.red[400]

// Disabled
border: BorderSide(color: Colors.grey[700])
fillColor: #1F1F1F
labelColor: Colors.grey[600]
```

### Primary Button

**Height**: 56px  
**Border Radius**: 12px  
**Background**: Blue 400  
**Text**: White, 16px, SemiBold  
**Padding**: 16px vertical

**States:**

```dart
// Enabled
backgroundColor: Colors.blue[400]
foregroundColor: Colors.white
elevation: 2

// Disabled (loading)
backgroundColor: Colors.blue[400].withOpacity(0.5)
foregroundColor: Colors.white
showLoadingIndicator: true

// Pressed
backgroundColor: Colors.blue[500]
elevation: 4
```

### Checkbox

**Size**: 24x24px  
**Active Color**: Blue 400  
**Label**: "Remember credentials and auto-login"  
**Label Color**: Grey 300, 14px

---

## Interaction Specifications

### Form Validation

| Field | Validation Rule | Error Message |
|-------|-----------------|---------------|
| Username | Required | "Please enter SIP username" |
| Password | Required | "Please enter SIP password" |
| Server | Required | "Please enter SIP server" |
| Port | Required, 1-65535 | "Please enter a valid port number" |

### Loading State

**Trigger**: User taps "Connect" button  
**Behavior**:
1. Validate all fields
2. Show loading spinner in button
3. Disable button interaction
4. Save credentials to storage
5. Navigate to dashboard on success

**Duration**: 1-3 seconds (typical)

### Auto-Login Flow

```
App Launch
    │
    ├─► Check if first run
    │   │
    │   ├─ First run → Show Auth Screen
    │   └─ Not first run → Check auto-login
    │       │
    │       ├─ Auto-login enabled → Load credentials → Authenticate
    │       └─ Auto-login disabled → Show Auth Screen
    │
    └─► Navigate to Dashboard
```

### Error Handling

**Authentication Failure:**
- Show SnackBar at bottom
- Background: Red
- Message: "Authentication failed: [error]"
- Duration: 4 seconds
- Action: "Dismiss"

---

## User Flow

### First-Time Setup

```
1. User launches app
2. Auth screen displayed
3. User enters SIP credentials:
   - Username
   - Password
   - Server
   - Port
4. User checks "Remember credentials"
5. User taps "Connect"
6. Credentials validated
7. Credentials saved to storage
8. First run flag set to complete
9. Navigate to Dashboard
```

### Returning User (Auto-Login Enabled)

```
1. User launches app
2. Auto-login check
3. Credentials loaded from storage
4. Automatic authentication
5. Navigate to Dashboard
```

### Returning User (Auto-Login Disabled)

```
1. User launches app
2. Auth screen displayed
3. Fields pre-filled from saved credentials
4. User can modify or tap "Connect"
5. Authenticate and navigate to Dashboard
```

---

## Accessibility

### Text Scaling

- Support system font size up to 200%
- Input field heights adjust with text size
- Button text wraps if needed

### Screen Reader Support

- All input fields have labels
- Icons have semantic labels
- Error messages announced
- Loading state announced

### Keyboard Navigation

- Tab order: Username → Password → Server → Port → Checkbox → Button
- Enter key moves to next field
- Last field Enter triggers authentication

### Color Contrast

- Text on background: 7:1 (AAA)
- Input text on input bg: 4.5:1 (AA)
- Button text on button bg: 4.5:1 (AA)

---

## Responsive Design

### Layout Constraints

| Screen Width | Padding | Max Width |
|--------------|---------|-----------|
| < 360px | 16px | 100% |
| 360-600px | 24px | 100% |
| > 600px | 24px | 480px (centered) |

### Orientation

- **Portrait**: Default layout
- **Landscape**: Center content vertically, maintain max width

---

## Animation Specifications

### Screen Transition

**Enter**: Fade in + slight slide up (20px)  
**Duration**: 300ms  
**Curve**: easeOut

### Input Focus

**Border Color**: Crossfade 200ms  
**Elevation**: 0 → 2, 200ms

### Button Loading

**Spinner**: Rotate animation, infinite  
**Duration**: 1s per rotation

---

## Testing Checklist

### Visual Tests

- [ ] All input fields render with correct colors
- [ ] Border radius is consistent (12px)
- [ ] Typography matches specifications
- [ ] Icons are properly aligned
- [ ] Loading spinner centered in button

### Interaction Tests

- [ ] Form validation works for all fields
- [ ] Error messages display correctly
- [ ] Checkbox toggles state
- [ ] Button disabled during loading
- [ ] Auto-login works when enabled
- [ ] Credentials saved and loaded correctly

### Accessibility Tests

- [ ] Screen reader announces all elements
- [ ] Keyboard navigation works
- [ ] Text scaling doesn't break layout
- [ ] Color contrast meets WCAG AA

---

## Related Screens

| Screen | Relationship |
|--------|--------------|
| Dashboard | Navigate after successful auth |
| Settings | View/edit saved configuration |
| Setup | Reconfigure gateway |

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - Detailed VDD  
**Status**: DRAFT - Pending review
