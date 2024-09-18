from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from events.filters import AssistanceOfferFilter, EventFilter, TicketFilter
from events.models import AssistanceOffer, Event, EventTag, Ticket
from events.permissions import EventPermission
from events.serializers import (
    AssistanceOfferSerializer,
    EventMapSerializer,
    EventSerializer,
    EventTagSerializer,
    SiteParseRequestSerializer,
    TicketSerializer,
)
from events.utils import mass_send_new_event
from services import (
    SiteParseEnum,
    create_events_excel,
    parse_dobro_ru,
    parse_leader_id,
    parse_timepad,
    parse_vk_event,
    parse_vk_wall,
    set_vk_admin_role,
)


class EventViewSet(ReadOnlyModelViewSet, CreateModelMixin):
    queryset = Event.objects.select_related("organization").prefetch_related("tags", "organization__users").all()
    serializer_class = EventSerializer
    filterset_class = EventFilter
    permission_classes = [EventPermission]

    parser_classes = [MultiPartParser]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer: EventSerializer):
        instance: Event = serializer.save()
        mass_send_new_event(instance)

    @extend_schema(parameters=[SiteParseRequestSerializer])
    @action(["get"], False, "parse_site", "parsesite")
    def parse_site(self, request, *args, **kwargs):
        serializer = SiteParseRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        link, site = serializer.validated_data["link"], serializer.validated_data["site"]

        if site == SiteParseEnum.DOBRO_RU.value:
            data = parse_dobro_ru(link)
        elif site == SiteParseEnum.LEADER_ID.value:
            data = parse_leader_id(link)
        elif site == SiteParseEnum.TIMEPAD.value:
            data = parse_timepad(link)
        elif site == SiteParseEnum.VK_WALL.value:
            data = parse_vk_wall(link)
        elif site == SiteParseEnum.VK_EVENT.value:
            data = parse_vk_event(link)
        else:
            return Response({"message": "Передан неизвестный тип"}, status.HTTP_400_BAD_REQUEST)

        return Response(data.__dict__)

    @action(["post"], True, "make_admin_in_vk_chat", "makeadmininvkchat")
    def make_admin_in_vk_chat(self, request, *args, **kwargs):
        if not self.request.user.vk_id:
            return Response({"message": "Пользователь не установил ВК"}, status.HTTP_400_BAD_REQUEST)

        if not set_vk_admin_role(self.get_object().vk_chat_id, self.request.user.vk_id):
            return Response({"message": "Пользователь не находится в чате"}, status.HTTP_400_BAD_REQUEST)

        return Response()

    @action(["get"], True, "make_ics", "makeics")
    def make_ics(self, request, *args, **kwargs):
        response = HttpResponse(self.get_object().make_ics())
        response["Content-Disposition"] = f'attachment; filename="calendar_{self.get_object().id}.ics"'
        return response

    @action(["get"], False, "download_statistics", "downloadstatistics")
    def download_statistics(self, request, *args, **kwargs):
        result = HttpResponse(create_events_excel(Event.objects.all()).read(), content_type="application/excel")
        result["Content-Disposition"] = "attachment; filename=data.xlsx"
        return result

    @extend_schema(filters=True)
    @action(["get"], False, "map_data", "mapdata")
    def map_data(self, request, *args, **kwargs):
        return Response(EventMapSerializer(self.filter_queryset(self.get_queryset()), many=True).data)


class EventTagViewSet(ReadOnlyModelViewSet):
    queryset = EventTag.objects.all()
    serializer_class = EventTagSerializer


class TicketViewSet(ReadOnlyModelViewSet, CreateModelMixin):
    queryset = (
        Ticket.objects.select_related("event__organization", "user")
        .prefetch_related("event__tags", "event__organization__users")
        .all()
    )
    serializer_class = TicketSerializer
    filterset_class = TicketFilter

    def get_serializer_context(self):
        return super().get_serializer_context() | {"request": self.request}


class AssistanceOfferViewSet(ReadOnlyModelViewSet, CreateModelMixin):
    queryset = (
        AssistanceOffer.objects.select_related("event__organization", "organization")
        .prefetch_related("event__tags", "event__organization__users", "organization__users")
        .all()
    )
    serializer_class = AssistanceOfferSerializer
    filterset_class = AssistanceOfferFilter
