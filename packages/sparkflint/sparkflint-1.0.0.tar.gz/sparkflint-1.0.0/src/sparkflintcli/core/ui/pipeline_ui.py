from sparkflintcli.core.models.pipeline_model import Pipeline
from sparkflintcli.core.ui.table import generate_table


def display_pipelines(pipelines: list[Pipeline]):
    rows = [
        [
            pipeline.name,
            pipeline.responsavel.nome,
            pipeline.id,
            pipeline.criado_em,
            pipeline.atualizado_em,
        ]
        for pipeline in pipelines
    ]

    columns = [
        {"header": "Nome", "style": "cyan"},
        {"header": "Responsável", "style": "green"},
        {"header": "ID", "style": "dim", "no_wrap": True},
        {"header": "Criado em", "style": "yellow"},
        {"header": "Atualizado em", "style": "red"},
    ]

    generate_table("Pipelines", columns, rows)
