from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django import forms
from .models import Artist, Painting, BlogPost, ContactRequest, SiteContact, BlogPostImage


class BlogPostImageInlineFormSet(forms.BaseInlineFormSet):
    """
    Формсет для inline-изображений поста в блоге.

    Проверяет, чтобы обложка была добавлена, если есть дополнительные изображения.
    """

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        has_extra_images = any(
            form.cleaned_data and not form.cleaned_data.get('DELETE', False)
            for form in self.forms
        )
        if has_extra_images and not self.instance.cover_image:
            raise ValidationError("Добавьте обложку поста, если есть дополнительные изображения.")


class BlogPostImageInline(admin.TabularInline):
    """
    Inline-админ для изображений поста в блоге.

    Позволяет добавлять до 5 изображений, с валидацией через формсет.
    """
    model = BlogPostImage
    extra = 0
    fields = ('image',)
    max_num = 5
    formset = BlogPostImageInlineFormSet
    verbose_name = "Дополнительное изображение"
    verbose_name_plural = "Дополнительные изображения"


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели Artist.

    Поддерживает singleton: только одна запись о художнике.
    """
    list_display = ('name', 'bio_preview', 'photo_preview')
    search_fields = ('name',)
    fields = ('name', 'bio', 'photo')

    def bio_preview(self, obj):
        """Возвращает сокращенную версию биографии для списка (без '...' если текст короткий)."""
        if not obj.bio:
            return ''
        if len(obj.bio) > 60:
            return obj.bio[:60] + '...'
        return obj.bio

    bio_preview.short_description = "Краткая биография"

    def photo_preview(self, obj):
        """Отображает превью фото художника в списке."""
        if obj.photo:
            return format_html('<img src="{}" width="150" style="object-fit: cover;" />', obj.photo.url)
        return "Нет фото"

    photo_preview.short_description = "Фото"

    def has_add_permission(self, request):
        """Запрещает добавление, если запись уже существует (singleton)."""
        return not Artist.objects.exists()

    def delete_queryset(self, request, queryset):
        """Удаляет объекты с вызовом метода delete() для очистки файлов."""
        for obj in queryset:
            obj.delete()


@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели Painting.

    Включает превью изображений, действия для избранных, фильтры и поиск.
    """
    list_display = ('title', 'creation_date', 'price', 'is_featured', 'thumbnail_preview')
    list_filter = ('is_featured', 'creation_date')
    search_fields = ('title', 'description')
    list_editable = ('is_featured', 'price')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'creation_date'
    actions = ['make_featured', 'remove_featured']
    fields = (
        'title', 'slug', 'description', 'creation_date', 'price', 'is_featured',
        'image', 'small_image', 'medium_image', 'large_image'
    )
    readonly_fields = ('small_image', 'medium_image', 'large_image')

    def thumbnail_preview(self, obj):
        """Отображает превью маленького изображения в списке."""
        if obj.small_image:
            return format_html('<img src="{}" width="100" />', obj.small_image.url)
        return "Нет изображения"

    thumbnail_preview.short_description = "Превью"

    def make_featured(self, request, queryset):
        """Делает выбранные картины избранными."""
        queryset.update(is_featured=True)

    make_featured.short_description = "Сделать избранными"

    def remove_featured(self, request, queryset):
        """Убирает выбранные картины из избранных."""
        queryset.update(is_featured=False)

    remove_featured.short_description = "Убрать из избранных"

    def delete_queryset(self, request, queryset):
        """Удаляет объекты с вызовом метода delete() для очистки файлов."""
        for obj in queryset:
            obj.delete()


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели BlogPost.

    Включает inline для изображений, превью обложки и содержания.
    """
    list_display = ('title', 'pub_date', 'cover_preview', 'content_preview')
    list_filter = ('pub_date',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'pub_date'
    fields = ('title', 'slug', 'content', 'cover_image')
    inlines = [BlogPostImageInline]

    def cover_preview(self, obj):
        """Отображает превью обложки в списке."""
        if obj.cover_image:
            return format_html('<img src="{}" width="100" />', obj.cover_image.url)
        return "Нет обложки"

    cover_preview.short_description = "Обложка"

    def content_preview(self, obj):
        """Возвращает сокращенную версию содержания для списка (без '...' если текст короткий)."""
        if not obj.content:
            return ''
        if len(obj.content) > 60:
            return obj.content[:60] + '...'
        return obj.content

    content_preview.short_description = "Содержание"

    def delete_queryset(self, request, queryset):
        """Удаляет объекты с вызовом метода delete() для очистки файлов."""
        for obj in queryset:
            obj.delete()

    def save_model(self, request, obj, form, change):
        """Сохраняет модель с обработкой изображений."""
        super().save_model(request, obj, form, change)


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели ContactRequest.

    Только просмотр и удаление заявок, без добавления.
    """
    list_display = ('name', 'email', 'created_at', 'message_preview')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('name', 'email', 'message', 'created_at')
    fields = ('name', 'email', 'message', 'created_at')

    def message_preview(self, obj):
        """Возвращает сокращенную версию сообщения для списка (без '...' если текст короткий)."""
        if not obj.message:
            return ''
        if len(obj.message) > 60:
            return obj.message[:60] + '...'
        return obj.message

    message_preview.short_description = "Сообщение"

    def has_add_permission(self, request):
        """Запрещает добавление новых заявок в админке."""
        return False

    def delete_queryset(self, request, queryset):
        """Удаляет объекты (нет файлов, но для consistency)."""
        for obj in queryset:
            obj.delete()


@admin.register(SiteContact)
class SiteContactAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели SiteContact.

    Поддерживает singleton: только одна запись с контактами.
    """
    list_display = ('phone', 'email', 'has_vk', 'has_instagram', 'has_telegram')
    fieldsets = (
        ('Основные контакты', {
            'fields': ('phone', 'email')
        }),
        ('Социальные сети', {
            'fields': ('vk_link', 'instagram_link', 'telegram_link'),
            'description': '* Деятельность Meta Platforms Inc. и принадлежащих ей социальных сетей Facebook и Instagram запрещена на территории РФ.'
        }),
    )

    def has_vk(self, obj):
        """Проверяет наличие ссылки на VK."""
        return bool(obj.vk_link)

    has_vk.boolean = True
    has_vk.short_description = "VK"

    def has_instagram(self, obj):
        """Проверяет наличие ссылки на Instagram."""
        return bool(obj.instagram_link)

    has_instagram.boolean = True
    has_instagram.short_description = "Instagram"

    def has_telegram(self, obj):
        """Проверяет наличие ссылки на Telegram."""
        return bool(obj.telegram_link)

    has_telegram.boolean = True
    has_telegram.short_description = "Telegram"

    def has_add_permission(self, request):
        """Запрещает добавление, если запись уже существует (singleton)."""
        return not SiteContact.objects.exists()

    def delete_queryset(self, request, queryset):
        """Удаляет объекты (нет файлов, но для consistency)."""
        for obj in queryset:
            obj.delete()
