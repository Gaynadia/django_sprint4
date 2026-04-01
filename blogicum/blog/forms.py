from django import forms
from django.utils import timezone
from .models import Post, Category, Location, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['author']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ограничиваем категории только опубликованными
        self.fields['category'].queryset = Category.objects.filter(
            is_published=True)
        # Ограничиваем местоположения только опубликованными
        self.fields['location'].queryset = Location.objects.filter(
            is_published=True)
        # Устанавливаем начальное значение для pub_date
        if not self.instance.pk:
            self.fields['pub_date'].initial = timezone.now()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }


class DeleteForm(forms.Form):
    """Пустая форма для подтверждения удаления."""
    pass
