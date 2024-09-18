from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from services import create_users_excel
from users.models import User
from users.serializers import UserShortSerializer, UserFullSerializer


class UserView(RetrieveAPIView):
    serializer_class = UserFullSerializer

    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(self.request.user).data)


class DownloadStatisticsView(RetrieveAPIView):
    serializer_class = None

    def retrieve(self, request, *args, **kwargs):
        result = HttpResponse(create_users_excel(User.objects.all()).read(), content_type="application/excel")
        result["Content-Disposition"] = f"attachment; filename=data.xlsx"
        return result


class RegistrationView(CreateAPIView):
    serializer_class = UserShortSerializer

    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**serializer.validated_data)
        return Response(self.get_serializer(user).data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    serializer_class = None

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        self.request.user.auth_token.delete()
        return Response()
