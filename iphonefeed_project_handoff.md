# iphonefeed.news — Документация проекта для передачи ИИ-агентам

**Дата последнего обновления:** 14.04.2026  
**Составлено:** Claude (Anthropic)

---

## 1. ОБЩАЯ ИНФОРМАЦИЯ О САЙТЕ

| Параметр | Значение |
|---|---|
| Домен | https://iphonefeed.news |
| CMS | WordPress |
| Хостинг | Hostinger |
| Панель хостинга | https://hpanel.hostinger.com |
| Hostinger File Manager | https://srv1795-files.hstgr.io/5f491fd663dc5d70/files |
| WordPress Admin | https://iphonefeed.news/wp-admin |
| Пользователь WP | Редакция iPhoneFeed |
| Тема сайта | Новостная (точное название уточнить в WP Admin → Внешний вид) |
| Основные плагины | Rank Math SEO, LiteSpeed Cache, miniOrange API Authentication |

---

## 2. ВЫПОЛНЕННЫЕ ЗАДАЧИ (✅ СДЕЛАНО)

### 2.1 Rank Math SEO — Мастер настройки
- Пройден 6-шаговый мастер первичной настройки
- Тип сайта: новостной
- Настроены базовые SEO-параметры

### 2.2 Google Search Console
- Сайт добавлен и верифицирован
- Sitemap отправлен: `https://iphonefeed.news/sitemap_index.xml`
- Статус: **Успешно**, обработано 100+ страниц (14.04.2026)

### 2.3 Страница «О нас» (post ID: 312)
- Создана страница `/о-нас`
- Заголовок: **«О нас»**
- Контент:
  > iPhoneFeed — ваш главный источник новостей об Apple и iPhone на русском языке.
  >
  > Мы публикуем актуальные новости, обзоры и аналитику о продуктах Apple: iPhone, iPad, Mac, Apple Watch и многом другом. Наша цель — оперативно и понятно рассказывать о мире Apple русскоязычной аудитории.
- Добавлена в навигационное меню (дубликат menu-item-319 удалён, оставлен menu-item-318)

### 2.4 Переименование автора
- Было: AppleDaily / "Редакция AppleDaily"
- Стало: iPhoneFeed / **"Редакция iPhoneFeed"**
- Изменено через WordPress REST API (`/wp-json/wp/v2/users/me`):
  - `last_name` → `iPhoneFeed`
  - `nickname` → `Редакция iPhoneFeed`
  - `name` (display name) → `Редакция iPhoneFeed`

### 2.5 Яндекс.Вебмастер
- Сайт добавлен: `https://iphonefeed.news`
- **Верификация выполнена** через HTML-файл (метатег не сработал — заблокирован LiteSpeed/miniOrange)
- Файл верификации: `yandex_17a0e428fd5e6618.html`
  - Путь на сервере: `/yandex_17a0e428fd5e6618.html` (в корне WordPress)
  - Содержимое: `<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>Verification: 17a0e428fd5e6618</body></html>`
- ID верификации Яндекс: `17a0e428fd5e6618`
- Сохранён в Rank Math → Веб-инструменты → Яндекс: `17a0e428fd5e6618`
- Владелец аккаунта Яндекс: **Kvazun1984**
- **Sitemap отправлен в Яндекс:** `https://iphonefeed.news/sitemap_index.xml` (добавлен 14.04.2026, очередь на обработку 1-2 недели)

### 2.6 Open Graph (Rank Math → Заголовки и мета → Главная)
Настройки сохранены в опции WordPress `rank-math-options-titles`:

| Поле | Значение |
|---|---|
| Мета описание главной | iPhoneFeed — актуальные новости Apple и iPhone на русском языке. Обзоры, аналитика и всё о продуктах Apple. |
| OG заголовок (homepage_facebook_title) | iPhoneFeed — Новости Apple и iPhone на русском |
| OG описание (homepage_facebook_description) | iPhoneFeed — актуальные новости Apple и iPhone на русском языке. Обзоры, аналитика и всё о продуктах Apple. |
| OG изображение (homepage_facebook_image) | Attachment ID: **117** (файл: `/wp-content/uploads/2026/04/600.jpg`, размер: 800×600px) |

