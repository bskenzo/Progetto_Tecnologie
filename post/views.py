from django.shortcuts import redirect
from django.contrib import messages
from post.models import Post


def remove_post(request, pk):
    comment = Post.objects.get(pk=pk)
    if comment.user == request.user or request.user.is_staff:
        comment.delete()
        messages.success(request, 'Post removed')
        return redirect('movie:list')
    else:
        return redirect('home')
