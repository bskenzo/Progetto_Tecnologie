from django.urls import path

from post.views import remove_post

app_name = 'post'

urlpatterns = [
    path('remove/<int:pk>', remove_post, name='remove'),
]
