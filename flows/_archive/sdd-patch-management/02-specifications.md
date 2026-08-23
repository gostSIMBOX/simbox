# Patch Management Specifications

> Technical specifications derived from code analysis.

## Architecture

### Patch Directory Structure

```
src/
└── patch_X.Y.Z/
    ├── patch.sh              # Patch application script
    └── src/
        └── pjsip2/
            ├── pjlib/
            │   └── include/pj/config_site.h
            ├── pjmedia/
            │   ├── src/pjmedia-audiodev/
            │   │   ├── android_jni_dev.c
            │   │   ├── oboe_dev.c (2.9+)
            │   │   └── opensl_dev.c (2.9+)
            │   ├── include/pjmedia/
            │   │   ├── audiodev.h
            │   │   └── stereo.h
            │   └── src/pjmedia/conference.c
            └── pjsip/
                ├── src/pjsua-lib/pjsua_aud.c
                └── include/pjsua-lib/pjsua.h
```

### Version Support Matrix

| PJSIP Version | Patch Directory | Key Features | Status |
|---------------|-----------------|--------------|--------|
| 2.7.1 | `src/patch_2.7.1/` | Android JNI, G.729, G.7221, AEC | Active |
| 2.9 | `src/patch_2.9/` | Android JNI + Oboe + OpenSL ES | Active |
| 2.10 | External repo | TBD | External |

---

## Patch Components

### 1. Configuration Site (`config_site.h`)

**Purpose**: Enable/disable PJSIP features at compile time

**Configuration** (2.7.1):
```c
#define PJ_CONFIG_ANDROID 1
#define PJMEDIA_HAS_G729_CODEC 1
#define PJMEDIA_HAS_G7221_CODEC 1
#include <pj/config_site_sample.h>
#define PJMEDIA_HAS_VIDEO 0
#define PJMEDIA_AUDIO_DEV_HAS_ANDROID_JNI 1
#define PJMEDIA_AUDIO_DEV_HAS_OPENSL 0
#define PJSIP_AUTH_AUTO_SEND_NEXT 1  // Try for Asterisk
#define PJMEDIA_HAS_SPEEX_AEC 1
#define PJMEDIA_SPEEX_AEC_USE_AGC 1
#define PJMEDIA_HAS_WEBRTC_AEC 1
#define PJMEDIA_WEBRTC_AEC_USE_MOBILE 1
#define PJSIP_AUTH_HEADER_CACHING 1  // Try for Asterisk
#define PJMEDIA_SPEEX_AEC_USE_DENOISE 0  // Remove adds
#define PJMEDIA_A_R 1
```

**Key Features**:
- `PJ_CONFIG_ANDROID`: Android platform detection
- `PJMEDIA_HAS_G729_CODEC`: G.729 codec support
- `PJMEDIA_HAS_G7221_CODEC`: G.7221 codec support
- `PJMEDIA_AUDIO_DEV_HAS_ANDROID_JNI`: Android JNI audio device
- `PJMEDIA_HAS_SPEEX_AEC`: Acoustic Echo Cancellation
- `PJMEDIA_SPEEX_AEC_USE_AGC`: Automatic Gain Control
- `PJMEDIA_HAS_WEBRTC_AEC`: WebRTC AEC (mobile-optimized)
- `PJSIP_AUTH_AUTO_SEND_NEXT`: Auto-retry auth for Asterisk
- `PJSIP_AUTH_HEADER_CACHING`: Cache auth headers

---

### 2. Android JNI Audio Device (`android_jni_dev.c`)

**Purpose**: Native Android audio I/O via JNI

**Key Structures**:
```c
struct android_aud_factory {
    pjmedia_aud_dev_factory base;
    pj_pool_factory *pf;
    pj_pool_t *pool;
};

struct android_aud_stream {
    pjmedia_aud_stream base;
    pj_pool_t *pool;
    pj_str_t name;
    pjmedia_dir dir;
    pjmedia_aud_param param;
    
    // Record
    jobject record;
    pjmedia_aud_rec_cb rec_cb;
    pj_thread_t *rec_thread;
    
    // Playback
    jobject track;
    pjmedia_aud_play_cb play_cb;
    pj_thread_t *play_thread;
};
```

