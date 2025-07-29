import os


def detect_shell() -> str | None:
    """
    Detecta o shell do usuário com base na variável de ambiente SHELL.
    """
    shell_path = os.environ.get("SHELL", "")
    if "zsh" in shell_path:
        return "zsh"
    elif "bash" in shell_path:
        return "bash"
    return None


def append_autocomplete(shell: str) -> bool:
    """
    Adiciona o autocompletar ao shell (zsh ou bash), se ainda não estiver presente.
    Retorna True se foi adicionado, False se já existia ou não foi possível.
    """
    line = f"source <(sparkflint --show-completion {shell})"
    rc_file = "~/.zshrc" if shell == "zsh" else "~/.bashrc"
    rc_path = os.path.expanduser(rc_file)

    if not os.path.exists(rc_path):
        return False

    try:
        with open(rc_path, "r") as f:
            if line in f.read():
                return False  # já existe
        with open(rc_path, "a") as f:
            f.write(f"\n# Autocompletar SparkFlint CLI\n{line}\n")
        return True
    except Exception:
        return False
