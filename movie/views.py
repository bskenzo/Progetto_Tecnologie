import os

import stripe
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.shortcuts import render, redirect

# Create your views here.
from account.models import Account
from movie.forms import FilmForm, ReviewForm
from movie.mixins import AuthorRequiredMixin
from movie.models import Film, CATEGORY_CHOICES, Review, MyList
from playlist.models import Playlist
from playlist.views import add_to_playlist

stripe.api_key = "sk_test_51JjpSBH1UjLFf6ccnvnflqfD1NkLyfRXOC0OxKjvwi4sYv2I3bpSz5Deiu7dgP0296tb8dy5OuwT7sXjJjZBBjWx00c3Hiu3VB"


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
        context['playlist'] = Playlist.objects.filter(user_id=self.request.user.pk)
        context['rating'] = Review.objects.filter(reviewed_film_id=self.kwargs['pk']).aggregate(Avg('rating'))
        try:
            my_purchase = MyList.objects.get(user_id=self.request.user.pk).film.all()
            film = Film.objects.get(id=self.kwargs['pk'])
            if film in my_purchase:
                context['movie'] = film
        except:
            pass
        return context

    def get(self, request, *args, **kwargs):
        try:
            playlist = request.GET
            playlist = playlist['playlist']
            playlist = playlist.split('-')
            add_to_playlist(request, operation='add', pk=kwargs['pk'], playlist_id=playlist[0])
        except:
            try:
                name = request.GET
                name = name['name']
                pl = Playlist()
                pl.name = name
                pl.user_id = request.user.pk
                pl.save()
                add_to_playlist(request, operation='add', pk=kwargs['pk'], playlist_id=pl.pk)
            except:
                pass

        return super(FilmDetailView, self).get(request, *args, **kwargs)


class FilmUpdateView(LoginRequiredMixin, UpdateView):
    model = Film
    form_class = FilmForm
    template_name = 'movie/update.html'

    def dispatch(self, request, *args, **kwargs):

        prod = Film.objects.get(id=self.get_object().pk)
        context = {'prod': prod, 'choices': CATEGORY_CHOICES}

        if request.method == "POST":
            if request.FILES is not None:
                try:
                    _ = request.FILES['image']
                    os.remove(prod.poster.path)
                    prod.poster = request.FILES['image']
                except:
                    pass

                try:
                    _ = request.FILES['video']
                    os.remove(prod.video.path)
                    prod.video = request.FILES['video']
                except:
                    pass

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

    def delete(self, request, *args, **kwargs):
        film = Film.objects.get(id=self.get_object().pk)
        film.poster.delete()
        film.video.delete()
        film.delete()
        return redirect('home')


class FilmStreamView(LoginRequiredMixin, DetailView):
    model = Film
    template_name = 'movie/stream.html'

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            next_page = f'?next=/movie/{kwargs["pk"]}/streaming'
            return redirect(reverse('account:must_authenticate') + next_page)

        context = {}
        film = Film.objects.get(id=kwargs['pk'])
        context['film'] = film

        if request.user.is_subscribe == 'active':
            return super(FilmStreamView, self).get(request, *args, context)

        try:
            my_list = MyList.objects.get(user_id=request.user.pk).film.all()
            if film in my_list:
                return super(FilmStreamView, self).get(request, *args, context)
            else:
                messages.error(request, "You didn't purchase this film")
                return redirect('movie:film-detail', kwargs['pk'])
        except:
            messages.error(request, "You didn't purchase this film")
            return redirect('movie:film-detail', kwargs['pk'])


class MovieListView(ListView):
    model = Film
    template_name = 'movie/movielist.html'
    context_object_name = 'films'


class TopListView(ListView):
    model = Review
    template_name = "movie/toplist.html"
    context_object_name = "films"

    def get_queryset(self):
        return Film.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        # return Film.objects.all().order_by('price') Ordina in base al prezzo


