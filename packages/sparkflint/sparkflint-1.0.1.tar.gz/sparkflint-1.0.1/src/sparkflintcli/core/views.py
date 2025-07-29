import toml
from ..constants import SPARKFLINT_VIEWS_FILE


def load_views() -> dict:
    if not SPARKFLINT_VIEWS_FILE.exists():
        return {}
    with open(SPARKFLINT_VIEWS_FILE, "r") as f:
        return toml.load(f)


def save_view(name: str, url: str) -> None:
    views = load_views()
    views[name] = url
    SPARKFLINT_VIEWS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SPARKFLINT_VIEWS_FILE, "w") as f:
        toml.dump(views, f)


def get_view(name: str) -> str | None:
    views = load_views()
    return views.get(name)


def remove_view(name: str) -> bool:
    views = load_views()
    if name not in views:
        return False
    del views[name]
    with open(SPARKFLINT_VIEWS_FILE, "w") as f:
        toml.dump(views, f)
    return True


def autocomplete_views():
    return list(load_views().keys())
