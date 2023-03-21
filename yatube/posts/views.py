# posts/views.py
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .utils import paginate_queryset


def index(request):
    post_list = Post.objects.all()

    page_obj = paginate_queryset(request, post_list)

    context = {
        'title': settings.TITLE_INDEX,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginate_queryset(request, post_list)

    context = {
        'group': group,
        'page_obj': page_obj,

    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()

    page_obj = paginate_queryset(request, post_list)

    context = {
        'author': author,
        'title': settings.TITLE_INDEX,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_list = post.author.posts.all()

    page_obj = paginate_queryset(request, post_list)

    is_edit = request.user == post.author
    context = {
        'post': post,
        'title': settings.TITLE_INDEX,
        'page_obj': page_obj,
        'is_edit': is_edit

    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    postForm = PostForm(request.POST or None)
    template = 'posts/create_post.html'
    if postForm.is_valid():
        text = postForm.cleaned_data['text']
        group = postForm.cleaned_data['group']
        author = request.user
        result = Post(author=author, text=text, group=group)
        result.save()
        return redirect('posts:profile', author)
    return render(request, template, {'form': postForm})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if not request.user == post.author:
        return redirect('posts:post_detail', post.author)

    postForm = PostForm(request.POST or None, instance=post)
    template = 'posts/create_post.html'
    if postForm.is_valid():
        postForm.save()
        return redirect('posts:post_detail', post_id)

    return render(request, template, {'form': postForm, 'is_edit': True})
