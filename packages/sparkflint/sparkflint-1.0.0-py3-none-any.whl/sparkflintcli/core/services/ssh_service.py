import os
import subprocess
from pathlib import Path
from typing import List
from sparkflintcli.core.models.ssh_model import SSHKey


def start_agent_if_needed():
    if "SSH_AUTH_SOCK" not in os.environ:
        result = subprocess.run("eval $(ssh-agent)", shell=True, executable="/bin/bash")
        if result.returncode != 0:
            raise RuntimeError("Erro ao iniciar ssh-agent")


def add_key_to_agent(private_key_path: Path) -> bool:
    result = subprocess.run(["ssh-add", str(private_key_path)], capture_output=True)
    return result.returncode == 0


def list_loaded_keys() -> List[str]:
    result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return result.stdout.strip().splitlines()


def copy_key_to_remote(host: str, user: str, port: int, public_key_path: Path) -> bool:
    cmd = ["ssh-copy-id", "-i", str(public_key_path), "-p", str(port), f"{user}@{host}"]
    result = subprocess.run(cmd)
    return result.returncode == 0


def generate_keypair(group: str, key_dir: Path) -> SSHKey:
    key_dir.mkdir(parents=True, exist_ok=True)
    private_key_path = key_dir / f"id_rsa_{group}"
    public_key_path = key_dir / f"id_rsa_{group}.pub"

    if private_key_path.exists():
        raise FileExistsError(f"Chave para o grupo '{group}' já existe.")

    subprocess.run(
        [
            "ssh-keygen",
            "-t",
            "rsa",
            "-b",
            "4096",
            "-f",
            str(private_key_path),
            "-N",
            "",
        ],
        check=True,
    )

    return SSHKey(
        group=group, private_key_path=private_key_path, public_key_path=public_key_path
    )
