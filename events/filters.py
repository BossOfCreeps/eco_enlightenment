import datetime
from functools import reduce
from operator import and_

import django_filters
from django.db.models import QuerySet, Q
from django.utils import timezone

from events.models import Event, EventTag, Ticket, AssistanceOffer
from organizations.models import Organization
from services import parse_text


class EventFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(method="filter_date")
    q = django_filters.CharFilter(method="filter_q")
    tags = django_filters.ModelMultipleChoiceFilter(queryset=EventTag.objects.all(), method="filter_tags")
    organization = django_filters.ModelMultipleChoiceFilter(queryset=Organization.objects.all())
    source = django_filters.ChoiceFilter(
        method="filter_source", choices=[("ALL", "ALL"), ("ACTIVE", "ACTIVE"), ("ARCHIVE", "ARCHIVE")]
    )

    @staticmethod
    def filter_date(queryset: QuerySet[Event], _: str, value: datetime.date) -> QuerySet:
        return queryset.filter(start_date__date__lte=value, finish_date__date__gte=value) if value else queryset

    @staticmethod
    def filter_q(queryset: QuerySet[Event], _: str, value: str) -> QuerySet:
        if not value:
            return queryset

        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | reduce(and_, [Q(extra__search__icontains=word) for word in parse_text(value)])
        )

    @staticmethod
    def filter_tags(queryset: QuerySet[Event], _: str, value: list[EventTag]) -> QuerySet:
        for v in value:
            queryset = queryset.filter(tags=v)
        return queryset

    @staticmethod
    def filter_source(queryset: QuerySet[Ticket], _, value: str):
        if value == "ALL":
            return queryset
        elif value == "ACTIVE":
            return queryset.filter(start_date__date__gte=timezone.now())
        elif value == "ARCHIVE":
            return queryset.filter(start_date__date__lt=timezone.now())

    class Meta:
        model = Event
        fields = []


class TicketFilter(django_filters.FilterSet):
    source = django_filters.ChoiceFilter(
        method="filter_source", choices=[("ALL", "ALL"), ("ACTIVE", "ACTIVE"), ("ARCHIVE", "ARCHIVE")]
    )

    def filter_source(self, queryset: QuerySet[Ticket], _, value: str):
        if value == "ALL":
            return queryset.filter(user=self.request.user)
        elif value == "ACTIVE":
            return queryset.filter(user=self.request.user, event__start_date__date__gte=timezone.now())
        elif value == "ARCHIVE":
            return queryset.filter(user=self.request.user, event__start_date__date__lt=timezone.now())

    class Meta:
        model = Ticket
        fields = ["event", "user"]


class AssistanceOfferFilter(django_filters.FilterSet):
    class Meta:
        model = AssistanceOffer
        fields = ["event", "organization"]
