from dataclasses import dataclass

from osvutils.core.filters.base import FilterCheck, BaseFilter, OptionCheck
from osvutils.types.osv import OSV


@dataclass
class DatabaseFilter(BaseFilter):
    """
        Class to store options for filtering entries by using database fields

        Attributes:
            prefix_is_cve (bool): Whether to filter out non-CVE entries
    """
    prefix_is_cve: bool = False

    def check(self, entry: OSV) -> FilterCheck:
        filter_check = FilterCheck()
        filter_check.update('prefix_is_cve', OptionCheck(self.prefix_is_cve, entry.get_cve_id() is not None))

        return filter_check