class GenreListView(ListView):
    model = Film
    template_name = "movie/genre.html"
    context_object_name = "films"

    def get_queryset(self):
        genre = Film.objects.filter(genre__contains=self.kwargs["genre"])
        if genre:
            return Film.objects.filter(genre__contains=self.kwargs["genre"])
        else:
            raise Http404


class MyListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = 'movie/mylist.html'
    context_object_name = 'films'

    def get_context_data(self, *, object_list=None, **kwargs):
        try:
            account = Account.objects.get(email=self.request.user.email)
            my_list = MyList.objects.get(user_id=account.pk).film.all()
        except:
            my_list = {}
            pass
        return super(MyListView, self).get_context_data(object_list=my_list)

    def get(self, request, *args, **kwargs):

        if request.user.is_subscribe == 'active':
            return redirect('home')

        return super(MyListView, self).get(request, *args, **kwargs)


class CheckoutView(LoginRequiredMixin, UpdateView):

    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('account:must_authenticate')

        if request.user.is_subscribe == 'active':
            return redirect('account:pricing')

        product_id = request.GET['price']
        product = Film.objects.get(id=product_id)
        account = Account.objects.get(email=request.user.email)

        if account.stripe_id != "id_test":

            stripe.PaymentIntent.create(
                amount=int(float(product.price) * 100),
                currency="eur",
                payment_method_types=["card"],
                customer=account.stripe_id,
                description=f'Acquisto del film {product.title}',
                confirm=True,
                metadata={
                    'product_id': product.id
                }
            )
        else:
            stripe_customer = stripe.Customer.create(email=request.user.email,
                                                     source=request.POST['stripeToken'])

            stripe.PaymentIntent.create(
                amount=int(float(product.price) * 100),
                currency="eur",
                payment_method_types=["card"],
                customer=stripe_customer.stripe_id,
                description=f'Acquisto del film {product.title}',
                confirm=True,
                metadata={
                    'product_id': product.id
                }
            )

            account.stripe_id = stripe_customer.id
            account.save()

        try:
            my_list = MyList.objects.get(user_id=account.pk)
            my_list.film.add(product)
        except:
            model = MyList()
            model.user_id = account.pk
            model.save()
            model.film.add(product)

        messages.add_message(
            self.request, messages.SUCCESS,
            'Payment successfully!'
        )

        return redirect('movie:my-list')

    def get(self, request, *args, **kwargs):

        film = 'No_Choice'
        amount = 0.00
        amount_html = 0.00
        prod = None

        try:
            prod = Film.objects.get(id=request.GET['price'])
            film = prod.title
            amount = float(prod.price)
            amount_html = prod.price
        except:
            pass

        if prod is None:
            raise Http404

        return render(request, 'movie/payments/checkout.html', {'film': film, 'amount': amount * 100,
                                                                'amount_html': amount_html, 'prod': prod})


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'movie/createreview.html'

    def dispatch(self, request, *args, **kwargs):
        context = {}

        user = request.user
        if not user.is_authenticated:
            next_page = f'?next=/movie/{kwargs["pk"]}/create-review/'
            return redirect(reverse('account:must_authenticate') + next_page)

        if user.is_subscribe == 'not_active':
            messages.info(request, 'You must be subscribe')
            return redirect('account:pricing')

        form = ReviewForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            obj = form.save(commit=False)
            writer = Account.objects.filter(email=user.email).first()
            reviewed_film = kwargs['pk']
            obj.writer = writer
            obj.reviewed_film_id = reviewed_film
            obj.save()
            return redirect('movie:film-detail', kwargs['pk'])

        context['film_pk'] = kwargs['pk']
        context['form'] = form

        return render(request, 'movie/createreview.html', context)


class ReviewUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'movie/updatereview.html'
    success_url = reverse_lazy('movie:film-detail')

    def get_success_url(self):
        return reverse('movie:film-detail', kwargs={'pk': self.object.reviewed_film_id})


class ReviewDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Review
    template_name = 'movie/deletereview.html'
    success_url = reverse_lazy('movie:list')
