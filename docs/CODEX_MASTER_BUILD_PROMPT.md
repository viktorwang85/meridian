# MASTER BUILD PROMPT FOR CODEX DESKTOP
## Project: BALI CONTENT OS

Ты работаешь внутри репозитория BALI_CONTENT_OS_STARTER.

Главный документ:
`BALI_CONTENT_OS_MASTER.md`

Прочитай его полностью до начала изменений.

Твоя роль:
ты — lead engineer + content systems architect + automation engineer.

Твоя задача — превратить спецификацию в работающий локальный MVP, которым Viktor сможет пользоваться через Codex Desktop.

---

# РЕЗУЛЬТАТ

После выполнения в репозитории должна существовать рабочая система, которая:

1. хранит контентные эксперименты;
2. создаёт уникальные ID;
3. генерирует hypotheses, hooks и scripts;
4. создаёт shooting briefs;
5. принимает сырой ролик;
6. умеет создавать несколько ОСМЫСЛЕННЫХ монтажных вариантов;
7. готовит captions и CTA;
8. ведёт publishing queue;
9. принимает метрики после публикации;
10. рассчитывает score;
11. определяет winners;
12. создаёт descendants победителей;
13. показывает dashboard;
14. хранит learnings;
15. готовит ежедневный список действий для Viktor.

---

# ВАЖНЫЕ ПРАВИЛА

- Не строй систему вокруг обхода механизмов обнаружения повторов Instagram.
- Не меняй метаданные с целью скрыть повторную публикацию.
- Основная вариативность создаётся через hooks, first frame, пересъёмку, монтаж, B-roll, duration, CTA, framing и story angle.
- Publishing layer проектируй через официальные/разрешённые интеграции.
- Сначала MVP.
- Минимизируй зависимости.
- macOS — основной runtime.
- Любая автоматизация должна иметь dry-run.
- Любая публикация требует человеческого approve, пока отдельно не включён auto-publish.
- Не удаляй пользовательские файлы.
- Не перезаписывай исходники footage.
- Все generated assets сохраняй отдельно.

---

# TECHNOLOGY

Предпочтительный стек:

- Python 3.12 для orchestration/data
- SQLite для MVP database
- pandas только если действительно нужен
- FastAPI для local API
- simple HTML/JS или lightweight React для dashboard
- Remotion для render templates
- ffmpeg для low-level media operations
- CSV export/import
- Markdown knowledge files

Не создавай Supabase/Vercel на первом этапе, если локальная версия решает задачу.

---

# СТРУКТУРА

Доработай текущую структуру примерно до:

bali-content-os/
  app/
  cli/
  config/
  data/
  db/
  experiments/
  content/
  footage/
  render/
  analytics/
  publishing/
  skills/
  tests/
  docs/

Не ломай существующие файлы.

---

# DATABASE

Создай SQLite schema:

experiments
- id
- hypothesis
- audience
- pillar
- angle
- hook
- script
- format
- footage_type
- duration
- cta
- status
- created_at
- updated_at

variants
- id
- experiment_id
- variant_type
- hook
- first_frame
- edit_style
- duration
- cta
- file_path
- status

publications
- id
- variant_id
- platform
- trial
- published_at
- external_id
- status

metrics
- publication_id
- collected_at
- views
- reach
- avg_watch_time
- completion_rate
- shares
- saves
- comments
- profile_visits
- follows
- dms
- applications
- qualified_leads
- sales
- revenue

learnings
- id
- experiment_id
- category
- learning
- confidence
- created_at

---

# CLI

Создай команды:

`bali init`
`bali experiments import`
`bali experiments list`
`bali experiment new`
`bali hooks generate <id>`
`bali script generate <id>`
`bali shoot-brief <id>`
`bali variants plan <id>`
`bali metrics import`
`bali score`
`bali winners`
`bali evolve <id>`
`bali today`
`bali dashboard`

Все команды должны иметь `--help`.

---

# CONTENT ENGINE

LLM-provider сделай abstraction layer.

На первом этапе:
- шаблоны prompt хранятся в Markdown;
- пользователь может выбрать provider;
- если API key отсутствует, CLI генерирует prompt-файл, который можно отдать Codex вручную.

Создай prompt templates для:
- Idea Miner
- Hook Lab
- Script Writer
- Shooting Director
- Caption Writer
- Analyst
- Winner Evolver

---

# HOOK LAB

Для одного experiment генерировать минимум 10 hooks разных типов:

