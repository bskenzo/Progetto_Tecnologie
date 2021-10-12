from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.views.generic.list import ListView
from django.shortcuts import render

# Create your views here.
from movie.models import Review, Film


class TopListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = "movie/toplist.html"
    context_object_name = "films"

    def get_queryset(self):
        return Film.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
