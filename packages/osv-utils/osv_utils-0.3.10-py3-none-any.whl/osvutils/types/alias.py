from enum import Enum
from pydantic import BaseModel


class AliasType(Enum):
    CVE = 'CVE'
    Other = 'Other'


class Alias(BaseModel):
    type: AliasType
    value: str

    def is_cve(self) -> bool:
        return self.type == AliasType.CVE
