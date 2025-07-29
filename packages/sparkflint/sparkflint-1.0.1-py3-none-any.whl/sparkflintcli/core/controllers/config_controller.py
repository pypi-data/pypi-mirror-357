import typer
from pathlib import Path
from sparkflintcli.core.context import console
from sparkflintcli.core.services.config_service import ConfigService
from sparkflintcli.core.services.auth_service import AuthService
from sparkflintcli.core.ui.messages import warning, success, error

config_service = ConfigService()
auth_service = AuthService(config_service=config_service)


def show_config():
    config = config_service.load()
    console.print(f"[bold]Origin:[/bold] {config.url or '(não definida)'}")
    console.print(f"[bold]Username:[/bold] {config.username or '(não definido)'}")
    console.print(
        f"[bold]Password:[/bold] {'(definida)' if config.password else '(não definida)'}"
    )


def init_config(url: str, username: str, password: str) -> Path:
    if not config_service.validate_origin(url):
        error(
            f"Não foi possível acessar a origin: {url}. Verifique a URL e sua conexão com a rede."
        )
        raise typer.Exit(code=1)
    config_service.set_origin(url)
    success("URL de Origin válida.")

    try:
        auth_service.login(url, username, password, force=True)
    except RuntimeError:
        error("Usuário e/ou senha inválidos.")
        raise typer.Exit(code=1)

    config_service.set_username(username)
    config_service.set_password(password)
    success("Usuário e senha válidos.")
    return config_service.file_path


def init_config_from_file(file_path: str) -> Path:
    file = Path(file_path)
    if not file.exists():
        error(f"Arquivo {file_path} não encontrado.")
        raise typer.Exit(code=1)

    custom_service = ConfigService(file)
    config_data = custom_service.load()

    origin = config_data.url
    username = config_data.username
    password = config_data.password

    if not all([origin, username, password]):
        print(config_data, origin, username, password)
        error("O arquivo precisa conter url, username e password em \\[origin\\")
        raise typer.Exit(code=1)

    # Reaproveita o fluxo já testado para validar e salvar
    return init_config(origin, username, password)


def clear_config():
    config_service.set_origin(None)
    config_service.set_username(None)
    config_service.set_password(None)
    success("Configuração limpa com sucesso.")


def get_origin():
    try:
        origin = config_service.get_origin()
        console.print(origin)
    except ValueError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(code=1)


def set_origin(url: str):
    config_service.set_origin(url)
    success(f"Origin definida como: {url}")


def get_user():
    try:
        username = config_service.get_username()
        console.print(username)
    except ValueError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(code=1)


def set_user(username: str):
    config_service.set_username(username)
    success(f"Username definido como: {username}")


def get_password():
    try:
        password = config_service.get_password()
        console.print(password)
    except ValueError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(code=1)


def set_password(password: str):
    config_service.set_password(password)
    success("Senha configurada com sucesso.")
