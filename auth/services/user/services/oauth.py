import json
import secrets
from string import ascii_letters, digits
from typing import TypedDict

import services.user.layer_models as layer_models
import services.user.payload_models as payload_models
import services.user.repositories as repo
import utils.exceptions as exc
from core.config import settings
from core.logger import get_logger
from flask import redirect, request, url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_security.utils import hash_password
from rauth import OAuth2Service

logger = get_logger(__name__)
db_repo = repo.get_user_db_repo()
tms_repo = repo.get_user_tms_repo()


class CredentialsConf(TypedDict):
    name: str
    client_id: str
    client_secret: str
    authorize_url: str
    access_token_url: str
    base_url: str


class OAuthBase:
    providers = None

    def __init__(
        self,
        provider_name: str,
        db_repository: repo.UserRepositoryProtocol = db_repo,
        tm_storage_repository: repo.UserTmStorageRepositoryProtocol = tms_repo,
    ):
        self.provider_name = provider_name
        _credentials: CredentialsConf = settings.oauth.credentials.get(provider_name)
        self.credentials: CredentialsConf = _credentials
        self.consumer_id = _credentials.get('client_id')
        self.consumer_secret = _credentials.get('client_secret')
        self.db_repo = db_repository
        self.tms_repo = tm_storage_repository

    @classmethod
    def get_provider(cls, provider_name: str):
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers[provider_name]

    def authorize(self):
        """
        Перенаправить на сайт провайдера.

        :return: Response
        """
        ...

    def callback(self) -> layer_models.OAuth:
        """
        Получить данные пользователя от провайдера.

        :raises NoAccessError: если провайдер не предоставил code
        """
        ...


class OAuthRegister(OAuthBase):
    def get_callback_url(self):
        return url_for('oauth.oauth_register_callback', provider=self.provider_name, _external=True)

    @staticmethod
    def _generate_password():
        symbols = ascii_letters + digits + '@$!%*#?&'
        return ''.join(secrets.choice(symbols) for _ in range(16))

    def register(self, user: payload_models.OAuthPayload) -> None:
        """
        Создание пользователя через OAuth.

        :param user: данные нового пользователя
        :raises EmailAlreadyExist: если email уже сущетсвует
        :raises UniqueConstraintError: если social_id и username существует
        """
        password = self._generate_password()
        _new_user = payload_models.UserCreatePayload(
            username=user.username,
            email=user.email,
            password=hash_password(password),
        )
        try:
            new_user = self.db_repo.create(_new_user)
        except exc.UniqueConstraintError as ex:
            logger.info('Ошибка при регистрации пользователя через OAuth: \n %s', str(ex))
            raise exc.EmailAlreadyExist from ex
        _social_account = payload_models.SocialAccountPayload(
            user_id=new_user.id,
            social_id=user.social_id,
            social_name=self.provider_name,
        )
        try:
            self.db_repo.create_social_account(_social_account)
        except exc.UniqueConstraintError as ex:
            logger.info('Ошибка при создании social_account через OAuth: \n %s', str(ex))
            raise


class OAuthLogin(OAuthBase):
    def get_callback_url(self):
        return url_for('oauth.oauth_login_callback', provider=self.provider_name, _external=True)

    def login(self, user: payload_models.OAuthPayload):
        """

        Возвращает access и refresh токены и user_id пользователя через OAuth.

        :param user: данные пользователя для входа
        :return: кортеж из access, refresh токенов.
        :raises NotFoundError: если пользователя не существует
        """
        try:
            _social_account = self.db_repo.get_social_account(social_id=user.social_id, social_name=self.provider_name)
        except exc.NotFoundError as ex:
            logger.info('Ошибка при попытке получить social_account через OAuth: \n %s', str(ex))
            raise
        try:
            _user = self.db_repo.get_by_id(_social_account.user_id)
        except exc.NotFoundError as ex:
            logger.info('Ошибка при попытке получить пользователя через OAuth: \n %s', str(ex))
            raise
        _device = payload_models.UserDevicePayload(
            user_id=_user.id,
            user_agent=user.user_agent,
        )
        try:
            user_device = self.db_repo.get_allowed_device(_device)
        except exc.NotFoundError:
            user_device = self.db_repo.add_allowed_device(_device)
        self.db_repo.add_new_session(
            session=payload_models.SessionPayload(
                user_id=_user.id,
                device_id=user_device.id,
            ),
        )
        _permissions = self.db_repo.get_user_permissions(_user.id)
        additional_claims = {
            'permissions': [permission.code for permission in _permissions],
            'is_super': _user.is_super,
        }
        access_token = create_access_token(
            identity=_user.id,
            additional_claims=additional_claims,
            expires_delta=settings.jwt.ACCESS_TOKEN_EXP,
        )
        refresh_token = create_refresh_token(
            identity=_user.id,
            expires_delta=settings.jwt.REFRESH_TOKEN_EXP,
        )
        user_id = str(_user.id)
        self.tms_repo.set(
            user.user_agent + str(_user.id),
            refresh_token,
            ex=settings.jwt.REFRESH_TOKEN_EXP,
        )
        return access_token, refresh_token, user_id


