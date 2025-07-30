import os
import json

from google.cloud import storage
from google.api_core.exceptions import Forbidden, NotFound

from canonmap.logger import setup_logger

logger = setup_logger(__name__)

def validate_service_account_path(gcp_service_account_json_path: str):
    logger.info("Validating service account JSON file path: %s", gcp_service_account_json_path)
    if not os.path.exists(gcp_service_account_json_path):
        logger.error("Service account JSON file not found at %s", gcp_service_account_json_path)
        raise FileNotFoundError(f"Service account JSON file not found at {gcp_service_account_json_path}")
    logger.success(f"Service account JSON file found at {gcp_service_account_json_path}")


def validate_bucket_config(self, troubleshooting: bool = False):
    logger.info("Attempting to access bucket: %s", self.gcp_bucket_name)
    client = storage.Client.from_service_account_json(self.gcp_service_account_json_path)
    
    try:
        bucket = client.get_bucket(self.gcp_bucket_name)
        logger.success("Successfully accessed GCP bucket: %s", self.gcp_bucket_name)
    except Forbidden as e:
        logger.error("Permission denied accessing GCP bucket '%s': %s", self.gcp_bucket_name, e)
        if troubleshooting:
            logger.info("Troubleshooting mode enabled - generating remediation script")
            logger.warning(
                "Permission denied accessing GCP bucket '%s': %s",
                self.gcp_bucket_name,
                e
            )
            # Load service account info
            logger.info("Loading service account information for troubleshooting")
            try:
                with open(self.gcp_service_account_json_path) as f:
                    sa_info = json.load(f)
                sa_email = sa_info.get("client_email", "<SERVICE_ACCOUNT_EMAIL>")
                project_id = sa_info.get("project_id", "<PROJECT_ID>")
                logger.info("Service account email: %s", sa_email)
                logger.info("Project ID: %s", project_id)
            except Exception as load_error:
                logger.warning("Failed to load service account info: %s", load_error)
                sa_email = "<SERVICE_ACCOUNT_EMAIL>"
                project_id = "<PROJECT_ID>"

            # Prepare troubleshooting directory and script
            dir_path = "canonmap_troubleshooting"
            logger.info("Creating troubleshooting directory: %s", dir_path)
            os.makedirs(dir_path, exist_ok=True)
            script_name = f"permission_{self.gcp_bucket_name}.sh"
            script_path = os.path.join(dir_path, script_name)
            logger.info("Generating troubleshooting script: %s", script_path)

            # Bash script content
            script_contents = f"""#!/usr/bin/env bash
# Troubleshooting script for GCP bucket permissions
echo "Checking for gcloud CLI..."
if ! command -v gcloud &> /dev/null; then
echo "gcloud CLI not found. Installing Google Cloud SDK..."
curl https://sdk.cloud.google.com | bash
exec -l "$SHELL"
fi

echo "Authenticating with Google Cloud..."
gcloud auth login

echo "Setting active project to {project_id}..."
gcloud config set project {project_id}

# Grant bucket metadata viewing
gcloud projects add-iam-policy-binding {project_id} \\
--member="serviceAccount:{sa_email}" \\
--role="roles/storage.bucketViewer"

# Grant object viewing
gcloud projects add-iam-policy-binding {project_id} \\
--member="serviceAccount:{sa_email}" \\
--role="roles/storage.objectViewer"

echo "Done! You should now have access to the bucket {self.gcp_bucket_name}."
"""

            # Write (overwrite) the script file
            logger.info("Writing troubleshooting script to file")
            with open(script_path, "w") as file:
                file.write(script_contents)
            # Make sure the script is executable
            os.chmod(script_path, 0o755)
            logger.success("Troubleshooting script created and made executable")

            logger.info("Troubleshooting script saved to %s", script_path)
            logger.info("Run it with:")
            logger.info(f"\n\n\n{'#' * 37}  GCP BUCKET PERMISSION COMMANDS  {'#' * 37}\n\nchmod +x {script_path}\n{script_path}\n\n{'#' * 111}\n\n\n")
            logger.warning(
                "IAM changes may take 2-3 minutes to propagate. Please wait before retrying access."
            )
            raise PermissionError(
                f"Access denied to bucket '{self.gcp_bucket_name}'. "
                "A troubleshooting script has been saved; please review and run it."
            )
        else:
            logger.error("Troubleshooting mode disabled - cannot generate remediation instructions")
            raise PermissionError(
                f"Access denied to bucket '{self.gcp_bucket_name}'. "
                "Enable troubleshooting to generate remediation instructions."
            )
    except NotFound:
        logger.error("GCP bucket '%s' not found", self.gcp_bucket_name)
        if getattr(self, "auto_create_bucket", False):
            logger.info("Auto-create bucket enabled - creating bucket: %s", self.gcp_bucket_name)
            try:
                bucket = client.create_bucket(self.gcp_bucket_name)
                logger.success("Successfully created GCP bucket: %s", self.gcp_bucket_name)
            except Forbidden as e:
                logger.error("Permission denied creating GCP bucket '%s': %s", self.gcp_bucket_name, e)
                if troubleshooting:
                    # reuse troubleshooting script generation logic
                    logger.info("Troubleshooting mode enabled - generating remediation script for bucket creation")
                    # Load service account info
                    try:
                        with open(self.gcp_service_account_json_path) as f:
                            sa_info = json.load(f)
                        sa_email = sa_info.get("client_email", "<SERVICE_ACCOUNT_EMAIL>")
                        project_id = sa_info.get("project_id", "<PROJECT_ID>")
                    except Exception as load_error:
                        sa_email = "<SERVICE_ACCOUNT_EMAIL>"
                        project_id = "<PROJECT_ID>"
                    dir_path = "canonmap_troubleshooting"
                    os.makedirs(dir_path, exist_ok=True)
                    script_name = f"create_bucket_{self.gcp_bucket_name}.sh"
                    script_path = os.path.join(dir_path, script_name)
                    script_contents = f"""#!/usr/bin/env bash
# Troubleshooting script for creating GCP bucket
echo "Checking for gcloud CLI..."
if ! command -v gcloud &> /dev/null; then
  echo "gcloud CLI not found. Installing Google Cloud SDK..."
  curl https://sdk.cloud.google.com | bash
  exec -l "$SHELL"
fi

echo "Authenticating with Google Cloud..."
gcloud auth login

echo "Setting active project to {project_id}..."
gcloud config set project {project_id}

echo "Creating bucket {self.gcp_bucket_name}..."
gcloud storage buckets create gs://{self.gcp_bucket_name} --project={project_id}

echo "Done! Bucket '{self.gcp_bucket_name}' should now exist."
"""
                    if getattr(self, "auto_create_bucket_prefix", False):
                        logger.info("Auto-create bucket prefix enabled - including prefix creation in troubleshooting script")
                        script_contents += f"""

# Auto-create prefix marker for '{self.gcp_bucket_prefix}'
echo "Creating prefix marker for prefix '{self.gcp_bucket_prefix}'..."
touch .keep
gcloud storage cp .keep gs://{self.gcp_bucket_name}/{self.gcp_bucket_prefix.rstrip('/')}/.keep
echo "Prefix marker created."
"""
                    with open(script_path, "w") as file:
                        file.write(script_contents)
                    os.chmod(script_path, 0o755)
                    logger.success("Troubleshooting script for bucket creation saved to %s", script_path)
                    logger.warning("IAM changes may take 2-3 minutes to propagate. Please wait before retrying.")
                    logger.info("Run it with:")
                    logger.info(f"\n\n\n{'#' * 37}  GCP BUCKET CREATION COMMANDS  {'#' * 37}\n\nchmod +x {script_path}\n{script_path}\n\n{'#' * 107}\n\n\n")
                    raise PermissionError(
                        f"Failed to create bucket '{self.gcp_bucket_name}'. "
                        "A troubleshooting script has been saved; please review and run it."
                    )
                else:
                    raise PermissionError(
                        f"Permission denied creating bucket '{self.gcp_bucket_name}'. "
                        "Enable troubleshooting to generate remediation instructions."
                    )
        else:
            raise FileNotFoundError(f"GCP bucket '{self.gcp_bucket_name}' not found.")

    # Only validate prefix if it was passed in
    if self.gcp_bucket_prefix:
        logger.info("Validating bucket prefix: %s", self.gcp_bucket_prefix)
        # list_blobs is lazy; avoid loading entire list if not needed
        blob_iterator = bucket.list_blobs(prefix=self.gcp_bucket_prefix)
        if not any(blob.name.startswith(self.gcp_bucket_prefix.rstrip("/") + "/") for blob in blob_iterator):
            if getattr(self, "auto_create_bucket_prefix", False):
                logger.info("Auto-create bucket prefix enabled - creating prefix marker for '%s'", self.gcp_bucket_prefix)
                try:
                    marker_blob = bucket.blob(f"{self.gcp_bucket_prefix.rstrip('/')}/.keep")
                    marker_blob.upload_from_string("", content_type="application/octet-stream")
                    logger.success("Successfully created prefix '%s' in bucket '%s'", self.gcp_bucket_prefix, self.gcp_bucket_name)
                except Forbidden as e:
                    logger.error(
                        "Permission denied creating prefix marker for '%s' in bucket '%s': %s",
                        self.gcp_bucket_prefix,
                        self.gcp_bucket_name,
                        e
                    )
                    if troubleshooting:
                        logger.info("Troubleshooting mode enabled - generating remediation script for prefix creation")
                        # Load service account info
                        try:
                            with open(self.gcp_service_account_json_path) as f:
                                sa_info = json.load(f)
                            sa_email = sa_info.get("client_email", "<SERVICE_ACCOUNT_EMAIL>")
                            project_id = sa_info.get("project_id", "<PROJECT_ID>")
                        except Exception:
                            sa_email = "<SERVICE_ACCOUNT_EMAIL>"
                            project_id = "<PROJECT_ID>"
                        dir_path = "canonmap_troubleshooting"
                        os.makedirs(dir_path, exist_ok=True)
                        script_name = f"create_prefix_{self.gcp_bucket_name}_{self.gcp_bucket_prefix.rstrip('/')}.sh"
                        script_path = os.path.join(dir_path, script_name)
                        script_contents = f"""#!/usr/bin/env bash
# Troubleshooting script for GCP bucket prefix permissions
echo "Checking for gcloud CLI..."
if ! command -v gcloud &> /dev/null; then
  echo "gcloud CLI not found. Installing Google Cloud SDK..."
  curl https://sdk.cloud.google.com | bash
  exec -l "$SHELL"
fi

echo "Authenticating with Google Cloud..."
gcloud auth login

echo "Setting active project to {project_id}..."
gcloud config set project {project_id}

# Grant object creation
gcloud projects add-iam-policy-binding {project_id} \\
  --member="serviceAccount:{sa_email}" \\
  --role="roles/storage.objectCreator"

echo "Uploading prefix marker..."
touch .keep
gcloud storage cp .keep gs://{self.gcp_bucket_name}/{self.gcp_bucket_prefix.rstrip('/')}/.keep

echo "Done! Prefix marker should now exist."
"""
                        with open(script_path, "w") as file:
                            file.write(script_contents)
                        os.chmod(script_path, 0o755)
                        logger.success("Troubleshooting script for prefix creation saved to %s", script_path)
                        logger.warning("IAM changes may take 2-3 minutes to propagate. Please wait before retrying.")
                        logger.info("Run it with:")
                        logger.info(f"\n\n\n{'#' * 37}  GCP PREFIX CREATION COMMANDS  {'#' * 37}\n\nchmod +x {script_path}\n{script_path}\n\n{'#' * 111}\n\n\n")
                        raise PermissionError(
                            f"Failed to create prefix marker '{self.gcp_bucket_prefix}' in bucket '{self.gcp_bucket_name}'. "
                            "A troubleshooting script has been saved; please review and run it."
                        )
                    else:
                        raise PermissionError(
                            f"Permission denied creating prefix marker '{self.gcp_bucket_prefix}' in bucket '{self.gcp_bucket_name}'. "
                            "Enable troubleshooting to generate remediation instructions."
                        )
            else:
                raise FileNotFoundError(
                    f"No objects found in bucket '{self.gcp_bucket_name}' with prefix '{self.gcp_bucket_prefix}'."
                )
        logger.success("Bucket prefix validation successful: %s", self.gcp_bucket_prefix)
    else:
        logger.info("No bucket prefix specified - skipping prefix validation")
