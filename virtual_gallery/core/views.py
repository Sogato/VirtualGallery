from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.urls import reverse_lazy
from .models import Artist, Painting, BlogPost, SiteContact
from .forms import ContactForm


class HomeView(TemplateView):
    """
    Представление главной страницы сайта.

    Отображает информацию о художнике и избранные картины.
    """
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет контекст для шаблона: художника и избранные картины.
        """
        context = super().get_context_data(**kwargs)
        context['artist'] = Artist.objects.first()  # Единственный художник
        context['featured_paintings'] = Painting.objects.filter(is_featured=True).order_by('-creation_date')
        return context


class PaintingListView(ListView):
    """
    Представление списка всех картин.

    Отображает картины в порядке от новых к старым.
    """
    model = Painting
    template_name = 'core/painting_list.html'
    context_object_name = 'paintings'

    def get_queryset(self):
        """
        Возвращает queryset с сортировкой по дате создания (новые сначала).
        """
        return super().get_queryset().order_by('-creation_date')


class PaintingDetailView(DetailView):
    """
    Представление детальной страницы картины.

    Использует slug для поиска картины.
    """
    model = Painting
    template_name = 'core/painting_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class BlogListView(ListView):
    """
    Представление списка постов в блоге.

    Отображает посты в порядке от новых к старым, с предзагрузкой изображений.
    """
    model = BlogPost
    template_name = 'core/blog_list.html'
    context_object_name = 'posts'
    ordering = '-pub_date'

    def get_queryset(self):
        """
        Возвращает queryset с предзагруженными изображениями для оптимизации.
        """
        return super().get_queryset().prefetch_related('images')


class ContactsView(FormView):
    """
    Представление страницы контактов с формой обратной связи.

    Обрабатывает отправку формы и отображает контактную информацию сайта.
    """
    template_name = 'core/contacts.html'
    form_class = ContactForm
    success_url = reverse_lazy('home')  # После отправки на главную

    def get_context_data(self, **kwargs):
        """
        Добавляет контекст для шаблона: контактную информацию сайта.
        """
        context = super().get_context_data(**kwargs)
        context['site_contact'] = SiteContact.objects.first()  # Контакты сайта
        return context

    def form_valid(self, form):
        """
        Сохраняет форму при успешной валидации.
        """
        form.save()
        return super().form_valid(form)
