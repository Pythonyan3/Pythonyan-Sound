from django.urls import path
from .views import ProfileDetailsView, OwnProfileDetailsUpdateView, ProfileCreateView, VerificationEmailView, \
    TokenRefreshView, \
    LogoutView, LoginView, ChangePasswordView, FollowsListView, FollowView, ResendVerificationEmailView

urlpatterns = [
    path('', OwnProfileDetailsUpdateView.as_view(), name="own-profile-details-update"),
    path('short/', OwnProfileDetailsUpdateView.as_view(), name="own-profile-short-details"),
    path('<int:user_id>/', ProfileDetailsView.as_view(), name="profile-details"),
    path('registration/', ProfileCreateView.as_view(), name="profile-registration"),
    path('registration/resend-verify-email/', ResendVerificationEmailView.as_view(), name="profile-resend-verify-email"),
    path('registration/email-verify/', VerificationEmailView.as_view(), name="email-verification"),
    path('password-change/', ChangePasswordView.as_view(), name="profile-change-password"),
    path('logout/', LogoutView.as_view(), name="profile-logout"),
    path('login/', LoginView.as_view(), name="profile-login"),
    path('token/refresh/', TokenRefreshView.as_view(), name="profile-token-refresh"),
    path('followings/', FollowsListView.as_view(), name="profile-followings"),
    path('followings/<int:profile_id>/', FollowView.as_view(), name="profile-followings-management"),
]
