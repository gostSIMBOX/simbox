# Duplicates Archive

This directory contains archived flow directories that were merged into other flows.

## Purpose

When duplicate or overlapping flows are detected:
1. Content is merged into the more complete/primary flow
2. The less complete flow is moved here for archival
3. A `MERGED.md` file documents what was transferred

## Archived Flows

| Flow | Type | Merged Into | Date |
|------|------|-------------|------|
| - | - | - | - |

*No flows archived yet*

## Restoration

To restore an archived flow:

```bash
mv flows/duplicates/[FLOW-NAME]/ flows/[FLOW-NAME]/
```

Then revert the merge changes in the primary flow using git history.

## MERGED.md Structure

Each archived flow contains a `MERGED.md` file with:
- Original flow information
- Merge reason
- Content transferred (requirements, specifications, etc.)
- Files archived
- References updated
- Rollback instructions

---

*Created: 2026-03-04*
*Managed by /duplicates command*
