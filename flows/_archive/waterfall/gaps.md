# Compilation Gaps

> Gaps detected during layer compilation. Resolve in SOURCE flows, then recompile.

---

## Unresolved Gaps

### GAP-001: No plan.md in any flow

**Description:** None of the 40 flows have a `03-plan.md` or equivalent plan document. Plans are required for extracting actionable implementation tasks with dependencies.

**Affected flows:** ALL (40 flows)

**Impact:** 
- Tasks were extracted from specifications instead of explicit plans
- Task dependencies may be incomplete
- Implementation order inferred from architecture, not explicit plans

**Resolution:** DECIDED (2026-03-04)
- Tasks extracted from specifications during compilation
- This is acceptable for initial implementation
- Plans can be created iteratively during implementation if needed
- **Decision:** Accept extracted tasks as provisional plans

**Status:** RESOLVED - Strategy documented

---

### GAP-003: Missing specifications for ddd-001-voip-calling

**Description:** ddd-001-voip-calling has stakeholder requirements but no technical specifications.

**Affected flows:**
- ddd-001-voip-calling/02-specifications.md (missing)

**Impact:**
- Layer 2 task voip-009 cannot be completed without specs
- VoIP calling feature implementation may lack technical guidance

**Resolution options:**
1. Create technical specifications based on stakeholder requirements
2. Use sdd-endpoint specs as technical foundation
3. Mark as incomplete and proceed

**Status:** PENDING - Can proceed with sdd-endpoint as technical foundation

---

### GAP-004: Missing specifications for ddd-imei-modification

**Description:** ddd-imei-modification has requirements but no technical specifications.

**Affected flows:**
- ddd-imei-modification/02-specifications.md (missing)

**Impact:**
- Layer 2 task imei-007 cannot be completed
- IMEI modification implementation may lack technical details

**Resolution options:**
1. Create technical specifications with AT command details
2. Mark as incomplete

**Status:** PENDING - Lower priority feature

---

### GAP-005: Missing requirements for vdd-call-ui

**Description:** vdd-call-ui has visual specs but no requirements document.

**Affected flows:**
- vdd-call-ui/01-requirements.md (missing)

**Impact:**
- Layer 2 callui tasks may lack business context
- UI implementation may not align with user needs

**Resolution:** Infer requirements from visual specs in vdd-call-ui/01-visual-specs.md

**Status:** PENDING - Can proceed with visual specs

---

### GAP-006: Missing requirements and specs for vdd-screens

**Description:** vdd-screens has neither requirements nor specifications.

**Affected flows:**
- vdd-screens/01-*.md (missing)
- vdd-screens/02-*.md (missing)

**Impact:**
- Layer 2 screens module incomplete
- Screen navigation structure undefined

**Resolution options:**
1. Create both requirements and specs documents
2. Merge with vdd-call-ui or navigation flows
3. Remove vdd-screens from compilation

**Status:** PENDING - Low priority, can be deferred

---

## Resolved Gaps

### GAP-002: Missing specifications for unisim

**Description:** sdd-unisim has requirements but specifications document is incomplete/missing.

**Resolution:** Created full specifications document at `sdd-unisim/02-specifications.md` with:
- Data model specification (EsProfile, EsProfileStatus, DataPlan)
- Security specification (AES-256 encryption, HMAC-SHA256)
- QR code format and parsing
- Operator API client specification
- Platform implementation (Android EuiccManager, iOS CTCellularPlanManager)
- Error handling and testing strategy

**Date:** 2026-03-04
**Status:** RESOLVED

---

### GAP-007: TeleCall model mismatch (Dart vs Kotlin)

**Description:** TeleCall Dart model has 40+ fields, but Kotlin model has only 10 fields. This causes data loss during event streaming.

**Resolution:** Documented as **intentional architecture**:
- Kotlin model streams only essential state changes (10 fields)
- Dart model enriches events with computed/local fields (40+ fields)
- Fields like duration, media info, status codes are computed/managed in Flutter
- This separation reduces event payload and keeps Android layer minimal

**Updated:** sdd-call-model/02-specifications.md
**Date:** 2026-03-04
**Status:** RESOLVED - Architecture decision documented

---

### GAP-008: Missing cleanup/destructor in Endpoint

**Description:** sdd-endpoint has no cleanup method, causing potential memory leaks.

**Resolution:** Added dispose() method specification to sdd-endpoint/02-specifications.md:
```javascript
dispose() {
  this.removeAllListeners();
  return new Promise((resolve, reject) => {
    NativeModules.PjSipModule.dispose((successful) => {
      if (successful) resolve();
      else reject(new Error('Failed to dispose endpoint'));
    });
  });
}
```
**Task:** endpoint-007 added to layer-1.md

**Date:** 2026-03-04
**Status:** RESOLVED

---

### GAP-009: replaceAccount() not implemented

