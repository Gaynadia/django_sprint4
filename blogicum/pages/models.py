from django.db import models


class FlatPage(models.Model):
    """Статическая страница."""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    content = models.TextField(
        verbose_name='Содержание'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        verbose_name = 'статическая страница'
        verbose_name_plural = 'Статические страницы'

    def __str__(self):
        return self.title
