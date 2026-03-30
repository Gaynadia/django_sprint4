from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from .models import Post, Comment, Category
from .forms import PostForm, CommentForm

User = get_user_model()


def get_posts_queryset(
    is_published=False,
    author=None,
    with_comments=False,
    order_by='-pub_date'
):
    """Возвращает queryset постов с фильтрами и опциями."""
    queryset = Post.objects.select_related('category', 'location', 'author')
    if is_published:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    if author:
        queryset = queryset.filter(author=author)
    if with_comments:
        queryset = queryset.annotate(comment_count=Count('comments'))
    return queryset.order_by(order_by)


def index(request):
    """Главная страница с 5 последними опубликованными постами."""
    posts = get_posts_queryset(is_published=True, with_comments=True)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_slug):
    """Страница одного поста."""
    # Первый вызов: проверить существование поста для авторства
    post = get_object_or_404(Post, slug=post_slug)
    # Если пользователь не автор, проверить опубликованность
    if request.user != post.author:
        get_object_or_404(
            Post.objects.filter(
                slug=post_slug,
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        )
    # Получить пост с select_related
    post = (
        Post.objects
        .select_related('category', 'location', 'author')
        .get(slug=post_slug)
    )
    comments = post.comments.all()
    if request.user.is_authenticated:
        form = CommentForm()
    else:
        form = None
    context = {'post': post, 'comments': comments, 'form': form}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Страница категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = (
        get_posts_queryset(is_published=True, with_comments=True)
        .filter(category=category)
    )

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'post_list': post_list,
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    """Страница профиля пользователя."""
    user = get_object_or_404(User, username=username)
    posts = get_posts_queryset(
        author=user,
        with_comments=True,
        order_by='-created_at'
    )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'author': user, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def post_create(request):
    """Создание нового поста."""
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('profile', username=request.user.username)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def post_edit(request, post_id):
    """Редактирование поста."""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_slug=post.slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_slug=post.slug)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    """Удаление поста."""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_slug=post.slug)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    # На GET показываем страницу поста для подтверждения удаления
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        id=post_id
    )
    comments = post.comments.all()
    context = {
        'post': post,
        'comments': comments,
        'form': None,
        'is_delete_confirmation': True
    }
    return render(request, 'blog/detail.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария к посту."""
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', post_slug=post.slug)
    else:
        form = CommentForm()
    context = {'form': form, 'post': post}
    return render(request, 'blog/comment.html', context)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_slug=comment.post.slug)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_slug=comment.post.slug)
    else:
        form = CommentForm(instance=comment)
    context = {'form': form, 'post': comment.post, 'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_slug=comment.post.slug)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_slug=comment.post.slug)
    # На GET показываем комментарий для подтверждения удаления
    context = {
        'comment': comment,
        'post': comment.post,
        'is_delete_confirmation': True
    }
    return render(request, 'blog/comment.html', context)
