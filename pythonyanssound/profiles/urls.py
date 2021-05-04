from django.urls import path
from .views import ProfileDetailsView, OwnProfileView, ProfileCreateView, EmailVerificationView, TokenRefreshView, \
    LogoutView, LoginView, ChangePasswordView, FollowsListView, FollowView

urlpatterns = [
    path('', OwnProfileView.as_view(), name="own-profile-details"),
    path('<int:user_id>/', ProfileDetailsView.as_view(), name="profile-details"),
    path('registration/', ProfileCreateView.as_view(), name="profile-registration"),
    path('registration/email-verify/<str:token>/', EmailVerificationView.as_view(), name="email-verification"),
    path('password-change/', ChangePasswordView.as_view(), name="profile-change-password"),
    path('logout/', LogoutView.as_view(), name="profile-logout"),
    path('login/', LoginView.as_view(), name="profile-login"),
    path('token/refresh/', TokenRefreshView.as_view(), name="profile-token-refresh"),
    path('followings/', FollowsListView.as_view(), name="profile-followings"),
    path('followings/<int:profile_id>/', FollowView.as_view(), name="profile-followings-management"),
]
