# VDD: Settings Screen

## Screen Overview

**Purpose**: View and modify gateway configuration  
**Type**: Configuration  
**Users**: Administrators  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  Settings                               │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  SIP Configuration                ║ │
│  ║  Username: admin                  ║ │
│  ║  Domain: sip.example.com          ║ │  ← SIP Config
│  ║  Port: 5060                       ║ │
│  ║  Secure: Yes                      ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  SMPP Configuration               ║ │
│  ║  Host: smpp.example.com           ║ │
│  ║  Port: 2775                       ║ │  ← SMPP Config
│  ║  System ID: gateway               ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Gateway Settings                 ║ │
│  ║  Auto Answer: Yes                 ║ │
│  ║  Logging: Enabled                 ║ │  ← Settings
│  ║  Route SIP→GSM: Yes               ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  Actions                          ║ │
│  ║  ✏️ Reconfigure Gateway          ║ │
│  ║  🔄 Restart Services              ║ │  ← Actions
│  ║  🗑️ Clear Logs                    ║ │
│  ║  ℹ️ About                         ║ │
│  ╚═══════════════════════════════════╝ │
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Primary | `#1E88E5` | App bar |
| Background | `#FAFAFA` | Screen bg |
| Card | `#FFFFFF` | Card bg |
| Text Primary | `#1F2937` | Main text |
| Text Secondary | `#6B7280` | Labels |

---

## Component Specifications

### Config Cards

**Border Radius**: 12px  
**Padding**: 16px  
**Elevation**: 1

### Config Rows

**Layout**:
```
[Label (Bold)]          [Value (Grey)]
```

### Action List Items

**Height**: 72px  
**Leading Icon**: 24px  
**Title**: 16px Bold  
**Subtitle**: 14px Grey

---

## Interaction Specifications

### Actions

| Action | Behavior |
|--------|----------|
| Reconfigure | Navigate to Setup screen |
| Restart Services | Show confirm → Restart |
| Clear Logs | Show confirm → Clear |
| About | Show about dialog |

### Confirm Dialogs

**Title**: Action name  
**Content**: Confirmation message  
**Buttons**: Cancel / Continue

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
