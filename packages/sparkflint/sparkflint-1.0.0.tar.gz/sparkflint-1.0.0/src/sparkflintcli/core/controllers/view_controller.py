from sparkflintcli.core.services.view_service import save_view, get_view
from sparkflintcli.core.ui.app_ui import display_apps, open_url_in_browser
from sparkflintcli.core.ui.messages import error, success
import typer


def add_views(name: str, url: str):
    try:
        if not url.startswith("http"):
            error("A URL deve começar com http ou https.")
            return

        save_view(name, url)
        success(f"View '{name}' adicionada com sucesso!")
    except Exception as e:
        error(f"Erro ao adicionar view {name}.")
        error(str(e))
        raise typer.Exit(code=2)


# def list_views():
#     try:
#         with console.status(
#             "[bold green]Buscando aplicações...[/bold green]", spinner="dots"
#         ):
#             apps_data = get_yarn_apps()
#             if apps_data is None:
#                 error("Nenhum dado retornado do YARN.")
#                 return
#             display_apps(apps_data)
#     except Exception as e:
#         error("Erro ao buscar aplicações do YARN.")
#         error(str(e))
#         raise typer.Exit(code=2)


# def open_view(app_id: str):
#     """
#     Abre detalhes da aplicação no navegador.
#     """
#     try:
#         with console.status(
#             f"[bold green]Abrindo detalhes da aplicação {app_id} no navegador...[/bold green]",
#             spinner="dots",
#         ):
#             url = get_view(app_id)
#             if url is None:
#                 error("Nenhuma view encontrada com o nome 'yarn'")
#                 return
#             open_url_in_browser(url)
#     except Exception as e:
#         error(f"Erro ao abrir detalhes da aplicação {app_id} no navegador")
#         error(str(e))
#         raise typer.Exit(code=2)
