# Requirements: simbox-app-channel-table-uiux

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-08-23
> **Extracted 2026-08-23 from `vdd-simbox-app-uiux` v1.3** (that flow's
> AC #8 amendment + CRITICAL product note) at Anton's explicit
> instruction — this is now the authoritative home for the "Каналы"
> table/view-mode work; `vdd-simbox-app-uiux` keeps only a forward
> reference. Nothing below is new content, only relocated — see that
> flow's `_status.md` for the extraction note.

## Problem Statement

`vdd-simbox-app-uiux` built `apps/simbox-app`'s base screens (Tasks
1-13: navigation shell, theme, four screens including a "Симки"
SIM-list screen with a GOSTSIMBOX-ADMIN dense table on desktop and a
card list on phone/tablet). During that flow, in response to a
clarifying question about where a "always show table view" toggle
should live, Anton redirected the whole screen's product framing —
what started as a small toggle-location question became a full
redesign: renaming the screen, introducing a dual view mode (grouped
by modem with expandable rows, or flat by SIM), and rejecting several
candidate terms ("Звонки", "Транк") before landing on "Каналы"
(Channels). This flow is the extracted, self-contained record of that
redesign and its implementation (originally Tasks 14-18 of
`vdd-simbox-app-uiux`'s plan).

## ⚠️ CRITICAL — PERMANENT PRODUCT NOTE (verbatim, do not delete)

Anton, 2026-08-23, in response to a toggle-location question in
`vdd-simbox-app-uiux` (quoted verbatim, in Russian, at his explicit
instruction — never delete or paraphrase away this note in any future
edit of this file or of `03-specifications.md`):

> Хороший вопрос. По сути дела эта страница вообще должна называться
> "Звонки" (фактически текущие + возможные). Звонки могут отображаться
> по модемам, по симкартам (выбор все симкарты, или только активные в
> модеме в текущий момент) или по линиям (например для модемов
> поддерживающие 2 линии). Запиши это дословно как особенно важное и
> никогда не удаляй в требования и в спецификации

English gloss (for readers who don't read Russian — the Russian above
remains the authoritative source, not this gloss): *Good question.
Essentially this page should actually be called "Звонки" (Calls) —
covering both actual/current calls and possible ones. Calls can be
displayed by modem, by SIM card (choice: all SIM cards, or only those
currently active in a modem), or by line (e.g. for modems supporting 2
lines).*

### Follow-up exchange (also verbatim, same permanence rule, 2026-08-23)

Claude asked whether "Звонки" (the reframed screen name) means renaming
the "Симки" tab, merging it with the existing "Звонки" (Операции) tab,
or a separate new screen. Anton:

> Переименовать/переосмыслить "Симки" в "Звонки"

Claude then asked what "возможные" (possible, as opposed to "текущие" /
current) calls means. Anton, redirecting the naming question itself
rather than answering directly:

> Может быть есть более правильный термин для "Звонки", например в
> английском (и это не к истории звонков)?

Claude proposed "Каналы"/"Channels" or "Линии"/"Lines" as candidate
screen names (reasoning: the screen isn't a call-history log, it's a
call-*readiness* state per modem/SIM/line; "Channels" matches
chan_dongle's own code-level terminology and GSM-gateway industry
usage — "N-channel gateway"). Anton:

> Может быть Транк (trunk). Как называется транк в котором только 1
> единица?

Claude explained that "trunk" in classical telephony denotes an
*aggregate, multiplexed* facility (e.g. an E1 trunk carrying 30
channels sharing one physical transport) — there is no standard name
for "a trunk of one," since "trunk" itself implies plurality; a single
call-capable path is just a "channel"/"line." Claude recommended
"Trunk" (if used at all) name the whole gateway/its SIP-facing
aggregate, not a per-modem or per-row concept. Anton:

> Тогда может быть Каналы (по симкам, по модемам, ...) А так же
> например у 1 модема может быть 2 транка (если внутри модема
> поддерживаются 2 линии одновременно.); А если у модема 2 симки, то
> является ли модем транком в котором 2 канала на каждую из симок?

Claude's answer (also load-bearing for the resolved model below): a
dual-SIM modem is **not** "a trunk with 2 channels" in the strict
sense — each SIM has its own independent radio path/identity, they
don't share a common multiplexed transport the way real trunk channels
(E1/PRI) do. More accurate: **a modem hosts 1 or more independent
channels**; "trunk," if ever needed, stays reserved for a different,
higher-level concept (the whole gateway's SIP-facing side) and is
**not used anywhere in this screen's UI**. Anton confirmed by proposing
the screen name directly:

> Может быть в таблицу к элементам (например к модему добавить
> дропдаун с раскрывашкой по модемам/по симкам?)

(asking whether expandable/collapsible rows — a modem row that
expands to reveal its channel rows — could serve the "by modem"
grouping, instead of/alongside a separate filter control). Claude
proposed the hybrid resolved below and confirmed it addresses the "all
SIM cards" case (some SIMs may not be seated in any modem right now —
e.g. a spare/tray SIM — so they have no modem row to nest under,
meaning a pure modem-rooted tree can't be the *only* view). Anton:

> Сохрани мои высказывания дословно и давай на данном этапе сделаем
> как ты видишь.

("Save my statements verbatim and let's go with what you [Claude]
think, at this stage" — the resolved model below is Claude's design
judgment call, explicitly authorized, not independently re-confirmed
line-by-line by Anton.)

## Resolved Design (Claude's judgment call, per Anton's explicit go-ahead above)

- **Screen renamed**: "Симки" → **"Каналы"** (Channels). "Звонки" (call
  log, under Операции) stays a **separate**, already-existing screen —
  not merged. "Модемы" (hub/port console) also stays separate — Каналы
  is about call-readiness per channel, Модемы is about physical
  device/hub management.
- **Domain model**: a **Modem** (physical device) hosts one or more
  independent **Channels** (a channel = one call-capable path, tied to
  one SIM, optionally distinguished further by **Line** for modems
  that support multiple simultaneous lines per SIM/slot). "Trunk" is
  **not used** anywhere in this UI — it doesn't cleanly map onto
  independent, non-multiplexed GSM channels; reserved (if ever needed)
  for a future, unrelated concept.
- **Default view — grouped by modem, expandable rows**: each modem is
  a parent row; expanding it reveals its channel(s) (1 for a normal
  modem, 2+ for dual-SIM/dual-line modems) as child rows, each showing
  its own call-readiness state. This is the primary, GOSTSIMBOX-ADMIN-
  styled dense-table view (`vdd-simbox-app-uiux`'s AC #3 still applies
  — same tokens, same `assets/adminka/`/`assets/fugue/` icons).
- **Secondary view — flat, by SIM (all)**: a flat list of every known
  SIM card, including ones not currently seated in any modem (e.g. a
  spare/tray SIM) — these have no parent modem row to nest under, so
  they cannot be represented in the modem-rooted tree above, which is
  why this needs to be a genuinely separate flat mode, not just a
  filter on the same tree. "Only active in a modem right now" (the
  other half of Anton's original SIM-filter framing) is the natural
  subset of this same flat view where `modem != null` — no separate
  third mode needed for that half.
- **By line**: handled by the same expand/collapse mechanism as
  channels — a multi-line modem's row expands to reveal its lines,
  exactly like channels (line and channel are the same tree level for
  this purpose; a "line" is just how a channel is identified/labeled
  when a modem has more than one simultaneous call path per SIM).

## Acceptance Criteria

### Must Have

1. **Added 2026-08-23, at Anton's explicit request** ("для консервативных
   пользователей" — for conservative users). **Given** `vdd-simbox-app-uiux`'s
   AC #3/#5 already require the GOSTSIMBOX-ADMIN dense table on desktop
   and a card view on phone/tablet (matching the 2026 prototype's own
   responsive design)
   **When** a user explicitly prefers the traditional dense-table layout
   they're used to from the 2015 admin panel, regardless of their current
   screen size
   **Then** Каналы exposes a user-facing toggle (Настройки → Интерфейс)
   that forces the GOSTSIMBOX-ADMIN dense table — same design tokens, same
   `assets/adminka/`/`assets/fugue/` icons as the desktop table, no
   simplified/reduced-column variant — on phone too, not just desktop.
   On narrower viewports the table keeps its fixed desktop-width
   columns and scrolls horizontally (matches the DS's own "CSS grid + one
   scroller" rule — confirmed by Anton 2026-08-23). The toggle's setting
   persists across app restarts (a genuine user preference, not
   ephemeral UI state). The card view remains the default on
   phone/tablet; this is an opt-in override, not a replacement of the
   existing responsive default — confirmed with Anton directly (the
   alternative read, "just tighten wording for desktop fidelity," was
   explicitly not what was meant).

2. **Given** the Resolved Design above
   **When** the Каналы screen is specified/built
   **Then** it supports both view modes (По модемам — expandable
   modem→channel/line rows; По SIM, все — flat) via a segmented
   switcher, on desktop and (when the AC #1 toggle is on) phone.

3. **Given** the domain-model finding above (a dual-SIM/dual-line
   modem is not a "trunk")
   **When** any UI copy, code identifier, or documentation for this
   screen is written
   **Then** "Транк"/"Trunk" is never used to describe a per-modem or
   per-row concept in this screen's UI or its supporting code.

### Won't Have (This Iteration)

- Extending the table-view-anywhere toggle to the Модемы screen —
  discovered during implementation that Модемы's real tablet/desktop
  layout is a flat list, not a dense table, so there's no existing
  table representation for the toggle to surface on phone. Scoped
  down to Каналы only; flagged as a legitimate future enhancement, not
  silently dropped. See `05-implementation-log.md`.
- По-SIM-все's "не в модеме" row for SIM cards not seated in any modem
  — needs `sdd-flutter_gsmsip-interface` to expose SIM-inventory-
  independent-of-modem data, which it doesn't today (see that flow's
  specifications addendum, added 2026-08-23). Ships seated-only until
  that lands.

## Constraints

- **Inherited from `vdd-simbox-app-uiux`**: design source of truth
  (`design/simbox-app-maket-v2026` + `design/nativemind-designsystem-v1.8`),
  Linux-desktop-first platform scope, per-glyph asset vendoring — this
  flow doesn't restate them, just builds on the same base screens that
  flow already shipped.
- **Shared font-asset blocker**: `vdd-simbox-app-uiux`'s SF Pro Text
  TTF files are invalid (GitHub HTML pages, not fonts) — this flow's
  UI is built on the same app, so final visual-fidelity sign-off is
  gated on the same resolution (valid licensed fonts or an approved
  platform-native fallback). Does not block writing/testing code — see
  `_status.md`.

## Open Questions

- [x] **Resolved by Anton (2026-08-23)**: the dense table scrolls
      horizontally on phone when forced on — same fixed desktop-width
      columns, same GOSTSIMBOX-ADMIN design/icons, just a narrower
      viewport with a horizontal scroller. No reduced/adaptive column
      variant.
- [x] **Resolved 2026-08-23 via the CRITICAL note's follow-up
      exchange and Resolved Design above**: the "Симки" tab is
      renamed/reconceived as **"Каналы"** (not merged with the
      existing "Звонки"/Операции tab, not a separate new screen).
      "Trunk" terminology is explicitly rejected for this UI. The
      GOSTSIMBOX-ADMIN dense table remains the right presentation,
      extended with expandable modem→channel/line rows plus a
      separate flat by-SIM(all) mode. "Возможные" (possible) calls
      turned out to be a naming red herring, not a literal
      requirement — the resolved framing is "channel call-readiness
      state," not a distinct possible-vs-current call type; if a real
      "possible but not yet placed call" concept turns out to be
      needed later, it wasn't specified here and should be raised
      fresh, not assumed from the original phrasing.

## References

- `vdd-simbox-app-uiux` — parent flow, source of the base screens this
  work extends and of the extraction note in its `_status.md`.
- [[sdd-flutter_gsmsip-interface]] — carries the SIM-inventory-
  independent-of-modem follow-up (both copies, `libsFlutter/flutter_gsm/
  flows/` and `libsFlutter/flutter_gsmsip/flows/`).
- `design/nativemind-designsystem-v1.8/readme.md` — GOSTSIMBOX-ADMIN
  dense-table guidance this screen's table styling follows.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-08-23 (as `vdd-simbox-app-uiux` v1.3's AC #8
      amendment, before extraction into this flow)
- [x] Notes: Content unchanged by the extraction — this is the same
      approved requirement, relocated.
