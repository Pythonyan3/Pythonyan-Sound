from django.urls import path
from .views import ProfileDetailsView, OwnProfileView, ProfileCreateView, EmailVerificationView, TokenRefreshView, \
    LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path('', OwnProfileView.as_view()),
    path('<int:user_id>/', ProfileDetailsView.as_view()),
    path('registration/', ProfileCreateView.as_view()),
    path('registration/email-verify/<str:token>/', EmailVerificationView.as_view(), name="email-verification"),
    path('logout/', LogoutView.as_view()),

    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
]
