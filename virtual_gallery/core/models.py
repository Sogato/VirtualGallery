from django.db import models
from django.utils.text import slugify
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


def crop_to_aspect(image, target_width, target_height):
    """Обрезает изображение до заданного соотношения сторон (target_width:target_height)."""
    target_ratio = target_width / target_height
    current_width, current_height = image.size
    current_ratio = current_width / current_height

    if current_ratio > target_ratio:
        new_width = int(current_height * target_ratio)
        left = (current_width - new_width) // 2
        top = 0
        right = left + new_width
        bottom = current_height
    else:
        new_height = int(current_width / target_ratio)
        left = 0
        top = (current_height - new_height) // 2
        right = current_width
        bottom = top + new_height

    return image.crop((left, top, right, bottom))


class Artist(models.Model):
    name = models.CharField(max_length=200, verbose_name="Имя художника")
    bio = models.TextField(blank=True, verbose_name="Короткая информация")
    photo = models.ImageField(upload_to='artist/', null=True, blank=True, verbose_name="Фото художника")

    class Meta:
        verbose_name = "Художник"
        verbose_name_plural = "Художники"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.photo:
            # Открываем загруженное изображение
            img = Image.open(self.photo)
            # Resize без crop, max 800 width, preserve aspect
            if img.width > 800:
                ratio = 800 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((800, new_height), Image.LANCZOS)
            # Сохраняем в WEBP и перезаписываем photo
            io = BytesIO()
            img.save(io, format='WEBP', quality=90)
            name = os.path.splitext(os.path.basename(self.photo.name))[0] + '.webp'
            self.photo.save(name, ContentFile(io.getvalue()), save=False)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        path = self.photo.path if self.photo else None
        super().delete(*args, **kwargs)
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Ошибка при удалении файла {path}: {e}")


class Painting(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    creation_date = models.DateField(verbose_name="Дата создания")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена")
    is_featured = models.BooleanField(default=False, verbose_name="Избранная")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL-имя")
    image = models.ImageField(upload_to='paintings/original/', verbose_name="Оригинальное изображение")
    small_image = ProcessedImageField(
        upload_to='paintings/small/',
        processors=[ResizeToFill(400, 300)],
        format='WEBP',
        options={'quality': 80},
        null=True,
        blank=True,
        verbose_name="Маленькое изображение (для каталога)"
    )
    medium_image = ProcessedImageField(
        upload_to='paintings/medium/',
        processors=[ResizeToFill(800, 600)],
        format='WEBP',
        options={'quality': 85},
        null=True,
        blank=True,
        verbose_name="Среднее изображение (для избранного)"
    )
    large_image = ProcessedImageField(
        upload_to='paintings/large/',
        processors=[ResizeToFill(1920, 1440)],  # Placeholder, но в save переопределим без crop
        format='WEBP',
        options={'quality': 90},
        null=True,
        blank=True,
        verbose_name="Большое изображение (для страницы)"
    )

    class Meta:
        verbose_name = "Картина"
        verbose_name_plural = "Картины"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Painting.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        if self.image and (not self.small_image or not self.medium_image or not self.large_image or self.image != getattr(self, '_original_image', None)):
            img = Image.open(self.image)

            # Small: crop 4:3, resize 400x300, WEBP quality 80
            small_img = crop_to_aspect(img.copy(), 400, 300)
            small_img = small_img.resize((400, 300), Image.LANCZOS)
            small_io = BytesIO()
            small_img.save(small_io, format='WEBP', quality=80)
            small_name = os.path.splitext(os.path.basename(self.image.name))[0] + '_small.webp'
            self.small_image.save(small_name, ContentFile(small_io.getvalue()), save=False)

            # Medium: crop 4:3, resize 800x600, WEBP quality 85
            medium_img = crop_to_aspect(img.copy(), 800, 600)
            medium_img = medium_img.resize((800, 600), Image.LANCZOS)
            medium_io = BytesIO()
            medium_img.save(medium_io, format='WEBP', quality=85)
            medium_name = os.path.splitext(os.path.basename(self.image.name))[0] + '_medium.webp'
            self.medium_image.save(medium_name, ContentFile(medium_io.getvalue()), save=False)

            # Large: NO crop, resize to max 1920 width, preserve aspect, WEBP quality 90
            large_img = img.copy()
            if large_img.width > 1920:
                ratio = 1920 / large_img.width
                new_height = int(large_img.height * ratio)
                large_img = large_img.resize((1920, new_height), Image.LANCZOS)
            large_io = BytesIO()
            large_img.save(large_io, format='WEBP', quality=90)
            large_name = os.path.splitext(os.path.basename(self.image.name))[0] + '_large.webp'
            self.large_image.save(large_name, ContentFile(large_io.getvalue()), save=False)

            self._original_image = self.image

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        paths = [
            self.image.path if self.image else None,
            self.small_image.path if self.small_image else None,
            self.medium_image.path if self.medium_image else None,
            self.large_image.path if self.large_image else None,
        ]
        super().delete(*args, **kwargs)
        for path in paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Ошибка при удалении файла {path}: {e}")


class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL-имя")
    image = models.ImageField(upload_to='blog/', null=True, blank=True, verbose_name="Изображение для поста")

    class Meta:
        verbose_name = "Пост в блоге"
        verbose_name_plural = "Посты в блоге"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        if self.image:
            # Открываем загруженное изображение
            img = Image.open(self.image)
            # Resize без crop, max 800 width, preserve aspect (оригинальный формат)
            if img.width > 800:
                ratio = 800 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((800, new_height), Image.LANCZOS)
            # Сохраняем в WEBP и перезаписываем image
            io = BytesIO()
            img.save(io, format='WEBP', quality=85)
            name = os.path.splitext(os.path.basename(self.image.name))[0] + '.webp'
            self.image.save(name, ContentFile(io.getvalue()), save=False)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        path = self.image.path if self.image else None
        super().delete(*args, **kwargs)
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Ошибка при удалении файла {path}: {e}")


class ContactRequest(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="E-mail")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заявка на обратную связь"
        verbose_name_plural = "Заявки на обратную связь"

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d')}"


class SiteContact(models.Model):
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="E-mail")

    class Meta:
        verbose_name = "Контактная информация сайта"
        verbose_name_plural = "Контактная информация сайта"

    def __str__(self):
        return "Контакты сайта"