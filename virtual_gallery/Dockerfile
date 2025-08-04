# Базовый образ
FROM python:3.12-slim

# Настройки окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Рабочая директория
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники
COPY . /app/

# Устанавливаем переменные для production
ENV DJANGO_SETTINGS_MODULE=virtual_gallery.settings.prod

# Собираем статику
RUN python manage.py collectstatic --noinput

# Копируем статику в путь, который использует nginx
RUN mkdir -p /usr/share/nginx/html/static && cp -r staticfiles/* /usr/share/nginx/html/static/

# Открываем порт
EXPOSE 8000

# Запуск gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "virtual_gallery.wsgi:application"]
