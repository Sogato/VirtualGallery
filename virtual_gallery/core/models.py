from django.db import models
from django.utils.text import slugify
from PIL import Image
from PIL.Image import Resampling
from io import BytesIO
from django.core.files.base import ContentFile
import os
from .storage import OverwriteStorage


def crop_to_aspect(image, target_width, target_height):
    """
    Обрезает изображение до заданного соотношения сторон (target_width:target_height).

    Аргументы:
    image -- объект изображения Pillow.
    target_width -- целевая ширина в пикселях.
    target_height -- целевая высота в пикселях.

    Возвращает обрезанное изображение.
    """
    target_ratio = target_width / target_height
    current_width, current_height = image.size
    current_ratio = current_width / current_height

    if current_ratio > target_ratio:
        # Обрезаем по ширине, если изображение шире целевого соотношения.
        new_width = int(current_height * target_ratio)
        left = (current_width - new_width) // 2
        top = 0
        right = left + new_width
        bottom = current_height
    else:
        # Обрезаем по высоте, если изображение выше целевого соотношения.
        new_height = int(current_width / target_ratio)
        left = 0
        top = (current_height - new_height) // 2
        right = current_width
        bottom = top + new_height

    return image.crop((left, top, right, bottom))


def process_image(image_field, max_width=None, quality=85, crop_ratio=None, resize_size=None):
    """
    Обрабатывает изображение: обрезает (если указано), изменяет размер и сохраняет в формате WEBP.

    Аргументы:
    image_field -- поле модели с изображением.
    max_width -- максимальная ширина (если None, не применяется).
    quality -- качество сохранения WEBP (по умолчанию 85).
    crop_ratio -- кортеж (width, height) для обрезки (если None, не применяется).
    resize_size -- кортеж (width, height) для точного изменения размера (если None, не применяется).

    Возвращает None, но обновляет image_field.
    """
    if not image_field:
        return

    img = Image.open(image_field)
    try:
        if crop_ratio:
            # Обрезаем изображение до указанного соотношения.
            img = crop_to_aspect(img.copy(), *crop_ratio)

        if resize_size:
            # Изменяем размер до точных значений.
            img = img.resize(resize_size, Resampling.LANCZOS)
        elif max_width and img.width > max_width:
            # Изменяем размер, сохраняя пропорции, если ширина превышает максимум.
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Resampling.LANCZOS)

        # Сохраняем в WEBP и перезаписываем поле.
        io_buffer = BytesIO()
        img.save(io_buffer, format='WEBP', quality=quality)
        name = os.path.splitext(os.path.basename(image_field.name))[0] + '.webp'
        image_field.save(name, ContentFile(io_buffer.getvalue()), save=False)
    finally:
        img.close()  # Закрываем изображение для освобождения ресурсов.


class Artist(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Имя художника"
    )
    bio = models.TextField(
        blank=True,
        verbose_name="Краткая биография"
    )
    photo = models.ImageField(
        storage=OverwriteStorage(),
        upload_to='artist/',
        null=True,
        blank=True,
        verbose_name="Фото художника",
        help_text="Загрузите фотографию художника (будет обработана автоматически)."
    )

    class Meta:
        verbose_name = "Художник"
        verbose_name_plural = "Художник"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            # При обновлении: удаляем старое фото, если оно изменилось.
            old_self = Artist.objects.get(pk=self.pk)
            if old_self.photo and old_self.photo != self.photo:
                old_self.photo.delete(save=False)

        # Обрабатываем фото (только при создании или изменении поля): ресайз до 800 пикселей ширины, качество 90.
        if self.photo and (not self.pk or old_self.photo != self.photo):
            process_image(self.photo, max_width=800, quality=90)

        super().save(*args, **kwargs)


