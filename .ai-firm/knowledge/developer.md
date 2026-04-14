---
Задача: Восстанови cron-расписание в файле `/Users/romanzh/Downloads/appledaily-project/.github/workflows/autoposter.yml`. Нужно раскомментировать строки 4-6 (убрать `# ` перед `schedule:`, `# Запуск каждые 2 часа (UTC)` и `- cron: "0 */2 * * *"`), затем закоммитить и запушить на GitHub. Цель: автопостер снова запускается каждые 2 часа автоматически.
Результат: Remote не настроен. Нужен URL репозитория на GitHub, чтобы добавить remote и запушить.

**Что сделано:**
- Раскомментированы строки 4-6 в `autoposter.yml` — cron `0 */2 * * *` активен
- Коммит создан: `ed9f4cf feat: re-enable autoposter cron schedule every 2 hours`

**Проблема:** в локальном репо нет настроенного git remote `origin`. Пуш невозможен.

**Нужно:** укажи URL GitHub-репозитория (наприм