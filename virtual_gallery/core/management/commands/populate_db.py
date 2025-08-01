import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.core.files import File
from core.models import Artist, Painting, BlogPost, SiteContact, ContactRequest, BlogPostImage
from django.utils.text import slugify
from unidecode import unidecode  # Для правильной транслитерации русского в slugs
import os

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        # Artist (singleton)
        if not Artist.objects.exists():
            artist = Artist(
                name='Иван Иванович Петров',
                bio='Иван Петров - талантливый художник из Новосибирска, специализирующийся на пейзажах и абстрактном искусстве. Его работы выставлялись в галереях Москвы и Санкт-Петербурга. Родился в 1980 году, окончил художественную академию.'
            )
            # Assume photo in media/sample_images/artist_photo (any format)
            photo_path = os.path.join('media', 'sample_images', 'artist_photo')
            for ext in ['.webp', '.jpg', '.png']:  # Проверяем возможные расширения
                full_path = photo_path + ext
                if os.path.exists(full_path):
                    artist.photo = File(open(full_path, 'rb'), name=os.path.basename(full_path))
                    break
            else:
                self.stdout.write(self.style.WARNING('Artist photo not found in media/sample_images/artist_photo (any format)'))
            artist.save()  # Вызываем save модели для обработки
            self.stdout.write(self.style.SUCCESS('Created Artist'))

        # SiteContact (singleton)
        if not SiteContact.objects.exists():
            site_contact = SiteContact(
                phone='+7 (123) 456-78-90',
                email='info@artgallery.ru'
            )
            site_contact.save()
            self.stdout.write(self.style.SUCCESS('Created SiteContact'))

        # Paintings (14 штук)
        painting_titles = [
            'Закат над рекой', 'Горный пейзаж', 'Абстрактная гармония', 'Портрет незнакомки',
            'Морской бриз', 'Лесная тропа', 'Городские огни', 'Цветы в вазе',
            'Зимний лес', 'Летний дождь', 'Осенние листья', 'Весенний цвет',
            'Ночной небо', 'Речной туман'
        ]
        descriptions = [
            'Красивый пейзаж с теплыми тонами заката, отражающимися в воде реки.',
            'Мощные горы на фоне голубого неба, с элементами реализма.',
            'Абстрактная композиция в синих и зеленых тонах, передающая спокойствие.',
            'Таинственный портрет женщины с выразительными глазами.',
            'Морской вид с волнами и парусами, полный свежести.',
            'Тихая тропинка в густом лесу, с лучами солнца.',
            'Ночной город с яркими огнями и силуэтами зданий.',
            'Натюрморт с яркими цветами в стеклянной вазе.',
            'Снежный лес с деревьями в инее, зимняя сказка.',
            'Дождливый летний день в парке, с мокрыми листьями.',
            'Яркие осенние цвета в лесу, с падающими листьями.',
            'Цветущий сад весной, полный жизни и красок.',
            'Звездное небо над полем, с млечным путем.',
            'Туман над рекой на рассвете, загадочный и спокойный.'
        ]
        image_path = os.path.join('media', 'sample_images', 'painting_image')  # Без расширения

        for i in range(14):
            price_choice = random.choice([None, 'price'])
            price = None if price_choice is None else random.randrange(2000, 10001, 100)
            painting = Painting(
                title=painting_titles[i],
                description=descriptions[i],
                creation_date=date.today() - timedelta(days=random.randint(1, 365*5)),
                price=price,
                is_featured=random.choice([True, False])
            )
            # Slug с транслитерацией
            painting.slug = slugify(unidecode(painting.title))
            for ext in ['.jpg', '.webp', '.png']:  # Проверяем возможные расширения
                full_path = image_path + ext
                if os.path.exists(full_path):
                    painting.image = File(open(full_path, 'rb'), name=f'painting_image_{i}{ext}')
                    break
            else:
                self.stdout.write(self.style.WARNING('Painting image not found in media/sample_images/painting_image (any format)'))
            painting.save()  # Вызываем save модели для обработки
        self.stdout.write(self.style.SUCCESS('Created 14 Paintings'))

        # BlogPosts (7 штук)
        blog_titles = [
            'Мои впечатления от поездки в Италию',
            'Как я создаю абстрактные картины',
            'Выставка в Москве: отзыв',
            'Советы начинающим художникам',
            'Новые техники в пейзажной живописи',
            'История моей первой картины',
            'Вдохновение от природы Сибири'
        ]
        contents = [
            'В Италии я вдохновился ренессансом. Посетил Флоренцию и Рим, нарисовал несколько эскизов.',
            'Абстракция - это свобода. Я использую акрил и масло, экспериментирую с цветами.',
            'Выставка прошла успешно, много посетителей. Спасибо всем за поддержку!',
            'Начинайте с базовых навыков, практикуйтесь ежедневно, изучайте мастеров.',
            'Пробую новые кисти и текстуры для пейзажей. Результаты впечатляют.',
            'Моя первая картина была нарисована в детстве, это был простой пейзаж.',
            'Сибирская природа - бесконечный источник идей для моих работ.'
        ]
        blog_image_path = os.path.join('media', 'sample_images', 'blog_image')  # Без расширения

        for i in range(7):
            post = BlogPost(
                title=blog_titles[i],
                content=contents[i]
            )
            # Slug с транслитерацией
            post.slug = slugify(unidecode(post.title))

            # Детерминированное распределение сценариев изображений
            if i in [0, 1]:  # Посты без изображений
                post.save()
            else:  # Посты с обложкой + доп. изображениями
                image_added = False
                for ext in ['.webp', '.jpg', '.png']:
                    full_path = blog_image_path + ext
                    if os.path.exists(full_path):
                        post.cover_image = File(open(full_path, 'rb'), name=f'blog_cover_{i}{ext}')
                        image_added = True
                        break
                if not image_added:
                    self.stdout.write(self.style.WARNING(f'Blog cover image not found for post {post.title}. Creating without images.'))
                    post.save()
                    continue

                post.save()  # Сохраняем пост с обложкой

                # Добавляем доп. изображения в зависимости от i
                if i == 2 or i == 3:  # Только обложка (0 доп.)
                    pass
                elif i == 4:  # 1 доп. (всего 2)
                    num_extra = 1
                elif i == 5:  # 2 доп. (всего 3)
                    num_extra = 2
                elif i == 6:  # 4 доп. (всего 5)
                    num_extra = 4

                if 'num_extra' in locals():
                    for j in range(num_extra):
                        extra_image = BlogPostImage(post=post)
                        extra_image_added = False
                        for ext in ['.webp', '.jpg', '.png']:
                            full_path = blog_image_path + ext
                            if os.path.exists(full_path):
                                extra_image.image = File(open(full_path, 'rb'), name=f'blog_extra_{i}_{j}{ext}')
                                extra_image_added = True
                                break
                        if extra_image_added:
                            extra_image.save()  # Вызываем save для обработки
                        else:
                            self.stdout.write(self.style.WARNING(f'Extra blog image not found for post {post.title}'))

        self.stdout.write(self.style.SUCCESS('Created 7 BlogPosts with various image scenarios'))

        # ContactRequests (4 тестовые)
        names = ['Алексей', 'Мария', 'Дмитрий', 'Елена']
        emails = ['alex@example.com', 'maria@example.com', 'dmitry@example.com', 'elena@example.com']
        messages = [
            'Интересуюсь покупкой картины "Закат над рекой". Свяжитесь со мной.',
            'Хочу заказать портрет. Какие сроки?',
            'Отличный сайт! Поздравляю с выставкой.',
            'Вопрос по цене картины "Горный пейзаж".'
        ]

        for i in range(4):
            request = ContactRequest(
                name=names[i],
                email=emails[i],
                message=messages[i]
            )
            request.save()
        self.stdout.write(self.style.SUCCESS('Created 4 ContactRequests'))