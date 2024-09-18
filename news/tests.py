from unittest import skip

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from freezegun import freeze_time
from parameterized import parameterized
from rest_framework import status

from news.models import News
from test_utils import _APITestCase


class NewsTests(_APITestCase):
    @parameterized.expand(
        [
            ({}, [1, 2, 3, 4, 5]),
            ({"limit": 2}, [1, 2]),
            ({"offset": 2}, [3, 4, 5]),
            ({"limit": 2, "offset": 2}, [3, 4]),
            ({"tags": [1]}, [1, 2, 3, 5]),
            ({"tags": [2]}, [3, 4]),
            ({"tags": [1, 2]}, [3]),
        ]
    )
    def test_list(self, query, result):
        response = self.client.get(reverse("news:news-list"), query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([r["id"] for r in response.json()["results"]], result)

    def test_detail(self):
        response = self.client.get(reverse("news:news-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": 1,
                "name": "a",
                "description": "description",
                "created_at": "2024-09-16T03:00:00+03:00",
                "image": None,
                "organization": {
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
                    "image": "/media/foo1.jpg",
                },
                "tags": [{"id": 1, "name": "name"}],
            },
        )

    @freeze_time("2017-06-23 07:28:00")
    def test_create(self):
        response = self.client.post(
            reverse("news:news-list"),
            {
                "name": "name",
                "description": "description",
                "organization": 1,
                "tags": "1,2",
                "image": SimpleUploadedFile("foo_4.jpg", b"1", "image/jpeg"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json(),
            {
                "id": 6,
                "name": "name",
                "description": "description",
                "created_at": "2017-06-23T10:28:00+03:00",
                "image": "http://testserver/media/foo_4.jpg",
                "organization": {
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
                    "image": "/media/foo1.jpg",
                },
                "tags": [{"id": 1, "name": "name"}, {"id": 2, "name": "second"}],
            },
        )

    @skip
    def test_update(self):
        response = self.client.patch(reverse("events:news-detail", args=[1]), {"name": "new"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {})

    @skip
    def test_delete(self):
        response = self.client.delete(reverse("news:news-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(News.objects.count(), 4)


class NewsTagTests(_APITestCase):
    def test_list(self):
        response = self.client.get(reverse("news:tags-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [{"id": 1, "name": "name"}, {"id": 2, "name": "second"}])

    def test_detail(self):
        response = self.client.get(reverse("news:tags-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"id": 1, "name": "name"})
