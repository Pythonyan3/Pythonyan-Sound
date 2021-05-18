from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from profiles.models import Profile
from profiles.serializers import EmailVerifySerializer, ProfileCreateSerializer, LogoutSerializer, \
    PasswordChangeSerializer
from profiles.tokens import VerifyToken, CustomRefreshToken
from .tasks import send_verify_email_task


def register_new_profile(request: Request):
    """
    Performs Profile registration;
    Validate request data and create new Profile object;
    Sends verification email message with Celery task.
    """
    serializer = ProfileCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    profile = Profile.objects.create_user(
        email=serializer.validated_data['email'],
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password'],
    )
    # sending verification message
    send_verify_email_task.delay(
        str(VerifyToken.for_user(profile)),
        profile.email,
        profile.username
    )
    return profile


def verify_email_address(request: Request):
    """
    Performs verification of user's email address;
    Checks request data and sets user's is_verified field to True;
    Selects user's from DB by id extracted from token.
    """
    serializer = EmailVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token = VerifyToken(serializer.validated_data["token"])

    profile = Profile.objects.get(pk=token.get('user_id'))
    profile.is_verified = True
    profile.save()


def blacklist_refresh_token(request: Request):
    """
    Perform user logout;
    Checks request data with serializer;
    Puts user's refresh token to blacklist.
    """
    serializer = LogoutSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token = CustomRefreshToken(serializer.validated_data["refresh"])
    token.blacklist()


def change_user_password(request: Request):
    """
    Checks request data and sets new user's password.
    """
    serializer = PasswordChangeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if not request.user.check_password(serializer.validated_data['old_password']):
        raise ValidationError(
            detail={"detail": ["Incorrect profile's password!"]},
            code=status.HTTP_400_BAD_REQUEST
        )

    if serializer.validated_data['new_password'] != serializer.validated_data['confirm_new_password']:
        raise ValidationError(
            detail={"detail": ["New passwords must match!"]},
            code=status.HTTP_400_BAD_REQUEST
        )

    request.user.set_password(serializer.validated_data['new_password'])
    request.user.save()
