from random import randint
from django.test import SimpleTestCase
from django.urls import reverse, resolve

# Create your tests here.
from account.views import PricingView, LoginUser, LogoutUser, RegisterUser, MustAuthenticate, PasswordChangeViewP, \
    DeleteAccountView, CheckoutView, UpdateUser


class TestUrls(SimpleTestCase):

    def test_pricing_url_resolved(self):
        url = reverse('account:pricing')
        self.assertEqual(resolve(url).func.view_class, PricingView)

    def test_register_url_resolved(self):
        url = reverse('account:register')
        self.assertEqual(resolve(url).func.view_class, RegisterUser)

    def test_login_url_resolved(self):
        url = reverse('account:login')
        self.assertEqual(resolve(url).func.view_class, LoginUser)

    def test_logout_url_resolved(self):
        url = reverse('account:logout')
        self.assertEqual(resolve(url).func.view_class, LogoutUser)

    def test_update_url_resolved(self):
        url = reverse('account:account')
        self.assertEqual(resolve(url).func.view_class, UpdateUser)

    def test_must_authenticated_resolved(self):
        url = reverse('account:must_authenticate')
        self.assertEqual(resolve(url).func.view_class, MustAuthenticate)

    def test_checkout_url_resolved(self):
        url = reverse('account:checkout')
        self.assertEqual(resolve(url).func.view_class, CheckoutView)

    def test_delete_url_resolved(self):
        pk = randint(0, 10000)
        url = reverse('account:delete', args=[pk])
        self.assertEqual(resolve(url).func.view_class, DeleteAccountView)

    def test_password_change_url_resolved(self):
        url = reverse('account:password_change')
        self.assertEqual(resolve(url).func.view_class, PasswordChangeViewP)