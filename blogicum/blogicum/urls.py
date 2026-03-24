from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from blog.views import SignUp

urlpatterns = [
    path('admin/', admin.site.urls),
    # Пути для работы с пользователями (вход, выход, смена пароля)
    path('auth/', include('django.contrib.auth.urls')),
    # Переопределяем маршрут регистрации
    path('auth/registration/', SignUp.as_view(), name='signup'),
    # Основные маршруты приложения blog
    path('', include('blog.urls')),
    # Маршруты для статических страниц
    path('pages/', include('pages.urls')),
]

# Подключаем кастомные обработчики ошибок
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
handler403 = 'pages.views.csrf_failure'

# Обслуживание картинок в режиме разработки
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
