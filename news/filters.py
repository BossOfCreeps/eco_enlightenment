import django_filters
from django.db.models import QuerySet

from news.models import News, NewsTag


class NewsFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(queryset=NewsTag.objects.all(), method="filter_tags")

    @staticmethod
    def filter_tags(queryset: QuerySet[News], _: str, value: list[NewsTag]) -> QuerySet:
        for v in value:
            queryset = queryset.filter(tags=v)
        return queryset

    class Meta:
        model = News
        fields = []
