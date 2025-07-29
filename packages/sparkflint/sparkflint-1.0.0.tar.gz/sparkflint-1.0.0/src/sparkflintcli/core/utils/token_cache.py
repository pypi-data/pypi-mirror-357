import json
from pathlib import Path
from sparkflintcli.config.constants import SPARKFLINT_CACHE_FILE


def save_token(token: str, file_path: Path = SPARKFLINT_CACHE_FILE):
    """
    Salva token de acesso no cache.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"access_token": token}, f)


def load_token(file_path: Path = SPARKFLINT_CACHE_FILE) -> str | None:
    """
    Recupera token de acesso do cache.
    """
    if not file_path.exists():
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f).get("access_token")
        except json.JSONDecodeError:
            return None


def delete_token(file_path: Path = SPARKFLINT_CACHE_FILE):
    """
    Exclui o token de acesso do cache.
    """
    if file_path.exists():
        file_path.unlink()
