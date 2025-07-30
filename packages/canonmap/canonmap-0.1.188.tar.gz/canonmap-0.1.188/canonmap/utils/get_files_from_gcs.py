import os

from google.cloud import storage
from canonmap.logger import setup_logger

logger = setup_logger(__name__)


def get_files_from_gcs(
    gcp_service_account_json_path: str,
    bucket_name: str,
    prefix: str,
    artifacts_local_path: str,
    sync_strategy: str = "none"
):
    replace_all = sync_strategy == "all"
    replace_existing = sync_strategy == "existing"

    if not os.path.exists(artifacts_local_path):
        os.makedirs(artifacts_local_path)
    elif not os.path.isdir(artifacts_local_path):
        raise NotADirectoryError(f"{artifacts_local_path} is not a directory")

    if replace_all:
        for filename in os.listdir(artifacts_local_path):
            file_path = os.path.join(artifacts_local_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.info("Deleted local artifact: %s", file_path)

    client = storage.Client.from_service_account_json(gcp_service_account_json_path)
    bucket = client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)

    downloaded_files = []
    for blob in blobs:
        filename = blob.name.split('/')[-1]
        local_path = os.path.join(artifacts_local_path, filename)

        if os.path.exists(local_path):
            if replace_existing:
                logger.info("Replacing existing file with GCP artifact: %s", local_path)
                blob.download_to_filename(local_path)
            else:
                logger.info("Skipping existing file (preserving local): %s", local_path)
                continue
        else:
            logger.info("Downloading new artifact from GCP: %s", local_path)
            blob.download_to_filename(local_path)

        downloaded_files.append(local_path)
    return downloaded_files