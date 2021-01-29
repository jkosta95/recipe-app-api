from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

"""
    reverse - allow us to generate URLs for our Django admin page
    Client - allow us to make test requests to our application in our unit test

"""


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email = "admin@mail.com",
            password = 'pass123'
        )
        self.client.force_login(self.admin_user) # log a user in with the Django AuthenticationMiddleware
        self.user = get_user_model().objects.create_user(
            email = "test@mail.com",
            password = "pass123",
            first_name = "John",
            last_name = "Cubick"
        )

    def test_users_listed(self):
        """ Test that users are listed on user page """
        url = reverse('admin:core_user_changelist') #read about this
        res = self.client.get(url) # perform a http get on the url using client

        self.assertContains(res, self.user.first_name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """ Test that the user edit page works """

        url = reverse('admin:core_user_change', args=[self.user.id])
        #/admin/core/user/1 -> id
        res = self.client.get(url)

        self.assertEqual(res.status_code , 200) # response is 200 -> checklist

    def test_create_user_page(self):
        """ Test that the create user page works """

        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
