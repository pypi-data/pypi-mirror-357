from dataclasses import dataclass, field

from osvutils.core.filters.base import FiltersEvaluator
from osvutils.core.filters.database import DatabaseFilter
from osvutils.core.filters.affected_packages import AffectedPackagesFilter
from osvutils.core.filters.references import ReferencesFilter
from osvutils.types.osv import OSV


@dataclass
class LoaderFilters:
    """
        Class to store options for filtering entries by using loader fields

        Attributes:
            database_filter (DatabaseFilter): Filter for database fields
            affected_packages_filter (AffectedPackagesFilter): Filter for affected packages fields
            references_filter (ReferencesFilter): Filter for references fields
    """
    database_filter: DatabaseFilter = field(default_factory=DatabaseFilter)
    affected_packages_filter: AffectedPackagesFilter = field(default_factory=AffectedPackagesFilter)
    references_filter: ReferencesFilter = field(default_factory=ReferencesFilter)

    def __call__(self, entry: OSV) -> FiltersEvaluator:
        filters_eval = FiltersEvaluator()
        filters_eval.update('database_filter', self.database_filter.check(entry))
        filters_eval.update('affected_packages_filter', self.affected_packages_filter.check(entry))
        filters_eval.update('references_filter', self.references_filter.check(entry))

        return filters_eval