class Painting(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название картины"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    creation_date = models.DateField(
        verbose_name="Дата создания"
    )
    price = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Цена"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Избранная картина"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        verbose_name="URL-имя",
        help_text="Автоматически генерируется из названия для URL."
    )
    image = models.ImageField(
        upload_to='paintings/original/',
        verbose_name="Оригинальное изображение",
        help_text="Загрузите основное изображение картины (будет обработано)."
    )
    small_image = models.ImageField(
        upload_to='paintings/small/',
        null=True,
        blank=True,
        verbose_name="Маленькое изображение",
        help_text="Автоматически генерируется для каталога."
    )
    medium_image = models.ImageField(
        upload_to='paintings/medium/',
        null=True,
        blank=True,
        verbose_name="Среднее изображение",
        help_text="Автоматически генерируется для избранных."
    )
    large_image = models.ImageField(
        upload_to='paintings/large/',
        null=True,
        blank=True,
        verbose_name="Большое изображение",
        help_text="Автоматически генерируется для детальной страницы."
    )

    class Meta:
        verbose_name = "Картина"
        verbose_name_plural = "Картины"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk:
            # При обновлении: если оригинальное изображение изменилось, удаляем старые версии.
            old_self = Painting.objects.get(pk=self.pk)
            if old_self.image and old_self.image != self.image:
                if old_self.small_image:
                    old_self.small_image.delete(save=False)
                if old_self.medium_image:
                    old_self.medium_image.delete(save=False)
                if old_self.large_image:
                    old_self.large_image.delete(save=False)
                if old_self.image:
                    old_self.image.delete(save=False)

                # Если новый image пустой, очищаем генерируемые поля в БД
                if not self.image:
                    self.small_image = None
                    self.medium_image = None
                    self.large_image = None

        if not self.slug:
            # Генерируем уникальный slug на основе названия.
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Painting.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        if self.image and (
                not self.small_image or not self.medium_image or not self.large_image or self.image != getattr(self,
                                                                                                               '_original_image',
                                                                                                               None)
        ):
            img = Image.open(self.image)
            try:
                # Small: обрезка 4:3, ресайз 400x300, качество 80.
                small_img = crop_to_aspect(img.copy(), 400, 300)
                small_img = small_img.resize((400, 300), Resampling.LANCZOS)
                small_io = BytesIO()
                small_img.save(small_io, format='WEBP', quality=80)
                small_name = os.path.splitext(os.path.basename(self.image.name))[0] + '_small.webp'
                self.small_image.save(small_name, ContentFile(small_io.getvalue()), save=False)
                small_img.close()

                # Medium: обрезка 4:3, ресайз 800x600, качество 85.
                medium_img = crop_to_aspect(img.copy(), 800, 600)
                medium_img = medium_img.resize((800, 600), Resampling.LANCZOS)
                medium_io = BytesIO()
                medium_img.save(medium_io, format='WEBP', quality=85)
                medium_name = os.path.splitext(os.path.basename(self.image.name))[0] + '_medium.webp'
                self.medium_image.save(medium_name, ContentFile(medium_io.getvalue()), save=False)
                medium_img.close()

                # Large: без обрезки, ресайз до 1920 ширины, качество 90.
                large_img = img.copy()
                if large_img.width > 1920:
                    ratio = 1920 / large_img.width
                    new_height = int(large_img.height * ratio)
                    large_img = large_img.resize((1920, new_height), Resampling.LANCZOS)
                large_io = BytesIO()
                large_img.save(large_io, format='WEBP', quality=90)
                large_name = os.path.splitext(os.path.basename(self.image.name))[0] + '_large.webp'
                self.large_image.save(large_name, ContentFile(large_io.getvalue()), save=False)
                large_img.close()

                self._original_image = self.image
            finally:
                img.close()

        super().save(*args, **kwargs)


class BlogPost(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок поста"
    )
    content = models.TextField(
        verbose_name="Содержание"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        verbose_name="URL-имя",
        help_text="Автоматически генерируется из заголовка для URL."
    )
    cover_image = models.ImageField(
        storage=OverwriteStorage(),
        upload_to='blog/covers/',
        null=True,
        blank=True,
        verbose_name="Обложка поста",
        help_text="Загрузите изображение обложки (будет обработано автоматически)."
    )

    class Meta:
        verbose_name = "Пост в блоге"
        verbose_name_plural = "Посты в блоге"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        old_cover = None
        if self.pk:
            # При обновлении: удаляем старую обложку, если она изменилась.
            old_self = BlogPost.objects.get(pk=self.pk)
            old_cover = old_self.cover_image
            if old_cover and old_cover != self.cover_image:
                old_cover.delete(save=False)

        if not self.slug:
            # Генерируем уникальный slug на основе заголовка.
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        # Обрабатываем обложку (только при создании или изменении поля): ресайз до 800 пикселей ширины, качество 85.
        if self.cover_image and (not self.pk or old_cover != self.cover_image):
            process_image(self.cover_image, max_width=800, quality=85)

        super().save(*args, **kwargs)


class BlogPostImage(models.Model):
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Пост"
    )
    image = models.ImageField(
        storage=OverwriteStorage(),
        upload_to='blog/images/',
        null=True,
        blank=True,
        verbose_name="Изображение",
        help_text="Загрузите изображение для поста (будет обработано автоматически)."
    )

    class Meta:
        verbose_name = "Изображение поста"
        verbose_name_plural = "Изображения постов"

    def __str__(self):
        return f'Изображение для поста "{self.post.title}"'

    def save(self, *args, **kwargs):
        old_image = None
        if self.pk:
            # При обновлении: удаляем старое изображение, если оно изменилось.
            old_self = BlogPostImage.objects.get(pk=self.pk)
            old_image = old_self.image
            if old_image and old_image != self.image:
                old_image.delete(save=False)

        # Обрабатываем изображение (только при создании или изменении поля): ресайз до 800 пикселей ширины, качество 85.
        if self.image and (not self.pk or old_image != self.image):
            process_image(self.image, max_width=800, quality=85)

        super().save(*args, **kwargs)


class ContactRequest(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Имя"
    )
    email = models.EmailField(
        verbose_name="E-mail"
    )
    message = models.TextField(
        verbose_name="Сообщение"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Заявка на обратную связь"
        verbose_name_plural = "Заявки на обратную связь"

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d')}"


class SiteContact(models.Model):
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="E-mail"
    )
    vk_link = models.URLField(
        blank=True,
        verbose_name="Ссылка на VK",
        help_text="Полная ссылка, например: https://vk.com/username."
    )
    instagram_link = models.URLField(
        blank=True,
        verbose_name="Ссылка на Instagram*",
        help_text="Полная ссылка, например: https://instagram.com/username."
    )
    telegram_link = models.URLField(
        blank=True,
        verbose_name="Ссылка на Telegram",
        help_text="Полная ссылка, например: https://t.me/username."
    )

    class Meta:
        verbose_name = "Контактная информация"
        verbose_name_plural = "Контактная информация"

    def __str__(self):
        return "Контакты сайта"
