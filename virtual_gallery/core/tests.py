import os
from io import BytesIO
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Artist, Painting, BlogPost, BlogPostImage, ContactRequest, SiteContact
from .forms import ContactForm


class BaseTestCase(TestCase):
    """
    Базовый класс для тестов, с методами для создания тестовых изображений и очисткой.
    """

    def create_sample_image(self, width=1000, height=500, format='JPEG'):
        """
        Создает простое тестовое изображение с заданными размерами.
        """
        img = Image.new('RGB', (width, height), color='red')
        img_io = BytesIO()
        img.save(img_io, format=format)
        img_io.seek(0)
        return SimpleUploadedFile(f'test.{format.lower()}', img_io.read(), f'image/{format.lower()}')

    def tearDown(self):
        """
        Очистка после каждого теста: удаление всех объектов моделей для вызова delete() и удаления файлов.
        """
        for model in [Artist, Painting, BlogPost, BlogPostImage, ContactRequest, SiteContact]:
            for obj in model.objects.all():
                obj.delete()


class ArtistModelTest(BaseTestCase):
    """
    Тесты для модели Artist.
    """

    def test_artist_creation_without_photo(self):
        """Тест создания художника без фото."""
        artist = Artist.objects.create(name='Test Artist', bio='Test bio')
        self.assertEqual(artist.name, 'Test Artist')
        self.assertEqual(artist.bio, 'Test bio')
        self.assertEqual(str(artist), 'Test Artist')
        self.assertFalse(artist.photo)  # Нет фото

    def test_artist_creation_with_photo(self):
        """Тест создания художника с фото: проверка обработки (resize, WEBP)."""
        artist = Artist(name='Test Artist', bio='Test bio')
        artist.photo = self.create_sample_image(width=1000, height=500)
        artist.save()

        self.assertTrue(artist.photo.name.endswith('.webp'))
        img = Image.open(artist.photo)
        try:
            self.assertEqual(img.format, 'WEBP')
            self.assertLessEqual(img.width, 800)  # Resize до max 800 ширины
            self.assertEqual(img.height, 400)  # Пропорции сохранены (1000x500 -> 800x400)
            self.assertTrue(default_storage.exists(artist.photo.name))
        finally:
            img.close()

    def test_artist_save_with_large_photo(self):
        """Тест обработки большого фото: resize сохраняет пропорции."""
        artist = Artist(name='Test Artist')
        artist.photo = self.create_sample_image(width=2000, height=1000)
        artist.save()

        img = Image.open(artist.photo)
        try:
            self.assertEqual(img.size, (800, 400))  # 2000x1000 -> 800x400
        finally:
            img.close()

    def test_artist_delete_removes_photo(self):
        """Тест удаления: фото удаляется из storage."""
        artist = Artist(name='Test Artist')
        artist.photo = self.create_sample_image()
        artist.save()
        photo_path = artist.photo.path
        self.assertTrue(os.path.exists(photo_path))
        artist.delete()
        self.assertFalse(os.path.exists(photo_path))

    def test_artist_update_photo(self):
        """Тест обновления фото: новое обрабатывается."""
        artist = Artist.objects.create(name='Test Artist')
        old_photo = self.create_sample_image()
        artist.photo = old_photo
        artist.save()

        new_photo = self.create_sample_image(width=1200, height=600)
        artist.photo = new_photo
        artist.save()
        self.assertTrue(artist.photo.name.endswith('.webp'))
        self.assertLessEqual(Image.open(artist.photo).width, 800)


