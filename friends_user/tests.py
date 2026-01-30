from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Friends_user

# Create your tests here.

class FriendsUserTests(APITestCase):

    ## Creating a user for testing purposes
    def test_user(self): 
        self.user = Friends_user.objects.create_user(
            username="testuser",
            emailid="testuser@example.com",
            phone_no="1234567890",
            password="testpassword",
            info="This is a test user."
        )

    def test_signup_sucess(self):
        url = reverse('signup')
        data = {
            "username": "newuser",
            "password": "newpass123",
            "emailid": "new@example.com",
            "phone_no": "8888888888"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser")

    def test_signup_missing_fields(self):
        url = reverse('signup')
        data = {
            "username": "incompleteuser",
            "password": "pass123"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_signup_existing_username(self):
        url = reverse('signup')
        data = {
            "username": "testuser",
            "password": "testpassword",
            "emailid": "test@example.com",
            "phone_no": "1234567890",
            "info": "Some info"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
    
    def test_signup_existing_email(self):
        url = reverse('signup')
        data = {
            "username": "uniqueuser",
            "password": "uniquepass",
            "emailid": "test@example.com",
            "phone_no": "9999999999",
            "info": "Some info"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
    
    def test_signup_existing_phone(self):
        url = reverse('signup')
        data = {
            "username": "anotheruser",
            "password": "anotherpass",
            "emailid": "another@example.com",
            "phone_no": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_login_success(self):
        self.test_user()
        url = reverse('login')
        data = {
            "username": "testuser",
            "password": "testpassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
        self.assertEqual(response.data["user"]["username"], "testuser")

    