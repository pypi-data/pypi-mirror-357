from http import HTTPStatus

import requests

from constance import Params
from .scheme import AuthResponse


class AuthenticationError(Exception):
    """Исключение для ошибок аутентификации."""


def auth(
        username,
        password,
        base_url,
        proto,
        verify,
        exclude_websocket: bool = False,
):
    session = requests.Session()
    login_data = {
        'user': username,
        'password': password,
    }
    if proto == 'http':
        response = session.post(
                f'{base_url}/login',
                json=login_data,
            )
    if proto == 'https':
        response = session.post(
            f'{base_url}/login',
            json=login_data,
            verify=verify,
        )
    if response.status_code != HTTPStatus.OK:
        raise AuthenticationError()
    auth_response = AuthResponse(**response.json())
    token = auth_response.data.authToken
    if exclude_websocket is False:
        Params.AUTH_TOKENS[f'token_{username}'] = token
    uid = auth_response.data.me.id
    return token, uid


class Auth:

    @staticmethod
    def session(
            username,
            password,
            base_url,
            proto,
            verify,
            exclude_websocket: bool = False,
    ):
        auth_token, uid = auth(
            username,
            password,
            base_url,
            proto,
            verify,
            exclude_websocket,
        )
        session = requests.Session()
        headers = {
            'X-Auth-Token': auth_token,
            'X-User-Id': uid,
        }
        session.headers.update(headers)
        session.username = username
        session.uid = uid
        return session
