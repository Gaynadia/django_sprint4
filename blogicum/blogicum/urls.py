from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pages import views as pages_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # auth путь + все стандартные страницы login/logout/password_*
    path('auth/', include('django.contrib.auth.urls')),

    # регистрация
    path('auth/registration/', pages_views.registration_view,
         name='registration'),

    # профиль
    path('profile/<str:username>/', pages_views.profile_view, name='profile'),
    path('profile/<str:username>/edit/', pages_views.profile_edit_view,
         name='profile_edit'),

    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

# Обработчики ошибок
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
handler500 = 'pages.views.server_error'
