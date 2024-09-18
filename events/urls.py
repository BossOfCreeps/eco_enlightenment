from rest_framework.routers import DefaultRouter

from events.views import AssistanceOfferViewSet, EventTagViewSet, EventViewSet, TicketViewSet

router = DefaultRouter()
router.register("events", EventViewSet, basename="events")
router.register("tags", EventTagViewSet, basename="tags")
router.register("tickets", TicketViewSet, basename="tickets")
router.register("assistance_offers", AssistanceOfferViewSet, basename="assistance_offers")

urlpatterns = router.urls
