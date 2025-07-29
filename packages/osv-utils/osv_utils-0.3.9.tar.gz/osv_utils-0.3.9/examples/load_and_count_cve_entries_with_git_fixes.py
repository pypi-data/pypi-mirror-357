from osvutils.core.loader import OSVDataLoader
from osvutils.core.filters.loader import LoaderFilters
from osvutils.core.filters.database import DatabaseFilter
from osvutils.core.filters.affected_packages import AffectedPackagesFilter


loader = OSVDataLoader(
    filters=LoaderFilters(
        database_filter=DatabaseFilter(
            prefix_is_cve=True
        ),
        affected_packages_filter=AffectedPackagesFilter(
            has_git_fixes=True
        )
    )
)

loader()

print(f"{len(loader)} records loaded")
print({eco: len(records) for eco, records in loader})
