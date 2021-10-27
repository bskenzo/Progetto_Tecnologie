from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.contrib.auth import logout, update_session_auth_hash, login, authenticate
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView

from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from django.urls import reverse_lazy, reverse
from account.models import Account
import stripe


class RegisterUser(CreateView):

    form_class = RegistrationForm
    template_name = 'account/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):

        try:
            self.success_url = self.request.GET['next']
        except:
            pass

        to_return = super().form_valid(form)
        user = authenticate(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
        )
        login(self.request, user)

        return to_return


class LogoutUser(LoginRequiredMixin, LogoutView):

    def get_next_page(self):

        next_page = super(LogoutUser, self).get_next_page()

        messages.add_message(
            self.request, messages.SUCCESS,
            'You successfully log out!'
        )
        return next_page


class LoginUser(LoginView):

    form_class = AccountAuthenticationForm
    template_name = 'account/login.html'
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        try:
            self.success_url = request.GET['next']
        except:
            pass

        return super(LoginUser, self).get(request, *args, **kwargs)


class UpdateUser(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = Account
    form_class = AccountUpdateForm
    template_name = 'account/account.html'
    success_url = reverse_lazy('account:account')
    success_message = "Updated successfully"
    permission_denied_message = "You must authenticate first!"

    def dispatch(self, request, *args, **kwargs):

        session = None

        if not request.user.is_authenticated:
            next_page = f'?next=/account/'
            return redirect(reverse('account:must_authenticate') + next_page)

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

    # Return the current object to display
    def get_object(self, queryset=None):
        return self.request.user

    # Message to display if write account in URL
    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return super(UpdateUser, self).handle_no_permission()


class PasswordChangeViewP(PasswordChangeView):

    def form_valid(self, form):
        form.save()
        self.request.session.flush()
        logout(self.request)
        update_session_auth_hash(self.request, form.user)
        return render(self.request, 'registration/password_change_done.html')


class MustAuthenticate(TemplateView):

    template_name = 'account/must_authenticate.html'

    def get(self, request, *args, **kwargs):
        try:
            context = {'next': self.request.GET['next']}
            kwargs.update(context)
            print(kwargs)
        except:
            pass
        return super(MustAuthenticate, self).get(request, *args, **kwargs)


class DeleteAccountView(LoginRequiredMixin, DeleteView):

    model = Account
    template_name = 'account/delete_account.html'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        if request.user.stripe_id != "id_test":
            stripe.Customer.delete(request.user.stripe_id)

        messages.success(request, "The user is deleted")
        return super().delete(request)


class PricingView(TemplateView):

    template_name = 'account/subscribe.html'


class CheckoutView(LoginRequiredMixin, UpdateView):

    template_name = 'account/payments/checkout.html'

    def post(self, request, *args, **kwargs):

        coupons = {'christmas': 20, 'easter': 10, 'epiphany': 5}

        # se l'utente esiste su stripe
        if request.user.stripe_id != "id_test":
            session = stripe.Customer.retrieve(request.user.stripe_id, expand=['subscriptions']) # recupero l'abbonamento
            # se esiste e non ha un abbonamento attivo, gli creiamo un abbonamento
            if not session.subscriptions.data:
                messages.add_message(
                    self.request, messages.SUCCESS,
                    'Payment successfully!'
                )
                if request.POST['price'] == 'Monthly':
                    price = 'price_1JjpqoH1UjLFf6ccEDLeXR4F'

                else:
                    price = 'price_1Jjps4H1UjLFf6ccT1s7xqtU'

                if request.POST['coupon'] in coupons:
                    percentage = coupons[request.POST['coupon'].lower()]
                    try:
                        stripe.Coupon.create(duration='once',
                                             id=request.POST['coupon'].lower(),
                                             percent_off=percentage)
                    except:
                        pass
                    subscription = stripe.Subscription.create(customer=request.user.stripe_id,
                                                              items=[{'price': price}],
                                                              coupon=request.POST['coupon'].lower(),
                                                              cancel_at_period_end=True)
                else:
                    subscription = stripe.Subscription.create(customer=request.user.stripe_id,
                                                              items=[{'price': price}],
                                                              cancel_at_period_end=True)

                session = stripe.Customer.retrieve(request.user.stripe_id, expand=['subscriptions']) # recuperiamo la sessione aggiornata
                customer = request.user
                customer.is_subscribe = True
                customer.stripe_subscription_id = subscription.id
                customer.expire_date = datetime.fromtimestamp(session.subscriptions.data[0].cancel_at).strftime('%Y-%m-%d')
                customer.save()
            # altrimenti se esiste e ha gia un abbonamento
            else:
                messages.add_message(
                    self.request, messages.SUCCESS,
                    'User just have a subscribe!'
                )
        # se non esiste su stripe
        else:
            messages.add_message(
                self.request, messages.SUCCESS,
                'Payment successfully!'
            )

            stripe_customer = stripe.Customer.create(email=request.user.email,
                                                     source=request.POST['stripeToken'])

            if request.POST['price'] == 'Monthly':
                price = 'price_1JjpqoH1UjLFf6ccEDLeXR4F'

            else:
                price = 'price_1Jjps4H1UjLFf6ccT1s7xqtU'

            if request.POST['coupon'] in coupons:
                percentage = coupons[request.POST['coupon'].lower()]
                try:
                    stripe.Coupon.create(duration='once',
                                         id=request.POST['coupon'].lower(),
                                         percent_off=percentage)
                except:
                    pass
                subscription = stripe.Subscription.create(customer=stripe_customer.id,
                                                          items=[{'price': price}],
                                                          coupon=request.POST['coupon'].lower(),
                                                          cancel_at_period_end=True)
            else:
                subscription = stripe.Subscription.create(customer=stripe_customer.id,
                                                          items=[{'price': price}],
                                                          cancel_at_period_end=True)

            customer = request.user
            customer.stripe_id = stripe_customer.id
            customer.is_subscribe = True
            customer.stripe_subscription_id = subscription.id
            session = stripe.Customer.retrieve(request.user.stripe_id, expand=['subscriptions'])
            customer.expire_date = datetime.fromtimestamp(session.subscriptions.data[0].cancel_at).strftime('%Y-%m-%d')
            customer.save()

        return redirect('home')

    def get(self, request, *args, **kwargs):
        coupons = {'christmas': 20, 'easter': 10, 'epiphany': 5}

        coupon_amount = 0
        coupon = 'none'
        price = 'Monthly'
        amount = 8.99
        original_amount = 8.99
        final_amount = 8.99
        if request.method == 'GET' and 'price' in request.GET:
            if request.GET['price'] == 'Annual':
                price = 'Annual'
                amount = 89.99
                original_amount = 89.99
                final_amount = 89.99

        if request.method == 'GET' and 'coupon' in request.GET:
            if request.GET['coupon'].lower() in coupons:
                coupon = request.GET['coupon'].lower()
                percentage = coupons[request.GET['coupon'].lower()]
                coupon_price = float((percentage/100)*amount)
                amount = amount - coupon_price
                coupon_amount = str(coupon_price)
                final_amount = str(round(amount, 2))

        return render(request, 'account/payments/checkout.html', {'price': price, 'amount': amount*100,
                                                                  'coupon': coupon, 'coupon_amount': coupon_amount,
                                                                  'final_amount': final_amount,
                                                                  'original_amount': original_amount})
