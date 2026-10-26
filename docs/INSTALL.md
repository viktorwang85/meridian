# Установка

Следуйте README из корня checkout. `uv sync --frozen --extra dev` использует uv.lock; `npm ci` в render использует package-lock.json. Никакие API-ключи или сторонние сервисы не требуются. Установщик не должен менять lockfiles.

`python scripts/bootstrap.py` повторяем: сохраняет существующие записи, добавляет отсутствующие seed ID и не генерирует уже сохранённые artifacts повторно. Импорт seed с несовпадающей последовательностью ID отменяется целиком: запускайте bootstrap до создания собственных записей в новой пустой базе.

`BALI_DB=/absolute/path/custom.sqlite3` выбирает отдельную базу. `bali init` создаёт только схему; `bali experiments import experiments/backlog.csv` отдельно загружает seed.

Проверка сервера: GET `/api/state` возвращает `overview.experiments=50` после bootstrap пустой базы; GET `/` возвращает dashboard. Для сохранённой пользовательской базы число может быть больше.

В облаке используйте существующий checkout `/workspace/meridian`; отдельный worktree не нужен. Процессы dashboard и Studio нужно запускать заново после восстановления среды. Не храните секреты в Git. В macOS повторите установку зависимостей: Linux .venv/node_modules переносить нельзя. На macOS приложение в этой сессии не проверялось.

В этой облачной среде Chrome уже установлен в `/usr/bin/chromium`. Для Remotion CLI добавьте `--browser-executable=/usr/bin/chromium`. Проверка кадра:

```sh
cd render
npx remotion still src/index.ts BaliReel /tmp/bali-preview.png --frame=0 --props=example.props.json --browser-executable=/usr/bin/chromium
```

Автозагрузка браузера с remotion.media ограничена сетевой политикой; установленный Chromium позволяет обойтись без изменения этой политики. На macOS выберите локальный Chrome либо разрешите стандартную загрузку браузера Remotion.
