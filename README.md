# Telon

A native Android application for audio recording and calling functionality, built with Kotlin and Android SDK.

## Features

- **Audio Recording**: High-quality audio recording with configurable format
- **Real-time Status**: Live recording status updates
- **Permission Management**: Proper handling of audio recording permissions
- **Modern UI**: Clean Material Design interface

## Requirements

- Android SDK 29+ (API level 29)
- Kotlin 1.8+
- Android Studio Arctic Fox or later
- Java 11

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Telon
```

2. Open the project in Android Studio

3. Sync Gradle files and build the project

4. Run the application on an Android device or emulator

## Usage

### Audio Recording

1. Launch the application
2. Grant microphone permissions when prompted
3. Use the "Start Recording" button to begin audio capture
4. Use the "Stop Recording" button to end recording
5. Monitor the recording status in real-time

### Audio Format

The application uses the following audio configuration:
- **Sample Rate**: 48kHz
- **Encoding**: PCM 16-bit
- **Channels**: Stereo
- **Buffer Size**: 2x minimum buffer size for optimal performance

## Project Structure

```
app/
├── src/main/
│   ├── java/net/nativemind/telon/
│   │   ├── MainActivity.kt          # Main activity with UI controls
│   │   ├── Recording.kt             # Audio recording utilities
│   │   └── PermissionRequest.kt     # Permission handling
│   ├── res/
│   │   ├── layout/                  # UI layouts
│   │   └── values/                  # String resources
│   └── AndroidManifest.xml
└── build.gradle.kts                 # Build configuration
```

## Key Components

### MainActivity
- Handles UI interactions
- Manages audio recorder lifecycle
- Updates recording status display

### Recording
- Provides audio format configuration
- Initializes AudioRecord instances
- Manages recording state and status updates

### PermissionRequest
- Handles runtime permission requests
- Manages microphone access permissions

## Development

### Building

```bash
./gradlew build
```

### Running Tests

```bash
./gradlew test                    # Unit tests
./gradlew connectedAndroidTest    # Instrumented tests
```

### Clean Build

```bash
./gradlew clean build
```

## Dependencies

- **AndroidX Core KTX**: Kotlin extensions for Android
- **AndroidX AppCompat**: Backward compatibility support
- **Material Design**: Modern UI components
- **JUnit**: Unit testing framework
- **Espresso**: UI testing framework

## TODO

- [ ] Implement audio file recording functionality
- [ ] Add calling features
- [ ] Improve permission handling for better user experience
- [ ] Add audio playback capabilities
- [ ] Implement background recording service
- [ ] Add audio format selection options

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions, please create an issue in the repository. 