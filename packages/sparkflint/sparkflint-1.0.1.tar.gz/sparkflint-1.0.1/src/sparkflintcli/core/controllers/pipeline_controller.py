from sparkflintcli.core.context import console
from sparkflintcli.core.services.pipeline_service import (
    get_pipelines,
)
from sparkflintcli.core.ui.messages import warning, error
from sparkflintcli.core.ui.pipeline_ui import display_pipelines
import typer


def kill_pipeline():
    print()


def list_pipelines():
    try:
        with console.status(
            "[bold green]Buscando pipelines...[/bold green]", spinner="dots"
        ):
            pipelines = get_pipelines()
            if not pipelines:
                warning("Nenhum pipeline encontrado.")
                raise typer.Exit(code=1)
            display_pipelines(pipelines)
    except Exception as e:
        error("Erro ao buscar pipelines.")
        error(str(e))
        raise typer.Exit(code=2)


def open_pipeline():
    print()


def run_pipeline():
    print()


def schedule_pipeline():
    print()


def status_pipeline():
    print()


def test_pipeline():
    print()
