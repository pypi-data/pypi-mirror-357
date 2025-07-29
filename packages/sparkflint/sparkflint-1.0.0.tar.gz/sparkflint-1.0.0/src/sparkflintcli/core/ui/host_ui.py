from sparkflintcli.core.models.host_model import HostList
from sparkflintcli.core.ui.table import generate_table
from sparkflintcli.core.ui.messages import warning, success


def display_hosts(host_list: HostList):
    if not host_list.hosts:
        warning("Nenhum host encontrado no arquivo hosts.ini")
        return

    rows = [[host.name, host.ip, host.group, host.user] for host in host_list.hosts]

    columns = [
        {"header": "Host", "style": "bold"},
        {"header": "IP", "style": "dim"},
        {"header": "Grupo", "style": "bold cyan"},
        {"header": "Usuário", "style": "green"},
    ]

    generate_table("Hosts", columns, rows)
