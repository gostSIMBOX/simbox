# Visual Mockups: Icon legend and glossary

> Version: 2.0
> Status: APPROVED
> Last Updated: 2026-09-02

## Owner correction that supersedes Visual 1.0

The Icons page is **not redesigned into a searchable/filterable registry**. Preserve the current
page exactly as it exists in `design/simbox-web-design-prototype-v2026`:

- same sidebar item `Иконки`;
- same page padding and title card;
- same sequence of group cards;
- same group header with title and asset path;
- same `Wrap` of fixed-width icon tiles;
- same icon + visible label + raw code arrangement;
- same hover tooltip;
- same scrolling and responsive wrapping behavior.

Only textual content changes: page title/instruction, group names where misleading, visible labels,
raw-code notation and tooltip text. Every existing tile remains in its current position and group;
no icon tile is added, removed, moved or replaced in this flow.

Visual 1.0's search bar, filters, badges, expanded provenance rows, collapsible groups and mobile
filter popover are withdrawn.

## Naming

The screen is correctly described as an **icon legend**:

- Navigation remains: **Иконки** / **Icons**.
- RU page title: **Легенда иконок GostSimBox**.
- EN page title: **GostSimBox icon legend**.
- “Legend” maps a visible symbol/code to its meaning and is appropriate for this page.
- “Catalog” may remain an internal code/data name, but is less natural as the operator-facing
  title.

A **Glossary** is separate: it explains domain terms and formulas that can appear in many tooltips
but are not themselves icons. Examples: ACD, ASR, Number B, IM, END_PARTY, CFUN.

## Screen 1: Icons — preserved current layout

```text
+--------------------------------------------------------------------------------+
| Легенда иконок GostSimBox                                                      |
| Наведите указатель на иконку, чтобы увидеть код, значение и имя файла.          |
+--------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------+
| Группа и расписание                           imgs/ · group + pause             |
|--------------------------------------------------------------------------------|
| [ico] В работе       [ico] Пауза               [ico] Пробуждение               |
|       100–299              pause=1                   pause=11                   |
|                                                                                |
| [ico] Сон            [ico] Рабочий день         [ico] Выходной                 |
|       pause=21             day=1                      day=2                     |
| ...                                                                            |
+--------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------+
| Состояние звонка                              imgs/state/                       |
|--------------------------------------------------------------------------------|
| [ico] Разговор       [ico] Нет ответа           [ico] Вызов                    |
|       ANSWER               NOANSWER                  RING                       |
| ...                                                                            |
+--------------------------------------------------------------------------------+
```

This is the current card + `Wrap` + 190-logical-pixel tile composition. No new controls are added.

### Tile contract

```text
[16 px icon]  Operator-facing meaning
              RAW_CODE
```

At high pixel density the matching 32×32 asset renders inside the same 16-logical-pixel footprint.
The visible first line is a concise meaning; the second line is the untranslated raw code. Long
labels retain the current ellipsis behavior. The full meaning is always available in the tooltip.

### Tooltip contract

```text
GOO — Хорошая история соединений: ACD ≥ 300 с и ASR ≥ 80%. (qos/igoo.png)
```

Tooltip order stays compatible with the current implementation:

1. raw code;
2. corrected operator-facing explanation;
3. source asset filename in parentheses.

No source-code paths, confidence badges or long provenance blocks appear visually. Unresolved
entries say that the meaning is unresolved/historical instead of inventing a confident label.

## Screen 1 examples: corrected content, unchanged geometry

```text
+--------------------------------------------------------------------------------+
| Классификация номера B (QoS)                  imgs/qos/                         |
|--------------------------------------------------------------------------------|
| [VIP] Доверенная       [GOO] Хорошая история   [NOR] Обычная история            |
|       VIP                    GOO                     NOR                        |
|                                                                                |
| [BAD] Плохая история   [NEW] Новый номер       [NOS] Нет классификации          |
|       BAD                    NEW                     NOS                        |
|                                                                                |
| [NEC] NEW + CAPTCHA    [ROB] Робот/автоматиз.  [BLO] Блокировка                 |
|       NEC                    ROB                     BLO                        |
+--------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------+
| Связь SIM с номером B и распознавание          imgs/im · imgs/recog_types       |
|--------------------------------------------------------------------------------|
| [B] Первая SIM в истории   [C] SIM есть в истории   [N] История пуста           |
|     IMB                         IMC                       IMN                    |
|                                                                                |
| [D] Новая SIM разрешена    [E] SIM не разрешена     [A] Исторический IMA        |
|     IMD                         IME                       IMA                    |
|                                                                                |
| [10] Тишина                [20] Автоответчик          [30] Сигнал «занято»       |
|      10                         20                          30                   |
+--------------------------------------------------------------------------------+
```