class PaintingModelTest(BaseTestCase):
    """
    Тесты для модели Painting.
    """

    def test_painting_creation_without_image(self):
        """Тест создания картины без изображения."""
        painting = Painting.objects.create(
            title='Test Painting',
            description='Test desc',
            creation_date='2023-01-01',
            price=100,
            is_featured=True
        )
        self.assertEqual(str(painting), 'Test Painting')
        self.assertEqual(painting.slug, 'test-painting')
        self.assertFalse(painting.image)
        self.assertFalse(painting.small_image)
        self.assertFalse(painting.medium_image)
        self.assertFalse(painting.large_image)

    def test_painting_creation_with_image(self):
        """Тест создания с изображением: генерация small/medium/large, slug."""
        painting = Painting(
            title='Test Painting',
            creation_date='2023-01-01',
            image=self.create_sample_image(width=1000, height=500)
        )
        painting.save()

        self.assertEqual(painting.slug, 'test-painting')

        # Small: crop 4:3 (400:300), resize 400x300, WEBP
        self.assertTrue(painting.small_image.name.endswith('_small.webp'))
        small_img = Image.open(painting.small_image)
        try:
            self.assertEqual(small_img.size, (400, 300))
            self.assertEqual(small_img.format, 'WEBP')
        finally:
            small_img.close()

        # Medium: crop 4:3 (800:600), resize 800x600, WEBP
        self.assertTrue(painting.medium_image.name.endswith('_medium.webp'))
        medium_img = Image.open(painting.medium_image)
        try:
            self.assertEqual(medium_img.size, (800, 600))
            self.assertEqual(medium_img.format, 'WEBP')
        finally:
            medium_img.close()

        # Large: no crop, resize max 1920 width, WEBP (original 1000x500 -> no resize)
        self.assertTrue(painting.large_image.name.endswith('_large.webp'))
        large_img = Image.open(painting.large_image)
        try:
            self.assertEqual(large_img.size, (1000, 500))
            self.assertEqual(large_img.format, 'WEBP')
        finally:
            large_img.close()

    def test_painting_save_with_large_image(self):
        """Тест с большим изображением: проверка resize large."""
        painting = Painting(title='Test Painting', creation_date='2023-01-01')
        painting.image = self.create_sample_image(width=2000, height=1000)
        painting.save()

        large_img = Image.open(painting.large_image)
        try:
            self.assertEqual(large_img.size, (1920, 960))  # Resize to 1920 width
        finally:
            large_img.close()

    def test_painting_crop_for_small_medium(self):
        """Тест обрезки: для изображения с другим соотношением."""
        # Изображение шире 4:3 (2000x1000 = 2:1 > 4:3≈1.33)
        painting = Painting(title='Test Wide', creation_date='2023-01-01')
        painting.image = self.create_sample_image(width=2000, height=1000)
        painting.save()

        small_img = Image.open(painting.small_image)
        try:
            self.assertEqual(small_img.size, (400, 300))
        finally:
            small_img.close()

        # Для высокого изображения (500x1000 = 0.5 <1.33)
        painting_high = Painting(title='Test High', creation_date='2023-01-01')
        painting_high.image = self.create_sample_image(width=500, height=1000)
        painting_high.save()

        small_high = Image.open(painting_high.small_image)
        try:
            self.assertEqual(small_high.size, (400, 300))
        finally:
            small_high.close()

    def test_painting_unique_slug(self):
        """Тест уникальности slug: добавление суффикса."""
        painting1 = Painting.objects.create(title='Test Painting', creation_date='2023-01-01',
                                            image=self.create_sample_image())
        painting2 = Painting.objects.create(title='Test Painting', creation_date='2023-01-01',
                                            image=self.create_sample_image())
        painting3 = Painting.objects.create(title='Test Painting', creation_date='2023-01-01',
                                            image=self.create_sample_image())
        self.assertEqual(painting1.slug, 'test-painting')
        self.assertEqual(painting2.slug, 'test-painting-1')
        self.assertEqual(painting3.slug, 'test-painting-2')

    def test_painting_update_image(self):
        """Тест обновления изображения: генерация новых версий."""
        painting = Painting.objects.create(title='Test Painting', creation_date='2023-01-01',
                                           image=self.create_sample_image())

        new_image = self.create_sample_image(width=1200, height=600)
        painting.image = new_image
        painting.save()

    def test_painting_delete_removes_images(self):
        """Тест удаления: все изображения удаляются."""
        painting = Painting(title='Test Painting', creation_date='2023-01-01')
        painting.image = self.create_sample_image()
        painting.save()
        paths = [
            painting.image.path,
            painting.small_image.path if painting.small_image else None,
            painting.medium_image.path if painting.medium_image else None,
            painting.large_image.path if painting.large_image else None,
        ]
        for path in paths:
            if path:
                self.assertTrue(os.path.exists(path))
        painting.delete()
        for path in paths:
            if path:
                self.assertFalse(os.path.exists(path))


