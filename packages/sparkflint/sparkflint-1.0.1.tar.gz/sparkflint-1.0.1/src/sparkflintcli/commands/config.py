import typer
from sparkflintcli.core.controllers import config_controller

app = typer.Typer(name="config", help="Gerencia configurações da CLI")


@app.command("show")
def show():
    config_controller.show_config()


@app.command("clear")
def clear():
    config_controller.clear_config()


@app.command("set-origin")
def set_origin(url: str):
    config_controller.set_origin(url)


@app.command("get-origin")
def get_origin():
    config_controller.get_origin()


@app.command("set-user")
def set_user(user: str):
    config_controller.set_user(user)


@app.command("get-user")
def get_user():
    config_controller.get_user()


@app.command("set-password")
def set_password(password: str = typer.Option(..., prompt=True, hide_input=True)):
    config_controller.set_password(password)


@app.command("get-password")
def get_password():
    config_controller.get_password()
