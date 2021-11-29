from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)

from posts.forms import CommentForm, PostForm

from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGE_COUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "posts": post_list,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    form = PostForm(request.POST or None, files=request.FILES or None)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.PAGE_COUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "group": group,
        "form": form,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_posts = author.posts.all()
    paginator = Paginator(user_posts, settings.PAGE_COUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "author": author,
        "page_obj": page_obj,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        "form": form,
        "comments": comments,
        "post": post,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        context = {"form": form}
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect("posts:profile", username=request.user)

    context = {
        "form": form,
        "is_edit": False,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    template = "posts/create_post.html"
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id)
    if form.is_valid():
        post.save()
        return redirect("posts:post_detail", post_id=post_id)
    return render(request, template,
                  {"form": form, "is_edit": False, "post": post})


@login_required
def add_comment(request, post_id):
    # Получите пост
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


def page_obj_gen(request, posts):
    paginator = Paginator(posts, settings.PAGE_COUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


@login_required
def follow_index(request):
    if Follow.objects.filter(user=request.user).exists():
        following_authors = get_object_or_404(Follow, user=request.user)
        posts = get_list_or_404(Post, author=following_authors.author)
    else:
        posts = Post.objects.all()
    return render(request, "posts/follow.html", {"page_obj": posts})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=request.user)
    if Follow.objects.filter(user=request.user, author=author).exists():
        following = False
    else:
        Follow.objects.create(user=user, author=author)
        following = True
    posts = author.posts.all()
    page_obj = page_obj_gen(request, posts)
    title = f"Профайл пользователя {author.get_full_name()}"
    context = {
        "following": following,
        "author": author,
        "page_obj": page_obj,
        "title": title,
    }
    return render(request, "posts/profile.html", context)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=request.user)
    if Follow.objects.filter(user=request.user, author=author).exists():
        Follow.objects.filter(user=user, author=author).delete()
        following = False
    else:
        following = True
    posts = author.posts.all()
    page_obj = page_obj_gen(request, posts)
    title = f"Профайл пользователя {author.get_full_name()}"
    context = {
        "following": following,
        "author": author,
        "page_obj": page_obj,
        "title": title,
    }
    return render(request, "posts/profile.html", context)
