from sparkflintcli import __version__
from sparkflintcli.commands import (
    add,
    config,
    init,
    # kill,
    list,
    open,
    remove,
    # run,
    # set,
    # show,
    ssh,
    # status,
    # test,
)
import typer
from typing import Optional

app = typer.Typer(
    help="SparkFlintCLI facilita a gestão de aplicações Spark em ambientes remotos."
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        False, "--version", "-v", help="Mostra a versão da CLI e sai", is_eager=True
    ),
):
    if version:
        typer.echo(f"SparkFlintCLI versão {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        # mostra help se nenhum comando for chamado
        typer.echo(ctx.get_help())
        raise typer.Exit()


# COMANDOS

app.add_typer(add.app, name="add", help="Adiciona hosts.")
app.add_typer(add.app, name="a", hidden=True)

app.add_typer(
    config.app, name="config", help="Gerencia arquivo de configuração do sparkflint."
)
app.add_typer(config.app, name="c", hidden=True)

app.command()(init.init)
app.command(name="i", hidden=True)(init.init)

# app.add_typer(kill.app, name="kill", help="Encerra aplicações spark em execução.")
# app.add_typer(kill.app, name="k", hidden=True)

app.add_typer(
    list.app,
    name="list",
    help="Lista aplicações spark, pipelines, dags Airflow ou hosts.",
)
app.add_typer(list.app, name="l", hidden=True)

app.add_typer(
    open.app, name="open", help="Abre UI de ferramentas big data no navegador."
)
app.add_typer(open.app, name="o", hidden=True)

app.add_typer(remove.app, name="remove", help="Remove hosts.")
app.add_typer(remove.app, name="rm", hidden=True)

# app.add_typer(run.app, name="run", help="Executa aplicações spark via Ansible.")
# app.add_typer(run.app, name="r", hidden=True)

# app.add_typer(set.app, name="set", help="Altera configurações do sparkflint.")

# app.add_typer(
#     show.app,
#     name="show",
#     help="Exibe configurações do sparkflint e logs de aplicações spark",
# )

app.add_typer(
    ssh.app,
    name="ssh",
    help="Gerencia chaves SSH para conexão com hosts remotos.",
)

# app.add_typer(
#     status.app,
#     name="status",
#     help="Exibe status de aplicações spark gerenciados pelo sparkflint",
# )
# app.add_typer(status.app, name="s", hidden=True)

# app.add_typer(
#     test.app,
#     name="status",
#     help="Valida pipelines, dags Airflow ou configurações do sparkflint",
# )
# app.add_typer(test.app, name="t", hidden=True)

if __name__ == "__main__":
    app()
