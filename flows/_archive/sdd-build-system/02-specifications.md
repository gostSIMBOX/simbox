# Build System Specifications

> Technical specifications derived from code analysis.

## Architecture

### High-Level Flow

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐     ┌────────┐
│ build_android   │────▶│ docker build │────▶│ docker run  │────▶│ docker   │────▶│ docker │
│ .sh             │     │ (image)      │     │ (container) │     │ cp       │     │ rm     │
└─────────────────┘     └──────────────┘     └─────────────┘     └──────────┘     └────────┘
       │                      │                      │                    │
       │                      │                      │                    │
       ▼                      ▼                      ▼                    ▼
  Copy patches           Download              Build PJSIP +        Extract          Cleanup
  to context             dependencies          codecs               artifacts
```

### Component Specifications

#### 1. Host Build Script (`build_android_X.Y.Z.sh`)

**Purpose**: Orchestrate Docker-based build process

**Inputs**:
- PJSIP version (e.g., "2.7.1", "2.9", "2.10")
- Patch directory: `src/patch_X.Y.Z/`
- Docker context: `android_X.Y.Z/`

**Process**:
```bash
1. rm -rf ./dist/android*
2. cp -r ./src/patch_X.Y.Z ./android_X.Y.Z/patch
3. docker build -t react-native-sip2-builder/android_X.Y.Z ./android_X.Y.Z/
4. docker run --name ${CONTAINER_NAME} ${IMAGE_NAME} bin/true
5. docker cp ${CONTAINER_NAME}:/dist/android ./dist/android_X.Y.Z
6. docker rm ${CONTAINER_NAME}
```

**Outputs**:
- `./dist/android_X.Y.Z/` - Built libraries and JNI bindings

**Key Variables**:
- `IMAGE_NAME`: `react-native-sip2-builder/android_${PJSIP_VERSION}`
- `CONTAINER_NAME`: `react-native-sip2-builder-${RANDOM}` (avoids collisions)

---

#### 2. Docker Image (`android_X.Y.Z/Dockerfile`)

**Base Image**: `ubuntu:latest`

**Dependencies Installed**:
- Android NDK r12b (from `android-ndk-r12b-linux-x86_64.zip`)
- Android SDK tools r25.2.5
- JDK 8 (`openjdk-8-jdk`)
- Build tools: `gcc`, `g++`, `binutils`, `make`, `autoconf`
- Libraries: `libssl-dev`, `libpcre3-dev`, `ant`, `unzip`, `mc`
- 32-bit compatibility: `libc6:i386`, `libstdc++6:i386`, `zlib1g:i386`

**Environment Variables**:
```dockerfile
ANDROID_NDK_ROOT=/sources/android_ndk
ANDROID_SETUP_APIS="19 22 23 24 25 26 27 28 29"
ANDROID_BUILD_TOOLS_VERSION=25
ANDROID_TARGET_API=23
TARGET_ARCHS="armeabi-v7a x86 arm64-v8a x86_64"
PATH=/sources/android_ndk:$PATH
```

**Source Downloads**:
- PJSIP: `https://github.com/pjsip/pjproject/archive/2.7.1.tar.gz`
- OpenSSL: `https://www.openssl.org/source/openssl-1.1.1g.tar.gz`
- OpenH264: `https://github.com/cisco/openh264/archive/v1.8.0.tar.gz`
- Opus: `http://downloads.xiph.org/releases/opus/opus-1.3.1.tar.gz`
- Swig: `https://ayera.dl.sourceforge.net/project/swig/swig/swig-3.0.7/swig-3.0.7.tar.gz`

**Directory Structure**:
```
/sources/
├── android_ndk/     # NDK toolchain
├── android_sdk/     # SDK tools
├── pjsip/           # PJSIP source
├── openssl/         # OpenSSL source
├── openh264/        # OpenH264 source
├── opus/            # Opus source
└── swig/            # Swig source

/output/
├── openssl/${ARCH}/     # Built OpenSSL per architecture
├── openh264/${ARCH}/    # Built OpenH264 per architecture
├── opus/${ARCH}/        # Built Opus per architecture
└── pjsip/${ARCH}/       # Built PJSIP per architecture

/dist/
└── android/         # Final output
    └── src/main/
        ├── jniLibs/${ARCH}/  # .so files per architecture
        └── java/             # JNI Java bindings
```

