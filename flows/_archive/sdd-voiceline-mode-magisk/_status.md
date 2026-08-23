# SDD: Voice Line Mode Magisk - Status

**Type**: SDD (Spec-Driven Development)
**Module**: voiceline-mode-magisk
**Status**: DRAFT
**Created**: 2026-03-06 (renamed 2026-03-06)
**Current Phase**: SPECIFICATIONS (Ready for Review)

---

## Progress

- [x] SDD flow initialized (renamed from voiceline-hardwarejack-mode)
- [x] Requirements document created (01-requirements.md) - v1.3
- [ ] Requirements approved
- [x] Specifications document created (02-specifications.md) - v1.2
- [ ] Specs approved
- [ ] Implementation plan created (03-plan.md)
- [ ] Plan approved
- [ ] Implementation started
- [ ] Tests created
- [ ] Documentation reviewed
- [ ] Approved for production

---

## Summary

**Magisk-based** voice line integration with **system-level** audio injection. Uses `InversionPort` for right channel inversion and Magisk module for privileged permissions (CAPTURE_AUDIO_OUTPUT).

### Key Characteristics

- **Root Required**: Magisk v20.0+ with system module
- **Electronic Injection**: Direct audio injection via CAPTURE_AUDIO_OUTPUT
- **Highest Quality**: No acoustic coupling loss
- **Differential Signaling**: TRRS/USB hardware adapter support

---

## Dependencies

### Requires

| SDD Flow | Purpose | Status |
|----------|---------|--------|
| `sdd-pjsip-mode-inversion` | Right channel inversion | In development |
| `sdd-magisk-voice-recording` | Magisk module for privileged permissions | In development |

### Related

| SDD Flow | Relationship |
|----------|--------------|
| `sdd-voiceline-mode-direct` | Fallback (no root, lower quality) |
| `sdd-voiceline-mode-earphone-to-mic` | Alternative acoustic coupling |

---

## Current Phase: SPECIFICATIONS

### What Has Been Specified

**Architecture**:
- Uses `InversionPort` from `sdd-pjsip-mode-inversion`
- Requires Magisk module (`sdd-magisk-voice-recording`)
- TRRS/USB hardware adapter with differential signaling
- Double inversion (software + hardware) for echo prevention

**Audio Path**:
```
SIP → InversionPort [L, -R] → Android Audio (VOICE_CALL) → 
Hardware Adapter (4R+1C) → Phone Line (L-R differential) → Echo cancelled
```

**Integration**:
- Uses: `inversion_port.c/h` (from sdd-pjsip-mode-inversion)
- Requires: Magisk module installation
- Modified: `android_jni_dev.c`

### Open Questions

- [ ] **Call Initiation**: Intent vs TelephonyManager API?
- [ ] **Call State Sync**: Synchronize SIP and GSM states?
- [ ] **Testing**: Test without physical hardware?

---

## Next Steps

1. Review requirements and specifications
2. Say "requirements approved" when ready
3. Say "specs approved" to move to implementation planning
4. Create implementation plan (03-plan.md)
5. Begin implementation

---

*Renamed from sdd-voiceline-hardwarejack-mode to sdd-voiceline-mode-magisk*
*Last Updated: 2026-03-06*
