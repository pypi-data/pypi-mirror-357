from sparkflintcli.core.controllers.host_controller import add_hosts
from sparkflintcli.core.controllers.view_controller import add_view
import typer

app = typer.Typer()


@app.command()
@app.command(name="h", hidden=True)
def host(
    hosts: str = typer.Argument(
        ..., help="Lista de hosts separados por vírgula (ex: fn01,fn02)"
    ),
    ips: str = typer.Option(
        None, "--ips", help="Lista de IPs ou nomes reais separados por vírgula"
    ),
    user: str = typer.Option(
        None, "--user", "-u", help="Usuário para conexão via Ansible"
    ),
    group: str = typer.Option(
        "default", "--group", "-g", help="Grupo Ansible (default: default)"
    ),
    ssh_port: int = typer.Option(22, "--ssh-port", help="Porta SSH"),
):
    """
    Adiciona um ou mais hosts ao arquivo Ansible hosts.ini
    """
    add_hosts(hosts, ips, user, group, ssh_port)


@app.command()
@app.command(name="v", hidden=True)
def view(
    name: str = typer.Argument(..., help="Nome da view"),
    url: str = typer.Argument(..., help="Url no navegador"),
):
    """
    Adiciona uma ou mais views.
    """
    add_view(name, url)
