import re
import json
import requests

from pydantic import AnyUrl

from pathlib import Path
from typing import List, Union, Tuple

from osvutils.types.alias import AliasType
from osvutils.types.ecosystem import EcosystemType
from osvutils.utils.patterns import CVE_REGEX


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def get_oss_fuzz_issue_id(url: Union[str, AnyUrl]) -> Tuple[str, str]:
    """
    Extracts the issue URL and issue ID from a given OSS-Fuzz or Chromium issue tracker URL.

    This function handles two known host formats:
    - For Chromium issues (`bugs.chromium.org`), it attempts to extract the final redirected URL
      containing the actual issue ID using a regex match on the response body.
    - For OSS-Fuzz issues (`issues.oss-fuzz.com`), it extracts the issue ID from the query component of the URL.

    Args:
        url (Union[str, AnyUrl]): The URL to extract the issue ID from. Can be a raw string or a pydantic `AnyUrl` object.

    Returns:
        Tuple[str, str]: A tuple containing:
            - The resolved issue URL (either the original or the redirected one),
            - The extracted issue ID as a string.

    Raises:
        Exception: If the URL's host is not recognized (i.e., not `bugs.chromium.org` or `issues.oss-fuzz.com`).

    Notes:
        - Uses a hardcoded User-Agent header to mimic a browser request.
        - Relies on regex to find redirect URLs in Chromium issue pages.
    """
    url_obj = AnyUrl(url) if isinstance(url, str) else url

    if url_obj.host == "bugs.chromium.org":
        response = requests.get(url, headers=headers, allow_redirects=True)
        match = re.search(r'const\s+url\s*=\s*"([^"]+)"', response.text)

        if match:
            redirect_url = match.group(1)
            print(f"Extracted redirect URL: {redirect_url}")
            return redirect_url, redirect_url.split("/")[-1]
        elif url_obj.query:
            print("Redirect URL not found in response. Fallback to default issue id.")
            return url, url_obj.query.split("=")[-1]
        else:
            raise ValueError("Could not extract redirect URL nor the issue ID.")

    elif url_obj.host == "issues.oss-fuzz.com":
        return url, url_obj.query.split("/")[-1]
    else:
        raise Exception(f"Unknown host: {url_obj.host}")


def load_osv_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    if path.suffix != '.json':
        raise ValueError(f"{path} is not a json file")
    if path.stat().st_size == 0:
        raise ValueError(f"{path} is empty")

    # read contents of the file
    with path.open('r') as f:
        osv_data = json.load(f)

    return osv_data


def get_ecosystems(ecosystems: list = None) -> List[EcosystemType]:
    ecosystem_list = []
    ecosystem_types = [ecosystem.value for ecosystem in EcosystemType]

    if ecosystems:
        for ecosystem in ecosystems:
            if ecosystem not in ecosystem_types:
                print(f"Invalid ecosystem: {ecosystem}")
                continue

            ecosystem_list.append(EcosystemType(ecosystem))

        if not ecosystem_list:
            print("No valid ecosystems found")
    else:
        ecosystem_list = list(EcosystemType)

    return ecosystem_list


def get_alias_type(value: str) -> AliasType:
    if re.search(CVE_REGEX, value):
        return AliasType.CVE

    return AliasType.Other


def is_cve_id(value: str) -> bool:
    return re.search(CVE_REGEX, value) is not None


def get_cve_match(value: str) -> str | None:
    match = re.search(CVE_REGEX, value)
    return match.group() if match else None