**⚠️ Примечание по OG изображению:** Использовано временное изображение из медиабиблиотеки (800×600px). Рекомендуется заменить на брендовый OG-баннер размером **1200×630px** (загрузить в медиабиблиотеку, затем установить через Rank Math → Заголовки и мета → Главная → Миниатюра домашней страницы для Facebook).

---

## 3. ОЖИДАЮЩИЕ ЗАДАЧИ (⏳ НЕ СДЕЛАНО)

### 3.1 ⚠️ СРОЧНО: Удалить временный PHP-файл
- Файл `rm_og_setup.php` находится в корне WordPress (`/rm_og_setup.php`)
- Использовался для установки OG изображения через PHP
- **Необходимо удалить** через Hostinger File Manager → My files → rm_og_setup.php → Delete
- URL файла для проверки: `https://iphonefeed.news/rm_og_setup.php`

### 3.2 Google Analytics
- **Что нужно сделать:**
  1. Создать/открыть аккаунт Google Analytics 4 на Google аккаунте владельца
  2. Создать ресурс для `iphonefeed.news`
  3. Получить Measurement ID (формат: `G-XXXXXXXXXX`)
  4. Добавить в WordPress одним из способов:
     - **Через Rank Math:** WP Admin → Rank Math → Общие настройки → Аналитика → Google Analytics ID
     - **Через плагин:** Site Kit by Google (рекомендуется — автоматически связывает GA4 + GSC)
     - **Вручную:** добавить GA4 скрипт в `<head>` через WP Admin → Внешний вид → Редактор → header.php

### 3.3 robots.txt
- **Что нужно проверить/настроить:**
  - Текущий robots.txt: `https://iphonefeed.news/robots.txt`
  - WordPress генерирует стандартный robots.txt автоматически
  - Rank Math может переопределить его через WP Admin → Rank Math → Общие настройки → Редактировать robots.txt
  - **Рекомендуемое содержимое:**
    ```
    User-agent: *
    Disallow: /wp-admin/
    Allow: /wp-admin/admin-ajax.php
    Sitemap: https://iphonefeed.news/sitemap_index.xml
    ```
  - Убедиться, что строка `Sitemap:` присутствует и указывает на правильный sitemap

### 3.4 OG изображение (улучшение)
- Создать брендовый OG-баннер 1200×630px с логотипом iPhoneFeed
- Загрузить в медиабиблиотеку WordPress
- Установить как `homepage_facebook_image` в Rank Math (через UI или повторить PHP-метод с новым attachment ID)

---

## 4. ИЗВЕСТНЫЕ ТЕХНИЧЕСКИЕ ПРОБЛЕМЫ

### 4.1 Белый экран при скролле в Rank Math (React SPA)
- **Проблема:** Страницы Rank Math SEO (`rank-math-options-*`) — это React SPA. При любом скролле страница становится белой (пустой).
- **Обходной путь:** Использовать JavaScript для заполнения полей без скролла, кнопки кликать через `ref` или JS `.click()`. Скролл вызывается через `element.scrollIntoView()` — тоже иногда ломает страницу.
- **Для сохранения настроек:** Кнопка «Сохранить изменения» активируется только когда React-состояние обновлено. При JS-заполнении через `nativeInputValueSetter` + `input` event — состояние обновляется и кнопка становится активной. После нажатия страница перезагружается (белый экран) — это нормально, данные сохраняются.

### 4.2 miniOrange API Authentication блокирует ботов
- Плагин miniOrange API Authentication блокирует внешние HTTP-запросы к сайту (Яндекс-бот, и пр.)
- При верификации Яндекс — метатег не был найден именно по этой причине
- При проверке Open Graph через внешние инструменты (Facebook Debugger, etc.) — может быть та же проблема

### 4.3 LiteSpeed Cache
- Установлен и активен
- При проблемах с кешем: WP Admin → `/wp-admin/admin.php?page=litespeed-cache&do=purge_all`

### 4.4 WordPress форма профиля → белый экран
- Форма редактирования профиля пользователя (`/wp-admin/profile.php`) вызывает белый экран после сохранения
- **Обходной путь:** Использовать WordPress REST API:
  ```javascript
  fetch('/wp-json/wp/v2/users/me', {
    method: 'POST',
    headers: {
      'X-WP-Nonce': wpApiSettings.nonce,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({last_name: 'iPhoneFeed', nickname: 'Редакция iPhoneFeed', name: 'Редакция iPhoneFeed'})
  })
  ```

---

