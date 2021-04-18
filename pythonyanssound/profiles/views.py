from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenViewBase

from .models import Profile
from .serializers import ProfileSerializer, TokenRefreshSerializer, LogoutSerializer
from .tokens import CustomRefreshToken
from .utils import ProfileUtil


class OwnProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Authenticated user Profile details
        """
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """
        Update user Profile data
        """
        self.check_object_permissions(request, request.user)
        serializer = ProfileSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data)


class ProfileDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        Profile details related to user with entered primary key
        user_id -- primary key
        """
        profile = Profile.objects.get(pk=user_id, is_active=True)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


class ProfileCreateView(APIView):
    def post(self, request):
        """
        Registration.
        Creates new user.
        Send email verification message.
        """
        profile = ProfileUtil.registration(request)
        return Response(
            {'username': profile.username, 'email': profile.email},
            status=status.HTTP_201_CREATED
        )


class EmailVerificationView(APIView):
    def get(self, request, token):
        """Email verification by token"""
        try:
            ProfileUtil.verify_profile(token)
        except TokenError:
            return Response({"error": "Token is invalid or expired."})
        except Profile.DoesNotExist:
            return Response({"error": "Token is invalid or expired."})
        return Response({"message": "Email verified successful."})


class TokenRefreshView(TokenViewBase):
    """
    Token Refresh View with custom serializer
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TokenRefreshSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data
        token.blacklist()

        return Response({"message": ["Logout successful"]})