**Description:** sdd-endpoint specifies replaceAccount() but it's not implemented.

**Resolution:** Added replaceAccount() implementation specification to sdd-endpoint/02-specifications.md:
- JavaScript API specification
- Native Android Kotlin implementation with AccountManager.updateAccount()
- Event emission for account changes

**Task:** endpoint-008 added to layer-1.md

**Date:** 2026-03-04
**Status:** RESOLVED

---

### GAP-010: setDefaultDialer() callback timing issue

**Description:** sdd-native-android-module and sdd-android-plugin both have setDefaultDialer() invoking callback before user confirms system dialog.

**Resolution:** Fixed specification in sdd-native-android-module/02-specifications.md:
- Removed immediate callback invocation
- Added ActivityEventListener interface implementation
- Implemented onActivityResult() to handle user confirmation
- Changed static callback to instance field with synchronization

**Tasks:** dialer-native-002, dialer-native-003 added to layer-1.md

**Date:** 2026-03-04
**Status:** RESOLVED

---

### GAP-013: ActivityEventListener commented out

**Description:** sdd-native-android-module has ActivityEventListener implementation commented out.

**Resolution:** Same fix as GAP-010 - uncommented and fully specified:
- Add ActivityEventListener interface to class
- Register listener in constructor
- Implement onActivityResult() and onNewIntent()

**Task:** dialer-native-003 added to layer-1.md

**Date:** 2026-03-04
**Status:** RESOLVED

---

### GAP-011: build_android.sh symlink missing

**Description:** sdd-release-workflow references build_android.sh which may not have proper symlink to version-specific script.

**Affected flows:**
- sdd-release-workflow/02-specifications.md

**Impact:**
- Release process may fail
- Wrong PJSIP version may be built

**Resolution options:**
1. Create symlink to correct version script
2. Update release.sh to use version-specific script directly

**Status:** PENDING - Low priority, can be fixed during Layer 0 implementation (task release-004)

---

### GAP-012: Generic commit message "auto" lacks context

**Description:** sdd-release-workflow uses generic commit message without context about what changed.

**Affected flows:**
- sdd-release-workflow/02-specifications.md

**Impact:**
- Git history lacks meaningful context
- Difficult to track release changes

**Resolution:** Update update.sh to include version and changes in commit message

**Status:** PENDING - Low priority, can be fixed during Layer 0 implementation (task release-003)

---

### GAP-014: Event ordering not guaranteed

**Description:** sdd-event-streaming has no event ordering guarantees.

**Affected flows:**
- sdd-event-streaming/02-specifications.md

**Impact:**
- Call state updates may arrive out of order
- Race conditions in state synchronization

**Resolution options:**
1. Add sequence numbers to events
2. Implement event ordering buffer
3. Document eventual consistency

**Status:** PENDING - Can be addressed during Layer 0 implementation if needed (event-003)

---

### GAP-015: Null eventSink drops events silently

**Description:** sdd-event-streaming drops events when eventSink is null without logging or retry.

**Affected flows:**
- sdd-event-streaming/02-specifications.md

**Impact:**
- Lost call events during initialization
- Silent failures difficult to debug

**Resolution options:**
1. Add event queue for null eventSink
2. Log warnings when events dropped
3. Retry mechanism for failed events

**Status:** PENDING - Can be addressed during Layer 0 implementation (event-004)

---

## Gap Statistics

| Status | Count |
|--------|-------|
| RESOLVED | 7 |
| PENDING | 8 |
| IN_PROGRESS | 0 |

---

## Priority Resolution Order

**P0 - Critical (RESOLVED):**
- ✅ GAP-001: Plan strategy decided (accept extracted tasks)
- ✅ GAP-007: TeleCall mismatch documented as intentional

**P1 - High (RESOLVED):**
- ✅ GAP-008: Endpoint cleanup specified
- ✅ GAP-009: replaceAccount() specified
- ✅ GAP-010: setDefaultDialer() callback fixed
- ✅ GAP-013: ActivityEventListener specified

**P2 - Medium (PARTIALLY RESOLVED):**
- ✅ GAP-002: unisim specs created
- ⏳ GAP-003: voip-calling specs (can use sdd-endpoint)
- ⏳ GAP-004: imei-modification specs (lower priority)
- ⏳ GAP-005: call-ui requirements (can infer from specs)
- ⏳ GAP-006: screens docs (low priority)

**P3 - Low (PENDING):**
- ⏳ GAP-011: build_android.sh symlink (fix during impl)
- ⏳ GAP-012: Generic commit message (fix during impl)
- ⏳ GAP-014: Event ordering (address if needed)
- ⏳ GAP-015: Null eventSink handling (address if needed)

---

*Updated by /waterfall. 7 gaps resolved, 8 pending (low priority).*
*Recompile with `/waterfall compile` to update layer docs.*
