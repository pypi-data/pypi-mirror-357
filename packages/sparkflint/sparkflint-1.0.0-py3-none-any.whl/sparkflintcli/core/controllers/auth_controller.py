from sparkflintcli.core.services.auth_service import AuthService
from sparkflintcli.core.ui.messages import success

auth_service = AuthService()


def login_user(force: bool = False) -> str:
    return auth_service.login(force=force)


def validate_login() -> bool:
    return auth_service.validate_login()


def logout_user():
    auth_service.logout()
    success("Logout realizado com sucesso.")
