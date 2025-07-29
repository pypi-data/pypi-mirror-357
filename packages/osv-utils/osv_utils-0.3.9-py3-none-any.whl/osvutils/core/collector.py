import zipfile
import logging

from pathlib import Path
from osvutils.utils.misc import get_ecosystems
from google.cloud import storage
from google.cloud.exceptions import NotFound

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
OSV_BUCKET_NAME = 'osv-vulnerabilities'


class OSVDataCollector:
    def __init__(self, data_path: str = '~/.osvutils/gs', verbose: bool = False):
        self.data_path = Path(data_path).expanduser()
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        self._gs_client = None
        self._osv_bucket = None

    @property
    def osv_bucket(self):
        """Get the Google Cloud Storage bucket."""
        if not self._osv_bucket:
            self._osv_bucket = self.gs_client.bucket(OSV_BUCKET_NAME)

        return self._osv_bucket

    @property
    def gs_client(self):
        """Get an anonymous Google Cloud Storage client."""
        if not self._gs_client:
            self._gs_client = storage.Client.create_anonymous_client()
        return self._gs_client

    def __call__(self, ecosystems: list = None) -> int:
        """
        Main entry point for collecting the OSV records.

        Args:
            ecosystems (list[str], optional): List of ecosystems to collect data for.

        Returns:
            int: Total number of records collected.
        """
        total_records = 0

        for ecosystem in get_ecosystems(ecosystems):
            total_records += self._collect_ecosystem(ecosystem.value)

        return total_records

    def _collect_ecosystem(self, ecosystem: str) -> int:
        """
        Collect the OSV records for the given ecosystem.

        Args:
            ecosystem (str): The name of the ecosystem to collect data for.

        Returns:
            int: Number of records collected
        """
        if self.verbose:
            logger.info(f"Collecting data for ecosystem: {ecosystem}")

        # get ecosystem blob
        object_name = f"{ecosystem}/all.zip"
        blob = self.osv_bucket.blob(object_name)

        blob_zip_file_path = Path(f"{self.data_path}/{ecosystem}.zip")
        ecosystem_data_path = Path(self.data_path / ecosystem)

        try:
            logger.info(f"Downloading {ecosystem} data...")
            blob.download_to_filename(blob_zip_file_path)

            # create output dir
            ecosystem_data_path.mkdir(exist_ok=True, parents=True)

            # unzip data
            with zipfile.ZipFile(blob_zip_file_path, "r") as zip_ref:
                zip_ref.extractall(ecosystem_data_path)
        except NotFound:
            logger.error(f"Blob {object_name} not found in bucket {OSV_BUCKET_NAME}.")
        except zipfile.BadZipFile:
            logger.error(f"The downloaded file {blob_zip_file_path} is not a valid zip file.")
        except Exception as e:
            logger.exception(f"An error occurred while collecting ecosystem data. {e}")
        finally:
            # Remove the zip file if it exists
            if blob_zip_file_path.exists():
                blob_zip_file_path.unlink()
                logger.info(f"Removed temporary file {blob_zip_file_path}.")

        return len(list(ecosystem_data_path.iterdir()))
