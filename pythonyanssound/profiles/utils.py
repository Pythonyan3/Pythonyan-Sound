from django.core.mail import EmailMessage
from django.urls import reverse


class EmailUtil:
    @staticmethod
    def send_verifications_message(domain: str, token: str, email: str, username: str):
        """
        Sends email message to user to verify email address.
        Message contains URL with token to perform email address verify
        """
        email = EmailMessage(
            subject="Email Verification",
            body=f"Hi {username}. Use link below to verify your email address.\n"
                 f"http://{domain}{reverse('email-verification', kwargs={'token': token})}",
            to=[email]
        )
        email.send()
