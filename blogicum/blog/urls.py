from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),

    # Посты
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),

    # Комментарии
    path('posts/<int:post_id>/comment/', views.comment_create,
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.comment_edit, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.comment_delete, name='delete_comment'),

    # Категории
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),

    # Профиль пользователя
    path('profile/<str:username>/', views.profile,
         name='profile'),
    path('profile/<str:username>/edit/', views.profile_edit,
         name='edit_profile'),

    # Регистрация
    path('registration/', views.SignUp.as_view(), name='registration'),
]