class YandexRegister(OAuthRegister):
    def __init__(self) -> None:
        super(YandexRegister, self).__init__('yandex')
        self.service = OAuth2Service(**self.credentials)

    def authorize(self):
        return redirect(
            self.service.get_authorize_url(
                scope='login:email login:info',
                response_type='code',
                redirect_uri=self.get_callback_url(),
            ),
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        code = request.args.get('code', default=None)
        if code is None:
            raise exc.NoAccessError
        oauth_session = self.service.get_auth_session(
            method='POST',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': self.consumer_id,
                'client_secret': self.consumer_secret,
            },
            decoder=decode_json,
        )
        user = oauth_session.get('', params={'format': 'json'}).json()
        return layer_models.OAuth(
            username=user['login'],
            email=user['default_email'],
            social_id=user['id'],
        )


class YandexLogin(OAuthLogin):
    def __init__(self) -> None:
        super(YandexLogin, self).__init__('yandex')
        self.service = OAuth2Service(**self.credentials)

    def authorize(self):
        return redirect(
            self.service.get_authorize_url(
                scope='login:email login:info',
                response_type='code',
                redirect_uri=self.get_callback_url(),
            ),
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        code = request.args.get('code', default=None)
        if code is None:
            raise exc.NoAccessError
        oauth_session = self.service.get_auth_session(
            method='POST',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': self.consumer_id,
                'client_secret': self.consumer_secret,
            },
            decoder=decode_json,
        )
        user = oauth_session.get('', params={'format': 'json'}).json()
        return layer_models.OAuth(
            username=user['login'],
            email=user['default_email'],
            social_id=user['id'],
        )


class GoogleRegister(OAuthRegister):
    def __init__(self) -> None:
        super(GoogleRegister, self).__init__('google')
        self.service = OAuth2Service(**self.credentials)

    def authorize(self):
        return redirect(
            self.service.get_authorize_url(
                scope='email profile',
                response_type='code',
                redirect_uri=self.get_callback_url(),
            ),
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        code = request.args.get('code', default=None)
        if code is None:
            raise exc.NoAccessError
        oauth_session = self.service.get_auth_session(
            method='POST',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': self.consumer_id,
                'client_secret': self.consumer_secret,
                'redirect_uri': self.get_callback_url(),
            },
            decoder=decode_json,
        )
        user = oauth_session.get('', params={'format': 'json'}).json()
        return layer_models.OAuth(
            username=user['name'],
            email=user['email'],
            social_id=user['id'],
        )


class GoogleLogin(OAuthLogin):
    def __init__(self) -> None:
        super(GoogleLogin, self).__init__('google')
        self.service = OAuth2Service(**self.credentials)

    def authorize(self):
        return redirect(
            self.service.get_authorize_url(
                scope='email profile',
                response_type='code',
                redirect_uri=self.get_callback_url(),
            ),
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        code = request.args.get('code', default=None)
        if code is None:
            raise exc.NoAccessError
        oauth_session = self.service.get_auth_session(
            method='POST',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': self.consumer_id,
                'client_secret': self.consumer_secret,
                'redirect_uri': self.get_callback_url(),
            },
            decoder=decode_json,
        )
        user = oauth_session.get('', params={'format': 'json'}).json()
        return layer_models.OAuth(
            username=user['name'],
            email=user['email'],
            social_id=user['id'],
        )
