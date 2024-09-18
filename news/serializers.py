from rest_framework import serializers

from news.models import News, NewsTag
from organizations.serializers import OrganizationSerializer


class NewsSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(write_only=True)

    @staticmethod
    def validate_tags(value):
        return value.split(",")

    def to_representation(self, instance: News):
        ret = super(NewsSerializer, self).to_representation(instance)
        ret["tags"] = NewsTagSerializer(instance.tags.all(), many=True).data
        ret["organization"] = OrganizationSerializer(instance.organization).data
        return ret

    class Meta:
        model = News
        fields = "__all__"


class NewsTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsTag
        fields = "__all__"
