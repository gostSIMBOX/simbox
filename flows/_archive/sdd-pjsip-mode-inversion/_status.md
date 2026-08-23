# SDD: PJSIP Mode Inversion (Right Channel) - Status

**Type**: SDD (Spec-Driven Development)
**Module**: pjsip-mode-inversion
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

Reusable PJSIP media port (`InversionPort`) that inverts the right audio channel for differential signaling. Used by hardware adapter integrations to prevent echo through phone echo cancellation.

### Key Design Insight (from user)

> "Нам от SIP поступает сигнал на проигрывание в телефонную линию. Если он моно, то мы проигрываем его в левый канал обычно, а в правый инвертировано. Если он стерео то проигрываем левый канал как есть, а правый инвертируем. Это даст то, что по факту в телефонную линию уйдет сложенный сигнал (казалось бы что сложенный сигнал L минус R должна уйти в линию пустота, но за счет того что в телефонах добавлено эхоподавление - из пустоты вычитается эхоподавление и по факту происходит именно проигрывание в телефонную линию). Ноухау с инвертированием правого канала нужен для того чтобы одновременно обратно в линию не уходил сигнал полученный с самой линии и не создавалось эхо."

---

## Current Phase: SPECIFICATIONS

### What Has Been Specified

**Architecture**:
- Custom `pjmedia_port` subclass (`InversionPort`)
- Factory function `create_inversion_port()`
- Reusable component for any audio path requiring differential signaling

**Audio Transformation**:
- **Mono Input**: `[L] → [L, -L]` (stereo expansion with inverted right)
- **Stereo Input**: `[L, R] → [L, -R]` (right channel inversion only)
- **Sample Rate**: Any rate supported (no restrictions)
- **Processing**: In-place for stereo, buffered for mono

**Memory Management**:
- **Pool Strategy**: Shared pool from media endpoint
- **Buffers**: Pre-allocated `conversion_buffer` (no runtime allocations)

**Integration**:
- New files: `inversion_port.c`, `inversion_port.h`
- Consumers: `sdd-voiceline-hardwarejack-mode`, `sdd-pjsip-mode-voiceline`

### Resolved Questions

- [x] **Audio Format**: Any sample rate ✓
- [x] **Pool Management**: Shared pool ✓
- [x] **Buffer Strategy**: Pre-allocated buffer ✓

### Open Questions

- [ ] **MAX_SAMPLES_PER_FRAME**: 1920 (48kHz @ 20ms) or different?
- [ ] **Error Propagation**: Passthrough on error?
- [ ] **Logging Level**: DEBUG for frame processing?

---

## Consumers

This inversion port is used by:

| SDD Flow | Description | Status |
|----------|-------------|--------|
| `sdd-voiceline-hardwarejack-mode` | TRRS/USB hardware adapter integration | In development |
| `sdd-pjsip-mode-voiceline` | Direct voice line calling | In development |

---

## Next Steps

1. Review requirements and specifications
2. Say "requirements approved" when ready
3. Say "specs approved" to move to implementation planning
4. Create implementation plan (03-plan.md)
5. Begin implementation

---

*Created by /sdd - Split from sdd-voiceline-hardwarejack-mode to separate inversion logic*
