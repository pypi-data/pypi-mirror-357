import typer
from ..core.controllers.host_controller import remove_hosts, autocomplete_host_names

app = typer.Typer()


@app.command("host")
@app.command("h", hidden=True)
def host(
    hosts: str = typer.Argument(
        ...,
        help="Lista de hosts a remover, separados por vírgula",
        autocompletion=autocomplete_host_names,
    ),
    groups: str = typer.Option(
        None,
        "--groups",
        "-g",
        help="Grupos Ansible onde os hosts devem ser removidos (separados por vírgula). Se omitido, remove de todos.",
    ),
):
    """
    Remove um ou mais hosts do arquivo Ansible hosts.ini.
    """
    remove_hosts(hosts, groups)


# @app.command("view")
# @app.command("v", hidden=True)
# def host(
#     views: str = typer.Argument(
#         ...,
#         help="Lista de hosts a remover, separados por vírgula",
#         autocompletion=autocomplete_host_names,
#     ),
#     groups: str = typer.Option(
#         None,
#         "--groups",
#         "-g",
#         help="Grupos Ansible onde os hosts devem ser removidos (separados por vírgula). Se omitido, remove de todos.",
#     ),
# ):
#     """
#     Remove um ou mais hosts do arquivo Ansible hosts.ini.
#     """
#     remove_hosts(hosts, groups)
