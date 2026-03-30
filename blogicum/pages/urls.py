from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    # path('<slug:slug>/', views.FlatPageDetailView.as_view(),
    # name='flatpage'),
    path('create/', views.FlatPageCreateView.as_view(),
         name='create_flatpage'),
    path('<slug:slug>/edit/', views.FlatPageUpdateView.as_view(),
         name='edit_flatpage'),
]