class BlogPostModelTest(BaseTestCase):
    """
    Тесты для модели BlogPost.
    """

    def test_blogpost_creation_without_cover(self):
        """Тест создания поста без обложки."""
        post = BlogPost.objects.create(title='Test Post', content='Test content')
        self.assertEqual(str(post), 'Test Post')
        self.assertEqual(post.slug, 'test-post')
        self.assertFalse(post.cover_image)

    def test_blogpost_creation_with_cover(self):
        """Тест создания с обложкой: обработка (resize, WEBP)."""
        post = BlogPost(title='Test Post', content='Test content')
        post.cover_image = self.create_sample_image(width=1000, height=500)
        post.save()

        self.assertEqual(post.slug, 'test-post')
        self.assertTrue(post.cover_image.name.endswith('.webp'))
        img = Image.open(post.cover_image)
        try:
            self.assertEqual(img.format, 'WEBP')
            self.assertLessEqual(img.width, 800)
            self.assertEqual(img.height, 400)  # Пропорции
        finally:
            img.close()

    def test_blogpost_unique_slug(self):
        """Тест уникальности slug."""
        post1 = BlogPost.objects.create(title='Test Post')
        post2 = BlogPost.objects.create(title='Test Post')
        self.assertEqual(post1.slug, 'test-post')
        self.assertEqual(post2.slug, 'test-post-1')

    def test_blogpost_delete_removes_cover(self):
        """Тест удаления: обложка удаляется."""
        post = BlogPost(title='Test Post')
        post.cover_image = self.create_sample_image()
        post.save()
        path = post.cover_image.path
        self.assertTrue(os.path.exists(path))
        post.delete()
        self.assertFalse(os.path.exists(path))


class BlogPostImageModelTest(BaseTestCase):
    """
    Тесты для модели BlogPostImage.
    """

    def setUp(self):
        super().setUp()
        self.post = BlogPost.objects.create(title='Test Post')

    def test_blogpostimage_creation_without_image(self):
        """Тест создания изображения поста без файла."""
        image = BlogPostImage.objects.create(post=self.post)
        self.assertEqual(str(image), f'Изображение для поста "{self.post.title}"')

    def test_blogpostimage_creation_with_image(self):
        """Тест с изображением: обработка (resize, WEBP)."""
        bpi = BlogPostImage(post=self.post)
        bpi.image = self.create_sample_image(width=1000, height=500)
        bpi.save()

        self.assertTrue(bpi.image.name.endswith('.webp'))
        img = Image.open(bpi.image)
        try:
            self.assertEqual(img.format, 'WEBP')
            self.assertLessEqual(img.width, 800)
            self.assertEqual(img.height, 400)
        finally:
            img.close()

    def test_blogpostimage_delete_removes_image(self):
        """Тест удаления: изображение удаляется."""
        bpi = BlogPostImage(post=self.post)
        bpi.image = self.create_sample_image()
        bpi.save()
        path = bpi.image.path
        self.assertTrue(os.path.exists(path))
        bpi.delete()
        self.assertFalse(os.path.exists(path))

    def test_cascade_delete_with_post(self):
        """Тест каскадного удаления: при удалении поста изображения удаляются."""
        bpi = BlogPostImage(post=self.post, image=self.create_sample_image())
        bpi.save()
        path = bpi.image.path
        self.assertTrue(os.path.exists(path))
        self.post.delete()
        self.assertFalse(BlogPostImage.objects.exists())


class ContactRequestModelTest(BaseTestCase):
    """
    Тесты для модели ContactRequest.
    """

    def test_contactrequest_creation(self):
        """Тест создания заявки."""
        cr = ContactRequest.objects.create(name='Test', email='test@example.com', message='Test msg')
        self.assertEqual(str(cr), f"{cr.name} - {cr.created_at.strftime('%Y-%m-%d')}")


class SiteContactModelTest(BaseTestCase):
    """
    Тесты для модели SiteContact.
    """

    def test_sitecontact_creation(self):
        """Тест создания контактов сайта."""
        sc = SiteContact.objects.create(phone='123456', email='site@example.com', vk_link='https://vk.com/test')
        self.assertEqual(str(sc), "Контакты сайта")
        self.assertEqual(sc.phone, '123456')


