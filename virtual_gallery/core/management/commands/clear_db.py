from django.core.management.base import BaseCommand
from core.models import Artist, Painting, BlogPost, SiteContact, ContactRequest, BlogPostImage


class Command(BaseCommand):
    help = 'Clear all data from the database, including associated media files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation prompt'
        )

    def handle(self, *args, **options):
        if not options['force']:
            confirmation = input(
                "Are you sure you want to delete ALL data (including media files)? This is irreversible! (yes/no): ")
            if confirmation.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Operation cancelled'))
                return

        # Сначала удаляем BlogPostImage (чтобы вызвать delete() и удалить файлы)
        deleted_images = BlogPostImage.objects.count()
        for obj in BlogPostImage.objects.all():
            obj.delete()

        # Затем удаляем BlogPost (каскад уже не нужен, но если что — сработает)
        deleted_posts = BlogPost.objects.count()
        for obj in BlogPost.objects.all():
            obj.delete()

        # Удаляем Paintings (с файлами изображений)
        deleted_paintings = Painting.objects.count()
        for obj in Painting.objects.all():
            obj.delete()

        # Удаляем singleton'ы
        deleted_artists = Artist.objects.count()
        for obj in Artist.objects.all():
            obj.delete()
        deleted_contacts = SiteContact.objects.count()
        for obj in SiteContact.objects.all():
            obj.delete()

        # Удаляем ContactRequests (без файлов)
        deleted_requests = ContactRequest.objects.count()
        for obj in ContactRequest.objects.all():
            obj.delete()

        if deleted_artists + deleted_contacts + deleted_paintings + deleted_posts + deleted_images + deleted_requests == 0:
            self.stdout.write(self.style.NOTICE('Database was already empty'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Database cleared successfully: '
                f'{deleted_artists} Artists, '
                f'{deleted_contacts} SiteContacts, '
                f'{deleted_paintings} Paintings, '
                f'{deleted_posts} BlogPosts, '
                f'{deleted_images} BlogPostImages, '
                f'{deleted_requests} ContactRequests deleted (including media files)'
            ))
