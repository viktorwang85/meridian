# BALI CONTENT OS

Локальная рабочая система для контентных экспериментов Виктора и поездки Return to Bali. Python + SQLite + FastAPI, отдельный Remotion-шаблон. Работает без API-ключей. Ничего не публикует в Instagram автоматически.

## Быстрый старт

Нужны Python 3.12+, [uv](https://docs.astral.sh/uv/getting-started/installation/), Node.js 22+ и FFmpeg (на macOS: `brew install uv node ffmpeg`).

Из корня репозитория:

```sh
uv sync --frozen --extra dev
source .venv/bin/activate
python scripts/bootstrap.py
bali today
bali dashboard
```

Dashboard слушает порт 8000 только на локальном интерфейсе. Остановить: Ctrl+C. Семь экранов: Overview, Experiments, Pipeline, Winners, Content DNA, Leads, Revenue. Dashboard предназначен для чтения; изменения — через CLI. Оперативные данные находятся в `data/bali.sqlite3`, медиа — в `footage/`; эти каталоги не входят в Git. Делайте резервные копии при остановленном приложении.

```sh
bali experiment new --hypothesis 'Личный маршрут вызывает обращения за деталями' --angle 'Первое место для Насти' --duration 30
bali hooks generate BALI-0001
bali script generate BALI-0001 --provider prompt
bali prompt BALI-0001 script --output data/script-prompt.md
bali shoot-brief BALI-0001
bali variants plan BALI-0001
bali caption BALI-0001
bali today
```

`local` — детерминированные шаблоны, не ответы LLM. `prompt` — подготовка запроса для ручной работы с Codex. Все результаты сохраняются в `artifacts` SQLite и выводятся в JSON. Файлы из `content/BALI-*` — исходные примеры черновиков; актуальная работа хранится в SQLite.

## Видео

```sh
cd render
npm ci
npm run studio
# Экспорт только по явному решению человека:
npm run render -- out/BALI-0001.mp4 --props=example.props.json
```

В `example.props.json` задайте `source` относительно `render/public`, например `media/clip.mp4`. Исходник скопируйте в `render/public/media/` вручную, не перемещайте оригинал. Captions — JSON с миллисекундами; автоматической транскрибации нет. B-roll: `[{"source":"media/road.mp4","from":5,"duration":3}]`. Не используйте приватные медиа URL: браузер Remotion должен иметь доступ к источникам. 1080×1920, 30 fps, длительность 15/30/45/60, титры, первый кадр, CTA и мягкий zoom. Шаблон без source — демонстрационная карточка, не готовый Reel.

## Проверки

```sh
python -m pytest -q
cd render
npm run check
```

50 seed-гипотез созданы по мастер-документу: оригинального backlog во вложениях не было. Первые 10 сценариев — **черновики с местами для личного эпизода**, а не утверждённые сценарии для съёмки. Заполните их фактами, проверьте речь и тайминг. Все hypotheses требуют редакторской проверки. Демонстрационных продаж и фальшивых победителей нет.

Подробности: [установка](docs/INSTALL.md), [день работы](docs/DAILY_WORKFLOW.md), [контент](docs/CONTENT_WORKFLOW.md), [аналитика](docs/ANALYTICS.md), [публикация](docs/PUBLISHING.md), [состояние MVP](STATUS.md).
