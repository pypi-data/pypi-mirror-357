import json

from collections import defaultdict
from osvutils.core.loader import OSVDataLoader
from osvutils.core.filters.loader import LoaderFilters
from osvutils.core.filters.database import DatabaseFilter

loader = OSVDataLoader(
    ecosystems=['OSS-Fuzz']
)

loader()

print(f"{len(loader)} records loaded")

#cve_count_per_ecosystem = {ecosystem: len(records) for ecosystem, records in loader}
#print(cve_count_per_ecosystem)

vectors = defaultdict(int)

for ecosystem, records in loader:
    for _id, record in records.items():
        if record.affected:
            for affected in record.affected:
                if affected.severity:
                    vectors[affected.severity.score.vector] += 1

print(vectors)
