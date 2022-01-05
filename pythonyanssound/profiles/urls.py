from django.urls import path
from .views import (
    ProfileDetailsView, OwnProfileDetailsUpdateView, ProfileCreateView,
    LogoutView, LoginView, ResendVerificationEmailView, FollowView,
    ChangePasswordView, FollowsListView, VerificationEmailView,
    TokenRefreshView
)

urlpatterns = [
    path(
        route='',
        view=OwnProfileDetailsUpdateView.as_view(),
        name="own-profile-details-update"
    ),
    path(
        route='short/',
        view=OwnProfileDetailsUpdateView.as_view(),
        name="own-profile-short-details"
    ),
    path(
        route='<int:user_id>/',
        view=ProfileDetailsView.as_view(),
        name="profile-details"
    ),
    path(
        route='registration/',
        view=ProfileCreateView.as_view(),
        name="profile-registration"
    ),
    path(
        route='registration/resend-verify-email/',
        view=ResendVerificationEmailView.as_view(),
        name="profile-resend-verify-email"
    ),
    path(
        route='registration/email-verify/',
        view=VerificationEmailView.as_view(),
        name="email-verification"
    ),
    path(
        route='password-change/',
        view=ChangePasswordView.as_view(),
        name="profile-change-password"
    ),
    path(
        route='logout/',
        view=LogoutView.as_view(),
        name="profile-logout"
    ),
    path(
        route='login/',
        view=LoginView.as_view(),
        name="profile-login"
    ),
    path(
        route='token/refresh/',
        view=TokenRefreshView.as_view(),
        name="profile-token-refresh"
    ),
    path(
        route='followings/',
        view=FollowsListView.as_view(),
        name="profile-followings"
    ),
    path(
        route='followings/<int:profile_id>/',
        view=FollowView.as_view(),
        name="profile-followings-management"
    ),
]
