import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.shortcuts import render, redirect

# Create your views here.
from movie.forms import FilmForm
from movie.models import Film


class FilmCreateView(LoginRequiredMixin, CreateView):

    model = Film
    form_class = FilmForm
    template_name = 'movie/create.html'

    def dispatch(self, request, *args, **kwargs):

        if request.method == 'POST':
            form = FilmForm(request.POST, request.FILES)

            if form.is_valid():
                form.save()
                return redirect('home')
        else:
            form = FilmForm()

        return render(request, 'movie/create.html', {'form': form})


class FilmDetailView(DetailView):

    model = Film
    template_name = 'movie/detail.html'


class FilmUpdateView(LoginRequiredMixin, UpdateView):
    model = Film
    form_class = FilmForm
    template_name = 'movie/update.html'

    def dispatch(self, request, *args, **kwargs):

        prod = Film.objects.get(id=self.get_object().pk)
        context = {'prod': prod}

        if request.method == "POST":
            if len(request.FILES) != 0:
                if len(prod.poster) > 0:
                    os.remove(prod.poster.path)
                prod.poster = request.FILES['image']
            prod.title = request.POST.get('title')
            prod.genre = request.POST.get('genre')
            prod.director = request.POST.get('director')
            prod.plot = request.POST.get('plot')
            prod.release_date = request.POST.get('release_date')
            prod.price = request.POST.get('price')
            prod.save()

            messages.success(request, "Updated")
            return redirect('movie:film-detail', pk=prod.pk)

        return render(request, 'movie/update.html', context)


class FilmDeleteView(LoginRequiredMixin, DeleteView):
    model = Film
    template_name = 'movie/delete.html'
    success_url = reverse_lazy('home')


class MovieListView(ListView):
    model = Film
    template_name = 'movie/movielist.html'
    context_object_name = 'films'

    # def dispatch(self, request, *args, **kwargs):
    #
    #     context['']
