# Requirements: UI Theming

## Overview

The Theme Service provides comprehensive theme management with Material 3 support, enabling users to switch between Light, Dark, and System themes with persistent storage.

## Functional Requirements

### FR-1: Theme Mode Support

The system SHALL support three theme modes:

| Mode | Description | Default |
|------|-------------|---------|
| Light | Light theme for daytime use | No |
| Dark | Dark theme for technical monitoring | Yes |
| System | Auto-switch based on system settings | No |

### FR-2: Theme Operations

The system SHALL provide theme operations:

| Operation | Method | Description |
|-----------|--------|-------------|
| Set light | `setLightTheme()` | Switch to light theme |
| Set dark | `setDarkTheme()` | Switch to dark theme |
| Set system | `setSystemTheme()` | Switch to system theme |
| Toggle | `toggleTheme()` | Cycle through themes |
| Get info | `getThemeName()` | Get current theme name |

### FR-3: Theme Persistence

The system SHALL persist theme selection:

- Storage: SharedPreferences
- Key: `gost_simbox_theme`
- Format: ThemeMode index (int)
- Auto-save on theme change

### FR-4: Theme Information

The system SHALL provide theme information:

| Method | Returns | Description |
|--------|---------|-------------|
| `getThemeName()` | String | "Light", "Dark", or "System" |
| `getThemeDescription()` | String | User-friendly description |
| `getThemeIcon()` | IconData | Appropriate icon |
| `getAvailableThemes()` | List<ThemeOption> | All theme options |
| `getThemeDescription()` | String | Description of current theme |

### FR-5: Status Colors

The system SHALL provide status colors for technical monitoring:

| Status Type | States | Colors |
|-------------|--------|--------|
| Connection | connected/online | Green (#10B981) |
| Connection | connecting | Yellow (#F59E0B) |
| Connection | disconnected/offline | Red (#EF4444) |
| Signal | 80-100% | Green |
| Signal | 60-80% | Light green |
| Signal | 40-60% | Yellow |
| Signal | 20-40% | Orange |
| Signal | 0-20% | Red |
| Call | active/incoming/outgoing | Green |
| Call | ended/missed | Red |
| Call | idle/waiting | Yellow |

### FR-6: ChangeNotifier Integration

The system SHALL integrate with Flutter state management:

- Extend ChangeNotifier
- Notify listeners on theme change
- Support reactive UI updates

## Non-Functional Requirements

### NFR-1: User Experience

- SHALL default to Dark theme (technical monitoring preference)
- SHALL provide smooth theme transitions
- SHALL support intuitive theme cycling

### NFR-2: System Integration

- SHALL detect system theme changes
- SHALL respond to platform brightness changes
- SHALL handle system theme gracefully

### NFR-3: Performance

- SHALL load theme on initialization
- SHALL not block UI during theme changes
- SHALL cache theme settings

## Configuration

### ThemeOption Entity

```dart
class ThemeOption {
  final ThemeMode mode;
  final String name;
  final String description;
  final IconData icon;
}
```

### ThemeMode Values

```dart
enum ThemeMode {
  light,   // Index 0
  dark,    // Index 1
  system,  // Index 2 (default)
}
```

## User Experience Requirements

### Theme Toggle Behavior

```
toggleTheme() cycles: Light → Dark → System → Light
```

### Theme Descriptions

| Theme | Description |
|-------|-------------|
| Light | "Light theme for daytime use" |
| Dark | "Dark theme for technical monitoring" |
| System | "Automatic switching based on system settings" |

---

**Status**: DRAFT  
**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)
