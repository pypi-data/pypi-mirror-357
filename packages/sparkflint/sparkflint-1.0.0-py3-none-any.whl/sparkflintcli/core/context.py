from rich.console import Console
import requests

console = Console()
session = requests.Session()

# Exemplo: cabeçalhos padrão da sua API
session.headers.update(
    {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
)
