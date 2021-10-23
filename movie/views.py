import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.shortcuts import render, redirect

# Create your views here.
from account.models import Account
from movie.forms import FilmForm, ReviewForm
from movie.mixins import AuthorRequiredMixin
from movie.models import Film, CATEGORY_CHOICES, Review


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review'] = Review.objects.all()
        return context


class FilmUpdateView(LoginRequiredMixin, UpdateView):
    model = Film
    form_class = FilmForm
    template_name = 'movie/update.html'

    def dispatch(self, request, *args, **kwargs):

        prod = Film.objects.get(id=self.get_object().pk)
        context = {'prod': prod, 'choices': CATEGORY_CHOICES}

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
    success_url = reverse_lazy('movie:list')


class MovieListView(ListView):
    model = Film
    template_name = 'movie/movielist.html'
    context_object_name = 'films'


# class TopListView(LoginRequiredMixin, ListView):
#     model = Review
#     template_name = 'movie/toplist.html'
#     context_object_name = 'films'
#
#     def get_queryset(self):
#         return Film.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')


class ReviewCreateView(LoginRequiredMixin, CreateView):

    model = Review
    form_class = ReviewForm
    template_name = 'movie/createreview.html'

    def dispatch(self, request, *args, **kwargs):
        context = {}

        user = request.user
        if not user.is_authenticated:
            return redirect('must_authenticate')

        if user.is_subscribe == 'not_active':
            return redirect('account:pricing')

        form = ReviewForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            obj = form.save(commit=False)
            writer = Account.objects.filter(email=user.email).first()
            reviewed_film = kwargs['pk']
            obj.writer = writer
            print(obj)
            obj.reviewed_film_id = reviewed_film
            obj.save()
            return redirect('movie:film-detail', kwargs['pk'])

        context['form'] = form

        return render(request, 'movie/createreview.html', context)


class ReviewUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):

    model = Review
    form_class = ReviewForm
    template_name = 'movie/updatereview.html'
    success_url = reverse_lazy('movie:list')


class ReviewDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Review
    template_name = 'movie/deletereview.html'
    success_url = reverse_lazy('movie:list')
