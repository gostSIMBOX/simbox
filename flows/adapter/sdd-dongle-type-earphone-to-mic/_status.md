# SDD: Voice Line Mode Earphone-to-Microphone - Status

**Type**: SDD (Spec-Driven Development)
**Module**: voiceline-mode-earphone-to-mic
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

Earphone-to-microphone **acoustic coupling** mode. Uses physical contact between earphone speaker and device microphone for audio transfer, with **InversionPort** for right channel inversion.

### Key Characteristics

- **Physical Coupling**: Earphone pressed against microphone
- **InversionPort Required**: For differential signaling
- **No Root Required**: Works on standard Android devices
- **Lower Quality**: Inherent to acoustic coupling

---

## Dependencies

### Requires

| SDD Flow | Purpose | Status |
|----------|---------|--------|
| `sdd-pjsip-mode-inversion` | Right channel inversion | In development |

### Related

| SDD Flow | Relationship |
|----------|--------------|
| `sdd-voiceline-mode-magisk` | Electronic injection (better quality) |
| `sdd-voiceline-mode-direct` | Similar acoustic coupling |

---

## Current Phase: SPECIFICATIONS

### What Has Been Specified

**Architecture**:
- **Requires InversionPort** (from `sdd-pjsip-mode-inversion`)
- Physical acoustic coupling (earphone → microphone)
- Audio optimization for coupling (volume, AGC, AEC)

**Audio Path**:
```
SIP → InversionPort [L, -R] → Earphone → Physical Contact → Microphone → GSM
```

**Physical Setup**:
- Earphone speaker pressed against device microphone
- Secure with tape, holder, or custom mount
- Ensure good acoustic contact

**Integration**:
- New files: `voiceline_mode_earphone_mic.c/h`
- Uses: `inversion_port.c/h` (required)

### Open Questions

- [ ] **Volume Level**: Optimal volume for different devices?
- [ ] **Physical Mount**: Best way to secure earphone to microphone?
- [ ] **AEC Tuning**: How aggressive for acoustic coupling?

---

## Next Steps

1. Review requirements and specifications
2. Say "requirements approved" when ready
3. Say "specs approved" to move to implementation planning
4. Create implementation plan (03-plan.md)
5. Begin implementation

---

*Created by /sdd - Earphone-to-microphone acoustic coupling with InversionPort*
