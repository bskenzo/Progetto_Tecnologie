from django.urls import path

from post.views import remove_post, reply_post

app_name = 'post'

urlpatterns = [
    path('remove/<int:pk>/<int:film_pk>', remove_post, name='remove'),
    path('remove_reply/<int:pk>/<int:film_pk>', reply_post, name='remove_reply'),
]
