from django import forms
from .models import ContactRequest


class ContactForm(forms.ModelForm):
    """
    Форма для отправки заявки на обратную связь.

    Основана на модели ContactRequest, с кастомными виджетами для плейсхолдеров.
    """

    class Meta:
        model = ContactRequest
        fields = ['name', 'email', 'message']
        labels = {
            'name': 'Имя',
            'email': 'E-mail',
            'message': 'Сообщение',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ваш email'}),
            'message': forms.Textarea(attrs={'placeholder': 'Сообщение'}),
        }
