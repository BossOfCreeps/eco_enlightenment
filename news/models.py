from django.db import models

from organizations.models import Organization


class NewsTag(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тэг новости"
        verbose_name_plural = "Тэги новостей"


class News(models.Model):
    name = models.TextField("Название новости")
    description = models.TextField("Описание новости")
    full_text = models.TextField("Полный текст")
    organization = models.ForeignKey(Organization, models.CASCADE, verbose_name="Организация")
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(NewsTag, verbose_name="Тэги")
    image = models.FileField("Изображение", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
