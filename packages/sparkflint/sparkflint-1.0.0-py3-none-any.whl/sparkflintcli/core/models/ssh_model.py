from dataclasses import dataclass
from pathlib import Path


@dataclass
class SSHKey:
    group: str
    private_key_path: Path
    public_key_path: Path

    def label(self):
        return f"[{self.group}] {self.private_key_path.name}"
