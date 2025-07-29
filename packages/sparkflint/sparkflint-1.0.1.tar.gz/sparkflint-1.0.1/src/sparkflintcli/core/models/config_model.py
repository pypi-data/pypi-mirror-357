from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    url: str = None
    username: str = None
    password: str = None
