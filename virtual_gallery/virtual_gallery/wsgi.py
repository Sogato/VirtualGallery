"""
WSGI-конфигурация для проекта virtual_gallery.

Экспонирует WSGI-приложение как переменную модуля под именем ``application``.

Подробнее об этом файле см. в документации:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'virtual_gallery.settings.prod')  # По умолчанию prod для deployment

application = get_wsgi_application()
