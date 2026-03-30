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
from django import forms

from .models import FlatPage


class FlatPageDetailView(DetailView):
    model = FlatPage
    template_name = 'pages/flatpage.html'
    context_object_name = 'page'


class FlatPageCreateView(LoginRequiredMixin, CreateView):
    model = FlatPage
    fields = ['title', 'content', 'slug', 'is_published']
    template_name = 'pages/flatpage_form.html'
    success_url = reverse_lazy('pages:index')  # или куда-то


class FlatPageUpdateView(LoginRequiredMixin, UpdateView):
    model = FlatPage
    fields = ['title', 'content', 'slug', 'is_published']
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
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:index')  # или на профиль
    else:
        form = UserCreationForm()
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
    for post in page_obj:
        post.comment_count = post.comments.count()
    context = {'author': author, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def profile_edit_view(request, username):
    if request.user.username != username:
        return redirect('profile', username=username)
    user = request.user
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', username=username)
    else:
        form = UserEditForm(instance=user)
    return render(request, 'blog/profile_edit.html', {'form': form})


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
