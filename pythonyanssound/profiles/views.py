from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenViewBase

from pythonyanssound.pagination import CustomPageNumberPagination
from .models import Profile
from .serializers import ProfileSerializer, TokenRefreshSerializer, LogoutSerializer, LoginSerializer, \
    PasswordResetSerializer, ProfileCreateSerializer
from .tasks import send_verify_email_task
from .tokens import VerifyToken
from .utils import ProfileUtil


class OwnProfileView(APIView):
    """
    Works only with authenticated users
    Processes GET method to obtain user's data
    and PUT method to change user's data
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        """
        Authenticated user Profile's details
        """
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request: Request):
        """
        Update user Profile data
        """
        self.check_object_permissions(request, request.user)
        serializer = ProfileSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data)


class ProfileDetailsView(APIView):
    """
    Processes GET method to obtain user's info
    Takes user_id as user identifier
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, user_id: int):
        """
        Profile details related to user with entered primary key
        user_id -- primary key
        """
        profile = Profile.objects.get(pk=user_id, is_active=True)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


class ProfileCreateView(APIView):
    """
    Processes POST method to create new user's Profile
    Takes only required fields
    Also sends Email message, with special VerifyToken, to verify user's email address
    """
    serializer_class = ProfileCreateSerializer

    def post(self, request: Request):
        """
        Registration.
        Creates new user.
        Send email verification message.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        send_verify_email_task.delay(
            get_current_site(request).domain,
            str(VerifyToken.for_user(profile)),
            profile.email,
            profile.username
        )
        return Response(
            {'username': profile.username, 'email': profile.email},
            status=status.HTTP_201_CREATED
        )


class EmailVerificationView(APIView):
    """
    Processes GET method to verify user email address
    Uses custom VerifyToken, which was sent to email
    """
    def get(self, request: Request, token: str):
        """Email verification by token"""
        try:
            ProfileUtil.verify_profile(token)
        except TokenError:
            return Response({"details": ["Token is invalid or expired."]}, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({"details": ["Token is invalid or expired."]}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": ["Email verified successful."]}, status=status.HTTP_200_OK)


class LoginView(TokenViewBase):
    """
    Processes POST method to authenticate user
    Takes user's credentials and returns JSON web tokens (refresh and access).
    """
    serializer_class = LoginSerializer


class LogoutView(APIView):
    """
    Processes POST method to logout user by adding token to blacklist
    Takes user's refresh token
    """
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data
        token.blacklist()

        return Response({"message": ["Logout successful"]}, status=status.HTTP_200_OK)


class TokenRefreshView(TokenViewBase):
    """
    Processes POST method to refresh user's access token
    Takes user's refresh token
    """
    serializer_class = TokenRefreshSerializer


class ChangePasswordView(APIView):
    """
    Takes 3 user's credentials
    old_password -- old user's password to confirm
    new_password -- new user's password to replace old
    confirm_new_password -- repeated new user's password to confirm password correct enter
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.update(request.user, serializer.validated_data)
            return Response(data={"message": ["Password has been changed!"]}, status=status.HTTP_200_OK)


class FollowsListView(ListAPIView):
    """
    LIST OF USER'S FOLLOWS
    Processes GET method to obtain list of user's follows
    Allowed only for authenticated user's
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return self.request.user.followings.order_by("username")


class FollowView(APIView):
    """
    Processes POST method to add profile to authenticated user's follows list.
    Processes DELETE method to remove profile from authenticated user's follows list.
    Allows only for authenticated user's.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, profile_id: int):
        """
        FOLLOW ON PROFILE
        Retrieve profile by requested profile_id.
        Add profile to authenticated user's follows list
        """
        profile = Profile.objects.get(pk=profile_id)
        request.user.followings.add(profile)
        return Response(data={"message": f"Successful follow on {profile}"})

    def delete(self, request: Request, profile_id: int):
        """
        UNFOLLOW FROM PROFILE
        Retrieve profile by requested profile_id.
        Remove profile from authenticated user's follows list
        """
        profile = Profile.objects.get(pk=profile_id)
        request.user.followings.remove(profile)
        return Response(data={"message": f"Successful unfollow from {profile}"})
