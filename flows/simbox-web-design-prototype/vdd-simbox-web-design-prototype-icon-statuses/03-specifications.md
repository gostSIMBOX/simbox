# Specifications: Icon statuses and tooltips

> Version: 2.0
> Status: APPROVED
> Last Updated: 2026-09-02
> Requirements: [01-requirements.md](01-requirements.md)
> Visual: [02-visual.md](02-visual.md)

## Overview

Visual 2.0 preserves the current Icons page composition. Implementation corrects labels/tooltips
without adding, removing, moving or replacing any existing legend tile. A compact shared
terminology catalog prevents the corrected meanings from drifting between operational table
tooltips, the existing icon legend and the new separate Glossary page.

The semantic manifest below remains the source for corrected wording, but it does not drive a new
search/filter UI and does not cause missing historical icons to be inserted into the current
legend. Runtime telephony, selection and server classification behavior remain unchanged.

## Affected Systems

| System | Impact | Notes |
|--------|--------|-------|
| `lib/data/terminology.dart` | Create | Localized short labels, full tooltips and glossary definitions keyed by stable term ID |
| `lib/data/icon_map.dart` | Modify | Keep existing lookup functions/assets; replace incorrect hard-coded text with shared term references |
| `lib/data/icons_catalog.dart` | Modify | Keep every current group/item in the same order; replace pipe strings with typed items referencing shared terms |
| `lib/pages/icons_page.dart` | Modify | Text-only visual changes plus typed item access; preserve containers, padding, Wrap and 190px tiles |
| `lib/data/glossary_catalog.dart` | Create | Ordered glossary groups containing term IDs only; definitions remain in terminology catalog |
| `lib/pages/glossary_page.dart` | Create | Separate grouped term/definition reference screen from Visual 2.0 |
| `lib/state/app_state.dart` | Modify | Add `AdmPage.glossary` only; no operational state changes |
| `lib/main.dart` | Modify | Route `AdmPage.glossary` to `GlossaryPage` |
| `lib/widgets/sidebar.dart` | Modify | Append Glossary after Icons with Fugue `book-open-list.png` |
| `assets/fugue/` | Add pair | Vendor canonical `book-open-list.png` at 16×16 and `2.0x/` 32×32 |

## Data Models

### Shared terminology

```dart
typedef LocalizedText = Map<String, String>; // en, th, ru, hi, zh

enum TermConfidence { confirmed, derived, historical, unresolved }

class TermDefinition {
  final String id;                 // stable: qos.goo, im.primary, call.end.remote
  final LocalizedText shortLabel;  // compact tile/table label
  final LocalizedText tooltip;     // full context-correct explanation
  final LocalizedText? definition; // Glossary body; null for non-glossary decoration
  final String? formula;           // raw formula, never translated
  final List<String> aliases;      // raw/legacy names
  final TermConfidence confidence;
}
```

English is the default/fallback. Raw codes, filenames and formulas are not translated.

### Existing icon legend data, typed without changing composition

```dart
class IconLegendItem {
  final String file;   // unchanged current asset path
  final String code;   // unchanged/normalized visible raw code
  final String termId; // resolves label + tooltip
}

class IconGroup {
  final LocalizedText title;
  final String path;
  final List<IconLegendItem> items; // exact current order and count
}
```

`IconsPage._group()` and `_tile()` retain their existing widget tree. `_tile()` changes only from
splitting a pipe string to reading fields and resolving `TermDefinition`. Tooltip output remains:
`<code> — <full localized tooltip> (<file>)`.

### Glossary catalog

```dart
class GlossaryGroup {
  final String id;
  final LocalizedText title;
  final List<String> termIds;
}
```

Glossary groups contain only term IDs. They cannot duplicate definitions. Terms without a
source-backed definition remain explicitly unresolved or are omitted until resolved.

### Confirmed formula terms

```text
ACD = total_billsec / total_answered
ASR = total_answered / total_calls * 100
GOO_ACD = 300 seconds
GOO_ASR = 80 percent
GOO = ACD >= GOO_ACD && ASR >= GOO_ASR
```

These formulas are explanatory Glossary content. The prototype does not recompute or change the
server-provided `GOO` classification.

### Glossary navigation icon

