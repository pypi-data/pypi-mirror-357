from sparkflintcli.core.context import console
from sparkflintcli.core.services.host_service import get_hosts, save_hosts, delete_hosts
from sparkflintcli.core.models.host_model import Host
from sparkflintcli.core.ui.host_ui import display_hosts
from sparkflintcli.core.ui.messages import error, warning, success
import typer
from typing import List


def add_hosts(
    hosts: str,
    ips: str = None,
    user: str = None,
    group: str = None,
    ssh_port: int = 22,
):
    host_list = [h.strip() for h in hosts.split(",") if h.strip()]
    ip_list = [ip.strip() for ip in ips.split(",")] if ips else []

    ip_list = []
    if ips:
        ip_list = [ip.strip() for ip in ips.split(",")]
        if len(ip_list) != len(host_list):
            raise typer.BadParameter(
                "A quantidade de IPs deve ser igual à quantidade de hosts."
            )
    else:
        # Sem IPs fornecidos: use os names como IPs
        ip_list = host_list.copy()

    group = group.strip() if group else "default"

    new_hosts = []
    for name, ip in zip(host_list, ip_list):
        host = Host(name=name, ip=ip, user=user, group=group)
        new_hosts.append(host)

    added_hosts = save_hosts(new_hosts, ssh_user=user or "root", ssh_port=ssh_port)

    if added_hosts:
        success(
            f"Hosts adicionados ao grupo '{group}': {', '.join([h.name for h in added_hosts])}"
        )
    else:
        warning("Nenhum novo host adicionado.")


def list_hosts():
    try:
        with console.status(
            "[bold green]Buscando hosts...[/bold green]", spinner="dots"
        ):
            hosts = get_hosts()
            if not hosts:
                warning(
                    "Nenhum host encontrado. Por favor, adicione hosts usando [bold]sparkflint add host[/bold]"
                )
                raise typer.Exit(code=1)
            display_hosts(hosts)
    except Exception as e:
        error("Erro ao buscar hosts.")
        error(str(e))
        raise typer.Exit(code=2)


def remove_hosts(names: str, group: str = None):
    host_list = [h.strip() for h in names.split(",") if h.strip()]
    group = group.strip() if group else None

    hosts_to_delete = [Host(name=name, group=group) for name in host_list]
    removed = delete_hosts(hosts_to_delete)

    if removed:
        success(f"Hosts removidos: {', '.join(h.name for h in removed)}")
    else:
        warning("Nenhum host foi removido.")


def autocomplete_host_names(incomplete: str) -> List[str]:
    """
    Retorna lista de nomes de hosts que começam com o valor parcial digitado.
    """
    hosts = get_hosts()
    return [h.name for h in hosts if h.name.startswith(incomplete)]
