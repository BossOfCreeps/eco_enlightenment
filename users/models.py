from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from rest_framework.exceptions import ValidationError

from services import get_vk_user_id


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField("Электронная почта", primary_key=True, unique=True)

    full_name = models.TextField("ФИО", null=True, blank=True)
    image = models.FileField("Изображение", null=True, blank=True)
    vk_link = models.URLField("ВК ссылка", null=True, blank=True)

    vk_id = models.IntegerField("ВК ID", null=True, blank=True)
    eco_balance = models.IntegerField("Эко-баллы", default=0)
    is_department = models.BooleanField("Сотрудник департамента", default=False)

    username = None
    first_name = None
    last_name = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.vk_id:
            try:
                self.vk_id = get_vk_user_id(self.vk_link)
            except IndexError:
                raise ValidationError("Не удалось получить ВК ID пользователя")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
