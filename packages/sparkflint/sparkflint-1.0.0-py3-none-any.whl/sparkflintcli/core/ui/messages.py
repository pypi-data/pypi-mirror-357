from sparkflintcli.core.context import console


def success(msg):
    console.print(f"[green]✔ {msg}[/green]")


def warning(msg):
    console.print(f"[yellow]! {msg}[/yellow]")


def error(msg):
    console.print(f"[red]✘ {msg}[/red]")


def info(msg):
    console.print(f"[cyan]ℹ {msg}[/cyan]")
