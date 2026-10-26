# Состояние MVP

## Реализовано

- SQLite: experiments, variants, publications, metrics, learnings, artifacts, footage; атомарные ID, foreign keys.
- CLI-команды из задания, --help, глобальный --dry-run, CSV import/export, проверка статусов.
- 50 новых seed-гипотез на основе мастер-документа (исходный backlog не предоставлен).
- 100 hooks, 10 сценарных черновиков, 10 shooting briefs, captions и 30 монтажных планов.
- Provider abstraction: local и ручной prompt workflow; 7 Markdown prompt templates.
- Индексация FFprobe и ручные tags без изменения исходников.
- Медианный score, rates, бизнес-метрики, фильтр winners, 10 descendants с parent_id.
- Дневная очередь, learnings, очередь ручных публикаций с обязательным approve.
- FastAPI dashboard: 7 экранов, поиск experiments, Content DNA и агрегированные leads/revenue.
- Remotion 1080×1920: captions JSON, safe zones, B-roll, first frame, zoom, CTA, editable JSON props.

## Проверено в текущей Linux-среде

- `uv sync --frozen --extra dev`; `npm ci`.
- 7 pytest tests: IDs под конкурентной записью, import/dry-run, статусы/контент, scoring/winners/evolve, metrics validation/upsert, dashboard API, CLI dry-run и approval gate.
- Bootstrap выполнен повторно без дублирования seed; рабочая база содержит 50 experiments, без фиктивных публикаций и результатов.
- Dashboard поднят; HTTP /api/state и реальное выполнение JavaScript с переключением всех семи экранов проверены Chromium.
- `npm run check` прошёл; Studio HTTP отвечает; PNG первого кадра создан с системным Chromium и визуально проверен. Кадр с тестовым video-source, B-roll и captions также успешно создан. MP4 не экспортировался.
- FFprobe успешно индексирует сгенерированное тестовое видео.

## Ограничения и оставшаяся редакторская работа

- Это первый инженерный MVP, не завершение всей продуктовой спецификации. Сценарии пока требуют личных историй и проверки Виктором. Утверждённых сценариев для съёмки нет.
- Local hooks и seed — шаблонные предложения; ценность гипотез и соответствие pillar требуют редакторского отбора. Нет реального LLM-провайдера, vision tagging, транскрибации, CRM, attribution или официального publishing API.
- Рендер на реальном архиве пользователя не проверен: footage не предоставлен. Без source отображается демонстрационная карточка. Массового рендера нет.
- Локальный single-user инструмент; dashboard read-only, без внешней авторизации. Не выставлять сервер в Интернет.
- Scoring — эвристика с порогами, не статистическое доказательство. Нет бизнес-результатов до реальных публикаций и измерений.
- macOS не проверена. Облачный браузер Remotion нужно указывать явно: `/usr/bin/chromium`.
- Тестовый клиент Starlette выводит предупреждение о будущем переходе на httpx2; тесты проходят.
- Изменения находятся в рабочем каталоге; Git push и публикация окружения не выполнялись.
