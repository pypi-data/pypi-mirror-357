from sparkflintcli.core.context import console
from sparkflintcli.core.services.app_service import get_yarn_apps, get_app_url
from sparkflintcli.core.ui.app_ui import display_apps, open_url_in_browser
from sparkflintcli.core.ui.messages import error
import typer


def list_apps():
    try:
        with console.status(
            "[bold green]Buscando aplicações...[/bold green]", spinner="dots"
        ):
            apps_data = get_yarn_apps()
            if apps_data is None:
                error("Nenhum dado retornado do YARN.")
                return
            display_apps(apps_data)
    except Exception as e:
        error("Erro ao buscar aplicações do YARN.")
        error(str(e))
        raise typer.Exit(code=2)


def open_app(app_id: str):
    """
    Abre detalhes da aplicação no navegador.
    """
    try:
        with console.status(
            f"[bold green]Abrindo detalhes da aplicação {app_id} no navegador...[/bold green]",
            spinner="dots",
        ):
            url = get_app_url(app_id)
            if url is None:
                error("Nenhuma view encontrada com o nome 'yarn'")
                return
            open_url_in_browser(url)
    except Exception as e:
        error(f"Erro ao abrir detalhes da aplicação {app_id} no navegador")
        error(str(e))
        raise typer.Exit(code=2)


def status_app():
    print()
