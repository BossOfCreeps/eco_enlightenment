from django.contrib import admin

from news.models import News, NewsTag


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    pass


@admin.register(NewsTag)
class NewsTagAdmin(admin.ModelAdmin):
    pass
