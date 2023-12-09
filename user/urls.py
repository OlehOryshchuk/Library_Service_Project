from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from .views import CreateUserView, ManagerUserView

urlpatterns = [
    path("users/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    path("users/register/", CreateUserView.as_view(), name="create"),
    path("users/me/", ManagerUserView.as_view(), name="manage"),
]

app_name = "user"
