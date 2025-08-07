from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Конфигурация приложения 'core'.

    Устанавливает тип авто-поля по умолчанию и verbose_name для админки.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = "Виртуальная галерея"

    def ready(self):
        import core.signals  # Подключаем сигналы
