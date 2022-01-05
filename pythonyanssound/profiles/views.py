from django.db.models import Exists, OuterRef
from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenViewBase

from pythonyanssound.pagination import CustomPageNumberPagination
from .models import Profile
from .serializers import (
    ProfileSerializer, TokenRefreshSerializer, LogoutSerializer,
    LoginSerializer, ShortProfileSerializer, ProfileDetailsSerializer
)
from .services import (
    register_new_profile, verify_email_address, blacklist_refresh_token,
    change_user_password
)
from .tasks import send_verify_email_task
from .tokens import VerifyToken


class OwnProfileDetailsUpdateView(APIView):
    """
    Processes GET/PUT methods to retrieve/update authenticated user
    Profile data.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request: Request):
        """Returns authenticated user Profile details."""
        serializer = ProfileSerializer(instance=request.user)
        return Response(serializer.data)

    def put(self, request: Request):
        """Update authenticated user Profile data."""
        self.check_object_permissions(request, request.user)
        serializer = ProfileSerializer(
            instance=request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class OwnProfileShortDetailsView(APIView):
    """Processes GET method to retrieve authenticated user Profile info."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        """Returns authenticated user Profile data."""
        serializer = ShortProfileSerializer(instance=request.user)
        return Response(serializer.data)


class ProfileDetailsView(GenericAPIView):
    """
    Processes GET method to retrieve user's Profile info
    using passed user_id parameter as Profile identifier.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileDetailsSerializer

    def get(self, request: Request, user_id: int):
        """Returns data of Profile, which identified with 'user_id'."""
        profile = Profile.objects.annotate(
            is_followed=Exists(
                request.user.followings.filter(pk=OuterRef("pk"))
            )
        ).get(pk=user_id, is_active=True)
        serializer = self.get_serializer(instance=profile)
        return Response(serializer.data)


class ProfileCreateView(APIView):
    """Processes POST method to create (registration) new user's Profile."""

    def post(self, request: Request):
        """Performs creating new Profile and sending verification email."""
        profile = register_new_profile(request)
        return Response(
            {'username': profile.username, 'email': profile.email},
            status=status.HTTP_201_CREATED
        )


class ResendVerificationEmailView(APIView):
    """Processes POST method to resend verification email."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        """Sends email verification message."""
        # sending verification message
        send_verify_email_task.delay(
            str(VerifyToken.for_user(request.user)),
            request.user.email,
            request.user.username
        )
        return Response(data={"message": "Email has been sent."})


class VerificationEmailView(APIView):
    """Processes POST method to verify user email address."""

    def post(self, request: Request):
        """Verify email address (with passed custom JWT token)."""
        verify_email_address(request)
        return Response(
            {"message": ["Email verified successful."]},
            status=status.HTTP_200_OK
        )


class LoginView(TokenViewBase):
    """
    Processes POST method to authenticate user.

    Returns JSON web tokens (refresh and access)
    """
    serializer_class = LoginSerializer


class LogoutView(APIView):
    """Processes POST method to logout user."""
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request):
        """Logout user by appending user's refresh token to blacklist."""
        # TODO blacklist access token
        blacklist_refresh_token(request)
        return Response(
            {"message": ["Logout successful"]}, status=status.HTTP_200_OK
        )


class TokenRefreshView(TokenViewBase):
    """Processes POST method to refresh user's access token"""
    serializer_class = TokenRefreshSerializer


class ChangePasswordView(APIView):
    """Processes POST method to perform changing user's password."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        """Changes user's password."""
        change_user_password(request)
        return Response(
            data={"message": ["Password has been changed!"]},
            status=status.HTTP_200_OK
        )


class FollowsListView(ListAPIView):
    """Processes GET method to retrieve list of user's follows."""
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """Returns queryset of all user's followings."""
        return self.request.user.followings.order_by("username")


class FollowView(APIView):
    """
    Processes POST/DELETE methods to append/remove Profile (identified by id)
    to/from authenticated user's follows list (M2M relation).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, profile_id: int):
        """
        Appends Profile (with pk equals to 'profile_id')
        to authenticated user's follow list.
        """
        profile = Profile.objects.get(pk=profile_id)
        request.user.followings.add(profile)
        return Response(data={"message": f"Successful follow on {profile}"})

    def delete(self, request: Request, profile_id: int):
        """
        Removes Profile (with pk equals to 'profile_id')
        from authenticated user's follow list.
        """
        profile = request.user.followings.get(pk=profile_id)
        request.user.followings.remove(profile)
        return Response(data={"message": f"Successful unfollow from {profile}"})
