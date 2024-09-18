from rest_framework.routers import DefaultRouter

from news.views import NewsViewSet, NewsTagViewSet

router = DefaultRouter()
router.register("news", NewsViewSet, basename="news")
router.register("tags", NewsTagViewSet, basename="tags")

urlpatterns = router.urls
