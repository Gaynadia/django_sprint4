#!/usr/bin/env python
"""Простой скрипт для проверки Django проекта."""
import os
import sys

import django
from django.db import connection


def main():
    """Run project checks."""
    django.setup()

    from blog.models import Post, Comment, Category, Location
    from django.contrib.auth.models import User
    from blog.forms import PostForm, CommentForm, UserForm
    from blog.views import (
        index, category_posts, profile, post_detail,
        post_create, post_edit, post_delete,
        comment_create, comment_edit, comment_delete,
        profile_edit, SignUp
    )
    from pages.views import (
        page_not_found, csrf_failure, server_error,
        AboutView, RulesView
    )

    print("✓ Django models импортированы успешно")

    # Проверить, что модели имеют правильные поля
    assert hasattr(Post, 'image'), "Post не имеет поля image"
    assert hasattr(Post, 'author'), "Post не имеет поля author"
    assert hasattr(Comment, 'text'), "Comment не имеет поля text"
    assert hasattr(Comment, 'author'), "Comment не имеет поля author"
    assert hasattr(Comment, 'post'), "Comment не имеет поля post"

    print("✓ Все модели имеют необходимые поля")
    print("✓ Все forms импортированы успешно")
    print("✓ Все views импортированы успешно")
    print("✓ Все pages views импортированы успешно")

    # Проверить database
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]

        assert (
            'blog_post' in table_names
        ), "Таблица blog_post не существует"
        assert (
            'blog_comment' in table_names
        ), "Таблица blog_comment не существует"

    print("✓ Database таблицы созданы правильно")

    print(
        "\n✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Проект готов к запуску."
    )


if __name__ == '__main__':
    # Установить Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogicum.settings')

    # Инициализировать Django
    sys.path.insert(0, r'd:\Dev\django_sprint4\blogicum')
    main()