## 5. ПОЛЕЗНЫЕ ССЫЛКИ И URL

| Ресурс | URL |
|---|---|
| WordPress Admin | https://iphonefeed.news/wp-admin |
| Rank Math → Общие настройки | https://iphonefeed.news/wp-admin/admin.php?page=rank-math-options-general |
| Rank Math → Веб-инструменты | https://iphonefeed.news/wp-admin/admin.php?page=rank-math-options-general&view=webmaster |
| Rank Math → Заголовки и мета → Главная | https://iphonefeed.news/wp-admin/admin.php?page=rank-math-options-titles&view=homepage |
| Rank Math → Заголовки и мета → Соц. мета | https://iphonefeed.news/wp-admin/admin.php?page=rank-math-options-titles&view=social |
| Rank Math → XML Sitemap | https://iphonefeed.news/wp-admin/admin.php?page=rank-math-options-sitemap |
| Rank Math → robots.txt | https://iphonefeed.news/wp-admin/admin.php?page=rank-math-options-general&view=robots |
| Страница «О нас» | https://iphonefeed.news/о-нас/ |
| Sitemap | https://iphonefeed.news/sitemap_index.xml |
| robots.txt | https://iphonefeed.news/robots.txt |
| Google Search Console | https://search.google.com/search-console |
| Яндекс.Вебмастер | https://webmaster.yandex.ru/site/https:iphonefeed.news:443/ |
| Яндекс — Sitemap страница | https://webmaster.yandex.ru/site/https:iphonefeed.news:443/indexing/sitemap/ |
| Hostinger File Manager | https://srv1795-files.hstgr.io/5f491fd663dc5d70/files |
| LiteSpeed Cache — очистить | https://iphonefeed.news/wp-admin/admin.php?page=litespeed-cache&do=purge_all |

---

## 6. СТРУКТУРА ФАЙЛОВ НА СЕРВЕРЕ (важные файлы)

```
/ (корень WordPress)
├── yandex_17a0e428fd5e6618.html   ← верификация Яндекс (НЕ УДАЛЯТЬ!)
├── rm_og_setup.php                ← ⚠️ ВРЕМЕННЫЙ ФАЙЛ — УДАЛИТЬ!
├── wp-admin/
├── wp-content/
│   └── uploads/2026/04/
│       └── 600.jpg               ← текущий OG image (ID: 117, 800×600px)
├── wp-includes/
├── .htaccess
└── wp-config.php
```

---

## 7. WORDPRESS REST API — ПОЛЕЗНЫЕ КОМАНДЫ

Все запросы выполнять из консоли браузера на странице WP Admin (там есть `wpApiSettings.nonce`).

```javascript
// Получить nonce для REST API
wpApiSettings.nonce

// Обновить профиль пользователя
fetch('/wp-json/wp/v2/users/me', {
  method: 'POST',
  headers: {'X-WP-Nonce': wpApiSettings.nonce, 'Content-Type': 'application/json'},
  body: JSON.stringify({display_name: 'Редакция iPhoneFeed'})
})

// Получить список медиафайлов
fetch('/wp-json/wp/v2/media?media_type=image&per_page=20', {
  headers: {'X-WP-Nonce': wpApiSettings.nonce}
}).then(r=>r.json()).then(d=>console.log(d.map(m=>({id:m.id, url:m.source_url}))))

// Rank Math доступные REST маршруты
fetch('/wp-json/rankmath/v1/', {
  headers: {'X-WP-Nonce': rankMath.restNonce}
}).then(r=>r.json()).then(d=>console.log(Object.keys(d.routes)))
```

---

## 8. ПРИОРИТЕТ СЛЕДУЮЩИХ ДЕЙСТВИЙ

1. **🔴 СРОЧНО:** Удалить `/rm_og_setup.php` с сервера
2. **🟡 ВАЖНО:** Подключить Google Analytics 4
3. **🟡 ВАЖНО:** Проверить и настроить robots.txt (добавить Sitemap)
4. **🟢 ЖЕЛАТЕЛЬНО:** Создать и загрузить брендовый OG-баннер 1200×630px
5. **🟢 ЖЕЛАТЕЛЬНО:** Загрузить логотип сайта в WordPress (WP Admin → Внешний вид → Настроить → Идентификация сайта → Логотип)

---

*Документ создан автоматически на основе выполненной работы по SEO-настройке сайта iphonefeed.news*
