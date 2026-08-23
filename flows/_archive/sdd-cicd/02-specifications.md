# Specifications: CI/CD Pipeline (GitHub Actions)

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-03-11
> Requirements: [01-requirements.md](./01-requirements.md)

## Overview

Three GitHub Actions workflows will be created:
1. **android-ci.yml** - Android build + tests on all branches
2. **aurora-ci.yml** - Aurora OS build on all branches (separate, non-blocking)
3. **release.yml** - Creates GitHub Release with artifacts on `v*` tags

## Affected Systems

| System | Impact | Notes |
|--------|--------|-------|
| `.github/workflows/android-ci.yml` | Create | Android CI workflow |
| `.github/workflows/aurora-ci.yml` | Create | Aurora OS CI workflow |
| `.github/workflows/release.yml` | Create | Release workflow |
| `android/app/build.gradle.kts` | Modify | Ensure minSdk=19, add CI signing support |

## Architecture

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Push / PR Event                          │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
                    ▼                           ▼
    ┌───────────────────────────┐   ┌───────────────────────────┐
    │     android-ci.yml        │   │     aurora-ci.yml         │
    │  (runs independently)     │   │  (runs independently)     │
    ├───────────────────────────┤   ├───────────────────────────┤
    │ 1. Checkout               │   │ 1. Checkout               │
    │ 2. Setup Java 11          │   │ 2. Install Aurora SDK     │
    │ 3. Setup Flutter          │   │ 3. Setup Flutter          │
    │ 4. Get dependencies       │   │ 4. Get dependencies       │
    │ 5. Run tests              │   │ 5. Build Aurora package   │
    │ 6. Build APK (signed)     │   │ 6. Upload artifact        │
    │ 7. Upload artifact        │   └───────────────────────────┘
    └───────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Push Tag v* Event                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │        release.yml            │
              ├───────────────────────────────┤
              │ Job 1: build-android          │
              │   - Build signed APK          │
              │                               │
              │ Job 2: build-aurora           │
              │   - Build Aurora package      │
              │                               │
              │ Job 3: create-release         │
              │   - needs: [build-android,    │
              │            build-aurora]      │
              │   - Create GitHub Release     │
              │   - Upload all artifacts      │
              └───────────────────────────────┘
```

### Data Flow

```
GitHub Secrets (GATEWAY_*)
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│ Decode keystore │───►│ key.properties  │
│ from base64     │    │ (generated)     │
└─────────────────┘    └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Gradle build   │
                       │  (uses signing) │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Signed APK     │
                       └─────────────────┘
```

## Project Configuration

### Current State (from codebase analysis)

| Parameter | Value |
|-----------|-------|
| Flutter SDK | ^3.8.1 |
| Kotlin | 2.1.0 |
| Android Gradle Plugin | 8.7.3 |
| Java | 11 |
| NDK | 27.0.12077973 |
| Current minSdk | flutter.minSdkVersion (default) |
| Package name | org.telon.flutter_gsm_sip_gateway |
| Signing | key.properties (local file) |

### Required Changes

| Parameter | Current | Required |
|-----------|---------|----------|
| minSdk | flutter.minSdkVersion | 19 (hardcoded) |

## Workflow Specifications

### 1. android-ci.yml

**Trigger:**
```yaml
on:
  push:
    branches: ['**']
  pull_request:
    branches: ['**']
