from django.views.generic import TemplateView

from account.models import Account


class HomeView(TemplateView):

    model = Account
    template_name = 'personal/home.html'

    # Serve per passare i contenuti
    def get_context_data(self, **kwargs):

        context = {}

        accounts = Account.objects.all()
        context['accounts'] = accounts

        return context
