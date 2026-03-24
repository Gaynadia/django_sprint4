from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import Http404
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserForm

# Константа для пагинации
POSTS_PER_PAGE = 10


def index(request):
    """Главная страница с пагинацией."""
    posts = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('category', 'location', 'author')

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def category_posts(request, category_slug):
    """Страница категории с пагинацией."""
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    posts = category.post_set.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('location', 'author')

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


def profile(request, username):
    """Страница профиля пользователя."""
    profile_user = get_object_or_404(User, username=username)

    # Если это профиль текущего пользователя, показываем все его посты
    # иначе - только опубликованные
    if request.user == profile_user:
        posts = profile_user.post_set.all().select_related(
            'category', 'location'
        )
    else:
        posts = profile_user.post_set.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).select_related('category', 'location')

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


def post_detail(request, id):
    """Страница поста с комментариями."""
    # Автор может видеть свои неопубликованные посты
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=id)
        if post.author != request.user and (
            not post.is_published
            or not post.category.is_published
            or post.pub_date > timezone.now()
        ):
            raise Http404
    else:
        post = get_object_or_404(
            Post.objects.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            ),
            id=id
        )

    comments = post.comments.all()

    context = {
        'post': post,
        'comments': comments,
        'form': CommentForm(),
    }
    return render(request, 'blog/detail.html', context)


class SignUp(CreateView):
    """Регистрация пользователя."""

    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')
    template_name = 'registration/registration_form.html'


@login_required
def post_create(request):
    """Создание нового поста."""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()

    context = {'form': form}
    return render(request, 'blog/create.html', context)


def post_edit(request, id):
    """Редактирование поста."""
    post = get_object_or_404(Post, id=id)

    if post.author != request.user:
        return redirect('blog:post_detail', id=id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('blog:post_detail', id=post.id)
    else:
        form = PostForm(instance=post)

    context = {'form': form, 'post': post}
    return render(request, 'blog/create.html', context)


@login_required
def post_delete(request, id):
    """Удаление поста."""
    post = get_object_or_404(Post, id=id)

    if post.author != request.user:
        return redirect('blog:post_detail', id=id)

    if request.method == 'POST':
        username = post.author.username
        post.delete()
        return redirect('blog:profile', username=username)

    context = {'post': post}
    return render(request, 'blog/detail.html', context)


@login_required
def comment_create(request, id):
    """Добавление комментария."""
    post = get_object_or_404(Post, id=id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', id=id)
    else:
        form = CommentForm()

    context = {'form': form, 'post': post}
    return render(request, 'blog/comment.html', context)


@login_required
def comment_edit(request, id, comment_id):
    """Редактирование комментария."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=id)

    if comment.author != request.user:
        return redirect('blog:post_detail', id=id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save()
            return redirect('blog:post_detail', id=id)
    else:
        form = CommentForm(instance=comment)

    context = {'form': form, 'post': comment.post}
    return render(request, 'blog/comment.html', context)


@login_required
def comment_delete(request, id, comment_id):
    """Удаление комментария."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=id)
    post = comment.post

    if comment.author != request.user:
        return redirect('blog:post_detail', id=id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=id)

    context = {'post': post, 'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def profile_edit(request, username):
    """Редактирование профиля."""
    user = get_object_or_404(User, username=username)

    if request.user != user:
        return redirect('blog:profile', username=username)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=user.username)
    else:
        form = UserForm(instance=user)

    context = {'form': form, 'user': user}
    return render(request, 'blog/profile_edit.html', context)
