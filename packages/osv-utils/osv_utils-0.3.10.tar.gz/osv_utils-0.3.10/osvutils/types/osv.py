from datetime import datetime
from pydantic import BaseModel, field_validator, Field
from typing import List, Optional

from osvutils.types.alias import Alias
from osvutils.types.severity import Severity
from osvutils.types.reference import Reference
from osvutils.types.affected import Affected
from osvutils.types.range import GitRange
from osvutils.types.event import Fixed

from osvutils.utils.misc import get_alias_type, is_cve_id, get_cve_match


# Credit model
class Credit(BaseModel):
    name: str
    contact: Optional[List[str]] = None
    type: Optional[str] = None


# Main schema model: version 1.6.0
# TODO: implement other schema versions
class OSV(BaseModel):
    schema_version: str
    id: str
    modified: datetime
    published: datetime
    withdrawn: Optional[str] = None
    aliases: Optional[List[Alias]] = None
    related: Optional[List[str]] = None
    summary: Optional[str] = None
    details: Optional[str] = None
    severity: Optional[List[Severity]] = None
    affected: Optional[List[Affected]] = Field(
        default=None,
        description="List of affected objects with package details, severity, ranges, etc."
    )
    references: Optional[List[Reference]] = Field(
        default=None,
        description="List of reference objects or None"
    )
    credits: Optional[List[Credit]] = None
    database_specific: Optional[dict] = None  # TODO: to be extended for each database

    @field_validator('references', mode='before')
    def parse_references(cls, values):
        if not values:
            return []

        # filter out References without url key
        return [ref for ref in values if ref.get('url')]

    @field_validator('aliases', mode='before')
    def parse_aliases(cls, v: List[str]):
        if isinstance(v, list):
            # If v is a list, we assume it's already in the correct format
            return [Alias(type=get_alias_type(alias), value=alias) for alias in v]

        return []

    def has_aliases(self) -> bool:
        return self.aliases and len(self.aliases) > 0

    def has_cve_id(self) -> bool:
        if self.has_aliases():
            return any(alias.is_cve() for alias in self.aliases)

        return False

    def is_cve_id(self) -> bool:
        return is_cve_id(self.id)

    def get_cve_id(self) -> Optional[str]:
        # TODO: temporary solution, there should be a flag or variable to indicate/store the matched cve_id
        cve_id = get_cve_match(self.id)

        if cve_id:
            return cve_id

        if self.has_aliases():
            for alias in self.aliases:
                if alias.is_cve():
                    return alias.value

        return None

    def has_references(self) -> bool:
        return self.references and len(self.references) > 0

    def has_fix_refs(self) -> bool:
        if self.has_references():
            return any(ref.is_fix() for ref in self.references)

        return False

    def has_affected(self) -> bool:
        return self.affected and len(self.affected) > 0

    def has_git_ranges(self) -> bool:
        if self.has_affected():
            return any(affected.has_git_ranges() for affected in self.affected)

        return False

    def get_git_ranges(self) -> List[GitRange]:
        ranges = []

        if self.has_affected():
            for affected in self.affected:
                ranges.extend(affected.get_git_ranges())

        return ranges

    def get_git_fixes(self) -> List[Fixed]:
        fixes = []

        if self.has_affected():
            for affected in self.affected:
                for git_range in affected.get_git_ranges():
                    fixes.extend(git_range.get_fixed_events())

        return fixes

    def get_scores(self):
        if self.severity:
            return [s.score for s in self.severity]

        return []
