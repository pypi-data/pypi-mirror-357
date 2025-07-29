
from osvutils.core.collector import OSVDataCollector

collector = OSVDataCollector(verbose=True)
count = collector()

print(f"Total records collected: {count}")