---

#### 3. PJSIP Build Script (`build_pjsip.sh`)

**Purpose**: Configure and build PJSIP with codec support

**Inputs**:
- `TARGET_ARCH`: Target architecture (e.g., "armeabi-v7a")
- `/sources/pjsip/`: PJSIP source directory
- `/sources/patch/`: Patch directory (copied during image build)

**Configuration** (`config_site.h`):
```c
#define PJ_CONFIG_ANDROID 1
#define PJMEDIA_HAS_G729_CODEC 1
#define PJMEDIA_HAS_G7221_CODEC 1
#include <pj/config_site_sample.h>
#define PJMEDIA_HAS_VIDEO 0
#define PJMEDIA_AUDIO_DEV_HAS_ANDROID_JNI 1
#define PJMEDIA_AUDIO_DEV_HAS_OPENSL 0
#define PJSIP_AUTH_AUTO_SEND_NEXT 0
#define PJMEDIA_HAS_SPEEX_AEC 0
#define PJMEDIA_HAS_WEBRTC_AEC 1
```

**Build Commands**:
```bash
1. cp -r /sources/pjsip /tmp/pjsip
2. cd /tmp/pjsip
3. export TARGET_ABI=${TARGET_ARCH}
4. export APP_PLATFORM=android-${ANDROID_TARGET_API}
5. export ANDROID_NDK_ROOT=/sources/android_ndk
6. export NDK_TOOLCHAIN_VERSION=4.9
7. ./configure-android --use-ndk-cflags
8. make dep && make
```

**Outputs**:
- `/output/pjsip/${TARGET_ARCH}/` - Built libraries

**Note**: OpenSSL, OpenH264, Opus integration currently commented out in config (using `--use-ndk-cflags` only)

---

#### 4. Patch Application (`patch.sh`)

**Purpose**: Apply version-specific patches to built PJSIP

**Inputs**:
- `TARGET_ARCH`: Target architecture
- `/sources/patch/src/pjsip2/`: Patched source files

**Process**:
```bash
1. cp -r /sources/patch/src/pjsip2/* /tmp/pjsip
2. cd /tmp/pjsip
3. export TARGET_ABI=${TARGET_ARCH}
4. export APP_PLATFORM=android-${ANDROID_TARGET_API}
5. export ANDROID_NDK_ROOT=/sources/android_ndk
6. make dep && make
7. cd /tmp/pjsip/pjsip-apps/src/swig && make
8. mkdir -p /output/pjsip/jniLibs/${TARGET_ARCH}/
9. mv ./java/android/app/src/main/jniLibs/**/libpjsua2.so /output/pjsip/jniLibs/${TARGET_ARCH}/
10. mv ./java/android/app/src/main/java /output/pjsip/java (if not exists)
```

**Outputs**:
- `/output/pjsip/jniLibs/${ARCH}/libpjsua2.so` - Final PJSIP library
- `/output/pjsip/java/` - JNI Java bindings

---

#### 5. OpenSSL Build Script (`build_openssl.sh`)

**Purpose**: Build OpenSSL for each target architecture

**Architecture Configurations**:
| Architecture | Target | Toolchain | ARCH_FLAGS |
|--------------|--------|-----------|------------|
| armeabi-v7a | android-armv7 | arm-linux-androideabi-4.9 | `-march=armv7-a -mfloat-abi=softfp -mfpu=vfpv3-d16` |
| arm64-v8a | android | aarch64-linux-android-4.9 | (none) |
| armeabi | android | arm-linux-androideabi-4.9 | `-mthumb` |
| x86 | android-x86 | x86-4.9 | `-march=i686 -msse3 -mstackrealign -mfpmath=sse` |
| x86_64 | linux-x86_64 | x86_64-4.9 | (none) |

**Build Process**:
```bash
1. cp -r /sources/openssl /tmp/openssl
2. ./make-standalone-toolchain.sh --ndk-dir=/sources/android_ndk --platform=android-${API} --toolchain=${TOOLCHAIN}
3. ./Configure ${TARGET} no-asm no-unit-test --openssldir=${TARGET_PATH}
4. make && make install
```

