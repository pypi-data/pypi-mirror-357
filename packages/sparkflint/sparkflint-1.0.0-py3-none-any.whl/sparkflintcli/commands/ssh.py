import typer
from sparkflintcli.core.controllers import ssh_controller
from sparkflintcli.core.ui.messages import success, error, info, warning

app = typer.Typer(help="Gerencia chaves SSH para conexão com hosts remotos.")


@app.command("agent")
def start_agent():
    """Inicia o ssh-agent se necessário."""
    ssh_controller.setup_agent()


@app.command("generate")
def generate_key(group: str):
    """Gera uma nova chave SSH para um grupo."""
    try:
        key = ssh_controller.create_key(group)
        success(f"Chave criada: {key.private_key_path}")
    except FileExistsError:
        error(f"Chave para grupo '{group}' já existe.")


@app.command("load")
def load_key(group: str):
    """Carrega a chave de um grupo no ssh-agent."""
    if ssh_controller.load_key(group):
        success(f"Chave do grupo '{group}' carregada.")
    else:
        error("Falha ao carregar a chave.")


@app.command("list")
def list_loaded():
    """Lista as chaves carregadas no agente SSH."""
    keys = ssh_controller.list_keys()
    if keys:
        for k in keys:
            info(k)
    else:
        warning("Nenhuma chave carregada.")


@app.command("send")
def send_key(group: str, host: str, user: str = "root", port: int = 22):
    """Copia a chave pública para o host remoto via ssh-copy-id."""
    if ssh_controller.send_key(group, host, user, port):
        success(f"Chave enviada para {host}")
    else:
        error(f"Erro ao enviar chave para {host}")
