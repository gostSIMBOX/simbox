# Requirements: CI/CD Pipeline (GitHub Actions)

> Version: 1.1
> Status: DRAFT
> Last Updated: 2026-03-11

## Problem Statement

The project needs automated CI/CD pipelines to build, test, and release the application for Android and Aurora OS platforms. Currently, builds are performed manually, which is error-prone and time-consuming.

## User Stories

### Primary

**As a** developer
**I want** automated builds and tests triggered on push/PR
**So that** I can verify code changes don't break the build

**As a** developer
**I want** automated releases when tags are pushed
**So that** I can easily distribute new versions

### Secondary

**As a** maintainer
**I want** build artifacts stored and accessible
**So that** I can download and test specific versions

## Acceptance Criteria

### Must Have

1. **Given** a push to any branch
   **When** the Android workflow triggers
   **Then** tests run and Android APK is built successfully

2. **Given** a push to any branch
   **When** the Aurora OS workflow triggers (separate from Android)
   **Then** Aurora OS package is built successfully

3. **Given** a new version tag matching `v*` is pushed
   **When** the release workflow triggers
   **Then** signed release artifacts for both platforms are uploaded to GitHub Releases

4. **Given** Android build workflow
   **When** APK is built
   **Then** it is signed with the production keystore

### Should Have

- Build artifacts are cached to speed up subsequent builds
- Build status badges in README
- PR checks that must pass before merge

### Won't Have (This Iteration)

- iOS builds
- Deployment to app stores
- Split APKs per architecture (using Fat APK instead)

## Constraints

- **Technical**: Must use GitHub Actions (no external CI services)
- **Platform**: Android OS and Aurora OS only
- **Android**: minSdkVersion 19 (Android 4.4 KitKat and above)
- **Android APK**: Fat APK (all architectures: armeabi-v7a, arm64-v8a, x86_64)
- **Aurora OS**: SDK installed in workflow (не Docker), отдельный workflow чтобы не блокировать Android
- **Dependencies**: Requires Flutter SDK and platform-specific SDKs

## Decisions Made

| Question | Decision |
|----------|----------|
| Aurora OS build approach | Option C: Install SDK in workflow, separate workflow |
| Android min version | API 19 (Android 4.4) |
| Android APK type | Fat APK (all architectures in one) |
| Trigger branches | All branches |
| Release tag pattern | `v*` (e.g., v1.0.0, v2.1.0-beta) |
| Signing | Existing keystore via GitHub Secrets |
| Tests | Run on all builds |

## GitHub Secrets Required

The following secrets must be configured in **Settings → Secrets and variables → Actions → Repository secrets**:

| Secret Name | Description |
|-------------|-------------|
| `GATEWAY_ANDROID_KEYSTORE_BASE64` | Keystore file encoded in base64: `base64 -i your-key.jks` |
| `GATEWAY_ANDROID_KEYSTORE_PASSWORD` | Keystore password |
| `GATEWAY_ANDROID_KEY_ALIAS` | Key alias in keystore |
| `GATEWAY_ANDROID_KEY_PASSWORD` | Key password |

## References

- GitHub Actions documentation
- Flutter CI/CD guides
- Aurora OS SDK documentation

---

## Approval

- [x] Reviewed by: User
- [x] Approved on: 2026-03-11
- [x] Notes: All requirements confirmed
