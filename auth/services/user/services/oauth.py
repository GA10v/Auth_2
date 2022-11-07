import services.user.layer_models as layer_models
from core.config import settings
from flask import redirect, url_for
from rauth import OAuth2Service


class OAuthBase:
    providers = None

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        credentials = settings.oauth.credentials.get(provider_name)
        self.consumer_name = credentials.get('name')
        self.consumer_id = credentials.get('id')
        self.consumer_secret = credentials.get('secret')
        self.authorize_url = credentials.get('authorize_url')
        self.access_token_url = credentials.get('access_token_url')
        self.base_url = credentials.get('base_url')

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


class YandexRegister(OAuthRegister):
    def __init__(self) -> None:
        super(YandexRegister, self).__init__('yandex')
        self.service = OAuth2Service(
            name=self.consumer_name,
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=self.authorize_url,
            access_token_url=self.access_token_url,
            base_url=self.base_url,
        )

    def authorize(self):
        return redirect(
            self.service.get_authorize_url(
                scope='login:email login:info',
                response_type='code',
                redirect_uri=self.get_callback_url(),
            ),
        )

    def callback(self):
        ...
