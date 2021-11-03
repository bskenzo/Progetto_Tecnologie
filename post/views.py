from django.http import Http404
from django.shortcuts import redirect
from django.contrib import messages
from post.models import Post, Reply


def remove_post(request, pk, film_pk):
    comment = Post.objects.get(pk=pk)
    if comment.user == request.user or request.user.is_staff:
        comment.delete()
        messages.success(request, 'Post removed')
        return redirect('movie:film-detail', pk=film_pk)
    else:
        raise Http404


def reply_post(request, pk, film_pk):
    comment = Reply.objects.get(pk=pk)
    if comment.user == request.user or request.user.is_staff:
        comment.delete()
        messages.success(request, 'Reply removed')
        return redirect('movie:film-detail', pk=film_pk)
    else:
        raise Http404
