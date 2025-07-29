from enum import Enum

from typing import Optional
from pydantic import BaseModel


class EcosystemType(Enum):
    """
        See https://google.github.io/osv.dev/data/#covered-ecosystems
    """
    ALMALINUX = 'AlmaLinux'
    ALPINE = 'Alpine'
    ANDROID = 'Android'
    # BIOCONDUCTOR = 'Bioconductor'  # defined as ecosystem but not in the storage
    BITNAMI = 'Bitnami'
    CHAINGUARD = 'Chainguard'
    # CONAN_CENTER = 'Conan Center'  # defined as ecosystem but not in the storage
    CRAN = 'CRAN'
    CRATES = 'crates.io'
    DEBIAN = 'Debian'
    DWF = 'DWF'  # Not defined as ecosystem but in the storage, probably for future use
    # GHC = 'GHC'  # defined as ecosystem but not in the storage
    GIT = 'GIT'
    GITHUB_ACTIONS = 'GitHub Actions'
    GO = 'Go'
    GSD = 'GSD'  # Defined as database (Global Security Database) in the storage
    HACKAGE = 'Hackage'
    HEX = 'Hex'
    LINUX = 'Linux'
    # MAGEIA = 'Mageia'  # defined as a database (MGASA) and ecosystem but not in the storage
    MAVEN = 'Maven'
    NPM = 'npm'
    NUGET = 'NuGet'
    OSS_FUZZ = 'OSS-Fuzz'
    OPENSUSE = 'openSUSE'
    PACKAGIST = 'Packagist'
    # PHOTON_OS = 'Photon OS'  # defined as database (PHSA) and ecosystem but not in the storage
    PUB = 'Pub'
    PYPI = 'PyPI'
    # RED_HAT = 'Red Hat'  # defined as a database (RHSA/RHBA/RHEA) and ecosystem but not in the storage
    ROCKY_LINUX = 'Rocky Linux'
    RUBYGEMS = 'RubyGems'
    SUSE = 'SUSE'
    SWIFTURL = 'SwiftURL'
    UBUNTU = 'Ubuntu'
    WOLFI = 'Wolfi'
    # JAVASCRIPT = 'JavaScript'  # Not defined as ecosystem but in the storage, probably for future use
    # UVI = 'UVI'  # Not defined as ecosystem but in the storage, probably for future use


# Ecosystem model to store ecosystem and version separately
class Ecosystem(BaseModel):
    ecosystem: EcosystemType
    version: Optional[str] = None  # Version is optional
