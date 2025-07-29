
from pydantic import BaseModel, model_validator
from typing import Optional, List

from osvutils.types.range import Range, GitRange
from osvutils.types.package import Package
from osvutils.types.severity import Severity


# Affected model
class Affected(BaseModel):
    package: Optional[Package] = None
    severity: Optional[List[Severity]] = None
    ranges: Optional[List[Range]] = None
    versions: Optional[List[str]] = None
    ecosystem_specific: Optional[dict] = None  # Adjust according to your needs
    database_specific: Optional[dict] = None  # Adjust according to your needs

    def has_ranges(self) -> bool:
        return self.ranges and len(self.ranges) > 0

    def get_git_ranges(self) -> List[GitRange]:
        if self.has_ranges():
            return [range_obj for range_obj in self.ranges if isinstance(range_obj, GitRange)]

        return []

    def has_git_ranges(self) -> bool:
        git_ranges = self.get_git_ranges()

        return git_ranges and len(git_ranges) > 0

    @model_validator(mode='before')
    def validate_ranges(cls, values):
        ranges = values.get('ranges', [])
        processed_ranges = []

        for range_data in ranges:
            range_type = range_data.get('type')

            if range_type == 'GIT':
                # Use GitRange model if the type is GIT
                processed_ranges.append(GitRange(**range_data))
            else:
                # Use the normal Range model for SEMVER or ECOSYSTEM
                processed_ranges.append(Range(**range_data))

        # Replace the original 'ranges' data with the processed list of objects
        values['ranges'] = processed_ranges

        return values
