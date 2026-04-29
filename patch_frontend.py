import os

source_file = r"C:\Users\kip\Desktop\emotomo_finevers1\emotomo-ui\templates\manga.html"
dest_file = r"C:\Users\kip\Desktop\emotomo_finevers1\emotomo-ui\index.html"

with open(source_file, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Вырезаем Django-теги
html = html.replace("{% url 'core:catalog' %}", "catalog.html")
html = html.replace("'X-CSRFToken': '{{ csrf_token }}'", "")
html = html.replace(", 'X-CSRFToken': '{{ csrf_token }}'", "")
html = html.replace(",\n              'X-CSRFToken': '{{ csrf_token }}'", "")

# 2. Исправляем пути к файлам и медиа-ресурсам
html = html.replace(
    "const r = await fetch('/media/2d_pers/models.json', { cache: 'no-store' });",
    "const r = await fetch('media/2d_pers/models.json', { cache: 'no-store' });"
)
html = html.replace(
    "const MODEL_PATH = `/media/2d_pers/${item.folder}/${item.model3}`;",
    "const MODEL_PATH = `media/2d_pers/${item.folder}/${item.model3}`;"
)

# 3. Перенаправляем запросы на НОВЫЙ Gateway микросервисов
html = html.replace(
    "const API_BASE = deriveApiBase();",
    "const API_BASE = 'http://localhost:8000';"
)
html = html.replace(
    "window.API_URL || `${API_BASE}/api/reply`",
    "window.API_URL || `${API_BASE}/api/reply/sync`"
)

# 4. По дефолту ставим Тинъюнь, чтобы не было ошибки при открытии index.html
html = html.replace(
    "const slug = new URLSearchParams(location.search).get('slug');",
    "const slug = new URLSearchParams(location.search).get('slug') || 'tingyun';"
)
html = html.replace(
    "if (!slug) { alert('Нет slug. Открой со страницы каталога.'); return; }",
    "// Дефолтный slug применен"
)

# Сохраняем чистый HTML
with open(dest_file, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Фронтенд успешно пропатчен и отвязан от Django!")
print("✅ Создан файл: emotomo-ui/index.html")