```

**Jobs:**

| Step | Action | Notes |
|------|--------|-------|
| Checkout | actions/checkout@v4 | |
| Setup Java | actions/setup-java@v4 | JDK 11, temurin |
| Setup Flutter | subosito/flutter-action@v2 | channel: stable |
| Get dependencies | flutter pub get | |
| Analyze | flutter analyze | Static analysis |
| Run tests | flutter test | All tests in test/ |
| Setup signing | Custom script | Decode keystore from secrets |
| Build APK | flutter build apk | --release |
| Upload artifact | actions/upload-artifact@v4 | Retain 30 days |

**Caching:**
- Flutter SDK (via flutter-action)
- pub cache (~/.pub-cache)
- Gradle cache (~/.gradle/caches)

### 2. aurora-ci.yml

**Trigger:** Same as android-ci.yml

**Jobs:**

| Step | Action | Notes |
|------|--------|-------|
| Checkout | actions/checkout@v4 | |
| Install Aurora SDK | Custom script | Download and install SDK |
| Setup Flutter | Custom | Aurora-compatible Flutter |
| Get dependencies | flutter pub get | |
| Build Aurora package | aurora-cli build | RPM package |
| Upload artifact | actions/upload-artifact@v4 | Retain 30 days |

**Note:** Aurora OS SDK installation will be researched during implementation. May require:
- Official Aurora SDK download
- psdk (Platform SDK) setup
- Specific target architecture (armv7hl, aarch64, i486)

### 3. release.yml

**Trigger:**
```yaml
on:
  push:
    tags:
      - 'v*'
```

**Jobs:**

1. **build-android** - Same as android-ci but for release
2. **build-aurora** - Same as aurora-ci but for release
3. **create-release** - Creates GitHub Release with all artifacts

**Release artifacts:**
- `GOSTsimbox-gateway-{version}-android.apk`
- `GOSTsimbox-gateway-{version}-aurora.rpm` (or appropriate extension)

## Signing Configuration

### GitHub Secrets

| Secret | Description | How to generate |
|--------|-------------|-----------------|
| `GATEWAY_ANDROID_KEYSTORE_BASE64` | Keystore encoded in base64 | `base64 -i release-key.jks` |
| `GATEWAY_ANDROID_KEYSTORE_PASSWORD` | Keystore password | Your password |
| `GATEWAY_ANDROID_KEY_ALIAS` | Key alias | e.g., "release" |
| `GATEWAY_ANDROID_KEY_PASSWORD` | Key password | Your password |

### CI Signing Script

```bash
# Decode keystore
echo "$GATEWAY_ANDROID_KEYSTORE_BASE64" | base64 --decode > android/app/release-key.jks

# Create key.properties
cat > android/key.properties << EOF
storePassword=$GATEWAY_ANDROID_KEYSTORE_PASSWORD
keyPassword=$GATEWAY_ANDROID_KEY_PASSWORD
keyAlias=$GATEWAY_ANDROID_KEY_ALIAS
storeFile=release-key.jks
EOF
```

## Edge Cases

| Case | Trigger | Expected Behavior |
|------|---------|-------------------|
| Missing secrets | Secrets not configured | Build fails with clear error message |
| Aurora SDK unavailable | Download fails | Job fails, doesn't block Android |
| Tests fail | Test failure | Workflow fails, no artifact |
| Tag without v prefix | Push tag "1.0.0" | Release not triggered |

## Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| Signing failed | Invalid keystore/password | Clear error in logs, fail job |
| Flutter version mismatch | SDK incompatibility | Pin Flutter version in workflow |
| Out of memory | Large build | Increase runner memory config |

## Dependencies

### Requires

- GitHub repository with Actions enabled
- GitHub Secrets configured (GATEWAY_*)
- Flutter project with valid pubspec.yaml

### External Actions

| Action | Version | Purpose |
|--------|---------|---------|
| actions/checkout | v4 | Clone repository |
| actions/setup-java | v4 | Install JDK |
| subosito/flutter-action | v2 | Install Flutter |
| actions/upload-artifact | v4 | Store build artifacts |
| actions/download-artifact | v4 | Retrieve artifacts for release |
| softprops/action-gh-release | v1 | Create GitHub Release |

## Testing Strategy

### Manual Verification

- [ ] Push to branch triggers android-ci
- [ ] Push to branch triggers aurora-ci
- [ ] Tests run and report results
- [ ] Signed APK is produced
- [ ] Artifacts are downloadable
- [ ] Push tag v* triggers release
- [ ] Release contains all artifacts

## Open Design Questions

- [x] Aurora OS SDK installation method - решено: установка в workflow
- [ ] Aurora SDK specific version and download URL (will research during implementation)
- [ ] Aurora target architectures needed

---

## Approval

- [x] Reviewed by: User
- [x] Approved on: 2026-03-11
- [x] Notes: Approved
