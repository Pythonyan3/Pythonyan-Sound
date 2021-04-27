from profiles.utils import EmailUtil
from pythonyanssound.celery import app


@app.task
def send_verify_email_task(domain: str, token: str, email: str, username: str):
    """
    Celery task. Perform send verification message.
    """
    EmailUtil.send_verifications_message(domain, token, email, username)
