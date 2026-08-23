# VDD: Language Selection Screen

## Screen Overview

**Purpose**: Select application language  
**Type**: Settings / Configuration  
**Users**: All users  
**Status**: DRAFT

---

## Visual Design Specifications

### Layout Structure

```
┌─────────────────────────────────────────┐
│  Language                               │  ← AppBar
├─────────────────────────────────────────┤
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  🇬🇧 English              ✓      ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  🇷🇺 Русский                       ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  🇪🇸 Español                       ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
│  ╔═══════════════════════════════════╗ │
│  ║  🇨🇳 中文                          ║ │
│  ╚═══════════════════════════════════╝ │
│                                         │
└─────────────────────────────────────────┘
```

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Selected | `#1E88E5` | Checkmark |
| Background | `#FAFAFA` | Screen bg |
| Card | `#FFFFFF` | Card bg |
| Text | `#1F2937` | Main text |

---

## Component Specifications

### Language Items

**Height**: 56px  
**Leading**: Flag emoji (24px)  
**Title**: Language name (16px)  
**Trailing**: Checkmark (if selected)

---

## Interaction Specifications

### Selection

**Action**: Tap to select → Save → Restart app (if needed)

---

**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command) - VDD Screens  
**Status**: DRAFT
