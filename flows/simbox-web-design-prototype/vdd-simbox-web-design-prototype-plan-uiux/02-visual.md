# Visual Mockups: Plans editor UI/UX

> Version: 1.0
> Status: APPROVED
> Last Updated: 2026-09-02

## Overview

ASCII mockups for the Plans workspace — a registry+detail master-detail layout following the
already-shipped Наборы команд (`lib/features/command_sets/`) and Направления
(`lib/features/zones/`) precedents: searchable list on the left, semantic-section detail pane on
the right, one draft per plan governed by a shared Save/Cancel bar, responsive narrow-width
fallback. New to this flow: a dismissible Explanation Banner above the workspace, and a
Directions section whose route/group context is read-only and sourced live from the Zones
registry (never a second copy of that data).

---

## Screen: Plans workspace — wide layout, banner open, plan selected

```
+--------+----------------------------------------------------------------------------+
|SIDEBAR |  Планы                                                                     |
| ...    +----------------------------------------------------------------------------+
|[x]Планы|  +------------------------------------------------------------------------+ |
| ...    |  | (i) Пояснение                                                    [x]   | |
|        |  |     Планы нужны для 2 целей: 1) автоматизация хитрых запросов          | |
|        |  |     (например, вместо *100# — кнопка Get balance); 2) групповая        | |
|        |  |     установка параметров симок. Допустимо использовать план default    | |
|        |  |     для любых симок, экспериментов и новых операторов.                 | |
|        |  |                                                                          | |
|        |  |     time_wake / time_sleep — когда симка спит/просыпается (час),       | |
|        |  |     минуты выбираются алгоритмом индивидуально для каждой симки.       | |
|        |  |     Если значение не в [0;23] — расписание выключено.                  | |
|        |  |                                                                          | |
|        |  |     Пауза между звонками: diff_slow — гарантированная пауза в любом    | |
|        |  |     случае; diff_min — пауза на все звонки; пауза на симку берётся      | |
|        |  |     как min(diff_min; diff_min_out если GOO).                          | |
|        |  |                                                                          | |
|        |  |     После изменения плана нужно выбрать симки на вкладке «Симки» и     | |
|        |  |     нажать «Восстановить параметры плана».                             | |
|        |  +------------------------------------------------------------------------+ |
|        |                                                                              |
|        |  +------------------+  +--------------------------------------------------+ |
|        |  |Планы          [+]|  | tele2_spb_good                        [ico][≡]   | |
|        |  |[search______]    |  | набор: tele2_spb  ·  используется 6 симками       | |
|        |  |[Все наборы   v]  |  +----------------------------------------------------+ |
|        |  |-------------------|  | ▸ Идентичность и владение                        | |
|        |  |○default   (default)| | ▾ Ёмкость                                        | |
|        |  |------------------ | |   Макс. онлайн-симок      [ 5 ]                  | |
|        |  |●tele2_spb_good    | |   Макс. add/reserve        [ 1 ]                  | |
|        |  | tele2_spb  ·6 сим | | ▸ Режимы звонков и качество                       | |
|        |  |○tele2_spb_max     | | ▸ Тайминги и расписание                           | |
|        |  |○tele2_trash       | | ▸ Направления                                     | |
|        |  |... (33 всего)     | | ▸ Генерация входящих                              | |
|        |  |                   | | ▸ SMS и MAY/MON/MSM                               | |
|        |  +------------------+  +--------------------------------------------------+ |
+--------+----------------------------------------------------------------------------+
```

