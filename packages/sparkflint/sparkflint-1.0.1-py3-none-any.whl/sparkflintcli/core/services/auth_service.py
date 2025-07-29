import requests
from sparkflintcli.core.services.config_service import ConfigService
from sparkflintcli.core.utils.token_cache import (
    save_token,
    load_token,
    delete_token,
)
from sparkflintcli.core.context import session
from dataclasses import dataclass, field


@dataclass
class AuthService:
    config_service: ConfigService = field(default_factory=ConfigService)

    def login(self, url: str, username: str, password: str, force: bool = False) -> str:
        if not force:
            token = load_token()
            if token:
                return token

        origin = url or self.config_service.get_origin()
        username = username or self.config_service.get_username()
        password = password or self.config_service.get_password()

        try:
            response = session.post(
                f"{origin}/autenticacao/login",
                data={"username": username, "password": password},
                timeout=(3, 5),
            )

            response.raise_for_status()

            token = response.json().get("access_token")
            if not token:
                raise RuntimeError("Token de acesso não retornado pela API.")
            save_token(token)

            return token
        except requests.RequestException as e:
            raise RuntimeError(f"Erro ao tentar autenticar: {e}") from e

    def validate_login(self) -> bool:
        try:
            _ = self.login(force=True)
            return True
        except RuntimeError:
            return False

    def logout(self):
        delete_token()
