from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.urls import reverse_lazy
from .models import Artist, Painting, BlogPost, SiteContact
from .forms import ContactForm

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['artist'] = Artist.objects.first()  # Единственный художник
        context['featured_paintings'] = Painting.objects.filter(is_featured=True)
        return context

class PaintingListView(ListView):
    model = Painting
    template_name = 'core/painting_list.html'
    context_object_name = 'paintings'

class PaintingDetailView(DetailView):
    model = Painting
    template_name = 'core/painting_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

class BlogListView(ListView):
    model = BlogPost
    template_name = 'core/blog_list.html'
    context_object_name = 'posts'
    ordering = '-pub_date'

class ContactsView(FormView):
    template_name = 'core/contacts.html'
    form_class = ContactForm
    success_url = reverse_lazy('home')  # После отправки на главную

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_contact'] = SiteContact.objects.first()  # Контакты сайта
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)