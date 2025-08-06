# Базовый образ
FROM python:3.12-slim

# Настройки окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Рабочая директория
WORKDIR /app

# Установка зависимостей
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходников
COPY . /app/

# Установка переменных для production
ENV DJANGO_SETTINGS_MODULE=virtual_gallery.settings.prod

# Сбор статики
RUN python manage.py collectstatic --noinput

# Открытие порта
EXPOSE 8000

# Запуск Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "virtual_gallery.wsgi:application"]