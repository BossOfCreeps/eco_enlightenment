from uuid import UUID

import ics
from django.db import models

from organizations.models import Organization
from services import create_vk_chat, parse_text
from users.models import User


class EventTag(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тэг мероприятия"
        verbose_name_plural = "Тэги мероприятий"


class Event(models.Model):
    name = models.TextField("Название мероприятия")
    description = models.TextField("Описание")
    start_date = models.DateTimeField("Дата и время начала")
    finish_date = models.DateTimeField("Дата и время окончания")
    tags = models.ManyToManyField(EventTag, verbose_name="Тэги")
    image = models.FileField("Изображение", blank=True, null=True)
    address = models.TextField("Адрес")
    latitude = models.FloatField("Широта")
    longitude = models.FloatField("Долгота")
    organization = models.ForeignKey(Organization, models.CASCADE, "events", verbose_name="Организация")
    eco_balance = models.IntegerField("Эко-баллы")

    vk_chat_id = models.IntegerField(blank=True, null=True)
    vk_chat_link = models.URLField(blank=True, null=True)
    extra = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

    def make_ics(self):
        c = ics.Calendar()
        c.events.add(
            ics.Event(
                uid=str(UUID(int=self.id)),
                name=self.name,
                description=self.description,
                begin=self.start_date,
                end=self.finish_date,
                location=self.address,
            )
        )
        return "".join(c.serialize_iter())

    def save(self, *args, **kwargs):
        if not self.id:
            self.vk_chat_id, self.vk_chat_link = create_vk_chat(self.name)

        if self.extra is None:
            self.extra = {}

        self.extra["search"] = list(parse_text(self.name + " " + self.description))

        return super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/events/{self.id}/"  # TODO

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"
        ordering = ["-start_date", "id"]


class Ticket(models.Model):
    event = models.ForeignKey(Event, models.CASCADE, "tickets")
    user = models.ForeignKey(User, models.CASCADE, "tickets")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.id:
            self.user.eco_balance += self.event.eco_balance
            self.user.save()

    def __str__(self):
        return f"{self.user} на {self.event}"

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"


class AssistanceOffer(models.Model):
    event = models.ForeignKey(Event, models.CASCADE, "assistance_offers")
    organization = models.ForeignKey(Organization, models.CASCADE, "assistance_offers")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization} на {self.event}"

    class Meta:
        verbose_name = "Предложение помощи"
        verbose_name_plural = "Предложения помощи"
