import re, random
from sparkflintcli.core.utils.ansible import run_playbook
from sparkflintcli.core.models.app_model import AppData
from sparkflintcli.core.services.view_service import get_view_by_name
from sparkflintcli.core.services.host_service import get_hosts
from sparkflintcli.core.controllers.ssh_controller import load_key


def get_yarn_apps(target_host: str | None = None) -> AppData | None:
    """
    Executa playbook do Ansible e retorna dados estruturados com cabeçalho e linhas.
    """

    if target_host is None:
        hosts = get_hosts()
        if not hosts:
            raise RuntimeError("Inventário vazio, nenhum host encontrado.")
        target_host = random.choice(hosts)
    load_key(target_host.group)
    output = run_playbook("list_apps.yml", target_host=target_host.name)
    match = re.search(r'"yarn_output.stdout": "(.*?)"\s*}', output, re.DOTALL)
    if not match:
        return None

    yarn_output_raw = match.group(1)
    yarn_output = yarn_output_raw.encode("utf-8").decode("unicode_escape")

    return AppData.from_yarn_output(yarn_output)


def get_app_url(app_id: str) -> str | None:
    """
    Retorna a URL completa da aplicação no YARN.
    """
    base_view = get_view_by_name("yarn")
    if not base_view:
        return None
    return f"{base_view[:-5]}/app/{app_id}"
