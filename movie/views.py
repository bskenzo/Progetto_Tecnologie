import os
import re
from operator import attrgetter

import stripe
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, QuerySet
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
from post.models import Post, Reply

stripe.api_key = "sk_test_51JjpSBH1UjLFf6ccnvnflqfD1NkLyfRXOC0OxKjvwi4sYv2I3bpSz5Deiu7dgP0296tb8dy5OuwT7sXjJjZBBjWx00c3Hiu3VB"


class FilmCreateView(LoginRequiredMixin, CreateView):
    model = Film
    form_class = FilmForm
    template_name = 'movie/create.html'

    def post(self, request, *args, **kwargs):

        form = FilmForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('movie:list')
        else:
            form = FilmForm()

        return render(request, 'movie/create.html', {'form': form})


class FilmDetailView(DetailView, UpdateView):
    model = Film
    template_name = 'movie/detail.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review'] = Review.objects.all()
        context['posts'] = Post.objects.all()
        context['reply'] = Reply.objects.all()
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

    def post(self, request, *args, **kwargs):

        try:
            playlist = request.POST
            playlist = playlist['playlist']
            playlist = playlist.split('-')
            add_to_playlist(request, operation='add', pk=kwargs['pk'], playlist_id=playlist[0])
        except:
            pass

        try:
            _ = request.POST['checkbox']
            request.user.spoiler = True
            request.user.save()
        except:
            request.user.spoiler = False
            request.user.save()

        try:
            name = request.POST
            name = name['name']
            pl = Playlist()
            pl.name = name
            pl.user_id = request.user.pk
            pl.save()
            add_to_playlist(request, operation='add', pk=kwargs['pk'], playlist_id=pl.pk)
        except:
            pass

        try:
            text = request.POST
            com = text['comment']
            if com != '':
                comment = Post()
                try:
                    spoiler = text['spoiler']
                    if spoiler == 'on':
                        comment.spoiler = True
                except:
                    pass
                comment.comment = com
                comment.user_id = request.user.pk
                comment.film_id = self.kwargs['pk']
                comment.save()
        except:
            pass

        try:
            text = request.POST
            r = re.compile("reply-.*")
            reply_post = list(filter(r.match, request.POST))
            com = text[reply_post[0]]
            if com != '':
                reply = Reply()
                try:
                    spoiler = text['spoiler']
                    if spoiler == 'on':
                        reply.spoiler = True
                except:
                    pass
                reply.comment = com
                reply.user_id = request.user.pk
                reply.film_id = self.kwargs['pk']
                reply_post = reply_post[0].split('-')
                reply.post_id = reply_post[1]
                reply.save()
        except:
            pass

        request.POST = []

        return redirect('movie:film-detail', pk=kwargs['pk'])


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

            prod.title = request.POST.get('title')
            prod.genre = request.POST.get('genre')
            prod.director = request.POST.get('director')
            prod.plot = request.POST.get('plot')
            prod.release_date = request.POST.get('release_date')
            prod.price = request.POST.get('price')
            prod.video = request.POST.get('video')
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
        film.delete()
        return redirect('movie:list')


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
            film.views += 1
            film.save()
            try:
                my_list = MyList.objects.get(user_id=request.user.pk)
                my_list.film.add(film)
            except:
                model = MyList()
                model.user_id = request.user.pk
                model.save()
                model.film.add(film)
            return super(FilmStreamView, self).get(request, *args, context)

        try:
            my_list = MyList.objects.get(user_id=request.user.pk).film.all()
            if film in my_list:
                film.views += 1
                film.save()
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
    success_url = reverse_lazy('movie:list')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['films'] = context['object_list'].order_by('title')
        context['choices'] = CATEGORY_CHOICES

        try:
            query = self.request.GET['q']
            film = sorted(Film.objects.filter(title__icontains=query), key=attrgetter('release_date'), reverse=True)
            context['films'] = film
        except:
            pass

        try:
            genres = self.request.GET['genre']
            genres = genres.split(' ')

            context['films'] = None
            for genre in genres:
                query_set = Film.objects.filter(genre__contains=genre)

                if context['films'] is not None:
                    context['films'] = context['films'] | query_set.all()
                else:
                    context['films'] = query_set.all()
            context['films'] = context['films'].order_by('title')

            try:
                _ = self.request.GET['price_dec']
                context['films'] = context['films'].order_by('-price')

            except:
                pass

            try:
                _ = self.request.GET['price_cre']
                context['films'] = context['films'].order_by('price')
            except:
                pass

            try:
                _ = self.request.GET['rating']
                context['films'] = context['films'].annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
            except:
                pass

        except:
            try:
                _ = self.request.GET['price_dec']
                context['films'] = Film.objects.all().order_by('-price')
            except:
                pass

            try:
                _ = self.request.GET['price_cre']
                context['films'] = Film.objects.all().order_by('price')
            except:
                pass

            try:
                _ = self.request.GET['rating']
                context['films'] = Film.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
            except:
                pass

        return context

    def post(self, request, *args, **kwargs):

        try:
            query = request.POST['q']
            self.success_url = reverse('movie:list') + f'?q={query}'
        except:
            pass

        genre = ''
        for x, _ in CATEGORY_CHOICES:
            try:
                _ = (request.POST[x])
                if genre == '':
                    genre = x
                else:
                    genre = genre + ' ' + x
            except:
                pass
        if genre != '':
            self.success_url = reverse('movie:list') + f'?genre={genre}'

        if self.success_url != reverse('movie:list'):
            try:
                _ = request.POST['filter_price_dec']
                self.success_url += '&price_dec=on'
            except:
                pass

            try:
                _ = request.POST['filter_price_cre']
                self.success_url += '&price_cre=on'
            except:
                pass

            try:
                _ = request.POST['filter_rating']
                self.success_url += '&rating=on'
            except:
                pass
        else:
            try:
                _ = request.POST['filter_price_dec']
                self.success_url = reverse('movie:list') + '?price_dec=on'
            except:
                pass

            try:
                _ = request.POST['filter_price_cre']
                self.success_url = reverse('movie:list') + '?price_cre=on'
            except:
                pass

            try:
                _ = request.POST['filter_rating']
                self.success_url = reverse('movie:list') + '?rating=on'
            except:
                pass

        return redirect(self.success_url)


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


class WatchListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = 'movie/watchlist.html'
    context_object_name = 'films'

    def get_context_data(self, *, object_list=None, **kwargs):
        try:
            account = Account.objects.get(email=self.request.user.email)
            my_list = MyList.objects.get(user_id=account.pk).film.all()
        except:
            my_list = {}
            pass
        return super(WatchListView, self).get_context_data(object_list=my_list)

    def get(self, request, *args, **kwargs):
        if request.user.is_subscribe == 'not_active':
            return redirect('movie:my-list')

        return super(WatchListView, self).get(request, *args, **kwargs)


class CheckoutView(LoginRequiredMixin, UpdateView):

    def post(self, request, *args, **kwargs):

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

        if not request.user.is_authenticated:
            return redirect('account:must_authenticate')

        if request.user.is_subscribe == 'active' or request.user.is_admin:
            return redirect('account:pricing')

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
            next_page = f'?next=/movie/{kwargs["pk"]}/create-review/'
            return redirect(reverse('account:pricing') + next_page)

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

    def get_success_url(self):
        return reverse('movie:film-detail', kwargs={'pk': self.object.reviewed_film_id})


class ReviewDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Review
    template_name = 'movie/deletereview.html'

    def get_success_url(self):
        return reverse('movie:film-detail', kwargs={'pk': self.object.reviewed_film_id})
