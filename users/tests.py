from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from test_utils import _APITestCase
from users.models import User


class UserTests(_APITestCase):
    def test_me(self):
        self.client.force_login(User.objects.get(email="email@test.ru"))

        response = self.client.get(reverse("users:me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "email": "email@test.ru",
                "full_name": None,
                "has_organization": True,
                "image": None,
                "vk_link": "https://vk.com/bossofcreeps",
            },
        )

    @patch("services.vk.vk_group_api")
    def test_registration(self, mock_vk):
        mock_vk.users.get.return_value = [{"id": 7}]

        response = self.client.post(
            reverse("users:registration"),
            {
                "email": "t@t.ru",
                "password": "pass",
                "full_name": "name",
                "vk_link": "https://vk.com/",
                "image": SimpleUploadedFile("foo_2.jpg", b"1"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json(),
            {
                "email": "t@t.ru",
                "full_name": "name",
                "image": "http://testserver/media/foo_2.jpg",
                "vk_link": "https://vk.com/",
            },
        )

        self.assertEqual(User.objects.count(), 4)

    def test_registration_unique(self):
        response = self.client.post(
            reverse("users:registration"),
            {
                "email": "email@test.ru",
                "password": "pass",
                "full_name": "name",
                "vk_link": "https://vk.com/",
                "image": SimpleUploadedFile("foo_2.jpg", b"1"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"email": ["Пользователь with this Электронная почта already exists."]})

    def test_vk_id(self):
        self.assertEqual(User.objects.get(email="email@test.ru").vk_id, 7)
