from sparkflintcli.core.ui.table import (
    generate_table,
)
import webbrowser


def display_views(views: dict[str, str]):
    columns = [
        {"header": "Nome", "style": "cyan"},
        {"header": "URL", "style": "green"},
    ]

    rows = [[name, url] for name, url in views.items()]
    generate_table("Views Salvas", columns, rows)


def open_url_in_browser(url: str):
    webbrowser.open(url)
