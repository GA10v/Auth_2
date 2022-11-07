import services.user.layer_models as layer_models
from core.config import settings


class OAuthBase:
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        credentials = settings.oauth.credentials.get(provider_name)
        self.consumer_name = credentials.get('name')
        self.consumer_id = credentials.get('id')
        self.consumer_secret = credentials.get('secret')
        self.authorize_url = credentials.get('authorize_url')
        self.access_token_url = credentials.get('access_token_url')
        self.base_url = credentials.get('base_url')

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
