from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Artist, Painting, BlogPost, BlogPostImage


@receiver(pre_delete, sender=Artist)
def delete_artist_photo(sender, instance, **kwargs):
    """
    Удаляет фото художника перед удалением экземпляра модели Artist.
    """
    if instance.photo:
        instance.photo.delete(save=False)


@receiver(pre_delete, sender=Painting)
def delete_painting_images(sender, instance, **kwargs):
    """
    Удаляет все изображения картины (оригинал и генерируемые версии) перед удалением экземпляра модели Painting.
    """
    if instance.image:
        instance.image.delete(save=False)
    if instance.small_image:
        instance.small_image.delete(save=False)
    if instance.medium_image:
        instance.medium_image.delete(save=False)
    if instance.large_image:
        instance.large_image.delete(save=False)


@receiver(pre_delete, sender=BlogPost)
def delete_blog_post_cover(sender, instance, **kwargs):
    """
    Удаляет обложку поста в блоге перед удалением экземпляра модели BlogPost.
    """
    if instance.cover_image:
        instance.cover_image.delete(save=False)


@receiver(pre_delete, sender=BlogPostImage)
def delete_blog_post_image_files(sender, instance, **kwargs):
    """
    Удаляет дополнительное изображение поста в блоге перед удалением экземпляра модели BlogPostImage.
    """
    if instance.image:
        instance.image.delete(save=False)