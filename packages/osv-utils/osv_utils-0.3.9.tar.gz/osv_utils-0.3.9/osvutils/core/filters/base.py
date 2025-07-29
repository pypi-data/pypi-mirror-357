from typing import Dict

from abc import abstractmethod
from dataclasses import dataclass, field
from osvutils.types.osv import OSV


@dataclass
class OptionCheck:
    apply: bool = False
    value: bool = False


@dataclass
class FilterCheck:
    checks: Dict[str, OptionCheck] = field(default_factory=dict)

    def __call__(self):
        # get the set of options that apply
        to_apply = [v.value for v in self.checks.values() if v.apply]

        if not to_apply:
            return True

        return all(to_apply)

    def update(self, name: str, check: OptionCheck):
        self.checks[name] = check

    def to_dict(self):
        return {k: v.value for k, v in self.checks.items() if v.apply}


@dataclass
class BaseFilter:
    """
        Base class for filters
    """

    @abstractmethod
    def check(self, entry: OSV) -> FilterCheck:
        """
            Check if the given entry passes the filter
        """
        return FilterCheck()


@dataclass
class FiltersEvaluator:
    filters: Dict[str, FilterCheck] = field(default_factory=dict)

    def __call__(self):
        return all(check() for check in self.filters.values())

    def update(self, name: str, check: FilterCheck):
        self.filters[name] = check

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.filters.items()}
