from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient # make requests to our API and check what the response is
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')



def create_user(**params):
    return get_user_model().objects.create_user(**params)




class PublicUserApiTests(TestCase):
    """
        Test the users API (public)
    """
    def setUp(self):
        """ one client for our test suite that
            we can reuse for all of the tests
        """
        self.client = APIClient()

    def test_create_valid_user_success(self):

        """
            Test creating user with valid payload is successful.
            Payload - the object that you pass to the API when you

        """
        payload = {
            'email': 'test@kosta.com',
            'password' : 'test123',
            'first_name': 'Test name',
            'last_name' : 'Second name'
         }

         # make request
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data) #unwind the response
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):

        """ Test creating users that already exists fails """
        payload = {'email':'test@kosta.com', 'password':'test'}
        create_user(**payload)

        # make request
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_password_too_short(self):
        """ Test that the password must be more than 5 characters """
        payload = {'email': 'test@kosta.com', 'password': 'ab',
                    'first_name': 'Name'}

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Test that a token is created for the user """
        payload = {'email': 'kosta@test.com', 'password':'testpass'}
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invaild_credentials(self):
        """ Test that token is not created if invalid credentials are given """
        create_user(email='kosta@test.com', password='testpass')
        payload = {'email':'kosta@test.com', 'password':'wrong_pass'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """ Test that token is not created if user doesn't exist """

        payload = {'email': 'kosta@test.com', 'password':'testpass'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """ Test that email and password are required """
        res = self.client.post(TOKEN_URL, {'email':'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)