import subprocess, json
from importlib.resources import files
from ...config.constants import ANSIBLE_PKG, ANSIBLE_HOSTS_FILE


def run_playbook(
    playbook_name: str, target_host: str = "default", extra_vars=None
) -> str:
    """
    Executa um playbook do Ansible e retorna a saída como string.

    :param playbook_name: nome do playbook dentro de sparkflintcli/ansible/
    :param extra_vars: dicionário de variáveis extras
    :return: saída do comando
    """
    playbook_path = files(ANSIBLE_PKG) / playbook_name
    inventory_path = ANSIBLE_HOSTS_FILE

    # Garantir que extra_vars seja um dict
    if extra_vars is None:
        extra_vars = {}

    # Adiciona target_host em extra_vars
    extra_vars["target_host"] = target_host

    # Comando base
    cmd = ["ansible-playbook", "-i", str(inventory_path), str(playbook_path)]
    if extra_vars:
        formatted = " ".join(f"{k}={v}" for k, v in extra_vars.items())
        cmd += ["--extra-vars", formatted]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Erro ao executar o playbook:\n{e.stderr}") from e
