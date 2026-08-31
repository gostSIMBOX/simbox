# SDD: Magisk Voice Recording Integration - Status

**Type**: SDD (Spec-Driven Development)
**Module**: magisk-voice-recording
**Status**: DRAFT
**Created**: 2026-03-06

---

## Progress

- [x] Requirements document created (01-requirements.md)
- [x] Specifications document created (02-specifications.md)
- [ ] Implementation plan created (03-plan.md)
- [ ] Implementation started
- [ ] Tests created
- [ ] Documentation reviewed
- [ ] Approved for production

---

## Summary

This SDD documents the Magisk module that enables voice call recording from the Android phone line (radio interface) by:

1. **Granting Privileged Permissions**: CAPTURE_AUDIO_OUTPUT, READ_PRECISE_PHONE_STATE, MODIFY_PHONE_STATE
2. **Installing as System App**: Via Magisk's systemless framework
3. **Disabling Qualcomm Restrictions**: Via system properties (voice.record.conc.disabled=false)
4. **Enabling PJSIP Audio Capture**: VOICE_CALL, VOICE_UPLINK, VOICE_DOWNLINK sources
5. **Exposing Capabilities**: Via LineInfo model (canRecordVoiceToRadio, etc.)

---

## Key Components

| Component | File | Purpose |
|-----------|------|---------|
| Privapp Permissions | `system/etc/permissions/privapp-permissions-gateway.xml` | Grant privileged permissions |
| Module Metadata | `module.prop` | Magisk module info |
| Installation Script | `install.sh` | Module installation logic |
| Update Script | `META-INF/.../update-binary` | Magisk update framework |
| Build Script | `build.sh` | Package module |

---

## Capabilities Enabled

| Capability | Property | Default | With Magisk |
|------------|----------|---------|-------------|
| Record to Radio | `canRecordVoiceToRadio` | false | true |
| Get from Radio | `canGetVoiceFromRadio` | false | true |
| Write to Voice Comm | `canWriteToVoiceCommunication` | false | true |

---

## Permissions Granted

| Permission | Purpose | Protection Level |
|------------|---------|------------------|
| CAPTURE_AUDIO_OUTPUT | Capture voice call audio | privileged |
| READ_PRECISE_PHONE_STATE | Detailed phone state | privileged |
| MODIFY_PHONE_STATE | Call control | privileged |
| READ_LOGS | System logs | privileged |

---

## Dependencies

- **Magisk**: v20.0+ (version code 20000+)
- **Android**: 8.0+ (API 26+)
- **Hardware**: Qualcomm chipset (for restrictions disable)

---

## Open Questions

1. Should CallRecorder APK be included? (currently commented out)
2. Should system.prop be enabled for Qualcomm restrictions?
3. Should boot scripts be implemented?
4. How to handle legal compliance (call recording laws)?

---

## Next Steps

1. Review requirements and specifications
2. Create implementation plan (03-plan.md)
3. Implement Magisk module enhancements:
   - Enable system.prop for Qualcomm devices
   - Implement post-fs-data.sh for dynamic checks
   - Add installation logging
4. Test on target devices
5. Document device-specific workarounds

---

*Created by /legacy - DFS focus on Magisk voice telephony integration*