- curiosity
- confession
- authority
- contrarian
- story
- specific number
- identity
- invitation
- question
- visual-first

Каждый hook сохраняется.

---

# SCRIPT WRITER

Поддержать:

15 sec
30 sec
45 sec
60 sec

Структура:

HOOK
OPEN LOOP
STORY/PROOF
PAYOFF
CTA

Стиль:
живой разговорный русский;
короткие фразы;
естественная речь;
никакого рекламного канцелярита.

---

# SHOOTING BRIEF

На каждый script создать:

- shot list;
- A-roll;
- B-roll;
- location;
- wardrobe;
- first frame;
- camera distance;
- delivery note;
- natural actions;
- archive footage requests;
- CTA take.

---

# FOOTAGE LIBRARY

Создай индексатор директории footage.

Для каждого файла сохранять:
- path;
- duration;
- resolution;
- created date if available;
- tags;
- location text;
- people;
- scene;
- usable_as;
- notes.

На первом этапе ручные tags допустимы.

Подготовь интерфейс для будущего vision tagging.

---

# REMOTION

Создай MVP template для 9:16 Reel:

- 1080x1920
- captions
- safe zones
- optional B-roll
- optional first-frame card
- optional subtle zoom
- editable props JSON

Один JSON = один render.

Пример:

{
  "experiment_id": "BALI-0001",
  "source": "...",
  "hook": "...",
  "caption_style": "default",
  "cta": "...",
  "broll": [...]
}

Добавь preview через Remotion Studio.

Не рендери сотни файлов автоматически без команды пользователя.

---

# ANALYTICS

Рассчитывать:

share_rate
save_rate
comment_rate
follow_rate
profile_visit_rate
lead_rate
qualified_lead_rate
revenue_per_10k_reach

Сделать normalized score относительно медианы аккаунта.

Выводить:

TOP 10 experiments
TOP hooks
TOP pillars
TOP motives
TOP CTA
TOP formats

---

# WINNER EVOLVER

Winner получает descendants.

По умолчанию:

5 new hooks
3 new angles
2 new first frames
2 CTA
2 durations

Но не создавай полный Cartesian product автоматически.

Сначала предложи ranked shortlist 10 descendants.

---

# DAILY OPERATING MODE

`bali today` должен показывать:

1. что снять сегодня;
2. что смонтировать;
3. что готово к публикации;
4. какие метрики нужно собрать;
5. какие winners развить;
6. какой один highest-leverage action.

---

# DASHBOARD

Минимальные экраны:

Overview
Experiments
Pipeline
Winners
Content DNA
Leads
Revenue

Overview:
- total experiments
- published
- total reach
- followers
- qualified leads
- revenue
- current winners

---

# SEED DATA

Импортируй:
`experiments/backlog.csv`

Не меняй смыслы seed hypotheses без необходимости.

---

# TESTS

Напиши тесты минимум для:
- experiment IDs
- CSV import
- score calculation
- status transitions
- winner selection
- evolve shortlist

---

# DOCUMENTATION

Создай:

README.md
docs/INSTALL.md
docs/DAILY_WORKFLOW.md
docs/CONTENT_WORKFLOW.md
docs/ANALYTICS.md
docs/PUBLISHING.md

README должен позволить Viktor запустить систему без знания архитектуры.

---

# ПОРЯДОК РАБОТЫ

1. Проанализируй существующие файлы.
2. Составь TODO.md.
3. Создай минимальную архитектуру.
4. Реализуй database + CLI.
5. Импортируй seed.
6. Реализуй content prompts.
7. Реализуй analytics.
8. Реализуй dashboard.
9. Подготовь Remotion template.
10. Запусти тесты.
11. Исправь ошибки.
12. Обнови README.
13. Создай `STATUS.md`.

---

# DEFINITION OF DONE

Проект считается готовым к первой эксплуатации, если:

- установка проходит по README;
- `bali init` работает;
- 50 seed experiments импортируются;
- можно создать новый experiment;
- можно получить hook prompt;
- можно получить script prompt;
- можно получить shooting brief;
- metrics CSV импортируется;
- score рассчитывается;
- winners выводятся;
- evolve создаёт descendants;
- dashboard запускается;
- tests проходят;
- Remotion Studio открывает template;
- `bali today` выдаёт дневную очередь.

В конце:
1. покажи выполненные пункты;
2. покажи команды запуска;
3. перечисли ограничения MVP;
4. предложи ровно 3 следующих инженерных улучшения.

Начинай работу сразу.