class FormTestCase(BaseTestCase):
    """
    Тесты для форм.
    """

    def test_contactform_valid(self):
        """Тест валидной формы контактов."""
        data = {'name': 'Test', 'email': 'test@example.com', 'message': 'Test msg'}
        form = ContactForm(data)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.name, 'Test')

    def test_contactform_invalid_email(self):
        """Тест инвалидной формы: неверный email."""
        data = {'name': 'Test', 'email': 'invalid', 'message': 'Test msg'}
        form = ContactForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_contactform_missing_fields(self):
        """Тест инвалидной формы: пустые поля."""
        data = {'name': '', 'email': '', 'message': ''}
        form = ContactForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('message', form.errors)


class ViewTestCase(BaseTestCase):
    """
    Тесты для представлений (views).
    """

    def setUp(self):
        super().setUp()
        self.artist = Artist.objects.create(name='Test Artist', bio='Bio')
        self.painting1 = Painting.objects.create(
            title='Featured Painting', slug='featured-painting', creation_date='2023-02-01',
            is_featured=True, image=self.create_sample_image()
        )
        self.painting2 = Painting.objects.create(
            title='Regular Painting', slug='regular-painting', creation_date='2023-01-01',
            is_featured=False, image=self.create_sample_image()
        )
        self.post1 = BlogPost.objects.create(title='Post 1', slug='post-1', content='Content 1')
        self.post2 = BlogPost.objects.create(title='Post 2', slug='post-2', content='Content 2')
        BlogPostImage.objects.create(post=self.post1, image=self.create_sample_image())
        self.site_contact = SiteContact.objects.create(phone='123', email='test@example.com')

    def test_home_view(self):
        """Тест главной страницы: контекст с художником и избранными картинами."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('artist', response.context)
        self.assertIn('featured_paintings', response.context)
        self.assertEqual(response.context['artist'], self.artist)
        self.assertQuerySetEqual(
            response.context['featured_paintings'],
            [self.painting1],  # Только featured, ordered by -creation_date
            transform=lambda x: x
        )

    def test_painting_list_view(self):
        """Тест списка картин: все картины, ordered by -creation_date."""
        response = self.client.get(reverse('painting_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('paintings', response.context)
        self.assertQuerySetEqual(
            response.context['paintings'],
            [self.painting1, self.painting2],  # Новые сначала
            transform=lambda x: x
        )

    def test_painting_detail_view(self):
        """Тест детальной страницы картины: по slug."""
        response = self.client.get(reverse('painting_detail', kwargs={'slug': 'featured-painting'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.painting1)

    def test_painting_detail_view_invalid_slug(self):
        """Тест детальной страницы: 404 для неверного slug."""
        response = self.client.get(reverse('painting_detail', kwargs={'slug': 'invalid'}))
        self.assertEqual(response.status_code, 404)

    def test_blog_list_view(self):
        """Тест списка блога: посты с prefetch images, ordered by -pub_date."""
        response = self.client.get(reverse('blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.context)
        posts = list(response.context['posts'])
        images = [list(p.images.all()) for p in posts]
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0], self.post2)  # Новые сначала (post2 created after post1)

    def test_contacts_view_get(self):
        """Тест страницы контактов: GET с формой и site_contact."""
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('site_contact', response.context)
        self.assertEqual(response.context['site_contact'], self.site_contact)
        self.assertIsInstance(response.context['form'], ContactForm)

    def test_contacts_view_post_valid(self):
        """Тест POST валидной формы: сохранение и редирект."""
        data = {'name': 'Test', 'email': 'test@example.com', 'message': 'Test msg'}
        response = self.client.post(reverse('contacts'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        self.assertTrue(ContactRequest.objects.exists())
        cr = ContactRequest.objects.first()
        self.assertEqual(cr.name, 'Test')

    def test_contacts_view_post_invalid(self):
        """Тест POST инвалидной формы: не сохраняет, возвращает 200."""
        data = {'name': 'Test', 'email': 'invalid', 'message': 'Test msg'}
        response = self.client.post(reverse('contacts'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ContactRequest.objects.exists())
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
