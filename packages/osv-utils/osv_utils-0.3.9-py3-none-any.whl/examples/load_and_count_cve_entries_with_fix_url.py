from osvutils.core.loader import OSVDataLoader
from osvutils.core.filters.loader import LoaderFilters
from osvutils.core.filters.database import DatabaseFilter
from osvutils.core.filters.references import ReferencesFilter


loader = OSVDataLoader(
    filters=LoaderFilters(
        database_filter=DatabaseFilter(
            prefix_is_cve=True
        ),
        references_filter=ReferencesFilter(
            has_fix=True
        )
    )
)

loader()

print(f"{len(loader)} records loaded")
