from django.conf import settings
from django.core.mail import EmailMessage


class EmailUtil:
    @staticmethod
    def send_verifications_message(token: str, email: str, username: str):
        """
        Sends email message to user to verify email address.
        Message contains URL with token to perform email address verify
        """
        email = EmailMessage(
            subject="Email Verification",
            body=f"Hi {username}. Use link below to verify your email address.\n"
                 f"{settings.FRONTEND_BASE_URL}/profile/email-verification/{token}/",
            to=[email]
        )
        email.send()


def profile_photo_upload_folder(profile_instance, filename: str):
    return f"profiles/{profile_instance.pk}/photos/{filename}"
