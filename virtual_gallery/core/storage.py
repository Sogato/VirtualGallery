from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings


class OverwriteStorage(FileSystemStorage):
    """
    Кастомный storage для перезаписи файлов с одинаковыми именами.

    Удаляет существующий файл перед сохранением нового, чтобы избежать дубликатов с суффиксами.
    """

    def get_available_name(self, name, max_length=None):
        # Если файл с таким именем существует, удаляем его.
        full_path = os.path.join(settings.MEDIA_ROOT, name)
        if self.exists(name):
            os.remove(full_path)
        return name
