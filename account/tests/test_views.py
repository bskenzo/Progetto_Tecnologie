from django.test import TestCase
from django.urls import reverse

# Create your tests here.
from account.models import Account


class BaseTest(TestCase):

    def setUp(self):
        self.login_url = reverse('account:login')
        self.logout_url = reverse('account:logout')
        self.user = Account.objects.create_user(
            email='test@gmail.com',
            username='pippo',
            password='pluto123',
        )
        self.user.save()
        self.credentials = {
            'email': 'test@gmail.com',
            'password': 'pluto123'}
        return super(BaseTest, self).setUp()


class LoginTest(BaseTest):
    def test_login_view(self):
        response = self.client.get(self.login_url, follow=True)
        self.assertEqual(response.status_code, 200)
        print('login view\n', response.content, '\n\n')
        self.assertTemplateUsed(response, 'account/login.html')

    def test_login_user(self):
        self.client.login(email=self.credentials['email'], password=self.credentials['password'])
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        print(response.content)


class LogoutTest(BaseTest):

    def test_logout_view_no_authenticate(self):
        response = self.client.get(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)
        print('logout no authenticate\n', response.content, '\n\n')
        self.assertTemplateUsed(response, 'account/must_authenticate.html')

    def test_logout_view_authenticate(self):
        self.client.login(email=self.credentials['email'], password=self.credentials['password'])
        response = self.client.post(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)
        print('logout authenticate\n', response.content, '\n\n')
        self.assertTemplateUsed(response, 'movienet/home.html')