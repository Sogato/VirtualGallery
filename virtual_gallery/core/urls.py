from django.urls import path
from .views import (
    HomeView, PaintingListView, PaintingDetailView,
    BlogListView, ContactsView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('paintings/', PaintingListView.as_view(), name='painting_list'),
    path('paintings/<slug:slug>/', PaintingDetailView.as_view(), name='painting_detail'),
    path('blog/', BlogListView.as_view(), name='blog_list'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
]