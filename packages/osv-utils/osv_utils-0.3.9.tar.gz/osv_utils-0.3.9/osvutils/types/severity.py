from enum import Enum
from typing import Union
from cvss import CVSS2, CVSS3, CVSS4
from pydantic import BaseModel, model_validator


# Enum for the severity types
class SeverityType(str, Enum):
    CVSS_V2 = 'CVSS_V2'
    CVSS_V3 = 'CVSS_V3'
    CVSS_V4 = 'CVSS_V4'


SEVERITY_MAP = {
    SeverityType.CVSS_V2: CVSS2,
    SeverityType.CVSS_V3: CVSS3,
    SeverityType.CVSS_V4: CVSS4
}


# Severity model
class Severity(BaseModel):
    type: SeverityType
    score: Union[CVSS2, CVSS3, CVSS4]

    class Config:
        arbitrary_types_allowed = True  # Allow arbitrary types

    @model_validator(mode='before')
    def validate_severity(cls, values):
        severity_type = values.get('type')
        score = values.get('score')

        if severity_type not in SEVERITY_MAP:
            raise ValueError(f"Unknown severity type: {severity_type}")

        # TODO: fallback to patterns if this fails
        values['score'] = SEVERITY_MAP[severity_type](score)

        return values
