import time, typer
from rich.console import Console
from sparkflintcli.core.controllers.config_controller import (
    init_config,
    init_config_from_file,
)
from sparkflintcli.core.ui.messages import error, success, warning
from sparkflintcli.core.utils.autocomplete import detect_shell, append_autocomplete

console = Console()
app = typer.Typer()


def init(
    file: str = typer.Option(
        None, "--file", "-f", help="Arquivo de configuração do sparkflint (.toml)"
    ),
):
    """
    Inicializa a SparkFlintCLI com configurações interativas ou via arquivo.
    """
    console.print("[bold cyan]Iniciando configuração...[/bold cyan]")
    start = time.time()

    if file:
        file_path = init_config_from_file(file)
    else:
        origin = typer.prompt("Origin")
        username = typer.prompt("Usuário")
        password = typer.prompt("Senha", hide_input=True)

        # Chama o controller para validar e salvar os dados
        file_path = init_config(origin, username, password)

    shell = detect_shell()
    if shell:
        if append_autocomplete(shell):
            success(
                f"Autocompletar ativado para {shell}. Reinicie o terminal para aplicar."
            )
        else:
            warning(
                "Autocompletar já estava configurado ou não foi possível configurar automaticamente."
            )
    else:
        warning(
            "Shell não reconhecido. Configure o autocompletar manualmente se desejar."
        )

    end = time.time()
    success(f"Tempo total: {end - start:.2f} segundos")
    success(f"Configuração salva em {file_path}.")
    console.print(
        "[bold cyan]Configuração concluída![/bold cyan] Você já pode usar os comandos da CLI normalmente."
    )