Use canonical Fugue `book-open-list.png`, visually verified as an open reference book with a list.
Both upstream assets exist: original 16×16 and matching rebuild 32×32. Vendor only this density pair
under `assets/fugue/book-open-list.png` and `assets/fugue/2.0x/book-open-list.png`; render at the
existing 16 logical-pixel sidebar footprint.

## Semantic text manifest (all audited sections)

### Группа и расписание (`groupSchedule`)

| ID suffix | Asset | Raw condition | Label (RU) | Kind |
|---|---|---|---|---|
| working | play.png | 100–299 | В работе | Live |
| pauseWorkday | pause2.png+day_work.png | pause=1 | Пауза, рабочий день | Composite |
| pauseHoliday | pause2.png+day_holiday.png | pause=2 | Пауза, выходной | Composite |
| wakingWorkday | wake.png+day_work.png | pause=11 | Пробуждение, рабочий день | Composite |
| wakingHoliday | wake.png+day_holiday.png | pause=12 | Пробуждение, выходной | Composite |
| sleepingWorkday | sleep.png+day_work.png | pause=21 | Сон, рабочий день | Composite |
| sleepingHoliday | sleep.png+day_holiday.png | pause=22 | Сон, выходной | Composite |
| manualStop | stop.png | 300 | Ручная остановка | Raw |
| autoStopDatt | high_datt.png | 333 | Автостоп: высокий DATT/серия неудач | Raw |
| autoStopAcdl | low_acdl.png | 334 | Автостоп: низкий ACDL | Raw |
| autoStopBalanceSms | blocked_balance.png | 335 | Блок по SMS о балансе (**или** голосовое распознавание — Legacy Addition 1.8) | Raw |
| autoStopSimBlocked | simblocked.png | 336 | SIM заблокирована (**или** голосовое распознавание — Legacy Addition 1.8) | Raw |
| stopOther3xx | stop.png | 3xx прочие | Другая стоп/сервисная группа | Raw |
| lowBalance4xx | low_balance.png | 4xx | Низкий баланс | Raw |
| blocked5xx | blocked.png | 5xx | Заблокирована | Raw |
| unknownGroup | state/-1.png | G? | Группа неизвестна | Historical |

### Звонок: направление/процесс/результат (`callLiveResult`)

| ID suffix | Asset | Raw condition | Label (RU) | Kind |
|---|---|---|---|---|
| in | state_in.png | I | Входящий | Raw |
| out | state_out.png | O | Исходящий | Raw |
| liveDial | state/state_dial.png | DIAL | Набор номера | Live |
| liveRing | state/state_ring.png | RING | Ringback | Live |
| liveActive | state/state_active.png | ACTIVE | Разговор активен | Live |
| liveWait | state/state_wait.png | WAIT | Ожидание/cooldown | Live |
| sou | state/state_sout.png | SOU | Внутренний звонок между SIM | Classification |
| souIn | state/state_sout_in.png | SOU+I | SIM-to-SIM, принимающая сторона | Classification |
| souOut | state/state_sout_out.png | SOU+O | SIM-to-SIM, инициирующая сторона | Classification |
| resultAnswer | state/state_active.png | ANSWER | Звонок принят | Result |
| resultNoAnswer | state/state_dial.png | NOANSWER(_USERALERTING) | Без ответа | Result |
| resultBusy | **cup-empty (Fugue)** = recog_types/30.png | DIALSTATUS=BUSY | Абонент занят · обычно CC_CAUSE=17 | Result — shares asset with `recognition.busyTone`, see note |
| resultFailedUnknown | state/-1.png | FAILED/UNKNOWN | Ошибка/не классифицирован | Result |
| endPartyUnknown | state/end_party/-1.png | EP=-1 | Источник не определён | Raw |
| endPartyUs | state/end_party/1.png | EP=1 | Завершено нами | Raw |
| endPartyRemote | state/end_party/2.png | EP=2 | Завершено удалённой стороной | Raw |
| endPartyNetwork | state/end_party/3.png | EP=3 | Завершено сетью | Raw |

### Модем, SIM, сеть (`modemSimNetwork`)

