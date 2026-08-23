# SDD: PJSIP Mode Voice Line (Direct Call) - Status

**Type**: SDD (Spec-Driven Development)
**Module**: pjsip-mode-voiceline
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

PJSIP mode for direct voice line calling - bridges SIP calls to GSM radio via hardware adapters with differential signaling for echo-free audio.

---

## Dependencies

### Requires

| SDD Flow | Description | Status |
|----------|-------------|--------|
| `sdd-pjsip-mode-inversion` | Right channel inversion for differential signaling | In development |
| `sdd-voiceline-hardwarejack-mode` | Hardware adapter (TRRS/USB) integration | In development |

---

## Current Phase: SPECIFICATIONS

### What Has Been Specified

**Architecture**:
- Uses `InversionPort` from `sdd-pjsip-mode-inversion`
- Integrates with Android audio device (VOICE_CALL source)
- Routes SIP media to GSM radio via hardware adapter

**Call Flow**:
- SIP INVITE → Gateway → InversionPort → Android Audio → Hardware Adapter → GSM Radio
- Differential signaling (L - R) for echo cancellation
- Bidirectional audio between SIP and GSM

**Integration**:
- New files: `voiceline_mode.c`, `voiceline_mode.h`
- Modified: `android_jni_dev.c`, `pjsua_call.c`
- Depends on: `inversion_port.c/h`

### Open Questions

- [ ] **Call Initiation**: Intent vs TelephonyManager API?
- [ ] **Call State Sync**: How to handle state mismatches?
- [ ] **Error Recovery**: What if GSM call drops?
- [ ] **Multi-Call**: Support multiple simultaneous calls?

---

## Next Steps

1. Review requirements and specifications
2. Say "requirements approved" when ready
3. Say "specs approved" to move to implementation planning
4. Create implementation plan (03-plan.md)
5. Begin implementation

---

*Created by /sdd - Direct voice line calling mode*
