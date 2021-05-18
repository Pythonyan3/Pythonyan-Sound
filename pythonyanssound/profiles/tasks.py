from profiles.utils import EmailUtil
from pythonyanssound.celery import app


@app.task
def send_verify_email_task(token: str, email: str, username: str):
    """
    Celery task. Perform send verification message.
    """
    EmailUtil.send_verifications_message(token, email, username)

# TODO Mail information about latest releases
# TODO Daily Mixes generation
