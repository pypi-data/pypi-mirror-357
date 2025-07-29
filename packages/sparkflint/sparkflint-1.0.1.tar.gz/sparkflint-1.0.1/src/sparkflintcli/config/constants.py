from importlib.resources import files
from pathlib import Path

SPARKFLINT_HOME = Path.home() / ".sparkflint"
SPARKFLINT_CONFIG_FILE = SPARKFLINT_HOME / "config.toml"
SPARKFLINT_CACHE_FILE = SPARKFLINT_HOME / "token.json"
SPARKFLINT_VIEWS_FILE = SPARKFLINT_HOME / "views.toml"

ANSIBLE_DIR = SPARKFLINT_HOME / "ansible"
ANSIBLE_HOSTS_FILE = ANSIBLE_DIR / "hosts.ini"
ANSIBLE_PKG = "sparkflintcli.ansible"

SSH_KEY_DIR = Path.home() / ".sparkflint" / "ssh"
