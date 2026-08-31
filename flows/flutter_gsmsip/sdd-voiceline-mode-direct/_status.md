# SDD: Voice Line Mode Direct - Status

**Type**: SDD (Spec-Driven Development)
**Module**: voiceline-mode-direct
**Status**: DRAFT
**Created**: 2026-03-06
**Current Phase**: SPECIFICATIONS (Ready for Review)

---

## Progress

- [x] SDD flow initialized
- [x] Requirements document created (01-requirements.md)
- [ ] Requirements approved
- [x] Specifications document created (02-specifications.md)
- [ ] Specs approved
- [ ] Implementation plan created (03-plan.md)
- [ ] Plan approved
- [ ] Implementation started
- [ ] Tests created
- [ ] Documentation reviewed
- [ ] Approved for production

---

## Summary

Direct voice line calling **without Magisk root**. Uses Android's standard telephony API and acoustic coupling (earphone → microphone) for audio transfer to GSM radio.

### Key Characteristics

- **No Root Required**: Works on standard Android devices
- **Acoustic Coupling**: Audio travels through air (earphone → microphone)
- **Lower Quality**: Inherent quality loss from acoustic coupling
- **Fallback Mode**: Use when Magisk module not available

---

## Dependencies

### Uses

| SDD Flow | Purpose | Required |
|----------|---------|----------|
| `sdd-pjsip-mode-inversion` | Right channel inversion | Optional |

### Related

| SDD Flow | Relationship |
|----------|--------------|
| `sdd-voiceline-mode-magisk` | Alternative (better quality, requires root) |
| `sdd-voiceline-mode-earphone-to-mic` | Similar acoustic coupling approach |

---

## Current Phase: SPECIFICATIONS

### What Has Been Specified

**Architecture**:
- Android TelephonyManager for GSM call initiation
- Acoustic coupling (speaker → air → microphone)
- Optional InversionPort for better compatibility

**Audio Path**:
```
SIP → Android Audio → Speaker → Air → Microphone → GSM
```

**Integration**:
- New files: `voiceline_mode_direct.c/h`
- Modified: `MainActivity.kt`, `android_jni_dev.c`

### Open Questions

- [ ] **Call Initiation**: Intent vs TelephonyManager API?
- [ ] **Audio Routing**: Earphone vs speakerphone vs earpiece?
- [ ] **Echo Cancellation**: How effective can software AEC be?

---

## Next Steps

1. Review requirements and specifications
2. Say "requirements approved" when ready
3. Say "specs approved" to move to implementation planning
4. Create implementation plan (03-plan.md)
5. Begin implementation

---

*Created by /sdd - Direct voice line calling without Magisk*
