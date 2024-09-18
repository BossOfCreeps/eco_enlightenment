from django.db import models

from users.models import User


class Organization(models.Model):
    full_name = models.TextField("Полное название")
    short_name = models.TextField("Короткое название")
    address = models.TextField("Адрес")
    ogrn = models.TextField("ОРГН")
    inn = models.TextField("ИНН")
    kpp = models.TextField("КПП")
    okpo = models.TextField("ОКПО")
    director_full_name = models.TextField("Директор")
    director_inn = models.TextField("Директор ИНН")
    activities = models.TextField("Виды деятельности")
    reg_date = models.DateField("Дата регистрации")
    phone = models.TextField("Телефон")
    email = models.EmailField("Email")
    description = models.TextField("Описание")
    image = models.FileField("Изображение", blank=True, null=True)

    users = models.ManyToManyField(User, "organizations")

    def __str__(self):
        return self.short_name

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"
