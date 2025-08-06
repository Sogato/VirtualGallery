from django.core.management.base import BaseCommand
from core.models import Artist, Painting, BlogPost, SiteContact, ContactRequest, BlogPostImage


class Command(BaseCommand):
    """
    Команда для очистки всех данных из базы данных, включая связанные медиа-файлы.

    Удаляет объекты моделей по порядку, вызывая метод delete() для каждого, чтобы обеспечить удаление файлов.
    Поддерживает флаг --force для пропуска подтверждения.
    """
    help = 'Очищает базу данных от всех данных, включая медиа-файлы'

    def add_arguments(self, parser):
        """
        Добавляет аргументы команды: --force для принудительного удаления без подтверждения.
        """
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительное удаление без запроса подтверждения'
        )

    def handle(self, *args, **options):
        """
        Основной метод команды: запрашивает подтверждение (если не --force) и удаляет данные.
        """
        if not options['force']:
            confirmation = input(
                "Вы уверены, что хотите удалить ВСЕ данные (включая медиа-файлы)? Это необратимо! (yes/no): ")
            if confirmation.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Операция отменена'))
                return

        # Удаляем по порядку: сначала зависимые модели, чтобы избежать каскадных проблем
        deleted_images = self._delete_model(BlogPostImage)
        deleted_posts = self._delete_model(BlogPost)
        deleted_paintings = self._delete_model(Painting)
        deleted_artists = self._delete_model(Artist)
        deleted_contacts = self._delete_model(SiteContact)
        deleted_requests = self._delete_model(ContactRequest)

        total_deleted = deleted_artists + deleted_contacts + deleted_paintings + deleted_posts + deleted_images + deleted_requests
        if total_deleted == 0:
            self.stdout.write(self.style.NOTICE('База данных уже была пустой'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'База данных успешно очищена: '
                f'{deleted_artists} Художников, '
                f'{deleted_contacts} Контактных информаций, '
                f'{deleted_paintings} Картин, '
                f'{deleted_posts} Постов в блоге, '
                f'{deleted_images} Изображений постов, '
                f'{deleted_requests} Заявок на связь удалено (включая медиа-файлы)'
            ))

    def _delete_model(self, model):
        """
        Вспомогательный метод: удаляет все объекты указанной модели, вызывая delete() для каждого.

        Возвращает количество удаленных объектов.
        """
        count = model.objects.count()
        for obj in model.objects.all():
            obj.delete()
        return count
