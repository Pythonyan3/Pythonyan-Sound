from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenViewBase

from pythonyanssound.pagination import CustomPageNumberPagination
from .models import Profile
from .serializers import ProfileSerializer, TokenRefreshSerializer, LogoutSerializer, LoginSerializer, \
    ShortProfileSerializer
from .services import register_new_profile, verify_email_address, blacklist_refresh_token, change_user_password
from .tasks import send_verify_email_task
from .tokens import VerifyToken


class OwnProfileDetailsUpdateView(APIView):
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
        serializer = ProfileSerializer(instance=request.user)
        return Response(serializer.data)

    def put(self, request: Request):
        """
        Update user Profile data
        """
        self.check_object_permissions(request, request.user)
        serializer = ProfileSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class OwnProfileShortDetailsView(APIView):
    """
    Works only with authenticated users
    Processes GET method to obtain user's data (only id and username)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        """
        Authenticated user Profile's details (shortly form)
        """
        serializer = ShortProfileSerializer(instance=request.user)
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
        serializer = ProfileSerializer(instance=profile)
        return Response(serializer.data)


class ProfileCreateView(APIView):
    """
    Processes POST method to create new user's Profile
    Takes only required fields
    Also sends Email message, with special VerifyToken, to verify user's email address
    """

    def post(self, request: Request):
        """
        Registration.
        Creates new user.
        Send email verification message.
        """
        profile = register_new_profile(request)
        return Response(
            {'username': profile.username, 'email': profile.email},
            status=status.HTTP_201_CREATED
        )


class ResendVerificationEmailView(APIView):
    """
    Processes POST method to resend verification email
    Allowed only to authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        """
        Send email verification message.
        """
        # sending verification message
        send_verify_email_task.delay(
            str(VerifyToken.for_user(request.user)),
            request.user.email,
            request.user.username
        )
        return Response(data={"message": "Email has been sent."})


class VerificationEmailView(APIView):
    """
    Processes GET method to verify user email address
    Uses custom VerifyToken, which was sent to email
    """
    def post(self, request: Request):
        """Email verification by token"""
        verify_email_address(request)
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

    def delete(self, request: Request):
        blacklist_refresh_token(request)
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
        change_user_password(request)
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
        profile = request.user.followings.get(pk=profile_id)
        request.user.followings.remove(profile)
        return Response(data={"message": f"Successful unfollow from {profile}"})
