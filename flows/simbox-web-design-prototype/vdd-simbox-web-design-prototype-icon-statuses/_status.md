# Status: vdd-simbox-web-design-prototype-icon-statuses

## Current Phase

REQUIREMENTS

## Phase Status

AWAITING REQUIREMENTS APPROVAL

## Last Updated

2026-09-02 by Codex

## Blockers

- Mandatory VDD gate: explicit requirements approval.

## Progress

- [x] Requirements drafted
- [ ] Requirements approved
- [ ] Visual mockups drafted
- [ ] Visual approved
- [ ] Specifications drafted
- [ ] Specifications approved
- [ ] Plan drafted
- [ ] Plan approved
- [ ] Implementation started
- [ ] Implementation complete
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

- Target: `design/simbox-web-design-prototype-v2026`.
- Scope: status-icon names, labels, tooltips and the Icons reference page across all tables.
- Semantic sources of truth: legacy admin/runtime code and `libsCpp/asterisk-chan-svistok/src`.
- Icon assets must follow the GostSimBox taxonomy and Fugue 16×16/32×32 density contract.
- Visual appearance alone is not sufficient evidence for a status meaning.
- Deep MAY/MON/MSM audit complete: call MAY, command MAY, command MON and MSM fallback are four
  separate semantic entries; MSM is not Multiple-SIM and automatic MON is disabled in legacy.
- Owner-confirmed global MON semantic: request asking another person to top up this SIM's balance;
  Beeline service detail is the free “Пополни мой счёт”.
- Owner-confirmed SOU semantic: internal call from one managed SIM to another managed SIM;
  incoming/outgoing assets represent the two call legs, not a SIM calling itself.
- BUSY legacy trace complete: active call-result renderer uses `recog_types/30.png`, derived from
  Fugue `cup-empty.png`; call BUSY, recognition 30 and live resource busy remain separate meanings.

## Fork History

N/A — new flow.

## Next Actions

1. Review the full icon/code/meaning checklist.
2. Wait for explicit `requirements approved` before Visual.
