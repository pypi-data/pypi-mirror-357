# from ..core.auth import login_user
# from ..core.pipelines import get_pipeline_by_name
# from ..core.ansible import run_playbook
# from rich.console import Console
# import typer, requests, os, base64, json

# console = Console()


# def run(
#     aplicacao: str = typer.Argument(..., help="Nome da aplicação Spark"),
# ):
#     """
#     Executa pipeline cadastrado na origem.
#     """
#     local_job_path = os.path.abspath("src/sparkflintcli/pyspark/job.py")

#     try:
#         access_token = login_user("wiliam.ribeiro", "cluster.diinf")

#         with console.status(
#             "[bold green]Buscando pipeline...[/bold green]", spinner="dots"
#         ):
#             metadata = get_pipeline_by_name(aplicacao, access_token)

#         if metadata is None:
#             console.print(f"[red]❌ Pipeline '{aplicacao}' não encontrado.[/red]")
#             raise typer.Exit(code=1)

#         console.print(f"[green]✅ Pipeline encontrado:[/green] {metadata['nome']}")
#         print(metadata)
#         encoded_metadata = base64.b64encode(json.dumps(metadata).encode()).decode()

#         with console.status(
#             "[bold green]Lançando aplicação spark...[/bold green]", spinner="dots"
#         ):
#             output = run_playbook(
#                 "run_pipeline.yml",
#                 console,
#                 extra_vars={
#                     "local_job_path": local_job_path,
#                     "encoded_metadata": encoded_metadata,
#                 },
#             )
#         print(output)

#     except requests.exceptions.RequestException as e:
#         typer.secho("Erro ao conectar à origem:", fg=typer.colors.RED)
#         typer.echo(str(e))
#         raise typer.Exit(code=2)

import typer, re, codecs
from ..core.ansible import run_playbook
from ..core.rich import generate_table
from rich.console import Console

app = typer.Typer()
