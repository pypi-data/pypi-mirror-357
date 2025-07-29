from dataclasses import dataclass
from typing import Optional


@dataclass
class View:
    name: str
    url: str

    def is_valid(self) -> bool:
        return self.url.startswith("http")
