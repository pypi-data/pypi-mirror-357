import typer
from sparkflintcli.core.controllers.app_controller import open_app
from sparkflintcli.core.controllers.view_controller import open_view, autocomplete_views

app = typer.Typer()


# @app.command()
# def view(name: str = typer.Argument(..., autocompletion=autocomplete_views)):
#     """
#     Abre o atalho de view no navegador.
#     """
#     url = get_view(name)
#     if url is None:
#         print(f"[red]❌ Nenhuma view encontrada com o nome '{name}'")
#         raise typer.Exit(code=1)

#     webbrowser.open_new_tab(url)
#     print(f"[green]🌐 Abrindo '{name}': {url}")


@app.command("app")
@app.command("a")
def open_app_command(app_id: str):
    """
    Abre UI da aplicação YARN no navegador.
    """
    open_app(app_id)


@app.command()
@app.command("v")
def view(name: str = typer.Argument(..., autocompletion=autocomplete_views)):
    """
    Abre o atalho de view no navegador.
    """
    open_view(name)
