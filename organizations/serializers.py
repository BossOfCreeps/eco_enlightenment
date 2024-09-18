from rest_framework import serializers

from organizations.models import Organization
from users.serializers import UserShortSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    users = UserShortSerializer(many=True, read_only=True)

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.users.add(self.context["request"].user)
        return instance

    class Meta:
        model = Organization
        fields = "__all__"
