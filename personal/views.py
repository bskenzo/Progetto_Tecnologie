from datetime import datetime

import stripe
from django.views.generic import TemplateView
from django.db.models import Count
from account.models import Account
from movie.models import Film, MyList, CATEGORY_CHOICES


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
        if len(film) > 20:
            for i in range(20):
                lis.append(film[i])
            context['films'] = lis
        else:
            context['films'] = film

        if self.request.user.is_authenticated:
            try:
                context['list'] = MyList.objects.get(user_id=self.request.user.pk).film.all()
                film_genre = MyList.objects.get(user_id=self.request.user.pk).film.all().values('genre').annotate(count=Count('genre')).order_by('-count')
                max = None
                for f in film_genre:
                    genre = f['genre']
                    all_film = Film.objects.all().filter(genre=genre)
                    temp = context['list'].filter(genre=genre)
                    print('sono temp', temp)
                    print('sono difference', len(all_film.difference(temp)))
                    if len(all_film.difference(temp)) > 0:
                        max = all_film.difference(temp)
                        break

                if max is not None:
                    max = max.order_by('-views')
                    if len(max) > 20:
                        for i in range(20):
                            lis.append(max[i])
                        context['list'] = lis
                    else:
                        context['list'] = max
                else:
                    context['list'] = []
            except:
                pass

        context['choices'] = CATEGORY_CHOICES
        context['genres'] = []
        temp = {}

        for category in CATEGORY_CHOICES:
            try:
                film_category = Film.objects.all().filter(genre=category[0])
                if film_category:
                    counter = 0

                    for i in film_category:
                        counter += 1
                        temp.update({str(counter): i})

                    if len(film_category) > 20:
                        list_film = []
                        for i in range(1, 21):
                            list_film.append(temp.get(str(i)))
                        context['genres'].append([category[0], list_film])

                    else:
                        context['genres'].append([category[0], film_category])
            except:
                pass

        return context
