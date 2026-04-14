from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header


ACCESS_TOKEN_MINUTES = 60
REFRESH_TOKEN_DAYS = 7


def _build_token(user, token_type, ttl):
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user.id),
        'username': user.username,
        'type': token_type,
        'iat': int(now.timestamp()),
        'exp': int((now + ttl).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def build_token_pair(user):
    access = _build_token(user, 'access', timedelta(minutes=ACCESS_TOKEN_MINUTES))
    refresh = _build_token(user, 'refresh', timedelta(days=REFRESH_TOKEN_DAYS))
    return {'access': access, 'refresh': refresh}


def decode_token(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError as exc:
        raise exceptions.AuthenticationFailed('Token has expired.') from exc
    except jwt.InvalidTokenError as exc:
        raise exceptions.AuthenticationFailed('Invalid token.') from exc


class WaterMiJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'bearer':
            return None
        if len(auth) != 2:
            raise exceptions.AuthenticationFailed('Invalid authorization header.')

        token = auth[1].decode('utf-8')
        payload = decode_token(token)
        if payload.get('type') != 'access':
            raise exceptions.AuthenticationFailed('Access token required.')

        User = get_user_model()
        try:
            user = User.objects.get(pk=payload['sub'])
        except User.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed('User not found.') from exc
        return (user, token)