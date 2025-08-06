"""
ASGI-конфигурация для проекта virtual_gallery.

Экспонирует ASGI-приложение как переменную модуля под именем ``application``.

Подробнее об этом файле см. в документации:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'virtual_gallery.settings.dev')  # По умолчанию dev для локальной разработки

application = get_asgi_application()
