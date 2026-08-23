# Merged into [PRIMARY-FLOW-NAME]

**Date**: [YYYY-MM-DD]
**Merged by**: /duplicates command

---

## Original Flow Information

- **Name**: [FLOW-NAME]
- **Type**: [SDD/DDD/TDD/VDD/ADR]
- **Original Location**: `flows/[original-path]/`
- **Created**: [DATE]
- **Last Updated**: [DATE]

---

## Merge Reason

[ ] Duplicate functionality
[ ] Overlapping requirements
[ ] Consolidation of similar specs
[ ] Other: [describe]

**Primary flow**: `flows/[PRIMARY-FLOW-NAME]/`

**Rationale**: [Why this flow was chosen as duplicate instead of primary]

---

## Content Transferred

### Requirements

- [ ] FR-X: [Requirement title]
- [ ] FR-Y: [Requirement title]
- [ ] Other unique requirements

### Specifications

- [ ] Section X.Y: [Section title]
- [ ] Appendix: [Appendix title]
- [ ] Other unique specifications

### Implementation Notes

- [ ] [Unique implementation considerations]

### Other Content

- [ ] [Any other unique content]

---

## Files Archived

| Original File | Status |
|---------------|--------|
| 01-requirements.md | Archived |
| 02-specifications.md | Archived |
| 03-plan.md | Archived |
| 04-implementation-log.md | Merged/Archived |
| _status.md | Marked as MERGED |

---

## References Updated

- [ ] flows/sdd.md (if applicable)
- [ ] flows/ddd.md (if applicable)
- [ ] flows/tdd.md (if applicable)
- [ ] flows/vdd.md (if applicable)
- [ ] flows/adr-index.md (if applicable)
- [ ] flows/waterfall/_status.md
- [ ] Other: [list]

---

## Rollback Information

To restore this flow:

```bash
mv flows/duplicates/[FLOW-NAME]/ flows/[FLOW-NAME]/
# Then revert changes in primary flow
```

---

## Notes

[Any additional notes about the merge, content that wasn't transferred, or special considerations]

---

*This directory is archived. Refer to the primary flow for current specification.*
*Created by /duplicates command*