**Features**:
- JNI integration with Android AudioManager
- Separate threads for recording and playback
- Callbacks for audio buffer processing
- Support for mono/stereo conversion

---

### 3. OpenSL ES Device (2.9+) (`opensl_dev.c`)

**Purpose**: High-performance audio via OpenSL ES API

**Benefits**:
- Lower latency than JNI
- Hardware-accelerated audio processing
- Better integration with Android audio system

---

### 4. Oboe Device (2.9+) (`oboe_dev.c`)

**Purpose**: Modern Android audio API (Google Oboe library)

**Benefits**:
- Lowest latency audio path
- Automatic API selection (AAudio or OpenSL ES)
- Recommended for Android 8.0+

---

### 5. Audio Conference Bridge (`conference.c`)

**Purpose**: Multi-party audio conferencing

**Modifications**:
- Stereo mixing support
- Audio level monitoring

---

### 6. PJSUA Audio Layer (`pjsua_aud.c`, `pjsua.h`)

**Purpose**: High-level audio management

**Modifications**:
- Audio device selection
- Stream management improvements

---

## Patch Application Workflow

### Inside Docker Container

```bash
# From patch.sh
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

### Build Integration

**Host script** (`build_android_X.Y.Z.sh`):
```bash
# Copy patches into Docker build context
rm -rf ./android_${PJSIP_VERSION}/patch
cp -r ./src/patch_${PJSIP_VERSION} ./android_${PJSIP_VERSION}/patch

# Docker build applies patches during image creation
docker build -t ${IMAGE_NAME} ./android_${PJSIP_VERSION}/
```

**Dockerfile**:
```dockerfile
# Add patch directory to image
ADD patch /sources/patch

# Apply patches during build
RUN IFS=" " && \
    for arch in $TARGET_ARCHS; \
    do \
      /sources/patch/patch.sh ${arch}; \
    done
```

---

## Audio API Research Notes (from TODO.md)

### Android Audio Streams

| Stream Type | Value | Use Case |
|-------------|-------|----------|
| AUDIO_STREAM_VOICE_CALL | 0 | Voice calls |
| AUDIO_STREAM_SYSTEM | 1 | System sounds |
| AUDIO_STREAM_RING | 2 | Ringtone |
| AUDIO_STREAM_MUSIC | 3 | Media playback |
| AUDIO_STREAM_BLUETOOTH_SCO | 6 | Bluetooth headset |

### Qualcomm-Specific Notes

**Recording restrictions** (can be disabled via Magisk):
```
voice.record.conc.disabled=false
voice.voip.conc.disabled=false
```

**Playback workaround**: Use `AUDIO_STREAM_PATCH` to bypass restrictions

### Related APIs

- **OpenSL ES**: `SLES/OpenSLES.h`, `SLES/OpenSLES_AndroidConfiguration.h`
- **AAudio**: Modern low-latency API (Android 8.0+)
- **Oboe**: Cross-platform library wrapping AAudio/OpenSL ES

### Useful Links

- Android NDK samples: https://github.com/android/ndk-samples
- Oboe getting started: https://github.com/google/oboe/blob/master/docs/GettingStarted.md
- OpenSL ES reference: https://android.googlesource.com/platform/frameworks/wilhelm/+/master/include/SLES/

---

## Legacy Additions

> Added by /legacy on 2026-03-04

**Insights from code analysis**:

- **Config duplication**: `config_site.h` has duplicate `PJ_CONFIG_ANDROID` definitions
- **Asterisk compatibility**: `PJSIP_AUTH_AUTO_SEND_NEXT=1` and `PJSIP_AUTH_HEADER_CACHING=1` for Asterisk
- **WebRTC AEC**: Mobile-optimized WebRTC AEC enabled alongside Speex AEC
- **Denoise disabled**: `PJMEDIA_SPEEX_AEC_USE_DENOISE=0` to "remove adds"
- **Version evolution**: 2.9+ adds Oboe and OpenSL ES support (modern audio APIs)
- **Research notes**: TODO.md contains extensive Android audio API research

---

*Generated by /legacy analysis*
*Status: DRAFT*
