from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationReport:
    errors: List[dict] = field(default_factory=list)
    warnings: List[dict] = field(default_factory=list)

    def add_error(self, row: int, code: str, msg: str):
        self.errors.append({"row": row, "code": code, "msg": msg})

    def add_warning(self, row: int, code: str, msg: str):
        self.warnings.append({"row": row, "code": code, "msg": msg})

    def ok(self) -> bool:
        return len(self.errors) == 0
