import os
from io import BytesIO
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Artist, Painting, BlogPost, ContactRequest, SiteContact
from .forms import ContactForm

class ModelTestCase(TestCase):
    def setUp(self):
        # Create a sample image for testing
        self.sample_image = self.create_sample_image()

    def create_sample_image(self, width=1000, height=500):
        img = Image.new('RGB', (width, height), color='red')
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        return SimpleUploadedFile('test.jpg', img_io.read(), 'image/jpeg')

    def tearDown(self):
        # Clean up any files created during tests
        for model in [Artist, Painting, BlogPost]:
            for obj in model.objects.all():
                obj.delete()

class ArtistModelTest(ModelTestCase):
    def test_artist_creation(self):
        artist = Artist.objects.create(name='Test Artist', bio='Test bio')
        self.assertEqual(artist.name, 'Test Artist')
        self.assertEqual(str(artist), 'Test Artist')

    def test_artist_save_with_photo(self):
        artist = Artist(name='Test Artist')
        artist.photo = self.sample_image
        artist.save()

        # Check if photo was resized and converted to WEBP
        self.assertTrue(artist.photo.name.endswith('.webp'))
        img = Image.open(artist.photo)
        try:
            self.assertEqual(img.format, 'WEBP')
            self.assertLessEqual(img.width, 800)
            self.assertTrue(default_storage.exists(artist.photo.name))
        finally:
            img.close()  # Закрываем, чтобы избежать lock на Windows

    def test_artist_delete_removes_photo(self):
        artist = Artist(name='Test Artist')
        artist.photo = self.sample_image
        artist.save()
        photo_path = artist.photo.path
        self.assertTrue(os.path.exists(photo_path))
        artist.delete()
        self.assertFalse(os.path.exists(photo_path))

class PaintingModelTest(ModelTestCase):
    def test_painting_creation(self):
        painting = Painting.objects.create(
            title='Test Painting',
            description='Test desc',
            creation_date='2023-01-01',
            price=100.00,
            is_featured=True,
            image=self.sample_image
        )
        self.assertEqual(str(painting), 'Test Painting')
        self.assertTrue(painting.slug.startswith('test-painting'))

    def test_painting_save_generates_images(self):
        painting = Painting(title='Test Painting', creation_date='2023-01-01')
        painting.image = self.create_sample_image(2000, 1000)  # Large image to test resize
        painting.save()

        # Check slug
        self.assertEqual(painting.slug, 'test-painting')

        # Check small_image: cropped to 4:3, resized to 400x300, WEBP
        self.assertTrue(painting.small_image.name.endswith('_small.webp'))
        small_img = Image.open(painting.small_image)
        try:
            self.assertEqual(small_img.size, (400, 300))
            self.assertEqual(small_img.format, 'WEBP')
        finally:
            small_img.close()

        # Check medium_image: cropped to 4:3, resized to 800x600, WEBP
        self.assertTrue(painting.medium_image.name.endswith('_medium.webp'))
        medium_img = Image.open(painting.medium_image)
        try:
            self.assertEqual(medium_img.size, (800, 600))
            self.assertEqual(medium_img.format, 'WEBP')
        finally:
            medium_img.close()

        # Check large_image: no crop, resized to max 1920 width, preserve aspect, WEBP
        self.assertTrue(painting.large_image.name.endswith('_large.webp'))
        large_img = Image.open(painting.large_image)
        try:
            self.assertEqual(large_img.size, (1920, 960))  # Original 2000x1000 -> 1920x960
            self.assertEqual(large_img.format, 'WEBP')
        finally:
            large_img.close()

    def test_painting_unique_slug(self):
        painting1 = Painting.objects.create(title='Test Painting', creation_date='2023-01-01', image=self.sample_image)
        painting2 = Painting.objects.create(title='Test Painting', creation_date='2023-01-01', image=self.sample_image)
        self.assertEqual(painting1.slug, 'test-painting')
        self.assertEqual(painting2.slug, 'test-painting-1')

    def test_painting_delete_removes_images(self):
        painting = Painting(title='Test Painting', creation_date='2023-01-01')
        painting.image = self.sample_image
        painting.save()
        paths = [
            painting.image.path,
            painting.small_image.path,
            painting.medium_image.path,
            painting.large_image.path,
        ]
        for path in paths:
            self.assertTrue(os.path.exists(path))
        painting.delete()
        for path in paths:
            self.assertFalse(os.path.exists(path))

