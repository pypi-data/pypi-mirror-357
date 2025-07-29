from typing import List
from sparkflintcli.config.constants import SSH_KEY_DIR
from sparkflintcli.core.models.ssh_model import SSHKey
from sparkflintcli.core.services import ssh_service
from sparkflintcli.core.ui.messages import success, warning, error


def ensure_key_exists(group: str) -> bool:
    private_key = SSH_KEY_DIR / f"id_rsa_{group}"
    public_key = private_key.with_suffix(".pub")
    return private_key.exists() and public_key.exists()


def setup_agent():
    try:
        ssh_service.start_agent_if_needed()
        success("ssh-agent ativo!")
    except Exception as e:
        error(f"Erro ao iniciar o agente: {e}")


def create_key(group: str) -> SSHKey:
    return ssh_service.generate_keypair(group, SSH_KEY_DIR)


def load_key(group: str) -> bool:
    key_path = SSH_KEY_DIR / f"id_rsa_{group}"
    if not key_path.exists():
        error(f"Chave para grupo '{group}' não existe.")
        return False
    return ssh_service.add_key_to_agent(key_path)


def list_keys() -> List[str]:
    return ssh_service.list_loaded_keys()


def send_key(group: str, host: str, user: str = "root", port: int = 22) -> bool:
    key = SSHKey(
        group=group,
        private_key_path=SSH_KEY_DIR / f"id_rsa_{group}",
        public_key_path=SSH_KEY_DIR / f"id_rsa_{group}.pub",
    )
    return ssh_service.copy_key_to_remote(host, user, port, key.public_key_path)
