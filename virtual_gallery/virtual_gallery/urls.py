"""
URL-конфигурация для проекта virtual_gallery.

Список `urlpatterns` маршрутизирует URL к представлениям. Подробнее см.:
https://docs.djangoproject.com/en/5.2/topics/http/urls/

Примеры:
Функциональные представления:
    1. Импорт: from my_app import views
    2. Добавление URL: path('', views.home, name='home')

Классовые представления:
    1. Импорт: from other_app.views import Home
    2. Добавление URL: path('', Home.as_view(), name='home')

Включение другого URLconf:
    1. Импорт: from django.urls import include, path
    2. Добавление URL: path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Включаем URL из приложения core
]

# В режиме отладки: обслуживаем media и static файлы напрямую
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
