from rest_framework import serializers

from events.models import Event, EventTag, Ticket, AssistanceOffer
from organizations.serializers import OrganizationSerializer
from services import SiteParseEnum
from users.serializers import UserShortSerializer


class EventTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTag
        fields = "__all__"


class EventMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "latitude", "longitude", "address"]


class EventSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(write_only=True)

    @staticmethod
    def validate_tags(value):
        return value.split(",")

    def to_representation(self, instance: Event):
        ret = super(EventSerializer, self).to_representation(instance)
        ret["tags"] = EventTagSerializer(instance.tags.all(), many=True).data
        ret["organization"] = OrganizationSerializer(instance.organization).data
        return ret

    class Meta:
        model = Event
        exclude = ["extra"]


class TicketSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super(TicketSerializer, self).create(validated_data)

    def to_representation(self, instance: Ticket):
        ret = super(TicketSerializer, self).to_representation(instance)
        ret["event"] = EventSerializer(instance.event).data
        return ret

    class Meta:
        model = Ticket
        fields = "__all__"


class AssistanceOfferSerializer(serializers.ModelSerializer):
    def to_representation(self, instance: AssistanceOffer):
        ret = super(AssistanceOfferSerializer, self).to_representation(instance)
        ret["event"] = EventSerializer(instance.event).data
        ret["organization"] = OrganizationSerializer(instance.organization).data
        return ret

    class Meta:
        model = AssistanceOffer
        fields = "__all__"


class SiteParseRequestSerializer(serializers.Serializer):
    site = serializers.ChoiceField(choices=[(item.value, item.name) for item in SiteParseEnum])
    link = serializers.CharField()


class OrganizationParseRequestSerializer(serializers.Serializer):
    inn = serializers.CharField()
