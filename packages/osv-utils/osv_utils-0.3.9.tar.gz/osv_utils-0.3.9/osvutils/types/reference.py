from pydantic import BaseModel, AnyUrl, field_validator
from typing import Union
from enum import Enum


# Define the Enum for Reference types
class ReferenceType(str, Enum):
    ADVISORY = 'ADVISORY'
    ARTICLE = 'ARTICLE'
    DETECTION = 'DETECTION'
    DISCUSSION = 'DISCUSSION'
    REPORT = 'REPORT'
    FIX = 'FIX'
    INTRODUCED = 'INTRODUCED'
    GIT = 'GIT'
    PACKAGE = 'PACKAGE'
    EVIDENCE = 'EVIDENCE'
    WEB = 'WEB'


# Define the Reference model
class Reference(BaseModel):
    type: ReferenceType
    url: Union[AnyUrl, str]  # Try AnyUrl first, fallback to plain string

    # Custom validator to handle both valid URL and plain string cases
    @field_validator('url')
    def validate_url(cls, v):
        try:
            # Try to parse it as a valid URL (HttpUrl)
            AnyUrl(v)
            return v  # It's a valid URL
        except ValueError:
            # If it fails, treat it as a plain string (without a valid scheme)
            return v

    def is_full_url(self):
        return isinstance(self.url, AnyUrl)

    def is_git(self):
        return self.type == ReferenceType.GIT

    def is_fix(self):
        return self.type == ReferenceType.FIX
