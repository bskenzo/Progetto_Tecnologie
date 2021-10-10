from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.contrib.auth import logout, update_session_auth_hash
from django.views.generic import CreateView, TemplateView, UpdateView

from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from django.urls import reverse_lazy
from account.models import Account


class RegisterUser(CreateView):
    form_class = RegistrationForm
    template_name = 'account/register.html'
    success_url = reverse_lazy('home')


class LogoutUser(LogoutView):

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


class UpdateUser(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Account
    form_class = AccountUpdateForm
    template_name = 'account/account.html'
    success_url = reverse_lazy('account')
    success_message = "Updated successfully"
    permission_denied_message = "You must authenticate first!"

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
