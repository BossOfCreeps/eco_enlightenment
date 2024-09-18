from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.routers import DefaultRouter
from rest_framework_social_oauth2.views import TokenView

from users.views import DownloadStatisticsView, LogoutView, RegistrationView, UserView

router = DefaultRouter()

urlpatterns = [
    path("me/", UserView.as_view(), name="me"),
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", ObtainAuthToken.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("download_statistics/", DownloadStatisticsView.as_view(), name="download_statistics_users"),
    path("oauth/token/", TokenView.as_view(), name="oauth_token"),
] + router.urls
