import os

from rest_framework.test import APITestCase


class _APITestCase(APITestCase):
    maxDiff = None

    fixtures = ["test_fixture.json"]

    def setUp(self):
        for file in os.listdir("media"):
            if file.startswith("foo"):
                os.remove(f"media/{file}")
