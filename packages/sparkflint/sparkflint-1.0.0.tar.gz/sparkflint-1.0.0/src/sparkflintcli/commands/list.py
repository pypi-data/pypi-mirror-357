from sparkflintcli.core.controllers.app_controller import list_apps
from sparkflintcli.core.controllers.host_controller import list_hosts
from sparkflintcli.core.controllers.pipeline_controller import list_pipelines
import typer

app = typer.Typer()

# from ..core.pipelines import get_pipelines, show_pipelines
# from ..core.auth import login_user
# from ..core.apps import get_apps, show_apps
# from ..core.hosts import show_hosts
# from ..core.views import load_views
# from rich.console import Console
# from rich.table import Table

# console = Console()


@app.command()
@app.command(name="a", hidden=True)
def apps():
    """
    Lista as aplicações em execução (ou finalizadas) no YARN.
    """
    list_apps()


@app.command()
@app.command(name="h", hidden=True)
def hosts():
    """
    Lista os hosts do arquivo Ansible hosts.ini.
    """
    list_hosts()


@app.command()
@app.command(name="p", hidden=True)
def pipelines():
    """
    Lista pipelines cadastrados na origem.
    """
    list_pipelines()


# @app.command()
# @app.command(name="d", hidden=True)
# def dags():
#     """
#     Lista dags do Airflow.
#     """
#     import requests
#     from requests.auth import HTTPBasicAuth

#     url = "http://fn02-seplad.fazenda.net:8080/api/v1/dags"
#     response = requests.get(url, auth=HTTPBasicAuth("wiliam.ribeiro", "Cluster@25"))

#     for dag in response.json().get("dags", []):
#         print(dag["dag_id"])


# @app.command()
# @app.command(name="h", hidden=True)
# def hosts():
#     """
#     Lista todos os hosts do arquivo Ansible hosts.ini.
#     """
#     with console.status("[bold green]Buscando hosts...[/bold green]", spinner="dots"):
#         show_hosts()


# @app.command()
# @app.command(name="p", hidden=True)
# def pipelines():
#     """
#     Lista pipelines cadastrados na origem.
#     """
#     try:
#         access_token = login_user()
#         with console.status(
#             "[bold green]Buscando pipelines...[/bold green]", spinner="dots"
#         ):
#             pipelines = get_pipelines(access_token)
#         show_pipelines(pipelines)
#     except requests.exceptions.RequestException as e:
#         typer.secho("Erro ao conectar à origem:", fg=typer.colors.RED)
#         typer.echo(str(e))
#         raise typer.Exit(code=2)


# @app.command()
# @app.command(name="v", hidden=True)
# def views():
#     """
#     Lista todos os atalhos de view.
#     """
#     views = load_views()
#     if not views:
#         console.print("[yellow]⚠️ Nenhum atalho encontrado.")
#         raise typer.Exit()

#     table = Table(title="Atalhos de Views")
#     table.add_column("Nome", style="cyan")
#     table.add_column("URL", style="green")

#     for name, url in views.items():
#         table.add_row(name, url)

#     console.print(table)
