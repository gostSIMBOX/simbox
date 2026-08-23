# Implementation Plan: CI/CD Pipeline (GitHub Actions)

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-03-11
> Specifications: [02-specifications.md](./02-specifications.md)

## Summary

Implementation consists of 4 phases:
1. **Preparation** - Create directory structure, update build.gradle.kts
2. **Android CI** - Create and test android-ci.yml
3. **Aurora CI** - Create aurora-ci.yml (research SDK first)
4. **Release** - Create release.yml combining both builds

## Task Breakdown

### Phase 1: Preparation

#### Task 1.1: Create .github/workflows directory
- **Description**: Create directory for GitHub Actions workflows
- **Files**:
  - `.github/workflows/` - Create directory
- **Dependencies**: None
- **Verification**: Directory exists
- **Complexity**: Low

#### Task 1.2: Update minSdk in build.gradle.kts
- **Description**: Change minSdk from flutter.minSdkVersion to 19
- **Files**:
  - `android/app/build.gradle.kts` - Modify
- **Dependencies**: None
- **Verification**: `grep "minSdk = 19" android/app/build.gradle.kts`
- **Complexity**: Low

### Phase 2: Android CI Workflow

#### Task 2.1: Create android-ci.yml
- **Description**: Create main Android CI workflow with tests and build
- **Files**:
  - `.github/workflows/android-ci.yml` - Create
- **Dependencies**: Task 1.1, Task 1.2
- **Verification**: Workflow file is valid YAML, passes `actionlint` if available
- **Complexity**: Medium

**Workflow structure:**
```yaml
name: Android CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - Checkout
      - Setup Java 11
      - Setup Flutter
      - Cache pub dependencies
      - Cache Gradle
      - Get dependencies
      - Analyze code
      - Run tests
      - Setup signing (from secrets)
      - Build APK
      - Upload artifact
```

#### Task 2.2: Add .gitignore entries for CI artifacts
- **Description**: Ensure generated CI files are not committed
- **Files**:
  - `android/.gitignore` - Modify (add release-key.jks if not present)
- **Dependencies**: None
- **Verification**: `grep "release-key.jks" android/.gitignore`
- **Complexity**: Low

### Phase 3: Aurora CI Workflow

#### Task 3.1: Research Aurora OS SDK for CI
- **Description**: Find official method to install Aurora SDK in GitHub Actions
- **Files**: None (research only)
- **Dependencies**: None
- **Verification**: Document findings in implementation log
- **Complexity**: Medium
- **Note**: May require web search for Aurora OS documentation

#### Task 3.2: Create aurora-ci.yml
- **Description**: Create Aurora OS CI workflow
- **Files**:
  - `.github/workflows/aurora-ci.yml` - Create
- **Dependencies**: Task 1.1, Task 3.1
- **Verification**: Workflow file is valid YAML
- **Complexity**: High (depends on SDK availability)

**Workflow structure:**
```yaml
name: Aurora CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - Checkout
      - Install Aurora SDK (method TBD)
      - Setup Flutter for Aurora
      - Get dependencies
      - Build Aurora package
      - Upload artifact
```

### Phase 4: Release Workflow

#### Task 4.1: Create release.yml
- **Description**: Create release workflow triggered by version tags
- **Files**:
  - `.github/workflows/release.yml` - Create
- **Dependencies**: Task 2.1, Task 3.2
- **Verification**: Workflow file is valid YAML
- **Complexity**: Medium

**Workflow structure:**
```yaml
name: Release
on:
  push:
    tags: ['v*']
jobs:
  build-android:
    # Same as android-ci build job
  build-aurora:
    # Same as aurora-ci build job
  release:
    needs: [build-android, build-aurora]
    steps:
      - Download artifacts
      - Create GitHub Release
      - Upload release assets
```

## Dependency Graph

```
Task 1.1 ─────────┬─────────────────────────────────┐
(create dir)      │                                 │
                  ▼                                 ▼
Task 1.2 ──► Task 2.1 ──────────────────────► Task 4.1
(minSdk)    (android-ci)                     (release)
                  │                                 ▲
                  ▼                                 │
            Task 2.2                                │
            (.gitignore)                            │
                                                    │
Task 3.1 ──► Task 3.2 ──────────────────────────────┘
(research)  (aurora-ci)
```

## File Change Summary

| File | Action | Reason |
|------|--------|--------|
| `.github/workflows/` | Create | Directory for workflows |
| `.github/workflows/android-ci.yml` | Create | Android CI workflow |
| `.github/workflows/aurora-ci.yml` | Create | Aurora OS CI workflow |
| `.github/workflows/release.yml` | Create | Release workflow |
| `android/app/build.gradle.kts` | Modify | Set minSdk=19 |
| `android/.gitignore` | Modify | Add release-key.jks |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Aurora SDK not available for CI | Medium | High | Create placeholder workflow, document manual process |
| Flutter version incompatibility | Low | Medium | Pin specific Flutter version |
| Secrets misconfiguration | Medium | Medium | Add validation step with clear error messages |
| Tests flaky in CI | Low | Low | Add retry mechanism if needed |

## Rollback Strategy

If implementation fails:
1. Delete `.github/workflows/` directory
2. Revert `android/app/build.gradle.kts` changes
3. Revert `android/.gitignore` changes

All changes are additive and easily reversible.

## Checkpoints

After each phase:
- [ ] **Phase 1**: Directory exists, minSdk=19 in build.gradle.kts
- [ ] **Phase 2**: Android CI workflow created, syntax valid
- [ ] **Phase 3**: Aurora CI workflow created (or documented blockers)
- [ ] **Phase 4**: Release workflow created, all workflows syntax valid

## Implementation Order

1. Task 1.1 → Task 1.2 (sequential, foundation)
2. Task 2.1 → Task 2.2 (sequential, Android CI)
3. Task 3.1 → Task 3.2 (sequential, Aurora CI)
4. Task 4.1 (depends on 2.1 and 3.2)

**Parallel opportunity**: Phase 2 and Phase 3 can run in parallel after Phase 1.

## User Actions Required

After implementation, user must:

1. **Add GitHub Secrets** (Settings → Secrets → Actions):
   ```
   GATEWAY_ANDROID_KEYSTORE_BASE64
   GATEWAY_ANDROID_KEYSTORE_PASSWORD
   GATEWAY_ANDROID_KEY_ALIAS
   GATEWAY_ANDROID_KEY_PASSWORD
   ```

2. **Generate base64 keystore**:
   ```bash
   base64 -i your-release-key.jks | pbcopy  # macOS
   base64 -i your-release-key.jks | xclip   # Linux
   ```

3. **Push to trigger workflows**

---

## Approval

- [x] Reviewed by: User
- [x] Approved on: 2026-03-11
- [x] Notes: Approved
