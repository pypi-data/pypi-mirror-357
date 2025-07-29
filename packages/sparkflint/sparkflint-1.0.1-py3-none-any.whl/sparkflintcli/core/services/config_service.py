import toml, requests
from dataclasses import asdict, dataclass
from pathlib import Path

from sparkflintcli.config.constants import SPARKFLINT_CONFIG_FILE
from sparkflintcli.core.models.config_model import Config
from sparkflintcli.core.utils.cryptography import encrypt_password, decrypt_password
from sparkflintcli.core.context import session


@dataclass
class ConfigService:
    file_path: Path = SPARKFLINT_CONFIG_FILE

    def load(self) -> Config:
        if not self.file_path.exists():
            return Config()
        data = toml.load(self.file_path).get("origin", {})
        return Config(
            url=data.get("url"),
            username=data.get("username"),
            password=data.get("password"),
        )

    def save(self, config: Config):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        data = asdict(config)
        content = {
            "origin": {
                "url": data["url"],
                "username": data["username"],
                "password": data["password"],
            }
        }
        with self.file_path.open("w", encoding="utf-8") as f:
            toml.dump(content, f)

    def set_field(self, field: str, value: str, encrypt: bool = False):
        config = self.load()
        if encrypt and field == "password":
            value = encrypt_password(value)
        setattr(config, field, value)
        self.save(config)

    def get_field(self, field: str, decrypt: bool = False) -> str:
        config = self.load()
        value = getattr(config, field)
        if not value:
            raise ValueError(f"{field.capitalize()} não configurado.")
        if decrypt and field == "password":
            try:
                return decrypt_password(value)
            except Exception as e:
                raise ValueError(f"Erro ao descriptografar senha: {e}")
        return value

    def validate_origin(self, url: str | None = None) -> bool:
        url = url or self.get_field("url")
        try:
            response = session.get(f"{url}/pipelines", timeout=(3, 5))
            return response.status_code in [200, 401]
        except requests.RequestException:
            return False

    # Métodos públicos diretos (úteis para uso externo direto)
    def get_origin(self) -> str:
        return self.get_field("url")

    def set_origin(self, url: str):
        self.set_field("url", url)

    def get_username(self) -> str:
        return self.get_field("username")

    def set_username(self, username: str):
        self.set_field("username", username)

    def get_password(self) -> str:
        return self.get_field("password", decrypt=True)

    def set_password(self, password: str):
        self.set_field("password", password, encrypt=True)
