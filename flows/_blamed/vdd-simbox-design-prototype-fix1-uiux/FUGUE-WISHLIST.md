# Fugue wishlist — SimBox v2026

> Status: specification review  
> Catalog searched: full Fugue 3.5.6 3,570-icon inventory  
> Density rule: every resolved glyph must exist as the original 16×16 and matching 32×32 rebuild.

These slots intentionally remain text-only in the prototype until a semantically precise Fugue
glyph is selected or added. A merely similar hardware picture is not an acceptable fallback.

| Purpose / placement | Required meaning | Candidate variants | Recommended filename | Status / notes |
|---|---|---|---|---|
| SIM route | A removable subscriber identity module, not a handset | `card.png` — generic card; `mobile-phone.png` — handset/modem; `memory.png` — chip/RAM | `sim-card.png` *(proposed; not in archive)* | missing-upstream — no SIM-card glyph found after full-catalog search |
| Readers route | Physical SIM/smart-card reader | `drive.png` — generic drive; `scanner.png` — document scanner; `usb-flash-drive.png` — USB storage | `smart-card-reader.png` *(proposed; not in archive)* | missing-upstream — candidates misstate the hardware |
| Readers: KI Search | Search/extract the KI secret key | `key.png` — key only; `key--arrow.png` — key transfer, not search; `magnifier.png` — search only | `key--magnifier.png` *(proposed; not in archive)* | missing-upstream — use localized text with no misleading icon |
| Readers: APDU | Send an APDU command to a smart card | `card--arrow.png` — generic card transfer; `terminal--arrow.png` — terminal command; `card-import.png` — generic card import | `smart-card--arrow.png` *(proposed; not in archive)* | missing-upstream — no smart-card/APDU glyph found |

## Resolution rule

When artwork is added, it should follow Fugue's small hardware-object vocabulary and palette, use
`16×16` as the canonical source, provide a corresponding `32×32` density asset, retain the proposed
filename, and be clearly attributed as a NativeMind Fugue-style addition rather than upstream
Fugue. Until then, the accessible text label is the complete control.
