from rest_framework import serializers

from users.models import User


class UserShortSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "full_name", "vk_link", "password", "image", "is_department"]


class UserFullSerializer(UserShortSerializer):
    has_organization = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True)

    @staticmethod
    def get_has_organization(obj: User):
        return obj.organizations.exists()

    class Meta:
        model = User
        fields = ["email", "full_name", "vk_link", "password", "image", "has_organization", "is_department"]
