from typing import Optional
from pydantic import BaseModel, ValidationError, field_validator

from osvutils.types.ecosystem import Ecosystem, EcosystemType


# Package model
class Package(BaseModel):
    name: str
    ecosystem: Ecosystem
    purl: Optional[str] = None

    @field_validator('ecosystem', mode='before')
    def split_ecosystem(cls, v):
        """
        Custom validator to handle ecosystem and version splitting.
        If the input is in the format 'Ecosystem:Version', split it.
        """
        if isinstance(v, str):
            # Split input like 'AlmaLinux:8' into ('AlmaLinux', '8')
            split = v.split(':', 1)

            if len(split) > 1:
                ecosystem_name, version = split

                try:
                    return {'ecosystem': EcosystemType(ecosystem_name), 'version': version}
                except ValueError:
                    raise ValidationError(f"Invalid ecosystem: {ecosystem_name}")
            else:
                # If no version, just map to ecosystem
                return {'ecosystem': EcosystemType(v), 'version': None}

        return v
