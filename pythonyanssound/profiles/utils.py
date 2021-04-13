from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.urls import reverse

from .models import VerifyToken, Profile
from .serializers import ProfileCreateSerializer


class EmailUtil:
    @staticmethod
    def send_verifications_message(domain, token, email, username):
        email = EmailMessage(
            subject="Email Verification",
            body=f"Hi {username}. Use link below to verify your email address.\n"
                 f"http://{domain}{reverse('email-verification', kwargs={'token': token})}",
            to=[email]
        )
        email.send()


class ProfileUtil:
    @staticmethod
    def registration(request):
        serializer = ProfileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        token = VerifyToken.for_user(profile)
        EmailUtil.send_verifications_message(
            get_current_site(request).domain,
            token,
            profile.email,
            profile.username
        )
        return profile

    @staticmethod
    def verify_profile(token):
        token = VerifyToken(token)
        payload = token.payload
        profile = Profile.objects.get(pk=payload.get('user_id'))
        profile.is_verified = True
        profile.save()
