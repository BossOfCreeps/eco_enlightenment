from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from events.serializers import OrganizationParseRequestSerializer
from organizations.filters import OrganizationFilter
from organizations.models import Organization
from organizations.serializers import OrganizationSerializer
from services import create_organizations_excel, parse_organization_by_inn


class OrganizationViewSet(ReadOnlyModelViewSet, CreateModelMixin):
    queryset = Organization.objects.prefetch_related("users").all()
    serializer_class = OrganizationSerializer
    filterset_class = OrganizationFilter

    parser_classes = [MultiPartParser]

    def get_serializer_context(self):
        return super().get_serializer_context() | {"request": self.request}

    @extend_schema(parameters=[OrganizationParseRequestSerializer])
    @action(["get"], False, "parse_site", "parsesite")
    def parse_by_inn(self, request, *args, **kwargs):
        serializer = OrganizationParseRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        return Response(parse_organization_by_inn(serializer.validated_data["inn"]).__dict__)

    @action(["get"], False, "download_statistics", "downloadstatistics")
    def download_statistics(self, request, *args, **kwargs):
        result = HttpResponse(
            create_organizations_excel(Organization.objects.all()).read(), content_type="application/excel"
        )
        result["Content-Disposition"] = "attachment; filename=data.xlsx"
        return result
