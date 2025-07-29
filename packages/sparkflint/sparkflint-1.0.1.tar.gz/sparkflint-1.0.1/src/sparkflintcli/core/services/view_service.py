import toml
from pathlib import Path
from typing import Optional
from sparkflintcli.config.constants import SPARKFLINT_VIEWS_FILE
from sparkflintcli.core.models.view_model import View


def load_views() -> dict[str, str]:
    """
    Carrega todas as views salvas no arquivo TOML.

    Retorna:
    - Dicionário com nome da view como chave e URL como valor.
    """
    if not SPARKFLINT_VIEWS_FILE.exists():
        return {}
    with open(SPARKFLINT_VIEWS_FILE, "r", encoding="utf-8") as f:
        return toml.load(f)


def save_view(view: View) -> None:
    """
    Salva ou atualiza uma view no arquivo de configurações.

    Parâmetros:
    - name: nome da view (ex: yarn)
    - url: URL associada à view
    """
    views = load_views()
    views[view.name] = view.url
    Path(SPARKFLINT_VIEWS_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(SPARKFLINT_VIEWS_FILE, "w", encoding="utf-8") as f:
        toml.dump(views, f)


def get_view_by_name(name: str) -> Optional[str]:
    """
    Retorna a URL da view pelo nome, se existir.

    Parâmetros:
    - name: nome da view (ex: yarn)

    Retorna:
    - URL da view ou None
    """
    views = load_views()
    return views.get(name)


def remove_view(name: str) -> bool:
    """
    Remove uma view existente pelo nome.

    Parâmetros:
    - name: nome da view

    Retorna:
    - True se a view foi removida, False se não existia
    """
    views = load_views()
    if name not in views:
        return False
    del views[name]
    with open(SPARKFLINT_VIEWS_FILE, "w", encoding="utf-8") as f:
        toml.dump(views, f)
    return True


def autocomplete_views() -> list[str]:
    """
    Retorna todos os nomes de views salvos, útil para autocompletar no Typer.

    Retorna:
    - Lista de strings com os nomes das views
    """
    return list(load_views().keys())
