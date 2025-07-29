from sparkflintcli.core.models.app_model import AppData
from sparkflintcli.core.ui.table import generate_table
from sparkflintcli.core.ui.messages import warning, success
import webbrowser


def display_apps(apps_data: AppData):
    if not apps_data:
        warning("Nenhum dado para exibir.")
        return

    columns = [
        {"header": col, "no_wrap": True, "overflow": "fold"} for col in apps_data.header
    ]
    rows = apps_data.rows

    generate_table("Aplicações YARN", columns, rows)


def open_url_in_browser(url: str):
    webbrowser.open_new_tab(url)
    success(f"Página encontrada. Redirecionando para {url}")
