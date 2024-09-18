from unittest import skip

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from parameterized import parameterized
from rest_framework import status

from organizations.models import Organization
from test_utils import _APITestCase
from users.models import User


class OrganizationTests(_APITestCase):
    @parameterized.expand(
        [
            ({}, [1, 2]),
            ({"source": "MY"}, [1]),
        ]
    )
    def test_list(self, query, result):
        self.client.force_login(User.objects.get(email="email@test.ru"))

        response = self.client.get(reverse("organizations:organizations-list"), query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([r["id"] for r in response.json()], result)

    def test_detail(self):
        response = self.client.get(reverse("organizations:organizations-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": 1,
                "users": [
                    {"email": "2@test.ru", "full_name": None, "vk_link": None, "image": None},
                    {
                        "email": "email@test.ru",
                        "full_name": None,
                        "vk_link": "https://vk.com/bossofcreeps",
                        "image": None,
                    },
                ],
                "full_name": "Полное название",
                "short_name": "Короткое название",
                "address": "Адрес",
                "ogrn": "ОГРН",
                "inn": "ИНН",
                "kpp": "КПП",
                "okpo": "ОКПО",
                "director_full_name": "Дир ФИО",
                "director_inn": "Дир ИНН",
                "activities": "Активности",
                "reg_date": "2020-01-01",
                "phone": "Телефон",
                "email": "Email",
                "description": "Описание",
                "image": "http://testserver/media/foo1.jpg",
            },
        )

    def test_create(self):
        self.client.force_login(User.objects.get(email="email@test.ru"))

        response = self.client.post(
            reverse("organizations:organizations-list"),
            {
                "full_name": "Название",
                "short_name": "Короткое название",
                "address": "Адрес",
                "phone": "Телефон",
                "email": "Email@mail.ru",
                "description": "Описание",
                "ogrn": "ОГРН",
                "inn": "ИНН",
                "kpp": "КПП",
                "okpo": "ОКПО",
                "director_full_name": "Дир ФИО",
                "director_inn": "Дир ИНН",
                "activities": "Активности",
                "reg_date": "2020-01-01",
                "image": SimpleUploadedFile("foo_2.jpg", b"1"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json(),
            {
                "id": 3,
                "users": [
                    {
                        "email": "email@test.ru",
                        "full_name": None,
                        "vk_link": "https://vk.com/bossofcreeps",
                        "image": None,
                    }
                ],
                "full_name": "Название",
                "short_name": "Короткое название",
                "address": "Адрес",
                "ogrn": "ОГРН",
                "inn": "ИНН",
                "kpp": "КПП",
                "okpo": "ОКПО",
                "director_full_name": "Дир ФИО",
                "director_inn": "Дир ИНН",
                "activities": "Активности",
                "reg_date": "2020-01-01",
                "phone": "Телефон",
                "email": "Email@mail.ru",
                "description": "Описание",
                "image": "http://testserver/media/foo_2.jpg",
            },
        )

    @skip
    def test_update(self):
        response = self.client.patch(reverse("organizations:organizations-detail", args=[1]), {"phone": "новый"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": 1,
                "users": [
                    {"email": "2@test.ru", "full_name": None, "vk_link": None, "image": None},
                    {
                        "email": "email@test.ru",
                        "full_name": None,
                        "vk_link": "https://vk.com/bossofcreeps",
                        "image": None,
                    },
                ],
                "full_name": "Полное название",
                "short_name": "Короткое название",
                "address": "Адрес",
                "phone": "новый",
                "email": "Email",
                "vk": "ВК",
                "description": "Описание",
                "type": "NON_COMMERCIAL",
                "image": "http://testserver/media/foo1.jpg",
            },
        )

    @skip
    def test_delete(self):
        response = self.client.delete(reverse("organizations:organizations-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Organization.objects.count(), 1)
