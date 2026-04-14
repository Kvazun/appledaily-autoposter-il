# AppleDaily Israel — Инструкция по настройке

## Шаг 1: Домен и хостинг

1. Купи домен **appledaily.co.il** через JetServer (jetserver.co.il) или другой израильский регистратор
2. В настройках домена пропиши nameservers Hostinger:
   ```
   ns1.dns-parking.com
   ns2.dns-parking.com
   ```
3. На Hostinger → hPanel → "Добавить сайт" → введи домен appledaily.co.il

---

## Шаг 2: Создать WordPress-сайт на Hostinger

1. hPanel → Websites → Add website
2. Выбрать WordPress
3. **Язык установки: עברית (Hebrew)**
4. Название сайта: `AppleDaily ישראל`
5. Запомни логин/пароль администратора

---

## Шаг 3: Настройка WordPress под иврит (RTL)

1. Войди в WordPress Admin
2. **Settings → General**:
   - Site Language: **עברית**
   - Timezone: **Asia/Jerusalem**
3. **Appearance → Themes**: установи тему с поддержкой RTL. Рекомендую:
   - **Astra** (бесплатная, RTL-ready)
   - **GeneratePress** (как на русском сайте — уже знакомо)
4. После установки темы WordPress автоматически переключится в RTL-режим

---

## Шаг 4: Добавить REST API endpoint

1. WordPress Admin → Appearance → Theme File Editor
2. Открой файл `functions.php`
3. В **конец файла** (перед `?>` если есть) добавь весь код из файла `functions-php-snippet.php`
4. Сохрани файл
5. Проверь: открой в браузере `https://appledaily.co.il/wp-json/appledaily/v1/post` — должен вернуться JSON с ошибкой (это нормально, значит маршрут зарегистрирован)

**Важно:** Токен для нового сайта: `AppleDailyILToken2025Secret`

---

## Шаг 5: Создать GitHub репозиторий

1. Зайди на github.com/Kvazun
2. New repository → название: `appledaily-autoposter-il`
3. Public, без README
4. Загрузи файлы из папки `israel/`:
   - `autoposter.py`
   - `requirements.txt`
   - `.gitignore`
   - `.env.example`
   - `.github/workflows/autoposter.yml`

---

## Шаг 6: Добавить секреты в GitHub

Settings → Secrets and variables → Actions → New repository secret:

| Имя секрета | Значение |
|-------------|----------|
| `WP_URL` | `https://appledaily.co.il` |
| `WP_PASSWORD` | `AppleDailyILToken2025Secret` |
| `OPENAI_API_KEY` | твой ключ OpenAI (тот же что и для русского сайта) |

---

## Шаг 7: Тест

1. GitHub → Actions → "AppleDaily Israel Autoposter" → Run workflow
2. Проверь логи — должны появиться записи на иврите в WordPress

---

## Что отличается от русского сайта

| Параметр | Русский сайт | Израильский сайт |
|----------|-------------|-----------------|
| Язык | Русский | Иврит (RTL) |
| Домен | appledaily.news | appledaily.co.il |
| GPT промпт | На русском | На иврите |
| JSON ключи | title_ru / content_ru | title_he / content_he |
| Токен | AppleDailyToken2025Secret | AppleDailyILToken2025Secret |
| БД SQLite | seen_articles.db | seen_articles_il.db |
| GitHub репо | appledaily-autoposter | appledaily-autoposter-il |
