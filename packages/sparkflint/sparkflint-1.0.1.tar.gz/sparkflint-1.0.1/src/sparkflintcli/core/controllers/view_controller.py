import typer
from sparkflintcli.core.context import console
from sparkflintcli.core.models.view_model import View
from sparkflintcli.core.services import view_service
from sparkflintcli.core.ui.view_ui import display_views, open_url_in_browser
from sparkflintcli.core.ui.messages import success, error


def add_view(name: str, url: str):
    view = View(name=name, url=url)
    if not view.is_valid():
        error("A URL deve começar com http ou https.")
        raise typer.Exit(code=1)

    try:
        view_service.save_view(view)
        success(f"View '{name}' adicionada com sucesso!")
    except Exception as e:
        error(f"Erro ao adicionar view {name}.")
        error(str(e))
        raise typer.Exit(code=2)


def list_views():
    try:
        with console.status(
            "[bold green]Buscando views...[/bold green]", spinner="dots"
        ):
            views = view_service.load_views()
            if not views:
                error("Nenhuma view encontrada.")
                return
            display_views(views)
    except Exception as e:
        error("Erro ao buscar views.")
        error(str(e))
        raise typer.Exit(code=2)


def open_view(name: str):
    try:
        with console.status(
            f"[bold green]Abrindo view '{name}'...[/bold green]", spinner="dots"
        ):
            url = view_service.get_view_by_name(name)
            if not url:
                error(f"Nenhuma view encontrada com o nome '{name}'")
                return
            open_url_in_browser(url)
    except Exception as e:
        error(f"Erro ao abrir view '{name}'.")
        error(str(e))
        raise typer.Exit(code=2)


def autocomplete_views() -> list[str]:
    """
    Fornece autocomplete de views para CLI.
    """
    try:
        return view_service.autocomplete_views()
    except Exception:
        return []
