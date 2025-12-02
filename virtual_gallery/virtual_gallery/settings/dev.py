from .base import *

# Разработка: включен debug-режим
DEBUG = True

# Разрешенные хосты для dev
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# База данных: локальный PostgreSQL для разработки, данные из .env
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'gallery_dev'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
