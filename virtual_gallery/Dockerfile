# Базовый образ: Python 3.12, лёгкий
FROM python:3.12-slim

# Отключаем создание .pyc и буферизацию логов
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Рабочая директория
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY . /app/

# Собираем статические файлы
RUN python manage.py collectstatic --noinput --settings=virtual_gallery.settings.prod

# Открываем порт для Gunicorn
EXPOSE 8000

# Запускаем Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "virtual_gallery.wsgi:application"]