import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.core.files import File
from core.models import Artist, Painting, BlogPost, SiteContact, ContactRequest
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
            painting = Painting(
                title=painting_titles[i],
                description=descriptions[i],
                creation_date=date.today() - timedelta(days=random.randint(1, 365*5)),
                price = random.choice([None, random.randint(1000, 10000)]),
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
            'Вдохновение от природы Сибири',
            'Анализ работ великих мастеров'
        ]
        contents = [
            'В Италии я вдохновился ренессансом. Посетил Флоренцию и Рим, нарисовал несколько эскизов.',
            'Абстракция - это свобода. Я использую акрил и масло, экспериментирую с цветами.',
            'Выставка прошла успешно, много посетителей. Спасибо всем за поддержку!',
            'Начинайте с базовых навыков, практикуйтесь ежедневно, изучайте мастеров.',
            'Пробую новые кисти и текстуры для пейзажей. Результаты впечатляют.',
            'Моя первая картина была нарисована в детстве, это был простой пейзаж.',
            'Сибирская природа - бесконечный источник идей для моих работ.',
            'Изучаю технику Ван Гога и Моне, применяю в своих картинах.'
        ]
        blog_image_path = os.path.join('media', 'sample_images', 'blog_image')  # Без расширения

        for i in range(7):
            post = BlogPost(
                title=blog_titles[i],
                content=contents[i]
            )
            # Slug с транслитерацией
            post.slug = slugify(unidecode(post.title))
            for ext in ['.webp', '.jpg', '.png']:  # Проверяем возможные расширения
                full_path = blog_image_path + ext
                if os.path.exists(full_path):
                    post.image = File(open(full_path, 'rb'), name=f'blog_image_{i}{ext}')
                    break
            else:
                self.stdout.write(self.style.WARNING('Blog image not found in media/sample_images/blog_image (any format)'))
            post.save()  # Вызываем save модели для обработки
        self.stdout.write(self.style.SUCCESS('Created 7 BlogPosts'))

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