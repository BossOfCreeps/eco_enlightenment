from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ReadOnlyModelViewSet

from news.filters import NewsFilter
from news.models import News, NewsTag
from news.serializers import NewsSerializer, NewsTagSerializer


class NewsViewSet(ReadOnlyModelViewSet, CreateModelMixin):
    queryset = News.objects.select_related("organization").prefetch_related("organization__users", "tags").all()
    serializer_class = NewsSerializer
    filterset_class = NewsFilter

    pagination_class = LimitOffsetPagination


class NewsTagViewSet(ReadOnlyModelViewSet, CreateModelMixin):
    queryset = NewsTag.objects.all()
    serializer_class = NewsTagSerializer
