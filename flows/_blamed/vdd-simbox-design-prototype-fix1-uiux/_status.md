# Status: vdd-simbox-design-prototype-fix1-uiux

## Current Phase

IMPLEMENTATION

## Phase Status

IN PROGRESS — BROWSER ACCEPTANCE PENDING

## Last Updated

2026-09-01 by Codex

## Blockers

- Browser runtime в текущей сессии не предоставляет backend; P21 visual/interaction sweep ожидает
  доступного браузера или ручной проверки пользователем.

## Progress

- [x] Requirements drafted
- [x] Requirements approved
- [x] Visual mockups drafted
- [x] Visual mockups approved
- [x] Specifications drafted
- [x] Specifications approved
- [x] Plan drafted
- [x] Plan approved
- [x] Implementation started
- [ ] Implementation complete
- [ ] Documentation drafted
- [ ] Documentation approved

## Context Notes

- Новый самостоятельный VDD flow; это не fork `vdd-simbox-design-prototype-fix1`.
- Целевой прототип: `design/simbox-design-prototype-v2026/`.
- Источник истины по функциям, полям и телеком-семантике: `legacy/simbox-desktop-v2014/www/simbox/`.
- Целевой прототип использует CSS Grid/DC-компонент, а не HTML `<table>`; требования применяются ко всем data-grid экранам.
- Action groups уже расположены над grid и раскрываются absolute-панелью; нужно уплотнить toolbar и исключить перекрытие строк.
- Сортировка уже существует; hide/reorder/persistence отсутствуют.
- Текущий `index.html` монолитный: markup, CSS, data, columns, actions и icon catalog находятся в одном файле.
- Fugue применяется density-aware: 16×16 source на 1× и 32×32 source на Retina/2× в одном logical 16×16 box. 48px Fugue tier не существует.
- Предварительный статический inventory целевого файла содержит 141 уникальный bitmap path/filename; он должен быть нормализован и проверен по смыслу.
- `pause2.png` deprecated и не используется в legacy; заменить на канонический `pause.png` / Fugue `control-pause.png`.
- Scope расширен глубоким legacy-аудитом: каждая основная таблица реконструируется 1:1 по логическим столбцам, все столбцы видимы после Reset.
- `readers` выделен в самостоятельный пункт: `Readers` в English и `Ридеры` в Russian, отдельно от `hubs`.
- Проверенный baseline `readers.php`: 12 столбцов и 5 существующих действий (Refresh, Remove PIN, Set PIN, KI search, APDU).
- Выбран один финальный toolbar pattern: Morphing inline action rail; A/B/C больше не являются тремя вариантами реализации.
- Все generic UI glyphs должны быть Fugue; отсутствующие semantic matches попадают в Fugue wishlist без emoji/Lucide fallback.
- Hubs и Readers остаются отдельными routes; labels берутся только из активного locale.
- Локализация уточнена: в UI используется только один активный язык; bilingual labels запрещены. English `Hubs`/`Readers`, Russian `Хабы`/`Ридеры`; правило распространяется на весь интерфейс и все пять словарей.
- Billing navigation icon зафиксирована как Fugue `money.png`; broken/irrelevant `may.ico` запрещена.
- Processes navigation icon зафиксирована как Fugue `application-task.png`; heart-like `conn.png` запрещена.
- Конфликт Hubs разрешён пользователем: сохраняются только активные legacy-действия; KI Search и
  APDU остаются только в Readers. То же правило исключает другие закомментированные формы.
- SPECIFICATIONS содержит точные манифесты: SIM 43, Lines 26, Programmer 6, Hubs 9, Readers 12,
  Command sets 1, Plans 82, Billing 4, Debug 1+1.
- Billing уточнён без потери parity: Code и Operator отображаются внутри единственной legacy-колонки
  Direction, а не как два логических столбца.
- Specifications явно одобрены пользователем 2026-09-01.
- PLAN разбит на 22 атомарные задачи с отдельными проверками; целевой прототип остаётся runnable по
  `file://`, а `support.js` и `_ds/**` защищены от изменений.
- `design/simbox-design-prototype-v2026/` является отдельным чистым nested Git repository; проверки
  и handoff выполняются из его контекста.
- Plan явно одобрен пользователем 2026-09-01.
- P01–P20 реализованы; dependency-free verifier проходит 311 проверок.
- Прототип разнесён на отдельные CSS/core/locales/tables/screens файлы и работает без build/network
  зависимостей по `file://`.
- Все navigation routes и active actions теперь имеют Fugue icons: 46 semantic mappings на 45
  уникальных парах 16×16/32×32. SIM=`card.png`, Readers=`scanner.png`, KI Search=`magnifier.png`,
  APDU=`terminal--arrow.png`; wishlist хранит только пожелания для более точного будущего artwork.
- P21 не выполнен из-за отсутствия browser backend; статические, schema, asset и syntax checks
  проходят.

## Next Actions

1. Открыть `design/simbox-design-prototype-v2026/index.html` в доступном браузере.
2. Выполнить P21: все routes, actions, locales, column controls, responsive widths и DPR 1/2.
3. После успешного P21 завершить P22 и перейти к DOCUMENTATION.
