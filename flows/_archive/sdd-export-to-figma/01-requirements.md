# Requirements: Export App Screenshots to Figma

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-03-11

## Problem Statement

The GOSTsimbox Android Gateway Flutter app has multiple screens that need to be exported to Figma for design review, documentation, and collaboration purposes. Currently, screenshots are not organized in a design tool, making it difficult to share and review the UI/UX.

## User Stories

### Primary

**As a** developer/designer
**I want** to export all app screenshots to Figma organized by screen type
**So that** I can easily share, review, and collaborate on the UI design with the team

## Acceptance Criteria

### Must Have

1. **Given** the Flutter app has multiple screens
   **When** the export is complete
   **Then** all user-facing screens should be captured as screenshots and uploaded to Figma

2. **Given** the screenshots are uploaded
   **When** viewing the Figma file
   **Then** screens should be organized by type (Auth, Dashboard, Settings, Logs, etc.)

3. **Given** the Figma file URL
   **When** accessing it
   **Then** all screenshots should be visible and properly labeled

### Should Have

- Screenshots should be high quality and clearly show UI elements
- Each screen type should be visually separated in Figma
- Screen names/labels should be included

### Won't Have (This Iteration)

- Interactive prototypes or clickable flows
- Design annotations or comments
- Multiple device frame variations

## Constraints

- **Technical**: Must work with existing Flutter app
- **Platform**: Android screenshots (as per app target)
- **Dependencies**: Requires Figma access and authentication
- **Figma Target**: https://www.figma.com/design/FUBZIOMUleEqSDgQiuibXD/Telon?node-id=0-1&p=f&t=Auw4L4cQ0IG0wHND-0

## Open Questions

- [x] What screenshot capture method to use? → **Code analysis + manual Figma reconstruction**
- [x] Are there any specific screen states that need to be captured? → **Default states for each screen**
- [x] Should we include both light and dark theme variants? → **Dark theme only**
- [x] How to upload to Figma? → **Element-by-element reconstruction** (not screenshots)

## Screen Inventory

Based on codebase analysis, the app contains the following screens organized by type:

### Core Gateway Screens
- Auth Screen (`auth_screen.dart`) - SIP credentials login
- Dashboard Screen (`dashboard_screen.dart`) - Main gateway status and controls
- Settings Screen (`settings_screen.dart`) - General settings
- Setup Screen (`setup_screen.dart`) - Initial setup flow
- Logs Screen (`logs_screen.dart`) - Log viewer with search/filter

### Call Management Screens
- Call Screen (`call_screen.dart`) - Active call interface
- Calls Screen (`calls_screen.dart`) - Call history/list
- Incoming Video Call Screen (`incoming_video_call_screen.dart`)

### SIP & Network Screens
- Codecs Screen (`codecs_screen.dart`) - Audio codec configuration
- Base Stations Screen (`base_stations_screen.dart`) - Network information
- Info Screen (`info_screen.dart`) - App/system info

### SMS & Messaging Screens
- SMS Screen (`sms_screen.dart`) - SMS messaging interface
- USSD Screen (`ussd_screen.dart`) - USSD codes
- SMPP Logs Screen (`smpp_logs_screen.dart`) - SMPP protocol logs
- SMPP Settings Screen (`smpp_settings_screen.dart`) - SMPP configuration

### Configuration Screens
- Language Screen (`language_screen.dart`) - Language selection
- Language Selection Screen (`language_selection_screen.dart`)
- Theme Settings Screen (`theme_settings_screen.dart`)
- Theme Demo Screen (`theme_demo_screen.dart`)
- Analytics Screen (`analytics_screen.dart`)

### Voice Line Screens
- Voice Line Status Screen (`voice_line_status_screen.dart`)
- Voice Line Settings Screen (`voice_line_settings_screen.dart`)
- Select Method Screen (`voice_line/select_method_screen.dart`)
- Test Voice Line Screen (`voice_line/test_voice_line_screen.dart`)
- Enhanced Mode Screen (`voice_line/enhanced_mode_screen.dart`)
- TTY Config Screen (`voice_line/tty_config_screen.dart`)

### Dongle Screens
- Dongle Status Screen (`dongle/dongle_status_screen.dart`)
- Dongle Monitor Screen (`dongle/dongle_monitor_screen.dart`)
- Detect Type Screen (`dongle/detect_type_screen.dart`)
- Test Menu Screen (`dongle/test_menu_screen.dart`)
- TRRS Config Screen (`dongle/trrs_config_screen.dart`)
- USB Accessory Config Screen (`dongle/usb_accessory_config_screen.dart`)
- USB DAC Config Screen (`dongle/usb_dac_config_screen.dart`)
- Schematic Viewer Screen (`dongle/schematic_viewer_screen.dart`)

### Other Screens
- Lines Screen (`lines_screen.dart`)
- SIMs Screen (`sims_screen.dart`)

## References

- Figma File: https://www.figma.com/design/FUBZIOMUleEqSDgQiuibXD/Telon
- App: GOSTsimbox Android Gateway (Flutter)

---

## Approval

- [x] Reviewed by: User
- [x] Approved on: 2026-03-11
- [x] Notes: Requirements approved - proceeding to specifications
