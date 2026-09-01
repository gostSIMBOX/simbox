# Requirements: SimBox design prototype — compact table actions UI/UX

> Version: 1.0  
> Status: REVIEW  
> Last Updated: 2026-09-01

## Problem Statement

В текущем `design/simbox-design-prototype/index.html` действия для операционных таблиц расположены после таблиц и собраны в крупные постоянно видимые карточки. Для сверхшироких SIM-таблиц это разрывает связь между выделением строк и командой, увеличивает прокрутку и расходует вертикальное пространство. Раскрытие обычным блоком также сдвинуло бы таблицу, что нежелательно для операторской панели.

Нужно переработать панели действий над таблицами: сделать их компактными, контекстными и быстрыми, сохранив полный legacy-функционал без добавления новых бизнес-команд. Одновременно нужно подготовить структуру прототипа к выносу разных типов таблиц из монолитного `index.html` в отдельные `.js`-файлы.

## Sources of Truth

При расхождении источники применяются в следующем порядке:

1. **Функциональность, поля, область применения и названия команд:** `legacy/simbox-desktop-v2014/www/simbox/`, прежде всего `sim.php`, `dongle.php`, `diagmode.php`, `hubs.php`, `readers.php`, `nabor.php`, `plan.php`, `proc.php`, `bablo.php`, `upgrade.php`.
2. **Текущий состав экранов и демонстрационные данные:** `design/simbox-design-prototype/index.html` и `support.js`.
3. **Плотность и иконографика:** правила `nativemind-adminka` — нативные GostSimBox-иконки 16×16, позиционная семантика, текстовые подписи/tooltips и отсутствие emoji как основной иконографии.

## User Stories

### Primary

**Как оператор SimBox**  
**я хочу** видеть компактную панель доступных действий непосредственно над текущей таблицей  
**чтобы** выделить строки и выполнить нужную legacy-команду без длинной прокрутки и потери контекста.

**Как оператор SimBox**  
**я хочу** раскрывать параметры команды в overlay-слое той же toolbar-строки  
**чтобы** таблица не сдвигалась и не перекрывалась.

### Secondary

**Как разработчик прототипа**  
**я хочу** хранить определения разных операционных таблиц в отдельных `.js`-файлах  
**чтобы** уменьшить монолитный `index.html`, изолировать изменения экранов и оставить общую механику таблиц переиспользуемой.

## In-Scope Screens and Tables

Нужно проработать все восемь таблиц, отмеченных `data-table` в текущем прототипе:

| Table key | Экран / legacy source | Требуемая работа с действиями |
|---|---|---|
| `sim` | Симки / `sim.php` | Выбор, фильтры, обновить/сохранить, питание, простые, групповые/плановые, smart, complex, export, delayed/queue, KI/SuperSIM/rotator, SMS-рассылка |
| `nm` | Модемы normal mode / `dongle.php` | Обновить, IMEI, diagmode/restart, питание, PIN/card lock, mode, frequency lock, AT command, delayed/queue |
| `um` | Модемы update mode / `diagmode.php` | Существующие обновление/диагностические действия; новых команд не добавлять |
| `hubs_tree` | USB/hub tree / `hubs.php` | Обновить, питание/restart, delayed/queue и только те команды, которые относятся к выбранным hub-строкам |
| `hubs_readers` | Readers / `readers.php` | Обновить, PIN, KI search, APDU и только существующие reader-команды |
| `nabor` | Наборы команд / `nabor.php` | Существующие табличные операции редактирования/сохранения без выдуманных bulk actions |
| `plans` | Планы / `plan.php` | Показ групп колонок, обновить, сохранить, создать план; сохранить все поля и режимы |
| `billing` | Биллинг / `bablo.php` | Существующие фильтры/обновление данных; не добавлять отсутствующие legacy-действия |

Страницы `proc.php` и `upgrade.php` не получают выдуманный table toolbar, но их существующие command-панели должны визуально использовать ту же компактную систему группировки там, где это уместно. Debug и result dialogs не меняют функциональность.

## Functional Inventory That Must Not Be Lost

### SIM selection actions

