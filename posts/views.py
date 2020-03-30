from django.shortcuts import render, get_object_or_404
from .models import Post


def view_post(request, post_pk, post_slug):
    post = get_object_or_404(Post, pk=post_pk)
    return render(request, 'posts/view_post.html', {'post': post})
