from sparkflintcli.core.context import console
from rich.table import Table


def generate_table(title: str, columns: list[dict], rows: list[list[str]]):
    table = Table(title=title)

    for col in columns:
        table.add_column(
            col.get("header", ""),
            style=col.get("style", ""),
            no_wrap=col.get("no_wrap", False),
            overflow=col.get("overflow", None),
        )

    for row in rows:
        safe_row = [
            cell.strip() if isinstance(cell, str) and cell.strip() else "-"
            for cell in row
        ]
        table.add_row(*safe_row)

    console.print(table)
