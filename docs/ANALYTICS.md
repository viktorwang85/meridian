# Аналитика

Импорт: `bali metrics import data/metrics.csv`. Шаблон: `analytics/metrics.example.csv`. Записи требуют существующей publication со статусом PUBLISHED. `collected_at` — ISO 8601 с часовым поясом (рекомендуется UTC). Счётчики — целые неотрицательные, completion_rate — доля 0..1, выручка — неотрицательная в одной выбранной вами валюте. Пустые показатели считаются нулём, поэтому вводите полные накопительные snapshots.

Используется только последний snapshot каждой публикации по времени; повторный import publication_id + collected_at обновляет снимок. Разные варианты суммируются по эксперименту. Reach разных публикаций может включать одних людей: это сумма охватов, не уникальная аудитория аккаунта. Completion взвешивается по views.

Rates: shares/saves/comments/follows/profile_visits/applications/qualified_leads делятся на reach. Lead Score = qualified_leads/reach × 10 000. Revenue Score = revenue/reach × 10 000.

Experiment Score = 100 × сумма весов × отношение rate к медиане измеренных экспериментов аккаунта: shares 25%, saves 20%, follows 20%, profile visits 15%, comments 10%, completion 10%. Один компонент ограничен 3×. При нулевой медиане нулевой компонент получает нейтральный 1×, положительный — 2×. При reach=0 score=0. Это прозрачная MVP-конвенция, не статистическая значимость.

Winner: score ≥120, reach ≥1000 и минимум три эксперимента с reach>0. Автоматически менять статус на WINNER скоринг не будет. `bali winners` — текущая динамическая выборка. Dashboard Content DNA показывает top-10 по среднему score для hook/pillar/motive/CTA/format; размер выборки указан. Нет причинных выводов или статистической уверенности, коммерческие scores отдельно от engagement score.
