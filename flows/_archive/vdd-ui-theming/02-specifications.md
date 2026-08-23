# Specifications: UI Theming

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     ThemeService                             │
│                    (ChangeNotifier)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Theme Mode Management                   │   │
│  │  ThemeMode: Light | Dark | System                     │   │
│  │  Persistent storage via SharedPreferences             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Theme Information                       │   │
│  │  getThemeName()  getThemeDescription()               │   │
│  │  getThemeIcon()  getAvailableThemes()                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Status Color Palette                     │   │
│  │  Connection colors  Signal colors  Call colors        │   │
│  │  Technical monitoring color scheme                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. ThemeService (ChangeNotifier)

```dart
class ThemeService extends ChangeNotifier {
  static const String _themeKey = 'gost_simbox_theme';
  
  ThemeMode _themeMode = ThemeMode.dark;  // Default for technical app
  
  // Getters
  ThemeMode get themeMode;
  bool get isDarkMode;
  bool get isLightMode;
}
```

### 2. ThemeOption

```dart
class ThemeOption {
  final ThemeMode mode;
  final String name;
  final String description;
  final IconData icon;
  
  const ThemeOption({
    required this.mode,
    required this.name,
    required this.description,
    required this.icon,
  });
}
```

### 3. Available Themes

```dart
List<ThemeOption> getAvailableThemes() => [
  ThemeOption(
    mode: ThemeMode.light,
    name: 'Light',
    description: 'Light theme for daytime use',
    icon: Icons.wb_sunny,
  ),
  ThemeOption(
    mode: ThemeMode.dark,
    name: 'Dark',
    description: 'Dark theme for technical monitoring',
    icon: Icons.nightlight_round,
  ),
  ThemeOption(
    mode: ThemeMode.system,
    name: 'System',
    description: 'Automatic switching based on system settings',
    icon: Icons.settings_system_daydream,
  ),
];
```

## API Specifications

### Initialize

```dart
Future<void> initialize() async {
  await _loadThemeMode();
}

Future<void> _loadThemeMode() async {
  try {
    final prefs = await SharedPreferences.getInstance();
    final themeIndex = prefs.getInt(_themeKey) ?? 2;  // Default: dark (index 2)
    _themeMode = ThemeMode.values[themeIndex];
    notifyListeners();
  } catch (e) {
    _themeMode = ThemeMode.dark;
  }
}
```

### Set Theme

```dart
Future<void> setLightTheme() async {
  if (_themeMode != ThemeMode.light) {
    _themeMode = ThemeMode.light;
    await _saveThemeMode();
    notifyListeners();
  }
}

Future<void> setDarkTheme() async {
  if (_themeMode != ThemeMode.dark) {
    _themeMode = ThemeMode.dark;
    await _saveThemeMode();
    notifyListeners();
  }
}

Future<void> setSystemTheme() async {
  if (_themeMode != ThemeMode.system) {
    _themeMode = ThemeMode.system;
    await _saveThemeMode();
    notifyListeners();
  }
}
```

### Toggle Theme

```dart
Future<void> toggleTheme() async {
  if (_themeMode == ThemeMode.light) {
    await setDarkTheme();
  } else if (_themeMode == ThemeMode.dark) {
    await setSystemTheme();
  } else {
    await setLightTheme();
  }
}
```

### Save Theme

```dart
Future<void> _saveThemeMode() async {
  try {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_themeKey, _themeMode.index);
  } catch (e) {
    // Ignore save errors
  }
}
```

## Status Color Specifications

### Connection Status Colors

```dart
Color getConnectionStatusColor(String status) {
  switch (status.toLowerCase()) {
    case 'connected':
    case 'online':
      return const Color(0xFF10B981);  // Green
    case 'connecting':
    case 'connecting...':
      return const Color(0xFFF59E0B);  // Yellow
    case 'disconnected':
    case 'offline':
      return const Color(0xFFEF4444);  // Red
    default:
      return const Color(0xFF6B7280);  // Gray
  }
}
```

### Signal Level Colors

```dart
Color getSignalLevelColor(int level) {
  if (level >= 80) {
    return const Color(0xFF10B981);  // Excellent
  } else if (level >= 60) {
    return const Color(0xFF34D399);  // Good
  } else if (level >= 40) {
    return const Color(0xFFF59E0B);  // Fair
  } else if (level >= 20) {
    return const Color(0xFFF97316);  // Poor
  } else {
    return const Color(0xFFEF4444);  // Critical
  }
}
```

### Call Status Colors

```dart
Color getCallStatusColor(String status) {
  switch (status.toLowerCase()) {
    case 'active':
    case 'incoming':
    case 'outgoing':
      return const Color(0xFF10B981);  // Green
    case 'ended':
    case 'missed':
      return const Color(0xFFEF4444);  // Red
    case 'idle':
    case 'waiting':
      return const Color(0xFFF59E0B);  // Yellow
    default:
      return const Color(0xFF6B7280);  // Gray
  }
}
```

## Theme Information

### Theme Names

```dart
String getThemeName() {
  switch (_themeMode) {
    case ThemeMode.light: return 'Light';
    case ThemeMode.dark: return 'Dark';
    case ThemeMode.system: return 'System';
  }
}
```

### Theme Descriptions

```dart
String getThemeDescription() {
  switch (_themeMode) {
    case ThemeMode.light:
      return 'Light theme for daytime use';
    case ThemeMode.dark:
      return 'Dark theme for technical monitoring';
    case ThemeMode.system:
      return 'Automatic switching based on system settings';
  }
}
```

### Theme Icons

```dart
IconData getThemeIcon() {
  switch (_themeMode) {
    case ThemeMode.light: return Icons.wb_sunny;
    case ThemeMode.dark: return Icons.nightlight_round;
    case ThemeMode.system: return Icons.settings_system_daydream;
  }
}
```

## System Integration

### System Theme Detection

```dart
bool get isDarkMode {
  if (_themeMode == ThemeMode.system) {
    return WidgetsBinding.instance.platformDispatcher.platformBrightness == Brightness.dark;
  }
  return _themeMode == ThemeMode.dark;
}

bool get isLightMode {
  if (_themeMode == ThemeMode.system) {
    return WidgetsBinding.instance.platformDispatcher.platformBrightness == Brightness.light;
  }
  return _themeMode == ThemeMode.light;
}
```

## Testing Strategy

### Widget Tests

```dart
testWidgets('ThemeService toggles through all themes', (tester) async {
  final service = ThemeService();
  await service.initialize();
  
  expect(service.getThemeName(), 'Dark');  // Default
  
  await service.toggleTheme();
  expect(service.getThemeName(), 'System');
  
  await service.toggleTheme();
  expect(service.getThemeName(), 'Light');
  
  await service.toggleTheme();
  expect(service.getThemeName(), 'Dark');  // Back to start
});

testWidgets('ThemeService persists theme selection', (tester) async {
  final service = ThemeService();
  await service.initialize();
  
  await service.setLightTheme();
  expect(service.getThemeName(), 'Light');
  
  // Reload and verify
  final service2 = ThemeService();
  await service2.initialize();
  expect(service2.getThemeName(), 'Light');
});
```

## Dependencies

### External Dependencies

| Package | Purpose |
|---------|---------|
| shared_preferences | Theme persistence |
| flutter/material | ThemeMode, Icons |

---

**Status**: DRAFT  
**Created**: 2026-03-03  
**Source**: Legacy analysis (/legacy command)  
**Related**: 01-requirements.md
