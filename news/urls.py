from rest_framework.routers import DefaultRouter

from news.views import NewsTagViewSet, NewsViewSet

router = DefaultRouter()
router.register("news", NewsViewSet, basename="news")
router.register("tags", NewsTagViewSet, basename="tags")

urlpatterns = router.urls