**Outputs**:
- `/output/openssl/${ARCH}/` - Built OpenSSL libraries

---

#### 6. OpenH264 Build Script (`build_openh264.sh`)

**Purpose**: Build OpenH264 video codec

**Build Arguments**:
```bash
ARGS="OS=android ENABLEPIC=Yes NDKROOT=/sources/android_ndk NDKLEVEL=${OPENH264_TARGET_NDK_LEVEL}"
ARGS="${ARGS}TARGET=android-${ANDROID_TARGET_API} ARCH="
# Architecture-specific:
# armeabi-v7a: ARGS="${ARGS}arm APP_ABI=armeabi"
# arm64-v8a:   ARGS="${ARGS}arm64"
# x86:         ARGS="${ARGS}x86"
# x86_64:      ARGS="${ARGS}x86_64"
```

**Process**:
```bash
1. cp -r /sources/openh264 /tmp/openh264
2. cd /tmp/openh264
3. sed -i "s*PREFIX=/usr/local*PREFIX=${TARGET_PATH}*g" Makefile
4. make ${ARGS} install
```

---

#### 7. Opus Build Script (`build_opus.sh`)

**Purpose**: Build Opus audio codec

**Process**:
```bash
1. cp -r /sources/opus /tmp/opus
2. cd /tmp/opus/jni
3. ndk-build APP_ABI="${TARGET_ARCH}"
4. mkdir -p ${TARGET_PATH}/include ${TARGET_PATH}/lib
5. cp -r ../include ${TARGET_PATH}/include/opus
6. cp ../obj/local/${TARGET_ARCH}/libopus.a ${TARGET_PATH}/lib/
```

---

## Build Workflow Details

### Docker Container Lifecycle

1. **Build Image**: `docker build -t ${IMAGE_NAME} ./android_${PJSIP_VERSION}/`
2. **Create Container**: `docker run --name ${CONTAINER_NAME} ${IMAGE_NAME} bin/true`
   - Container runs `bin/true` (immediate exit) after build steps in Dockerfile
   - All build work happens during `docker build` (RUN instructions)
3. **Extract Artifacts**: `docker cp ${CONTAINER_NAME}:/dist/android ./dist/android_${PJSIP_VERSION}`
4. **Cleanup**: `docker rm ${CONTAINER_NAME}`

### Cleanup Script (`docker_clean.sh`)

```bash
docker container prune
docker image prune -a
```

**Purpose**: Remove unused containers and images to free disk space

---

## Version Support Matrix

| PJSIP Version | Build Script | Docker Context | Patch Directory | Status |
|---------------|--------------|----------------|-----------------|--------|
| 2.7.1 | `build_android_2.7.1.sh` | `android_2.7.1/` | `src/patch_2.7.1/` | Active |
| 2.9 | `build_android_2.9.sh` | `android_2.9/` | `src/patch_2.9/` | Active |
| 2.10 | `build_android_2.10.sh` | `android_2.10/` | `src/patch_2.10/` | Active (external source) |

**Note for 2.10**: Patches copied from `../2.10.git/pjsip2` (external repository)

---

## Output Structure

```
dist/
└── android_2.7.1/
    └── src/
        └── main/
            ├── jniLibs/
            │   ├── armeabi-v7a/
            │   │   ├── libpjsua2.so
            │   │   └── libopenh264.so
            │   ├── x86/
            │   ├── arm64-v8a/
            │   └── x86_64/
            └── java/
                └── org/pjsip/pjsua2/  # JNI bindings
```

---

## Legacy Additions

> Added by /legacy on 2026-03-04

**Insights from code analysis**:

- **Random container names**: Prevents collisions when running multiple builds
- **No volume mounts**: Uses `docker cp` for cleaner artifact extraction
- **Single-layer Dockerfile**: All dependencies in one layer (simplicity over optimization)
- **Sequential architecture builds**: TARGET_ARCHS loop builds one arch at a time
- **Patch integration**: Patches applied as part of Docker build, not post-build
- **Multiple SDK APIs**: Supports API levels 19-29 for broad device compatibility

---

*Generated by /legacy analysis*
*Status: DRAFT*