- `Обновить`, `Сохранить`, `ВКЛ`, `ВЫКЛ`.
- Simple: USSD; SMS (номер + сообщение); Call60; CallSpeak; CallDTMF (номер + последовательность).
- Group/plan: Set group; set plan без копирования; set plan с копированием; восстановить параметры плана; снять автоблокировки.
- Smart/plan-aware: Activate SIM; Get balance/number/minutes/tarif/options/dover; Activate work.
- Complex: Complex prepare; Complex prepare 2; Complex work.
- Export: dongles, numbers, masspayment с тремя balance/payment полями.
- Execution options: delay min, random delay, queue instead of immediate execution.
- SuperSIM/KI: Auto new supersim KI + owner + IMSI/ICCID/KI/SMSC + Set data; Auto new KI + те же поля; Rotator/New KI/loop/owner.
- SMS bulk send (`Разослать`).

### Modem, hub and reader actions

- Modem: change/blacklist IMEI; enter diagmode; restart dongle; power on/off; enter/change PIN; unlock CARDLOCK; U2DIAG; GSM/WCDMA; frequency lock; arbitrary AT command; delayed/queue.
- Hub: refresh; power on/off/restart; delayed/queue; KI search; APDU where legacy assigns it to that surface.
- Reader: refresh; remove/set PIN; KI search; APDU.
- Destructive or disruptive actions remain visually distinct and must not be promoted as the default primary action.

## UX Requirements

1. Для каждой операционной таблицы toolbar расположен **непосредственно над её горизонтальным scroller**, в одном контекстном блоке с table title/count/selection state.
2. Базовая высота toolbar — одна строка на рабочей ширине экрана; второстепенные команды группируются, а не переносятся в длинную панель.
3. Команды без параметров могут выполняться из compact button/menu. Команды с полями раскрывают anchored popover/command palette над toolbar или в свободную сторону от неё.
4. Раскрытие не меняет высоту страницы, не двигает таблицу и не перекрывает строки таблицы. Overlay должен иметь собственный `z-index`, collision/viewport positioning и закрываться по Escape, outside click и явной кнопке.
5. Одновременно открыт только один action popover в пределах экрана.
6. Selection-aware команды показывают число выбранных строк и недоступны при нулевом выборе. Команды уровня страницы не должны ошибочно зависеть от selection.
7. Частые безопасные действия доступны напрямую; редкие, сложные и опасные сгруппированы по задаче. Порядок legacy-карточек не является обязательным.
8. Пользователь должен различать: refresh/view controls, edit/save, device power, communications, plan/group, service/advanced, export и destructive commands.
9. Icon-only controls допустимы только при однозначной 16px-иконке, наличии accessible name и tooltip. Неоднозначные действия сохраняют короткую текстовую подпись.
10. На узкой ширине toolbar может переходить в компактный overflow, но таблица остаётся единственным горизонтальным scroller; не допускаются вложенные конкурирующие горизонтальные scrollbars.
11. Настройка колонок (`Columns`) становится частью toolbar и сохраняет текущее поведение: visibility/order, pinned ID where applicable, reset и local persistence.
12. Все команды и поля legacy остаются доступны максимум через один уровень группы и один открытый popover; скрытые многоуровневые меню не допускаются.
13. Для необратимых/системных команд используются danger styling и подтверждение в прототипе; обычные команды не получают лишних подтверждений.
14. Статусы выполнения (idle/running/success/error) показываются рядом с инициировавшей командой или как компактная toolbar status area, без layout shift таблицы.

## Design Alternatives to Explore in VISUAL

### A — Grouped toolbar + anchored popovers (recommended)

Одна строка: selection count, 2–4 частых действия, task-based segmented groups, Columns и overflow. Нажатие группы открывает anchored popover с формой. Лучший баланс плотности, доступности и отсутствия layout shift.

### B — Command palette in the toolbar

Одна кнопка/поле `Действия…` открывает searchable overlay; выбранная команда показывает её параметры в том же overlay. Самый компактный вариант, но частые команды менее заметны.

### C — Horizontal action tabs with one floating editor

В toolbar видны короткие категории (`Связь`, `План`, `Сервис`, `Экспорт`); категория переключает один floating editor. Быстро для опытного оператора, но требует аккуратной адаптации для таблиц с малым числом действий.

На VISUAL-фазе необходимо показать A/B/C на SIM-таблице и адаптацию рекомендованного варианта ко всем остальным таблицам.

## JavaScript Decomposition Requirements

