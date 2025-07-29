from dataclasses import dataclass

from osvutils.core.filters.base import FilterCheck, BaseFilter, OptionCheck
from osvutils.types.osv import OSV


@dataclass
class ReferencesFilter(BaseFilter):
    """
        Class to store options for filtering entries by using references fields

        Attributes:
            has_fix (bool): Whether to filter out entries with urls to fixes
    """
    has_fix: bool = False

    def check(self, entry: OSV) -> FilterCheck:
        filter_check = FilterCheck()
        filter_check.update('has_fix', OptionCheck(self.has_fix, entry.has_fix_refs()))

        return filter_check
