from sparkflintcli.config.constants import ANSIBLE_HOSTS_FILE
from sparkflintcli.core.models.host_model import HostList, Host
from sparkflintcli.core.ui.messages import warning, success, error, info
from typing import List


def copy_ssh_key_to_host(host: Host, ssh_user: str, ssh_port: int = 22) -> bool:
    from sparkflintcli.core.controllers import ssh_controller

    key_exists = ssh_controller.ensure_key_exists(host.group or "default")
    if not key_exists:
        error(f"Chave do grupo '{host.group}' não encontrada.")
        return False

    success(f"Usando chave do grupo: {host.group}")
    return ssh_controller.send_key(
        group=host.group or "default",
        host=host.name,
        user=ssh_user or "root",
        port=ssh_port,
    )


def get_hosts_ini_data() -> dict:
    """
    Carrega os dados brutos do arquivo hosts.ini agrupados por grupo.
    """
    if not ANSIBLE_HOSTS_FILE.exists():
        return {}

    with open(ANSIBLE_HOSTS_FILE, "r") as f:
        lines = f.readlines()

    content_by_group = {}
    current_group = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_group = stripped[1:-1]
            content_by_group.setdefault(current_group, [])
        elif current_group:
            content_by_group[current_group].append(stripped)

    return content_by_group


def get_hosts() -> HostList:
    raw_data = get_hosts_ini_data()
    return HostList.from_raw_ini(raw_data)


def save_hosts(new_hosts: List[Host], ssh_user: str, ssh_port: int = 22) -> List[Host]:
    """
    Adiciona uma lista de hosts ao arquivo ini, evitando duplicatas.
    Retorna lista de hosts adicionados.
    """
    # Garante que o caminho exista
    ANSIBLE_HOSTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Recupera dados brutos dos hosts
    existing_hosts_by_group = get_hosts_ini_data()

    # Converte dados brutos na class HostList
    host_list = HostList.from_raw_ini(existing_hosts_by_group)

    added_hosts = []

    # Tenta adicionar o host a hostlist
    for host in new_hosts:
        # Tenta copiar a chave pública antes de adicionar
        copied = copy_ssh_key_to_host(host, ssh_user, ssh_port)
        if not copied:
            warning(
                f"Não foi possível copiar a chave para {host.hostname}. Continue? (s/n)"
            )
            # Aqui você pode colocar lógica para o usuário confirmar (input)
            # ou abortar a operação. Exemplo simples abaixo:
            confirm = input().lower()
            if confirm != "s":
                warning(f"Host {host.hostname} não adicionado.")
                continue

        added, reason = host_list.add(host)
        if added:
            added_hosts.append(host)
        else:
            print(added, reason)
            warning(f"Host não adicionado ({reason}): {host.hostname}")

    # Serializa para ini e salva
    ini_data = host_list.to_ini_lines_by_group()
    with open(ANSIBLE_HOSTS_FILE, "w", encoding="utf-8") as f:
        for group, lines in ini_data.items():
            f.write(f"\n[{group}]\n")
            for line in lines:
                f.write(line + "\n")

    return added_hosts


def delete_hosts(hosts_to_delete: List[Host]) -> HostList:
    """
    Exclui uma lista de hosts do arquivo ini.
    Retorna lista de hosts excluídos.
    """
    existing_data = get_hosts_ini_data()
    host_list = HostList.from_raw_ini(existing_data)

    removed_hosts = []

    for to_delete in hosts_to_delete:
        original_len = len(host_list.hosts)
        host_list.hosts = [
            h
            for h in host_list.hosts
            if not (
                h.name == to_delete.name
                and (not to_delete.group or h.group == to_delete.group)
            )
        ]
        if len(host_list.hosts) < original_len:
            removed_hosts.append(to_delete)

    if not removed_hosts:
        warning("Nenhum host removido.")

    # Regrava o arquivo
    ini_data = host_list.to_ini_lines_by_group()
    with open(ANSIBLE_HOSTS_FILE, "w", encoding="utf-8") as f:
        for group, lines in ini_data.items():
            f.write(f"\n[{group}]\n")
            for line in lines:
                f.write(line + "\n")

    return removed_hosts