1. Да, таблицы разных типов можно и нужно вынести из монолитного HTML.
2. Предпочтительная целевая структура: общий table/toolbar runtime + отдельное определение каждого типа (`tables/sim.js`, `tables/modems-normal.js`, `tables/modems-update.js`, `tables/hubs.js`, `tables/readers.js`, `tables/command-sets.js`, `tables/plans.js`, `tables/billing.js`). Точная структура утверждается в SPECIFICATIONS.
3. Отдельные файлы содержат screen/table definitions, sample rows, columns и привязку разрешённых legacy actions; общий код содержит rendering, column preferences, selection и popover behavior.
4. Не добавлять framework, bundler или backend. Прототип должен оставаться запускаемым тем же простым способом; если используется `file://`, решение не должно ломаться из-за module/CORS restrictions.
5. Поведение и данные не должны дублироваться между table files; shared action definitions переиспользуются.

## Acceptance Criteria

### Must Have

1. **Given** открыта любая из восьми таблиц  
   **When** оператор смотрит на её верхнюю область  
   **Then** все относящиеся к ней controls/actions доступны из компактного toolbar над scroller.

2. **Given** оператор раскрывает группу или параметризованную команду  
   **When** overlay открыт/закрыт  
   **Then** координаты и высота таблицы не меняются, а overlay не закрывает строки таблицы.

3. **Given** ни одна строка не выбрана  
   **When** показан toolbar  
   **Then** selection-only команды disabled и ясно сообщают, что нужно выбрать строки.

4. **Given** выбраны одна или несколько строк  
   **When** оператор открывает группы действий  
   **Then** число выбранных элементов видно, а полный набор соответствующих legacy-команд доступен.

5. **Given** сравнение с перечисленными legacy PHP-экранами  
   **When** проводится functional audit  
   **Then** ни одно существующее поле или действие не потеряно и ни одна новая бизнес-команда не добавлена.

6. **Given** все восемь table types  
   **When** проверяются column controls, selection, density и overflow  
   **Then** поведение согласовано, при этом набор действий остаётся специфичным для конкретного типа таблицы.

7. **Given** table definitions вынесены в `.js`  
   **When** прототип запускается и переключает/показывает все экраны  
   **Then** sample data, columns, actions и column persistence работают без framework/bundler regression.

8. **Given** keyboard-only interaction  
   **When** пользователь проходит toolbar/popover  
   **Then** доступны focus order, Enter/Space activation, Escape close и возврат фокуса на trigger.

### Should Have

- Direct controls для Refresh и наиболее частых безопасных действий.
- Последняя выбранная группа может запоминаться в рамках текущего экрана, но не должна автоматически запускать команду.
- Состояния running/success/error представлены в mockups и реализованы без layout shift.
- Danger-команды визуально отделены от повседневных операций.

### Won't Have (This Iteration)

- Новые телеком-команды, автоматизации, permission model или backend API.
- Изменение legacy-семантики полей, массовых операций и результата команд.
- Полная переработка глобальной навигации, branding или всех result dialogs.
- Замена нативной 16px GostSimBox-иконографии на emoji или произвольный современный icon set.
- Framework migration или production rewrite PHP-приложения.

## Constraints

- **Functional:** legacy PHP — источник истины; редизайн не сокращает возможности.
- **Visual:** плотная операторская UI; таблица и её данные имеют приоритет над декоративными панелями.
- **Layout:** action expansion не перекрывает и не сдвигает table viewport.
- **Technical:** статический HTML/JS-прототип без новых зависимостей и build step.
- **Compatibility:** сохранить текущие `data-table`, column preferences/localStorage semantics либо предоставить прозрачную миграцию ключей.
- **Assets:** GostSimBox glyphs показываются в 16×16 с pixelated rendering для нативных bitmap-файлов; emoji только аварийный fallback.

## Open Questions

- [ ] Какой из трёх visual-вариантов утвердить после ASCII-сравнения? Предварительная рекомендация: A.
- [ ] Нужно ли сохранять поддержку прямого открытия через `file://`? До уточнения считаем, что да.

## References

- `design/simbox-design-prototype/index.html`
- `design/simbox-design-prototype/support.js`
- `legacy/simbox-desktop-v2014/www/simbox/`
- `/Users/anton/.codex/skills/nativemind-adminka/SKILL.md`

---

## Approval

- [ ] Reviewed by: user
- [ ] Approved on: pending
- [ ] Notes: требуется явное `requirements approved` перед фазой VISUAL

