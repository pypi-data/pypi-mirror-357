from dataclasses import dataclass


@dataclass
class Config:
    url: str
    username: str
    password: str
