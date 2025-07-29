
from tqdm import tqdm
from pathlib import Path
from typing import List

from osvutils.utils.misc import load_osv_file, get_ecosystems
from osvutils.types.osv import OSV
from osvutils.core.filters.loader import LoaderFilters


class OSVDataLoader:
    def __init__(self, data_path: str = '~/.osvutils/gs', verbose: bool = False, ecosystems: List[str] = None,
                 filters: LoaderFilters = None):
        self.data_path = Path(data_path).expanduser()
        self.verbose = verbose
        self.ecosystems = get_ecosystems(ecosystems)
        self.filters = filters

        if filters is None:
            self.filters = LoaderFilters()

        # check if the data path exists
        if not self.data_path.exists():
            raise FileNotFoundError(f"{self.data_path} not found")

        self.records = {k.value: {} for k in self.ecosystems}

    def __iter__(self):
        """
        Makes the loader iterable over the records.
        """
        return iter(self.records.items())

    def __len__(self):
        return sum([len(v) for v in self.records.values()])

    def __call__(self):
        """
            Main entry point for loading the OSV records.
        """

        for ecosystem in tqdm(self.ecosystems, desc="Loading ecosystems"):
            self._process_ecosystem(ecosystem.value)

    def _process_ecosystem(self, ecosystem: str):
        ecosystem_files = self.get_ecosystem_files(ecosystem)

        if ecosystem_files:
            if ecosystem not in self.records:
                self.records[ecosystem] = {}

            for file in tqdm(ecosystem_files, desc=f"Loading {ecosystem} entries", leave=False):
                if file.suffix != '.json':
                    continue

                if file.stem not in self.records[ecosystem]:
                    osv_data = load_osv_file(file)
                    osv_object = OSV(**osv_data)
                    filters_eval = self.filters(osv_object)

                    if filters_eval():
                        self.records[ecosystem][file.stem] = osv_object

    def get_ecosystem_files(self, ecosystem: str) -> List[Path]:
        ecosystem_path = self.data_path / ecosystem

        if ecosystem_path.exists():
            return list(ecosystem_path.iterdir())

        if self.verbose:
            print(f"{ecosystem_path} not found")

        return []
