from django.contrib import admin
from django.utils.html import format_html
from .models import Artist, Painting, BlogPost, ContactRequest, SiteContact


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'bio_preview')
    search_fields = ('name',)
    fields = ('name', 'bio', 'photo')

    def bio_preview(self, obj):
        return obj.bio[:50] + '...' if obj.bio else ''

    bio_preview.short_description = "Короткая био"

    def has_add_permission(self, request):
        # Singleton: не позволять добавлять больше одной записи
        return not Artist.objects.exists()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    list_display = ('title', 'creation_date', 'price', 'is_featured', 'thumbnail_preview')
    list_filter = ('is_featured', 'creation_date', 'price')
    search_fields = ('title', 'description')
    list_editable = ('is_featured', 'price')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'creation_date'
    actions = ['make_featured', 'remove_featured']
    fields = ('title', 'slug', 'description', 'creation_date', 'price', 'is_featured', 'image', 'small_image',
              'medium_image', 'large_image')
    readonly_fields = ('small_image', 'medium_image', 'large_image')  # Авто-генерируются, не редактировать вручную

    def thumbnail_preview(self, obj):
        if obj.small_image:
            return format_html('<img src="{}" width="100" height="75" />', obj.small_image.url)
        return "Нет изображения"

    thumbnail_preview.short_description = "Превью"

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    make_featured.short_description = "Сделать избранными"

    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)

    remove_featured.short_description = "Убрать из избранных"

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'content_preview')
    list_filter = ('pub_date',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'pub_date'
    fields = ('title', 'slug', 'content', 'image')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if obj.content else ''

    content_preview.short_description = "Превью содержания"

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'message_preview')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('name', 'email', 'message', 'created_at')  # Read-only, только просмотр/удаление
    fields = ('name', 'email', 'message', 'created_at')

    def message_preview(self, obj):
        return obj.message[:50] + '...' if obj.message else ''

    message_preview.short_description = "Превью сообщения"

    def has_add_permission(self, request):
        # Запретить добавление новых заявок в админке
        return False

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


@admin.register(SiteContact)
class SiteContactAdmin(admin.ModelAdmin):
    list_display = ('phone', 'email')

    def has_add_permission(self, request):
        # Singleton: не позволять добавлять больше одной записи
        return not SiteContact.objects.exists()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()
