# VDD: Setup Screen (Onboarding)

## Screen Overview

**Purpose**: Initial gateway configuration wizard  
**Type**: Onboarding / Wizard  
**Users**: First-time users, administrators  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  Setup Gateway ⚙️                       │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ████░░░░░░░░░░░░░░░░░░░░  Page 1/3   │  ← Progress
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  SIP Configuration                ║ │
│  ║                                   ║ │
│  ║  👤 Username                      ║ │
│  ║  [________________]               ║ │
│  ║                                   ║ │
│  ║  🔒 Password                      ║ │
│  ║  [________________]               ║ │  ← Page 1
│  ║                                   ║ │
│  ║  🌐 Domain/Server                 ║ │
│  ║  [________________]               ║ │
│  ║                                   ║ │
│  ║  ⚙️ Port       🔐 Secure         ║ │
│  ║  [____]         [☐]              ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│         [Back]          [Next]          │  ← Navigation
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Primary | `#1E88E5` | Progress, buttons |
| Background | `#FAFAFA` | Screen bg |
| Card | `#FFFFFF` | Card bg |
| Success | `#10B981` | Success states |
| Error | `#EF4444` | Validation errors |

### Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Page Title | 24px | Bold | Grey 900 |
| Page Subtitle | 14px | Regular | Grey 600 |
| Input Label | 14px | 500 | Grey 700 |
| Button | 16px | 600 | White |

---

## Component Specifications

### Progress Bar

**Height**: 4px  
**Border Radius**: 2px  
**Active**: Primary color  
**Inactive**: Grey 300

### Input Fields

**Height**: 56px  
**Border Radius**: 8px  
**Border**: Grey 300 (default), Blue (focused), Red (error)

### Navigation Buttons

**Back Button**: Text button  
**Next Button**: Elevated button  
**Loading**: Spinner in button

---

## Interaction Specifications

### Page Flow

| Page | Content | Validation |
|------|---------|------------|
| 1 | SIP Config | Required fields |
| 2 | SMPP Config | Optional (toggle) |
| 3 | Gateway Settings | Routing options |

### Validation

**Real-time**: Field-level validation  
**On Next**: Full form validation

### Success Dialog

**Title**: "Успех!" with checkmark icon  
**Content**: Success message + motivational quote  
**Button**: "Поехали! 🎉" → Navigate to Dashboard

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
