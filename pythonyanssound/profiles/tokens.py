import time

from django_redis import get_redis_connection
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token, BlacklistMixin, AccessToken
from rest_framework_simplejwt.utils import datetime_to_epoch


class CustomBlacklistMixin(BlacklistMixin):
    """Custom Token BlacklistMixin based on Redis."""
    def verify(self, *args, **kwargs):
        """Implementation of token verification."""
        self.check_blacklist()
        super().verify(*args, **kwargs)

    def check_blacklist(self):
        """
        Implementation of blacklist checking about token.

        Checks if this token is present in the token blacklist
        Raises TokenError if so
        """
        jti = self.payload[api_settings.JTI_CLAIM]

        redis = get_redis_connection("default")
        if redis.get(jti):
            raise TokenError('Token is blacklisted')

    def blacklist(self):
        """
        Implementation of adding token to blacklist

        Uses Redis to storing blacklisted tokens
        Redis key - token jti
        Redis value - token
        Sets expiration equals to rest of token lifetime
        """
        jti = self.payload[api_settings.JTI_CLAIM]
        exp = int(self.payload['exp']) - datetime_to_epoch(self.current_time)

        redis = get_redis_connection("default")
        redis.set(jti, str(self), ex=exp)
        return self

    @classmethod
    def for_user(cls, user):
        """Creating token for user."""
        return super().for_user(user)


class CustomRefreshToken(CustomBlacklistMixin, Token):
    """Custom refresh token with custom Blacklist mixin."""
    token_type = 'refresh'
    lifetime = api_settings.REFRESH_TOKEN_LIFETIME
    no_copy_claims = (
        api_settings.TOKEN_TYPE_CLAIM,
        'exp',
        api_settings.JTI_CLAIM,
        'jti',
    )

    @property
    def access_token(self):
        """
        Implementation of creating access token.

        Creates new access token and copy allowed claims from refresh token
        """
        access = AccessToken()

        access.set_exp(from_time=self.current_time)

        no_copy = self.no_copy_claims
        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        return access


class VerifyToken(Token):
    """JWT token with custom token type for email address verification."""
    token_type = 'verify'
    lifetime = api_settings.ACCESS_TOKEN_LIFETIME
