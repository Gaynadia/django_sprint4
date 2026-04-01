from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.views.decorators.csrf import requires_csrf_token
from django.views.generic import DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Count
from django import forms

from .models import FlatPage
from .forms import FlatPageForm, UserEditForm


def get_posts_with_comment_count(posts):
    """Добавляет comment_count к постам."""
    for post in posts:
        post.comment_count = post.comments.count()
    return posts


class FlatPageDetailView(DetailView):
    model = FlatPage
    template_name = 'pages/flatpage.html'
    context_object_name = 'page'


class FlatPageCreateView(LoginRequiredMixin, CreateView):
    model = FlatPage
    form_class = FlatPageForm
    template_name = 'pages/flatpage_form.html'
    success_url = reverse_lazy('pages:index')  # или куда-то


class FlatPageUpdateView(LoginRequiredMixin, UpdateView):
    model = FlatPage
    form_class = FlatPageForm
    template_name = 'pages/flatpage_form.html'
    success_url = reverse_lazy('pages:index')


@requires_csrf_token
def csrf_failure(request, reason=""):
    """Обработчик CSRF."""
    return render(request, 'pages/403csrf.html',
                  {'reason': reason}, status=403)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)


def registration_view(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('blog:index')  # или на профиль
    return render(request, 'registration/registration_form.html',
                  {'form': form})


def profile_view(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        # Автор видит все свои посты
        posts = author.posts.all().order_by('-pub_date')
    else:
        # Другие видят только опубликованные и прошедшие pub_date
        from django.utils import timezone
        posts = author.posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Добавляем comment_count для каждого поста
    get_posts_with_comment_count(page_obj)
    context = {'author': author, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def profile_edit_view(request, username):
    if request.user.username != username:
        return redirect('profile', username=username)
    user = request.user
    form = UserEditForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('profile', username=username)
    return render(request, 'blog/profile_edit.html', {'form': form})