| ID suffix | Asset | Raw condition | Label (RU) | Kind |
|---|---|---|---|---|
| cfunOn | p-on.png | CFUN=1 | Полный рабочий режим | Raw |
| cfunOff | p-off.png | CFUN=5 | Модем offline | Raw |
| cfunSimRemoved | state/cfun/4.png | CFUN=4 | SIM удалена (готовится CFUN=6) | Raw |
| cfunResetting | state/cfun/6.png | CFUN=6 | Перезапуск/reset | Raw |
| simstNotReady | state/simst/0.png | SIMST=0 | SIM не готова | Raw |
| simstReady | state/simst/1.png | SIMST=1 | SIM присутствует | Raw |
| simstReady3 | state/simst/1.png | SIMST=3 | SIM присутствует (**must not disappear**) | Raw |
| simstPresent4 | state/simst/4.png | SIMST=4 | SIM присутствует | Raw |
| simstAbsent | state/simst/255.png | SIMST=255 | SIM отсутствует | Raw |
| pinRequired | state/simst/16.png | pinrequired (SIMST=0) | Требуется PIN | Composite |
| srvstNone | state/srvst/0.png | SRVST=0 | Нет сети | Raw |
| srvstUp | state/srvst/1.png | SRVST=1 | Сеть доступна | Raw |
| srvstSearching | state/srvst/2.png | SRVST=2 | Поиск сети | Raw |
| srvstNetworkNoSim | state/srvst/112.png | SRVST=1 + invalid SIM | Сеть без валидной SIM | Composite |
| unknownRaw | state/-1.png | CFUN?/SIMST?/SRVST? | Неизвестное значение | Historical |

### Классификация исходящего вызова (`outgoingSourceClass`) — call attempt plus selected-SIM live alias (Legacy Addition 1.9)

| ID suffix | Asset | Raw condition | Label (RU) | Kind | Confidence |
|---|---|---|---|---|---|
| vip | qos/ivip.png | VIP | Доверенный источник | Classification | confirmed |
| goo | qos/igoo.png | GOO | Хорошая история соединений: ACD ≥300 с, ASR ≥80% | Classification | owner-confirmed formulas, constants and inclusive boundaries |
| nor | qos/inor.png | NOR | Известный номер, нормальные показатели | Classification | confirmed |
| bad | qos/ibad.png | BAD | Известный номер, плохие показатели | Classification | confirmed |
| new_ | qos/inew.png | NEW | Номер вне списков/истории | Classification | confirmed |
| nos | qos/inos.png | NOS | Сервер не ответил | Classification | confirmed |
| nec | qos/inec.png | NEC | NEW + капча пройдена | Classification | confirmed (Legacy Addition 1.6) |
| ne0 | qos/ine0.png | NE0 | *(producer commented out — unreachable today)* | Historical | unresolved-live-path |
| nem | qos/inem.png | NEM | *(producer commented out — unreachable today)* | Historical | unresolved-live-path |
| rob | qos/irob.png | ROB | Подозрение на автоматизацию | Classification | confirmed |
| blo | qos/iblo.png | BLO | Усиленная блокировка | Classification | confirmed |
| imo | (needs asset check) | IMO | IM-связанный класс запроса | Classification | unresolved |
| sys | (needs asset check) | SYS | Системный класс (не биллится, `billing_pay=0`) | Classification | confirmed |

Every entry carries `callLog` context for its raw string. Entries with a numeric selector code
also carry `sims.io.outgoing`; the winning SIM receives that numeric code in
`sim/state/<IMSI>.qos`. Live numeric `0` is labelled conservatively because it cannot distinguish
`NOS` from `SYS` without the separate billing/raw-call context.

### Давность предыдущего соединения (`incomingRecency`) — caller number + receiving SIM

| ID suffix | Asset | Raw condition | Label (RU) | Kind |
|---|---|---|---|---|
| very | qos/very.png | VERY (< 4 мин) | Очень недавно | Derived |
| fast | qos/fast.png | FAST (< 30 мин) | Недавно | Derived |
| slow | qos/slow.png | SLOW (≥ 30 мин) | Давно | Derived |
| never | qos/never.png | NEVER | Не было | Derived |
| spam | spam.png | SPAM | Подозрительно | Derived |
| souMarker | state/state_sout.png | SOU (same file) | Внутренний SIM-to-SIM | Classification |

`contexts: ['sims.io.incoming', 'incomingAutomation']`. Tooltip wording identifies the pair:
“Предыдущее соединение этого звонящего номера с этой SIM …”. The request supplies normalized
`CALLERID(num)` and the receiving `DONGLEIMSI`; exact server-side database semantics remain
unresolved because `conn_getstat.php` is outside this checkout.

