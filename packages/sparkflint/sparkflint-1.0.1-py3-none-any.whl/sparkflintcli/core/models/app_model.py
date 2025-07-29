from dataclasses import dataclass
from typing import List, Union


@dataclass
class AppData:
    header: List[str]
    rows: List[List[str]]

    @classmethod
    def from_yarn_output(cls, raw_output: str) -> Union["AppData", None]:
        lines = raw_output.strip().split("\n")
        if len(lines) < 2:
            return None

        header = [col.strip() for col in lines[1].split("\t") if col.strip()]
        rows = [
            [cell.strip() for cell in line.split("\t") if cell.strip()]
            for line in lines[2:]
            if line.strip()
        ]
        return cls(header=header, rows=rows)
