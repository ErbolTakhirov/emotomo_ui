# EMOTomo UI — Frontend Templates & Assets

Фронтенд для платформы AI-аватаров EMOTomo. Содержит HTML-шаблоны, CSS, JavaScript и ассеты Live2D моделей.

## ⚠️ Это НЕ SPA

- Нет `package.json`, npm, Node.js
- Нет бандлера (Vite, Webpack)
- Нет фреймворка (React, Vue, Svelte)

Это **набор HTML-шаблонов** с Django template тегами (`{% static %}`, `{% csrf_token %}`), которые раздаются и патчатся на лету через **Gateway** (backend, FastAPI).

## Как это работает

1. Gateway (`emotomo-v2`) при запуске монтирует эту папку
2. При запросе страницы Gateway читает HTML-файл
3. Функция `patch_html()` заменяет Django-теги на чистый HTML
4. Браузер получает готовую страницу

API вызовы из JavaScript используют **relative URLs** (`/api/reply/sync`), поэтому frontend и backend должны обслуживаться с одного хоста.

## Подключение к backend

### Локальная разработка

Клонируйте оба репо рядом:

```
parent-dir/
  emotomo-v2/    # backend
  emotomo-ui/    # этот репо
```

Запустите backend:

```bash
cd emotomo-v2
docker compose up -d
```

Gateway автоматически подхватит frontend через volume mounts в `docker-compose.yml`:

```yaml
volumes:
  - ../emotomo-ui/templates:/app/frontend:ro
  - ../emotomo-ui/static:/app/static:ro
  - ../emotomo-ui/media/2d_pers:/app/media/2d_pers:ro
```

Откройте: http://localhost:8000

### Production

Для production деплоя frontend копируется внутрь backend Docker образа (см. `emotomo-v2/deploy/Dockerfile.railway`).

## Структура

```
emotomo-ui/
├── templates/              # HTML страницы
│   ├── manga.html          # Главная — Live2D чат с аватаром (110KB)
│   ├── catalog.html        # Каталог персонажей
│   ├── index.html          # Лендинг/главная
│   ├── profile.html        # Профиль пользователя
│   ├── login.html          # Страница входа
│   ├── register.html       # Регистрация
│   ├── age_gate.html       # Верификация возраста
│   ├── onboarding.html     # Онбординг
│   ├── privacy.html        # Политика конфиденциальности
│   ├── terms.html          # Условия использования
│   ├── auth/               # Auth-страницы
│   └── dashboard/          # Dashboard-страницы
├── static/                 # CSS/JS ассеты
│   ├── style.css           # Основной CSS (25KB)
│   ├── analytics.js        # Аналитика
│   └── utils.js            # Утилиты
├── media/                  # Медиа-ассеты
│   ├── 2d_pers/            # Live2D модели персонажей
│   │   ├── models.json     # Реестр моделей
│   │   ├── tingyun/        # Тинъюнь
│   │   ├── fuxuan/         # Фу Сюань
│   │   ├── Alexia/         # Алексия
│   │   └── ...             # и другие (14 персонажей)
│   └── voice_previews/     # Превью голосов
└── docs/
    └── legacy/             # Устаревшие скрипты
```

## Персонажи (Live2D модели)

Каждый персонаж — это папка в `media/2d_pers/` с файлами Live2D:
- `*.model3.json` — конфигурация модели
- `*.moc3` — скомпилированная модель
- Текстуры, выражения, движения

Реестр моделей: `media/2d_pers/models.json`

## Переменные окружения

Frontend **не требует** переменных окружения. Все API URLs определяются динамически из `window.location`.

Если в будущем frontend будет переведён в SPA, потребуется:
```
VITE_API_BASE_URL=http://localhost:8000
```