### CAPTCHA (`captcha`)

| ID suffix | Asset | Raw condition | Label (RU) | Kind |
|---|---|---|---|---|
| capOk | qos/capok.png | CAP-OK | Капча пройдена | Result |
| capNew | qos/capnew.png | CAP-NEW | Новая/необработанная капча | Live |
| capFail | qos/capfail.png | CAP-FAIL | Капча не пройдена | Result |
| pal | qos/ipalevo.png | PAL | *(открытый вопрос — нормальное имя не найдено)* | Historical |

### Специальные режимы (`specialMode`)

| ID suffix | Asset | Raw condition | Label (RU) | Kind |
|---|---|---|---|---|
| no | state/-1.png | NO | Обычный звонок | Raw |
| pre | spec/pre.png | PRE | Предобработка | Capability |
| pos | spec/pos.png | POS | Постобработка | Capability |
| loc | spec/local.png | LOC | Локальный маршрут | Classification |
| lo2 | spec/local2.png | LO2 | Локальная сервисная операция | Classification |
| forwarding | spec/forwarding.png | FOR | Переадресация | Live |
| inWait | spec/in_wait.png | WAI | Ожидание входящего | Live |
| inSound | spec/in_sound.png | SPE | *(открытый вопрос — точное имя)* | Historical |
| carousel | spec/carousel.png | CAROUSEL | Карусельная маршрутизация | Classification |
| inter | conn.png | INTER | Interconnect-звонок | Classification |
| notVip | spec/notvip.png | NOTVIP | Политика «не VIP» | Capability |
| nav | spec/nav.png | NAV/30 | *(открытый вопрос — точное имя)* | Historical |
| mag | spec/mag.png | MAG/200 | *(открытый вопрос — точное имя)* | Historical |

### MAY / MON / MSM — четыре отдельных концепции (`mayMonMsm`, Legacy Addition 1.1)

| ID | Asset | Raw condition | Label (RU) | Kind |
|---|---|---|---|---|
| call.special.shortBeacon | spec/may.png | spec=MAY/20 | Короткий звонок-маяк | Live |
| command.operatorCallbackRequest | may.png | send_may | Операторский запрос перезвонить | Action |
| command.balanceTopUpRequest | mon.png | send_mon | Просьба пополнить счёт | Action |
| command.callbackSmsFallback | msm.png | MSM | SMS с просьбой перезвонить (MAY fallback) | Action |

### Привязка SIM к номеру (`imAffinity`)

| ID suffix | Asset | Raw condition | Label (RU) | Kind |
|---|---|---|---|---|
| ima | im/ima.png | IMA | Историческое: активный producer/consumer не найден | Historical |
| imn | im/imn.png | IMN | История пуста; разрешена любая SIM | Classification |
| imb | im/imb.png | IMB | Эта SIM первая/основная в истории номера B | Classification |
| imc | im/imc.png | IMC | Эта SIM есть в истории номера B, но не первая | Classification |
| imd | im/imd.png | IMD | Этой SIM нет в истории; другие есть, новая SIM разрешена | Classification |
| ime | im/ime.png | IME | Этой SIM нет в истории; разрешены только перечисленные SIM | Classification |

### Распознавание (`recognition`, Legacy Addition 1.8 — two mechanisms)

| ID suffix | Asset | Raw condition | Label (RU) | Kind | Confidence |
|---|---|---|---|---|---|
| silence | recog_types/10.png | REC=10 | Тишина (нет речи) | Result | confirmed |
| answeringMachine | recog_types/20.png | REC=20 | Автоответчик | Result | confirmed |
| busyTone | recog_types/30.png (shares asset w/ `call.result.busy`) | REC=30 | Акустический сигнал «занято» | Result | confirmed — likely acoustic, not spoken phrase |
| voice | recog_types/50.png | REC=50–59 | Обнаружена речь | Result | confirmed |
| technical90 | recog_types/90.png | REC=90 | *(код вычисляется на simserver — не разрешено)* | Historical | unresolved (server-side) |
| technical91 | recog_types/91.png | REC=91 | *(код вычисляется на simserver — не разрешено)* | Historical | unresolved (server-side) |
| technical92 | recog_types/92.png | REC=92 | *(код вычисляется на simserver — не разрешено)* | Historical | unresolved (server-side) |
| success | recog_types/100.png | REC=100 | Успешный результат | Result | confirmed |
| ownBalanceInsufficient | recog_types/110.png | REC=110–119 | Своя SIM: недостаточно средств (объявление оператора) | Result | confirmed (`recog_types_sim.php` comment+phrases) |
| ownNumberBlocked | recog_types/120.png | REC=120–129 | Своя SIM: номер заблокирован (объявление оператора) | Result | confirmed (`recog_types_sim.php` comment+phrases) |

