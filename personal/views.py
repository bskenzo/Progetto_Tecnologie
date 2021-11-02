from datetime import datetime

import stripe
from django.views.generic import TemplateView
from django.db.models import Count
from account.models import Account
from movie.models import Film, MyList


class HomeView(TemplateView):

    model = Account
    template_name = 'personal/home.html'

    def dispatch(self, request, *args, **kwargs):
        session = None

        if request.user.is_authenticated:
            if request.user.stripe_id != "id_test":
                session = stripe.Customer.retrieve(request.user.stripe_id, expand=['subscriptions'])
                if hasattr(session, 'deleted'):
                    if session.deleted:
                        request.user.stripe_id = "id_test"
                        request.user.is_subscribe = "not_active"
                        request.user.expire_date = "1970-01-01"
                        request.user.stripe_subscription_id = ""
                        request.user.save()
                elif not session.subscriptions.data:
                    request.user.is_subscribe = "not_active"
                    request.user.expire_date = "1970-01-01"
                    request.user.stripe_subscription_id = ""
                    request.user.save()
                else:
                    request.user.is_subscribe = session.subscriptions.data[0].status
                    request.user.expire_date = datetime.fromtimestamp(session.subscriptions.data[0].cancel_at).strftime('%Y-%m-%d')
                    request.user.save()
                    request.user.expire_date = datetime.fromtimestamp(session.subscriptions.data[0].cancel_at).strftime('%b %d, %Y')

        return super().dispatch(request, session)

    def get_context_data(self, **kwargs):

        context = {}
        film = Film.objects.order_by('-views')
        lis = []
        if len(film) > 10:
            for i in range(10):
                lis.append(film[i])
            context['films'] = lis
        else:
            context['films'] = film
        if self.request.user.is_authenticated:
            try:
                context['list'] = MyList.objects.get(user_id=self.request.user.pk).film.all()
            except:
                pass
            try:
                film_genre = MyList.objects.get(user_id=self.request.user.pk).film.all().values('genre').annotate(count=Count('genre')).order_by('-count').first()
                genre = film_genre['genre']
                all_film = Film.objects.all().filter(genre=genre)
                context['list'] = context['list'].filter(genre=genre)
                context['list'] = set(all_film).difference(set(context['list']))
                list_film = list(context['list'])
                lis = []
                if len(list_film) > 10:
                    for i in range(10):
                        lis.append(list_film[i])
                    context['list'] = set(lis)
                else:
                    pass
            except:
                pass
        accounts = Account.objects.all()
        context['accounts'] = accounts

        return context