The exact current icons remain. These examples demonstrate label correction only.

## Screen 1: narrow width

Current `Wrap` behavior remains the responsive design. Tiles move to the next row; their internal
geometry does not morph into another component.

```text
+---------------------------------------------+
| Легенда иконок GostSimBox                   |
| Наведите указатель на иконку...             |
+---------------------------------------------+
| Классификация номера B (QoS)                |
| imgs/qos/                                   |
|---------------------------------------------|
| [ico] Хорошая история    GOO                |
| [ico] Обычная история    NOR                |
| [ico] Плохая история     BAD                |
| [ico] Новый номер        NEW                |
+---------------------------------------------+
```

## Screen 2: separate Glossary

Add a separate adjacent navigation destination, not a mode/filter inside Icons:

```text
Sidebar
  ...
  Иконки
  [book-open-list] Глоссарий
```

The Glossary reuses the same title-card and group-card visual language. It is deliberately simple:
no icon is required for every term, and terms do not reuse status glyphs as decoration.

```text
+--------------------------------------------------------------------------------+
| Глоссарий SimBox                                                               |
| Термины, формулы и системные обозначения, используемые в интерфейсе.            |
+--------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------+
| Качество и статистика звонков                                                   |
|--------------------------------------------------------------------------------|
| ACD       Средняя длительность отвеченного звонка.                              |
|           total_billsec / total_answered                                        |
|                                                                                |
| ASR       Доля отвеченных звонков.                                               |
|           total_answered / total_calls × 100%                                   |
|                                                                                |
| GOO       Класс хорошей истории номера B: ACD ≥ 300 с и ASR ≥ 80%.              |
+--------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------+
| Номера и связь SIM                                                              |
|--------------------------------------------------------------------------------|
| Number A  Идентификатор/номер стороны A в контексте исходящего запроса.          |
| Number B  Номер назначения, по которому simserver хранит агрегированную историю.|
| IM        Связь кандидатной SIM с историей звонков на Number B.                  |
+--------------------------------------------------------------------------------+
```

### Initial glossary groups

1. Quality and call statistics: ACD, ASR, ACDL, DATT, PDD, PDDC, FAS.
2. Numbers and SIM identity: Number A, Number B, Number My, IMSI, IMEI, ICCID, Ki.
3. Call classification: QoS, GOO, NOR, BAD, NEW, NOS, VIP, ROB, BLO, NEC, IMO, SYS.
4. Multiple-SIM relationship: IM, IMA/IMB/IMC/IMD/IME/IMN.
5. Call lifecycle: DIALSTATUS, CC_CAUSE, END_PARTY, incoming/outgoing, SOU.
6. Modem/network: CFUN, SIMST, SRVST, RSSI, LAC, Cell ID.
7. Routing and configuration: DEF zone, `naprstr`, billing direction, Plan, Command set, Group.
8. Operator actions: MAY, MON, MSM, CAPTCHA.

Definitions follow confirmed legacy/owner evidence. Unresolved terms are marked unresolved rather
than completed from industry convention alone.

## Navigation flow

```text
Operational table --hover icon--> short tooltip
       |                               |
       +-- Sidebar: Icons ------------+--> full visual legend
       |
       +-- Sidebar: Glossary --------------> term/formula definition
```

There is no automatic cross-navigation requirement in this iteration. Icons and Glossary are two
independent reference screens accessible from the sidebar.

## States

### Icons

- Normal: current cards and tiles render with corrected text.
- Missing asset: current explicit unknown asset remains; tooltip includes raw code.
- Unresolved meaning: visible label says “Не определено”/“Историческое”; tooltip does not invent.
- Narrow: natural `Wrap`, as today.

### Glossary

- Normal: grouped term/definition rows.
- Missing translation: English fallback, following the app-wide localisation contract.
- Empty group is omitted; there is no empty card.
- Narrow: term appears above its definition, without horizontal scrolling.

## Non-goals

- No Icons-page search, filters, pills, badges, row expansion or collapsible groups.
- No visual redesign of Icons cards or tiles.
- No icon-tile additions, removals, replacements or rearrangement.
- No glossary definitions inferred solely from an abbreviation.
- No editing UI for either reference page.

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-02
- [x] Notes: Preserve current Icons layout; correct text only; separate Glossary approved.