### Сигнал (`signal`)

| ID suffix | Asset | Raw condition | Label (RU) |
|---|---|---|---|
| rssi0-4 | rssi/rssi-{0-4}.png | CSQ 0 / 1–6 / 7–14 / 15–19 / 20–31 | Derived signal bucket, exact boundaries per Requirements |

### Оборудование/USB, Diagmode, SMS/USSD/политики, Направления, Fugue-действия

Unchanged in substance from the base Requirements/prior chat listing. Only entries already present
in the current Icons legend remain in its current group/order. The broader manifest still corrects
operational table tooltips, but does not insert additional tiles into the legend.

## Behavior Specifications

### Happy Path

1. Existing `Ico.*()` functions keep their runtime lookup and asset behavior, but resolve corrected
   text by stable `termId`.
2. `IconsPage` renders the same groups, tiles, order and geometry as before. It resolves visible
   label and tooltip from the same terminology catalog.
3. `GlossaryPage` renders independent grouped term/definition rows by term ID.
4. Sidebar opens Icons and Glossary as separate destinations.

### Edge Cases

| Case | Trigger | Expected Behavior |
|---|---|---|
| Unknown current table value | `Ico.*()` has no known mapping | Preserve current explicit unknown asset/raw state; never show an empty tooltip |
| Historical/unresolved icon tile | current legend already contains IMA, PAL, REC 90/91/92, etc. | Keep tile and icon in place; label/tooltip says historical or unresolved |
| Same asset has two meanings | BUSY call result versus recognition 30 | Context-specific term IDs and tooltips; no asset replacement or tile insertion |
| Missing locale string | selected locale is not present | Fall back to English; raw code remains unchanged |
| Long legend label | current 190px tile cannot show full string | Keep current ellipsis; full corrected explanation is available in Tooltip |
| Glossary definition unresolved | abbreviation exists but source-backed meaning does not | Mark unresolved or omit; never fill from abbreviation alone |
| Glossary narrow width | definition does not fit beside term | Stack definition below term without horizontal scrolling |

## Testing Strategy

### Unit Tests

- [ ] Every `termId` referenced by icon map, legend or glossary resolves exactly once.
- [ ] Every current legend group retains the same item count, file sequence and raw-code sequence
      as the pre-change catalog snapshot.
- [ ] Every legend asset path resolves to an existing file under `assets/imgs/`.
- [ ] All glossary terms with formulas preserve the exact raw formula and localized definition.
- [ ] `GOO` tests assert inclusive thresholds: ACD `>=300`, ASR `>=80`.
- [ ] English fallback is deterministic for all five supported locales.
- [ ] Fugue `book-open-list.png` exists as 16×16 and 32×32 with identical filename.

### Manual Verification

- [ ] Before/after screenshots show identical Icons page controls, cards, tile order and wrapping;
      only textual content changes.
- [ ] Hover every Icons tile: tooltip is `<code> — <meaning> (<file>)` and is not stale.
- [ ] Glossary appears immediately after Icons in the sidebar and opens a separate page.
- [ ] Glossary narrow layout stacks term/definition cleanly.
- [ ] Representative operational table icons use the same corrected term text as Icons/Glossary.
- [ ] `flutter analyze` / existing test suite pass.

## Open Design Questions

Carried forward, unresolved, from Requirements — not blocking this doc's approval:

- [ ] `PAL` operator-facing name.
- [ ] Exact names for `NAV`/`MAG`/`SPE`.
- [ ] `REC=90/91/92` and `110-119`/`120-129` exact subcode meanings (server-side, may never be
      resolvable from this repo alone).
- [ ] `IMO` wording remains unresolved; Visual 2.0 forbids adding/replacing a legend asset.

---

## Approval

- [x] Reviewed by: Anton Dodonov
- [x] Approved on: 2026-09-02
- [x] Notes: Preserve current Icons layout/text-only corrections; separate shared-term Glossary.
