from dataclasses import dataclass
from typing import Optional


@dataclass
class Responsible:
    nome: str

    @classmethod
    def from_dict(cls, data: dict) -> "Responsible":
        return cls(nome=data.get("nome", ""))


@dataclass
class Pipeline:
    id: str
    name: str
    criado_em: str
    atualizado_em: Optional[str]
    responsavel: Responsible

    @classmethod
    def from_dict(cls, data: dict) -> "Pipeline":
        return cls(
            id=data.get("id", ""),
            name=data.get("nome", ""),
            criado_em=data.get("criado_em", ""),
            atualizado_em=data.get("atualizado_em") or "-",
            responsavel=Responsible.from_dict(data.get("responsavel", {})),
        )