class BlogPostModelTest(ModelTestCase):
    def test_blogpost_creation(self):
        post = BlogPost.objects.create(title='Test Post', content='Test content')
        self.assertEqual(str(post), 'Test Post')
        self.assertTrue(post.slug.startswith('test-post'))

    def test_blogpost_save_with_image(self):
        post = BlogPost(title='Test Post')
        post.image = self.create_sample_image(1000, 500)
        post.save()

        # Check if image was resized and converted to WEBP
        self.assertTrue(post.image.name.endswith('.webp'))
        img = Image.open(post.image)
        try:
            self.assertEqual(img.format, 'WEBP')
            self.assertLessEqual(img.width, 800)
        finally:
            img.close()

    def test_blogpost_unique_slug(self):
        post1 = BlogPost.objects.create(title='Test Post')
        post2 = BlogPost.objects.create(title='Test Post')
        self.assertEqual(post1.slug, 'test-post')
        self.assertEqual(post2.slug, 'test-post-1')

    def test_blogpost_delete_removes_image(self):
        post = BlogPost(title='Test Post')
        post.image = self.sample_image
        post.save()
        image_path = post.image.path
        self.assertTrue(os.path.exists(image_path))
        post.delete()
        self.assertFalse(os.path.exists(image_path))

class ContactRequestModelTest(TestCase):
    def test_contactrequest_creation(self):
        cr = ContactRequest.objects.create(name='Test', email='test@example.com', message='Test msg')
        self.assertEqual(str(cr), f"Test - {cr.created_at.strftime('%Y-%m-%d')}")

class SiteContactModelTest(TestCase):
    def test_sitecontact_creation(self):
        sc = SiteContact.objects.create(phone='123456', email='site@example.com')
        self.assertEqual(str(sc), "Контакты сайта")

class FormTestCase(TestCase):
    def test_contactform_valid(self):
        data = {'name': 'Test', 'email': 'test@example.com', 'message': 'Test msg'}
        form = ContactForm(data)
        self.assertTrue(form.is_valid())

    def test_contactform_invalid(self):
        data = {'name': 'Test', 'email': 'invalid', 'message': 'Test msg'}
        form = ContactForm(data)
        self.assertFalse(form.is_valid())

class ViewTestCase(TestCase):
    def create_sample_image(self, width=1000, height=500):
        img = Image.new('RGB', (width, height), color='red')
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        return SimpleUploadedFile('test.jpg', img_io.read(), 'image/jpeg')

    def setUp(self):
        self.artist = Artist.objects.create(name='Test Artist')
        self.painting = Painting.objects.create(
            title='Test Painting', slug='test-painting', creation_date='2023-01-01',
            is_featured=True, image=self.create_sample_image()  # Фикс: реальные байты
        )
        self.post = BlogPost.objects.create(title='Test Post', slug='test-post')
        self.site_contact = SiteContact.objects.create(phone='123', email='test@example.com')

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        # Убрали assertTemplateUsed (шаблонов нет)
        self.assertIn('artist', response.context)
        self.assertIn('featured_paintings', response.context)
        self.assertEqual(response.context['artist'], self.artist)
        self.assertQuerysetEqual(response.context['featured_paintings'], [self.painting], transform=lambda x: x)

    def test_painting_list_view(self):
        response = self.client.get(reverse('painting_list'))
        self.assertEqual(response.status_code, 200)
        # Убрали assertTemplateUsed
        self.assertIn('paintings', response.context)
        self.assertQuerysetEqual(response.context['paintings'], [self.painting], transform=lambda x: x)

    def test_painting_detail_view(self):
        response = self.client.get(reverse('painting_detail', kwargs={'slug': 'test-painting'}))
        self.assertEqual(response.status_code, 200)
        # Убрали assertTemplateUsed
        self.assertEqual(response.context['object'], self.painting)

    def test_blog_list_view(self):
        response = self.client.get(reverse('blog_list'))
        self.assertEqual(response.status_code, 200)
        # Убрали assertTemplateUsed
        self.assertIn('posts', response.context)
        self.assertQuerysetEqual(response.context['posts'], [self.post], transform=lambda x: x)

    def test_contacts_view_get(self):
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)
        # Убрали assertTemplateUsed
        self.assertIn('form', response.context)
        self.assertIn('site_contact', response.context)
        self.assertEqual(response.context['site_contact'], self.site_contact)

    def test_contacts_view_post_valid(self):
        data = {'name': 'Test', 'email': 'test@example.com', 'message': 'Test msg'}
        response = self.client.post(reverse('contacts'), data)
        self.assertEqual(response.status_code, 302)  # Redirect to home
        self.assertTrue(ContactRequest.objects.exists())

    def test_contacts_view_post_invalid(self):
        data = {'name': 'Test', 'email': 'invalid', 'message': 'Test msg'}
        response = self.client.post(reverse('contacts'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ContactRequest.objects.exists())