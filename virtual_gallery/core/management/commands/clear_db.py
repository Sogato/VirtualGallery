from django.core.management.base import BaseCommand
from core.models import Artist, Painting, BlogPost, SiteContact, ContactRequest, BlogPostImage

class Command(BaseCommand):
    help = 'Clear all data from the database'

    def handle(self, *args, **kwargs):
        confirmation = input("Are you sure you want to delete all data? (yes/no): ")
        if confirmation.lower() != 'yes':
            self.stdout.write(self.style.WARNING('Operation cancelled'))
            return

        # Цикл по объектам для вызова кастомного delete() с удалением файлов
        for obj in Artist.objects.all():
            obj.delete()
        for obj in SiteContact.objects.all():
            obj.delete()
        for obj in Painting.objects.all():
            obj.delete()
        for obj in BlogPost.objects.all():
            obj.delete()
        for obj in BlogPostImage.objects.all():
            obj.delete()  # Для удаления дополнительных изображений с файлами
        for obj in ContactRequest.objects.all():
            obj.delete()  # Для ContactRequest нет файлов, но на всякий

        self.stdout.write(self.style.SUCCESS('Database cleared successfully, including media files'))