from datetime import datetime

import stripe
from django.views.generic import TemplateView

from account.models import Account


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

    # Serve per passare i contenuti
    def get_context_data(self, **kwargs):

        context = {}

        accounts = Account.objects.all()
        context['accounts'] = accounts

        return context
