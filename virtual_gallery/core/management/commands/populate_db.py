import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.core.files import File
from core.models import Artist, Painting, BlogPost, SiteContact, ContactRequest, BlogPostImage
from django.utils.text import slugify
from unidecode import unidecode
import os


class Command(BaseCommand):
    """
    Команда для заполнения базы данных тестовыми данными на dev-сервере.

    Создает singleton-объекты (Artist, SiteContact), картины (14 шт.), посты в блоге (7 шт. с разными сценариями изображений)
    и заявки на связь (4 шт.). Ищет изображения в media/sample_images и прикрепляет их, если найдены.
    """
    help = 'Заполняет базу данных тестовыми данными для разработки'

    def handle(self, *args, **kwargs):
        """
        Основной метод команды: выполняет заполнение базы данных.
        """
        self._create_artist()
        self._create_site_contact()
        self._create_paintings()
        self._create_blog_posts()
        self._create_contact_requests()
        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена тестовыми данными.'))

    def _create_artist(self):
        """
        Создает единственного художника (singleton), если он не существует.
        """
        if not Artist.objects.exists():
            artist = Artist(
                name='Иван Иванович Петров',
                bio='Иван Петров - талантливый художник из Новосибирска, специализирующийся на пейзажах и абстрактном искусстве. Его работы выставлялись в галереях Москвы и Санкт-Петербурга. Родился в 1980 году, окончил художественную академию.'
            )
            # Пытаемся найти фото в media/sample_images/artist_photo (любое расширение)
            photo_path = os.path.join('media', 'sample_images', 'artist_photo')
            photo_found = self.attach_image(artist, 'photo', photo_path)
            artist.save()  # Сохраняем для обработки изображения
            self.stdout.write(self.style.SUCCESS('Создан Artist') if photo_found else self.style.WARNING(
                'Создан Artist без фото'))

    def _create_site_contact(self):
        """
        Создает контактную информацию сайта (singleton), если она не существует.
        """
        if not SiteContact.objects.exists():
            site_contact = SiteContact(
                phone='+7 (123) 456-78-90',
                email='info@artgallery.ru',
                vk_link='https://vk.com/artgallery_example',
                instagram_link='https://instagram.com/artgallery_example',
                telegram_link='https://t.me/artgallery_example'
            )
            site_contact.save()
            self.stdout.write(self.style.SUCCESS('Создан SiteContact с социальными ссылками'))

    def _create_paintings(self):
        """
        Создает или дополняет картины до 14 штук.
        """
        if Painting.objects.count() < 14:
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

            image_path = os.path.join('media', 'sample_images', 'painting_image')  # Путь к изображению

            for i in range(14):
                if Painting.objects.filter(title=painting_titles[i]).exists():
                    continue  # Пропускаем существующие
                painting = Painting(
                    title=painting_titles[i],
                    description=descriptions[i],
                    creation_date=date.today() - timedelta(days=random.randint(1, 365 * 5)),
                    price=random.choice([None, random.randrange(2000, 10001, 100)]),
                    is_featured=random.choice([True, False])
                )
                # Генерируем slug с unidecode для правильной транслитерации
                painting.slug = slugify(unidecode(painting.title))
                # Прикрепляем изображение (с суффиксом для уникальности)
                image_found = self.attach_image(painting, 'image', image_path, suffix=f'_{i}')
                painting.save()  # Сохраняем для генерации изображений и уникальности slug
                self.stdout.write(
                    self.style.SUCCESS(f'Создана картина "{painting.title}"') if image_found else self.style.WARNING(
                        f'Создана картина "{painting.title}" без изображения'))
            self.stdout.write(self.style.SUCCESS('Картины созданы/обновлены до 14 штук'))

    def _create_blog_posts(self):
        """
        Создает или дополняет посты в блоге до 7 штук с разными сценариями изображений.
        """
        if BlogPost.objects.count() < 7:
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

            blog_image_path = os.path.join('media', 'sample_images', 'blog_image')  # Путь к изображению

            for i in range(7):
                if BlogPost.objects.filter(title=blog_titles[i]).exists():
                    continue  # Пропускаем существующие
                post = BlogPost(
                    title=blog_titles[i],
                    content=contents[i]
                )
                # Генерируем slug с unidecode для правильной транслитерации
                post.slug = slugify(unidecode(post.title))
                # Сценарии изображений (детерминированные):
                # 0-1: без изображений
                # 2-3: только обложка
                # 4: обложка + 1 доп. изображение
                # 5: обложка + 2 доп.
                # 6: обложка + 4 доп. (макс. 5 всего)
                has_cover = i >= 2
                num_extra = 0 if i < 4 else (1 if i == 4 else (2 if i == 5 else 4))

                if has_cover:
                    # Прикрепляем обложку (с суффиксом)
                    cover_found = self.attach_image(post, 'cover_image', blog_image_path, suffix=f'_{i}')
                    if not cover_found:
                        self.stdout.write(
                            self.style.WARNING(f'Нет обложки для поста "{post.title}". Создаю без изображений.'))
                        num_extra = 0  # Без обложки — без доп. (по валидации)

                post.save()  # Сохраняем для обработки обложки и уникальности slug

                # Добавляем доп. изображения (с суффиксами)
                for j in range(num_extra):
                    extra_image = BlogPostImage(post=post)
                    extra_found = self.attach_image(extra_image, 'image', blog_image_path, suffix=f'_{i}_{j}')
                    if extra_found:
                        extra_image.save()  # Сохраняем для обработки
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Нет доп. изображения для поста "{post.title}" (#{j + 1}). Пропускаю.'))

                self.stdout.write(self.style.SUCCESS(f'Создан пост "{post.title}" с {num_extra} доп. изображениями'))
            self.stdout.write(self.style.SUCCESS('Посты созданы/обновлены до 7 с разными сценариями'))

    def _create_contact_requests(self):
        """
        Создает или дополняет заявки на связь до 4 штук.
        """
        if ContactRequest.objects.count() < 4:
            names = ['Алексей', 'Мария', 'Дмитрий', 'Елена']
            emails = ['alex@example.com', 'maria@example.com', 'dmitry@example.com', 'elena@example.com']
            messages = [
                'Интересуюсь покупкой картины "Закат над рекой". Свяжитесь со мной.',
                'Хочу заказать портрет. Какие сроки?',
                'Отличный сайт! Поздравляю с выставкой.',
                'Вопрос по цене картины "Горный пейзаж".'
            ]

            for i in range(4):
                if ContactRequest.objects.filter(name=names[i]).exists():
                    continue
                request = ContactRequest(
                    name=names[i],
                    email=emails[i],
                    message=messages[i],
                    created_at=date.today() - timedelta(days=random.randint(1, 30))  # Разные даты
                )
                request.save()
            self.stdout.write(self.style.SUCCESS('Заявки созданы/обновлены до 4 штук'))

    def attach_image(self, obj, field_name, base_path, suffix=''):
        """
        Вспомогательная функция: прикрепляет изображение к полю модели, если файл найден.

        Ищет файл с расширениями .webp, .jpg, .png. Добавляет суффикс к имени для уникальности.
        Возвращает True, если изображение прикреплено.
        """
        extensions = ['.webp', '.jpg', '.png']
        for ext in extensions:
            full_path = base_path + ext
            if os.path.exists(full_path):
                setattr(obj, field_name, File(open(full_path, 'rb'), name=os.path.basename(base_path) + suffix + ext))
                return True
        return False