Registry rows show a radio-style selection dot, plan ID, and (for the selected/hovered row) its
command set + usage count. Filter row: search box + command-set dropdown filter (Acceptance
Criteria #4). Detail pane: header (ID, command set — directly editable per resolved Open
Question #3 — usage count, icon/menu for Clone/Delete), then collapsed accordion of the seven
semantic policy families (Editable Policy Families #1-7) — one open at a time or several, TBD in
Specifications; shown here with "Ёмкость" expanded as an example.

## Screen: Plans workspace — banner dismissed

```
+--------+----------------------------------------------------------------------------+
|SIDEBAR |  Планы                                                    [?]                |
| ...    +----------------------------------------------------------------------------+
|        |  +------------------+  +--------------------------------------------------+ |
|        |  |Планы          [+]|  | tele2_spb_good                        [ico][≡]   | |
|        |  |[search______]    |  | набор: tele2_spb  ·  используется 6 симками       | |
...
```

`[?]` sits to the right of the "Планы" title, same row, appears only while the banner is closed.
Clicking it reopens the exact same banner (Acceptance Criteria #26) — state is in-memory,
session-only, matching `navCompact`/`logOpen`'s existing pattern.

## Screen: Detail pane — "Идентичность и владение" expanded (command-set direct edit)

```
+----------------------------------------------------+
| ▾ Идентичность и владение                            |
|   ID плана            tele2_spb_good   (неизменяемый)|
|   Набор команд        [tele2_spb            v]       |
|   Приоритет           [ 5 ]                          |
|   PRO (routing tag)   [__________]  necessary only    |
|                        for direction algorithms P/p/v |
+----------------------------------------------------+
```

The "Набор команд" field is a live, directly-editable dropdown (not gated behind Clone, per
Acceptance Criteria #23) sourced from the live Command Sets registry (Acceptance Criteria #3) —
changing it re-parents this plan to a different command set immediately in the draft, no
separate flow. "ID плана" is shown but not editable (stable identity).

## Screen: Detail pane — "Направления" (Directions) section, read-only route context

```
+--------------------------------------------------------------------------+
| ▾ Направления                                                              |
|   Слот L1                                                                  |
|     алгоритм [D v]   различие [не учитывать v]   мягкий/жёсткий [40][80]   |
|     Маршруты, использующие этот слот (read-only, из Направления):          |
|       (ico) МегаФон СПб · NS101   (ico) МегаФон СПб · NS205                |
|       [показать все 4 →]                                                    |
|   Слот L2                                                                   |
|     алгоритм [> v]   ...                                                    |
|     Маршруты: нет данных для этого набора команд                            |
|   ...                                                                       |
|   ⚠ Слоты 0 и 5 — совместимость, не редактируются как обычные направления   |
+--------------------------------------------------------------------------+
```

Per-slot policy (alg/nodiff/limits) is editable — it's Plan's own data. The "Маршруты,
использующие этот слот" line underneath is **read-only**, pulled live from the selected plan's
command-set's zones (via the shared `ZoneController`/`GroupRule.limitSlot` match) — never a
second copy of zone/group data (Acceptance Criteria #24). "показать все N" expands inline or
opens a small popover with the full route list — never all 6,073 masks (Acceptance Criteria
#17). Slots 0/5 get an explicit compatibility note instead of a normal editable row (Legacy
Addition 1.1's slot 0/5 caveat).

## Screen: Create plan dialog (Clone / Blank)

```
+----------------------------------------------+
|  Новый план                                    |
|  ( ) Клонировать существующий                 |
|      Источник  [tele2_spb_good        v]       |
|  (•) Пустой                                    |
|                                                 |
|  ID плана (латиницей, уникальный) *            |
|  [____________________]                        |
|  Набор команд *                                |
|  [tele2_spb                v]                  |
|                                                 |
|                    [Отмена]   [Создать]         |
+----------------------------------------------+
```

Matches Наборы команд's create-dialog shape (`SegmentedButton`-style Clone/Blank choice, source
dropdown only shown when Clone is selected) — Clone remains the default/primary creation path
(Recommended Interaction Model), separate from the direct-edit decision for *existing* plans.

## Screen: Delete — blocked (plan still referenced)

```
+----------------------------------------------+
|  🔒 Удаление недоступно                        |
|  План «tele2_spb_good» используется 6 симками. |
|  Переназначьте эти симки на другой план,        |
|  прежде чем удалять «tele2_spb_good».           |
|                              [Закрыть]          |
+----------------------------------------------+
```

## Screen: Delete — allowed (confirmation)

```
+----------------------------------------------+
|  Удалить план?                                 |
|  «tele2_trash» не используется ни одной симкой.|
|                     [Отмена]   [Удалить]        |
+----------------------------------------------+
```

`default` never reaches either dialog — its delete action is disabled/absent entirely
(Acceptance Criteria #8, protected).

## Screen: Narrow window — stacked layout

```
+--------------------------------------------------+
| Планы                                    [?]       |
+--------------------------------------------------+
| (i) Пояснение (collapsed to 1 line + "ещё")  [x]   |
+--------------------------------------------------+
| (ico) [tele2_spb_good          v] [+]              |
+--------------------------------------------------+
| tele2_spb_good              [ico][≡]               |
| набор: tele2_spb · 6 симок                          |
|------------------------------------------------------|
| ▾ Ёмкость                                            |
|   Макс. онлайн-симок [ 5 ]                           |
| ▸ Режимы звонков и качество                          |
| ...                                                  |
+--------------------------------------------------+
```

Matches Command Sets' `narrow = constraints.maxWidth < 900` breakpoint: registry collapses to a
dropdown+add row; banner (if open) truncates to one line with an inline "ещё"/expand affordance
rather than consuming the whole narrow viewport (Acceptance Criteria #13, no hidden fields, no
page-level horizontal scroll).

---

## Flow: Explanation banner dismiss/reopen

```
[Banner open] --(click X)--> [Banner closed, "?" shown] --(click "?")--> [Banner open]
```

## Flow: Switching plans with unsaved edits

```
[Plan A, dirty draft] --(click Plan B)--> [Guard dialog: Continue editing / Discard and switch]
```

Identical shape to Наборы команд's `requestSetSelection`/Направления's `requestZoneSelection` —
same three-way choice, same wording pattern.

## Flow: Editing the command-set field

```
[Plan selected, "tele2_spb"] --(pick "beeline_spb" in dropdown)--> [Draft dirty, command-set
field shows "beeline_spb", usage-count/route-context in Directions section refresh to reflect
the new command-set's zones] --(Save)--> [Persisted; registry row's command-set label updates]
```

---

## Component: Registry row

```
○ plan_id                      <- unselected
  command_set · N симок
●●● plan_id                    <- selected, filled dot, bold
  command_set · N симок
```

## Component: Semantic section (collapsed / expanded)

```
▸ Раздел                        <- collapsed, one-line summary optional (Should Have)
▾ Раздел
  [field]  [field]  [field]
```

## Component: Route-context chip (Directions section, read-only)

```
(ico) Zone name · BillingCode+Group     <- e.g. "МегаФон СПб · NS101"
```

Same icon source as the Zones registry (`napravleine/*.png`) — visually ties this read-only
context back to the screen that actually owns it.

## Component: Explanation banner (open / closed)

```
Open:
+--------------------------------------------------------+
| (i) Пояснение                                     [x]  |
|     <4 paragraphs, verbatim copy from Requirements>     |
+--------------------------------------------------------+

Closed:
Планы                                              [?]
```

---

## Notes

- No always-visible ultra-wide grid anywhere in this flow (Won't Have) — every dense value
  lives inside a labeled, unit-bearing field in a semantic section, never a raw spreadsheet
  column.
- The Directions section is the one place this screen touches Zones data — always read-only,
  always live (not a copied snapshot), per Acceptance Criteria #16-22 and #24.
- Save/Cancel bar, dirty-draft guard, Clone/Blank creation, and delete-with-usage-check all
  reuse the exact interaction shapes already shipped in Наборы команд and Направления — no new
  interaction patterns invented for this flow beyond the Explanation Banner and the read-only
  route-context chip.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-02
- [x] Notes:
