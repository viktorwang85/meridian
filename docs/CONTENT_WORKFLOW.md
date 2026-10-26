# Контент

SQLite — оперативный источник истины, `experiments/backlog.csv` — исходный seed. `bali experiments export data/export.csv` экспортирует текущие карточки в новый файл, не перезаписывая существующий. Импорт одинаковых ID не обновляет пользовательские данные.

Статусы: IDEA → SCRIPTED → READY_TO_SHOOT → SHOT → EDITING → READY → SCHEDULED → PUBLISHED → MEASURED → WINNER → ARCHIVED. ARCHIVED допускается из любого статуса. Пропуск стадий запрещён командой status. Генератор script/brief переводит только ранние стадии; название статуса не заменяет человеческую редактуру. Публикация регистрируется только для готового эксперимента.

LocalProvider отделён интерфейсом generate(kind, experiment); PROVIDERS — реестр. Реального облачного LLM-провайдера нет. Markdown prompts содержат ограничения по фактам, структуре и стилю. `bali prompt <id> <kind> --output <new-file>` сохраняет запрос для Codex без ключа. Генерация в local сохраняет результат в artifacts и сценарий в experiments.script.

Каждая автоматизация CLI имеет глобальный `--dry-run` **перед командой**, например `bali --dry-run evolve BALI-0001`. В dry-run изменения базы откатываются, файлы не создаются. Инициализируйте схему до остальных команд. Повторная генерация создаёт новый artifact; план variants и evolve повторяемы.

Descendants: shortlist из 10 идей с parent_id, 5 новыми hooks, 3 angles, вариацией CTA и duration; два first-frame предложения записаны в notes. Это эвристический порядок для редактора, не прогноз эффективности. Элементы не перемножаются. Winner определяется по метрикам; evolve отказывается развивать неподтверждённого победителя.
