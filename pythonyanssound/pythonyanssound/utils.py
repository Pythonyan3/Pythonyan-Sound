from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return response

    elif isinstance(exc, TokenError):
        return Response(data={"detail": exc.args[0]}, status=status.HTTP_401_UNAUTHORIZED)
    elif isinstance(exc, InvalidToken):
        return Response(data={"detail": exc.args[0]}, status=status.HTTP_400_BAD_REQUEST)
    elif isinstance(exc, ObjectDoesNotExist):
        return Response(data={"detail": "Profile does not exist"}, status=status.HTTP_404_NOT_FOUND)
    elif isinstance(exc, ValidationError):
        return Response(data={"detail": exc.args[0]}, status=status.HTTP_400_BAD_REQUEST)
