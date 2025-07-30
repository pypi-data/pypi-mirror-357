import os
import json
import re
import traceback

from google.cloud import storage
from google.api_core.exceptions import Forbidden, NotFound

from canonmap.logger import setup_logger

logger = setup_logger(__name__)


def validate_artifacts(
    artifacts_local_path: str,
    artifacts_gcp_sync_strategy: str,
    artifacts_gcp_service_account_json_path: str,
    artifacts_gcp_bucket_name: str,
    artifacts_gcp_bucket_prefix: str,
    artifacts_gcp_auto_create_bucket: bool,
    artifacts_gcp_auto_create_bucket_prefix: bool,
    troubleshooting: bool = False):
    """
    Validate artifacts configuration and connectivity.
    
    Args:
        artifacts_local_path: Local directory for artifacts storage.
        artifacts_gcp_sync_strategy: Sync strategy ("none", "missing", "overwrite", "refresh").
        artifacts_gcp_service_account_json_path: Path to GCP service account JSON.
        artifacts_gcp_bucket_name: GCP bucket name for artifacts storage.
        artifacts_gcp_bucket_prefix: Bucket prefix (subdirectory) for artifacts.
        artifacts_gcp_auto_create_bucket: Auto-create the GCP bucket if missing.
        artifacts_gcp_auto_create_bucket_prefix: Auto-create the bucket prefix.
        troubleshooting: If True, generate troubleshooting scripts on error.
        
    Raises:
        FileNotFoundError, PermissionError: On validation failures.
    """
    try:
        # === Strategy validation ===
        if artifacts_gcp_sync_strategy not in ["none", "missing", "overwrite", "refresh"]:
            raise ValueError(f"Invalid GCP sync strategy: {artifacts_gcp_sync_strategy}")

        # === Local path validation ===
        if not os.path.isdir(artifacts_local_path):
            if troubleshooting:
                logger.warning("Local artifacts path does not exist: %s", artifacts_local_path)
                os.makedirs(artifacts_local_path, exist_ok=True)
                logger.success("Created missing local artifacts directory: %s", artifacts_local_path)
            else:
                raise FileNotFoundError(f"Artifacts local path does not exist: {artifacts_local_path}")
        else:
            logger.success("Artifacts local path exists: %s", artifacts_local_path)

        # === Skip if sync strategy is none ===
        if artifacts_gcp_sync_strategy == "none":
            logger.info("GCP sync strategy is 'none'; skipping GCP validation")
            return

        # === Handle "refresh" strategy - clear local and sync from GCP ===
        if artifacts_gcp_sync_strategy == "refresh":
            logger.info("Artifacts GCP sync strategy is 'refresh' - clearing local directory and syncing from GCP")
            
            # Check if GCP has any artifacts
            gcp_has_artifacts = False
            try:
                client = storage.Client.from_service_account_json(artifacts_gcp_service_account_json_path)
                bucket = client.get_bucket(artifacts_gcp_bucket_name)
                blobs = list(bucket.list_blobs(prefix=artifacts_gcp_bucket_prefix))
                gcp_has_artifacts = len(blobs) > 0
                logger.info("GCP has %d artifacts in prefix '%s'", len(blobs), artifacts_gcp_bucket_prefix)
            except Exception as e:
                logger.warning("Could not check GCP artifacts before clearing local: %s", e)
                gcp_has_artifacts = False
            
            # Check if local has artifacts
            local_has_artifacts = os.path.isdir(artifacts_local_path) and any(
                os.path.isfile(os.path.join(artifacts_local_path, f)) 
                for f in os.listdir(artifacts_local_path)
            )
            
            if not gcp_has_artifacts and local_has_artifacts:
                logger.warning("GCP has no artifacts but local artifacts exist. Uploading local artifacts to GCP.")
                if troubleshooting:
                    try:
                        # Upload local artifacts to GCP
                        for fname in os.listdir(artifacts_local_path):
                            fpath = os.path.join(artifacts_local_path, fname)
                            if os.path.isfile(fpath):
                                blob_name = os.path.join(artifacts_gcp_bucket_prefix, fname) if artifacts_gcp_bucket_prefix else fname
                                blob = bucket.blob(blob_name)
                                blob.upload_from_filename(fpath)
                                logger.success("Uploaded artifact to GCP: %s", fpath)
                        logger.success("Local artifacts uploaded to GCP successfully")
                        gcp_has_artifacts = True
                    except Exception as e:
                        logger.error("Failed to upload local artifacts to GCP: %s", e)
                        raise FileNotFoundError(f"Failed to upload local artifacts to GCP: {e}")
                else:
                    raise FileNotFoundError("GCP has no artifacts and local artifacts exist, but troubleshooting is disabled")
            
            # Clear local directory and download from GCP
            if gcp_has_artifacts:
                if os.path.isdir(artifacts_local_path):
                    for fname in os.listdir(artifacts_local_path):
                        fpath = os.path.join(artifacts_local_path, fname)
                        if os.path.isfile(fpath):
                            os.remove(fpath)
                            logger.info("Deleted existing artifact: %s", fpath)
                else:
                    os.makedirs(artifacts_local_path)
                    logger.info("Created artifacts directory: %s", artifacts_local_path)
                
                # Download artifacts from GCP
                try:
                    blobs = list(bucket.list_blobs(prefix=artifacts_gcp_bucket_prefix))
                    for blob in blobs:
                        # Compute the relative path to preserve folder structure
                        rel_path = os.path.relpath(blob.name, artifacts_gcp_bucket_prefix) if artifacts_gcp_bucket_prefix else blob.name
                        dest = os.path.join(artifacts_local_path, rel_path)
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        blob.download_to_filename(dest)
                        logger.success("Downloaded artifact from GCP: %s", dest)
                    logger.success("Successfully synced %d artifacts from GCP", len(blobs))
                except Exception as e:
                    logger.error("Failed to download artifacts from GCP: %s", e)
                    if troubleshooting:
                        raise FileNotFoundError(f"Failed to download artifacts from GCP: {e}")
                    else:
                        raise
            else:
                logger.warning("No artifacts found in GCP and no local artifacts to upload. Creating empty artifacts directory.")
                os.makedirs(artifacts_local_path, exist_ok=True)

        # === Handle "missing" strategy - download only missing artifacts from GCP ===
        elif artifacts_gcp_sync_strategy == "missing":
            logger.info("Artifacts GCP sync strategy is 'missing' - downloading only missing artifacts from GCP")
            
            # Ensure local directory exists
            os.makedirs(artifacts_local_path, exist_ok=True)
            
            try:
                client = storage.Client.from_service_account_json(artifacts_gcp_service_account_json_path)
                bucket = client.get_bucket(artifacts_gcp_bucket_name)
                blobs = list(bucket.list_blobs(prefix=artifacts_gcp_bucket_prefix))
                
                if not blobs:
                    logger.warning("No artifacts found in GCP prefix '%s'", artifacts_gcp_bucket_prefix)
                    return
                
                # Get list of existing local files
                local_files = set()
                if os.path.isdir(artifacts_local_path):
                    local_files = set(os.listdir(artifacts_local_path))
                
                # Download only missing artifacts
                downloaded_count = 0
                for blob in blobs:
                    rel_path = os.path.relpath(blob.name, artifacts_gcp_bucket_prefix) if artifacts_gcp_bucket_prefix else blob.name
                    dest = os.path.join(artifacts_local_path, rel_path)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    if not os.path.exists(dest):
                        blob.download_to_filename(dest)
                        logger.success("Downloaded missing artifact from GCP: %s", dest)
                        downloaded_count += 1
                    else:
                        logger.debug("Artifact already exists locally: %s", rel_path)
                
                if downloaded_count > 0:
                    logger.success("Successfully downloaded %d missing artifacts from GCP", downloaded_count)
                else:
                    logger.info("All artifacts already exist locally - no downloads needed")
                    
            except Exception as e:
                logger.error("Failed to sync artifacts from GCP: %s", e)
                if troubleshooting:
                    raise FileNotFoundError(f"Failed to sync artifacts from GCP: {e}")
                else:
                    raise

        # === Handle "overwrite" strategy - download all artifacts from GCP, overwrite local ===
        elif artifacts_gcp_sync_strategy == "overwrite":
            logger.info("Artifacts GCP sync strategy is 'overwrite' - downloading all artifacts from GCP, overwriting local")
            
            # Ensure local directory exists
            os.makedirs(artifacts_local_path, exist_ok=True)
            
            try:
                client = storage.Client.from_service_account_json(artifacts_gcp_service_account_json_path)
                bucket = client.get_bucket(artifacts_gcp_bucket_name)
                blobs = list(bucket.list_blobs(prefix=artifacts_gcp_bucket_prefix))
                
                if not blobs:
                    logger.warning("No artifacts found in GCP prefix '%s'", artifacts_gcp_bucket_prefix)
                    return
                
                # Download all artifacts from GCP (overwriting local files)
                downloaded_count = 0
                for blob in blobs:
                    rel_path = os.path.relpath(blob.name, artifacts_gcp_bucket_prefix) if artifacts_gcp_bucket_prefix else blob.name
                    dest = os.path.join(artifacts_local_path, rel_path)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    blob.download_to_filename(dest)
                    logger.success("Downloaded artifact from GCP: %s", dest)
                    downloaded_count += 1
                
                logger.success("Successfully downloaded %d artifacts from GCP (overwriting local files)", downloaded_count)
                    
            except Exception as e:
                logger.error("Failed to sync artifacts from GCP: %s", e)
                if troubleshooting:
                    raise FileNotFoundError(f"Failed to sync artifacts from GCP: {e}")
                else:
                    raise

        # === GCP bucket/prefix validation ===
        try:
            logger.info("Connecting to GCP bucket: %s", artifacts_gcp_bucket_name)
            client = storage.Client.from_service_account_json(artifacts_gcp_service_account_json_path)
            bucket = client.get_bucket(artifacts_gcp_bucket_name)
            logger.success("Accessed GCP bucket: %s", artifacts_gcp_bucket_name)

            if artifacts_gcp_bucket_prefix:
                logger.info("Validating GCP prefix: %s", artifacts_gcp_bucket_prefix)
                blobs = list(bucket.list_blobs(prefix=artifacts_gcp_bucket_prefix))
                has_prefix = any(
                    blob.name.startswith(artifacts_gcp_bucket_prefix.rstrip("/") + "/") for blob in blobs
                )

                if not has_prefix:
                    if artifacts_gcp_auto_create_bucket_prefix and troubleshooting:
                        marker_blob = bucket.blob(f"{artifacts_gcp_bucket_prefix.rstrip('/')}/.keep")
                        marker_blob.upload_from_string("", content_type="application/octet-stream")
                        logger.success("Created prefix marker at: %s", f"{artifacts_gcp_bucket_prefix}/.keep")
                    elif not artifacts_gcp_auto_create_bucket_prefix:
                        raise FileNotFoundError(
                            f"No objects found with prefix '{artifacts_gcp_bucket_prefix}' "
                            f"in bucket '{artifacts_gcp_bucket_name}'"
                        )
                    else:
                        logger.warning("Prefix marker not found and creation skipped")
                else:
                    logger.success("GCP bucket prefix is valid: %s", artifacts_gcp_bucket_prefix)

        except Forbidden as e:
            logger.error("Permission denied accessing GCP bucket/prefix: %s", e)
            if troubleshooting:
                # Generate troubleshooting script for GCP permissions
                dir_path = "canonmap_troubleshooting"
                os.makedirs(dir_path, exist_ok=True)
                sanitized_bucket = re.sub(r'\W+', '_', artifacts_gcp_bucket_name)
                sanitized_prefix = re.sub(r'\W+', '_', artifacts_gcp_bucket_prefix or "root")
                script_name = f"fix_artifacts_gcp_permissions_{sanitized_bucket}_{sanitized_prefix}.sh"
                script_path = os.path.join(dir_path, script_name)
                
                # Extract service account email
                try:
                    with open(artifacts_gcp_service_account_json_path) as f:
                        sa_info = json.load(f)
                    sa_email = sa_info.get("client_email", "<SERVICE_ACCOUNT_EMAIL>")
                    project_id = sa_info.get("project_id", "<PROJECT_ID>")
                except Exception:
                    sa_email = "<SERVICE_ACCOUNT_EMAIL>"
                    project_id = "<PROJECT_ID>"
                
                script_contents = f"""#!/usr/bin/env bash
# Script to fix GCP storage permissions for artifacts bucket '{artifacts_gcp_bucket_name}' and prefix '{artifacts_gcp_bucket_prefix}'

set -e  # Exit on any error

echo "=========================================="
echo "GCP Artifacts Storage Permissions Fix Script"
echo "=========================================="
echo ""

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Installing Google Cloud SDK..."
    echo ""
    echo "Please install the Google Cloud SDK:"
    echo "  https://cloud.google.com/sdk/docs/install"
    echo ""
    echo "Or run this command:"
    echo "  curl https://sdk.cloud.google.com | bash"
    echo "  exec -l \"$SHELL\""
    echo ""
    exit 1
fi

echo "✅ gcloud CLI found"
echo ""

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with Google Cloud. Please authenticate:"
    echo ""
    gcloud auth login
    echo ""
else
    echo "✅ Already authenticated with Google Cloud"
fi

# Get current project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$CURRENT_PROJECT" ]; then
    echo "❌ No active project set. Please set your project:"
    echo ""
    echo "  gcloud config set project YOUR_PROJECT_ID"
    echo ""
    exit 1
fi

echo "✅ Using project: $CURRENT_PROJECT"
echo ""

# Extract project ID from service account JSON if possible
PROJECT_ID="$CURRENT_PROJECT"
if [ -f "{artifacts_gcp_service_account_json_path}" ]; then
    EXTRACTED_PROJECT=$(python3 -c "import json; print(json.load(open('{artifacts_gcp_service_account_json_path}')).get('project_id', ''))" 2>/dev/null || echo "")
    if [ -n "$EXTRACTED_PROJECT" ]; then
        PROJECT_ID="$EXTRACTED_PROJECT"
        echo "✅ Using project from service account: $PROJECT_ID"
    fi
fi

echo ""
echo "🔧 Fixing GCP storage permissions for artifacts..."
echo ""

# Check if bucket exists
echo "Checking if bucket '{artifacts_gcp_bucket_name}' exists..."
if gsutil ls gs://{artifacts_gcp_bucket_name} &>/dev/null; then
    echo "✅ Bucket '{artifacts_gcp_bucket_name}' exists"
else
    echo "❌ Bucket '{artifacts_gcp_bucket_name}' does not exist or you don't have access"
    echo ""
    echo "Attempting to create bucket '{artifacts_gcp_bucket_name}'..."
    gsutil mb gs://{artifacts_gcp_bucket_name} 2>&1 | tee /tmp/bucket_creation.log
    if [ $? -eq 0 ]; then
        echo "✅ Successfully created bucket '{artifacts_gcp_bucket_name}'"
    else
        echo "❌ Failed to create bucket. Checking error details..."
        if grep -q "already exists" /tmp/bucket_creation.log; then
            echo ""
            echo "⚠️  The bucket name '{artifacts_gcp_bucket_name}' is already taken globally."
            echo "   Bucket names must be unique across all Google Cloud projects."
            echo ""
            echo "🔧 Suggested solutions:"
            echo "1. Use a more specific bucket name with your project ID:"
            echo "   - {artifacts_gcp_bucket_name}-{project_id}"
            echo "   - {artifacts_gcp_bucket_name}-canonmap"
            echo "   - {artifacts_gcp_bucket_name}-$(date +%Y%m%d)"
            echo ""
            echo "2. Update your configuration to use a different bucket name"
            echo ""
            echo "3. Or use an existing bucket that you have access to"
            echo ""
            echo "To check what buckets you have access to, run:"
            echo "   gsutil ls"
            echo ""
        else
            echo "❌ Failed to create bucket. You may need to:"
            echo "  1. Have sufficient permissions to create buckets"
            echo "  2. Use the Google Cloud Console Storage UI instead:"
            echo "     https://console.cloud.google.com/storage/browser"
            echo "  3. Contact your GCP administrator"
            echo ""
        fi
        rm -f /tmp/bucket_creation.log
        exit 1
    fi
    rm -f /tmp/bucket_creation.log
fi

echo ""
echo "Granting permissions to service account {sa_email}..."
echo ""

# Grant storage.objectAdmin role to the service account
echo "Granting 'storage.objectAdmin' role to service account {sa_email}..."
echo ""

gcloud projects add-iam-policy-binding "$PROJECT_ID" \\
    --member="serviceAccount:{sa_email}" \\
    --role="roles/storage.objectAdmin" \\
    --quiet

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully granted storage.objectAdmin role to {sa_email}"
    echo ""
    echo "The service account now has the following permissions:"
    echo "  - storage.objects.create"
    echo "  - storage.objects.delete"
    echo "  - storage.objects.get"
    echo "  - storage.objects.list"
    echo "  - storage.objects.update"
    echo ""
else
    echo ""
    echo "❌ Failed to grant storage.objectAdmin permissions"
    echo ""
fi

# Grant storage.buckets.get permission specifically
echo "Granting 'storage.buckets.get' permission to service account {sa_email}..."
echo ""

gcloud projects add-iam-policy-binding "$PROJECT_ID" \\
    --member="serviceAccount:{sa_email}" \\
    --role="roles/storage.bucketViewer" \\
    --quiet

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully granted storage.bucketViewer role to {sa_email}"
    echo ""
    echo "The service account now has the following additional permissions:"
    echo "  - storage.buckets.get"
    echo "  - storage.buckets.list"
    echo ""
    echo "🎉 GCP artifacts permissions fixed! You can now retry your operation."
    echo ""
else
    echo ""
    echo "❌ Failed to grant storage.bucketViewer permissions. You may need to:"
    echo "  1. Have sufficient IAM permissions to modify IAM policies"
    echo "  2. Use the Google Cloud Console IAM UI instead:"
    echo "     https://console.cloud.google.com/iam-admin/iam"
    echo "  3. Contact your GCP administrator"
    echo ""
    exit 1
fi
"""
                with open(script_path, "w") as file:
                    file.write(script_contents)
                os.chmod(script_path, 0o755)
                logger.success("Troubleshooting script saved to %s", script_path)
                logger.info("Run it with:")
                logger.info(f"\n\n\n{'#' * 37}  GCP ARTIFACTS PERMISSIONS FIX COMMANDS  {'#' * 37}\n\nchmod +x {script_path}\n{script_path}\n\n{'#' * 111}\n\n\n")
                raise PermissionError(
                    f"Missing GCP permissions for artifacts bucket. "
                    f"Troubleshooting script saved to {script_path}"
                )
            else:
                raise PermissionError(f"Permission denied accessing GCP bucket or prefix: {e}")
                
        except NotFound:
            logger.error("GCP bucket not found: %s", artifacts_gcp_bucket_name)
            if artifacts_gcp_auto_create_bucket and troubleshooting:
                try:
                    bucket = client.create_bucket(artifacts_gcp_bucket_name)
                    logger.success("Created GCP bucket: %s", artifacts_gcp_bucket_name)
                except Exception as e:
                    logger.error("Failed to create GCP bucket: %s", e)
                    # Generate troubleshooting script for bucket creation
                    dir_path = "canonmap_troubleshooting"
                    os.makedirs(dir_path, exist_ok=True)
                    sanitized_bucket = re.sub(r'\W+', '_', artifacts_gcp_bucket_name)
                    script_name = f"create_artifacts_bucket_{sanitized_bucket}.sh"
                    script_path = os.path.join(dir_path, script_name)
                    
                    try:
                        with open(artifacts_gcp_service_account_json_path) as f:
                            sa_info = json.load(f)
                        project_id = sa_info.get("project_id", "<PROJECT_ID>")
                    except Exception:
                        project_id = "<PROJECT_ID>"
                    
                    script_contents = f"""#!/usr/bin/env bash
# Script to create GCP bucket for artifacts: {artifacts_gcp_bucket_name}

set -e  # Exit on any error

echo "=========================================="
echo "GCP Artifacts Bucket Creation Script"
echo "=========================================="
echo ""

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Installing Google Cloud SDK..."
    echo ""
    echo "Please install the Google Cloud SDK:"
    echo "  https://cloud.google.com/sdk/docs/install"
    echo ""
    echo "Or run this command:"
    echo "  curl https://sdk.cloud.google.com | bash"
    echo "  exec -l \"$SHELL\""
    echo ""
    exit 1
fi

echo "✅ gcloud CLI found"
echo ""

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with Google Cloud. Please authenticate:"
    echo ""
    gcloud auth login
    echo ""
else
    echo "✅ Already authenticated with Google Cloud"
fi

# Get current project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$CURRENT_PROJECT" ]; then
    echo "❌ No active project set. Please set your project:"
    echo ""
    echo "  gcloud config set project YOUR_PROJECT_ID"
    echo ""
    exit 1
fi

echo "✅ Using project: $CURRENT_PROJECT"
echo ""

# Extract project ID from service account JSON if possible
PROJECT_ID="$CURRENT_PROJECT"
if [ -f "{artifacts_gcp_service_account_json_path}" ]; then
    EXTRACTED_PROJECT=$(python3 -c "import json; print(json.load(open('{artifacts_gcp_service_account_json_path}')).get('project_id', ''))" 2>/dev/null || echo "")
    if [ -n "$EXTRACTED_PROJECT" ]; then
        PROJECT_ID="$EXTRACTED_PROJECT"
        echo "✅ Using project from service account: $PROJECT_ID"
    fi
fi

echo ""
echo "🔧 Creating GCP bucket for artifacts..."
echo ""

# Create the bucket
echo "Creating bucket '{artifacts_gcp_bucket_name}' in project '$PROJECT_ID'..."
echo ""

gcloud storage buckets create gs://{artifacts_gcp_bucket_name} \\
    --project="$PROJECT_ID" \\
    --location=US \\
    --uniform-bucket-level-access

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully created bucket '{artifacts_gcp_bucket_name}'"
    echo ""
    echo "🎉 GCP artifacts bucket created! You can now retry your operation."
    echo ""
else
    echo ""
    echo "❌ Failed to create bucket. You may need to:"
    echo "  1. Have sufficient IAM permissions to create buckets"
    echo "  2. Use the Google Cloud Console Storage UI instead:"
    echo "     https://console.cloud.google.com/storage/browser"
    echo "  3. Contact your GCP administrator"
    echo ""
    exit 1
fi
"""
                    with open(script_path, "w") as file:
                        file.write(script_contents)
                    os.chmod(script_path, 0o755)
                    logger.success("Troubleshooting script saved to %s", script_path)
                    logger.info("Run it with:")
                    logger.info(f"\n\n\n{'#' * 37}  GCP ARTIFACTS BUCKET CREATION COMMANDS  {'#' * 37}\n\nchmod +x {script_path}\n{script_path}\n\n{'#' * 111}\n\n\n")
                    raise FileNotFoundError(
                        f"Failed to create GCP bucket '{artifacts_gcp_bucket_name}'. "
                        f"Troubleshooting script saved to {script_path}"
                    )
            else:
                raise FileNotFoundError(f"GCP bucket not found: {artifacts_gcp_bucket_name}")
                
        except Exception as e:
            logger.error("Unexpected error during GCP validation: %s", e)
            if troubleshooting:
                # Generate general troubleshooting script
                dir_path = "canonmap_troubleshooting"
                os.makedirs(dir_path, exist_ok=True)
                sanitized_bucket = re.sub(r'\W+', '_', artifacts_gcp_bucket_name)
                script_name = f"fix_artifacts_gcp_general_{sanitized_bucket}.sh"
                script_path = os.path.join(dir_path, script_name)
                
                script_contents = f"""#!/usr/bin/env bash
# General troubleshooting script for artifacts GCP issues

echo "=========================================="
echo "GCP Artifacts General Troubleshooting Script"
echo "=========================================="
echo ""

echo "The error was: {e}"
echo ""

echo "🔍 Checking GCP configuration..."
echo ""

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Installing Google Cloud SDK..."
    curl https://sdk.cloud.google.com | bash
    exec -l "$SHELL"
fi

echo "✅ gcloud CLI found"
echo ""

# Check authentication
echo "Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated. Please authenticate:"
    gcloud auth login
else
    echo "✅ Already authenticated"
fi

# Check project
echo "Checking project..."
PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$PROJECT" ]; then
    echo "❌ No project set. Please set your project:"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    exit 1
else
    echo "✅ Using project: $PROJECT"
fi

echo ""
echo "🔧 Manual steps to fix:"
echo "1. Verify the bucket '{artifacts_gcp_bucket_name}' exists:"
echo "   gsutil ls gs://{artifacts_gcp_bucket_name}"
echo ""
echo "2. Check your service account permissions:"
echo "   gcloud projects get-iam-policy $PROJECT"
echo ""
echo "3. If the bucket doesn't exist, create it:"
echo "   gsutil mb gs://{artifacts_gcp_bucket_name}"
echo ""
echo "4. Grant permissions to your service account:"
echo "   gsutil iam ch serviceAccount:YOUR_SERVICE_ACCOUNT@$PROJECT.iam.gserviceaccount.com:objectAdmin gs://{artifacts_gcp_bucket_name}"
echo ""
"""
                with open(script_path, "w") as file:
                    file.write(script_contents)
                os.chmod(script_path, 0o755)
                logger.success("Troubleshooting script saved to %s", script_path)
                logger.info("Run it with:")
                logger.info(f"\n\n\n{'#' * 37}  GCP ARTIFACTS GENERAL FIX COMMANDS  {'#' * 37}\n\nchmod +x {script_path}\n{script_path}\n\n{'#' * 111}\n\n\n")
                raise FileNotFoundError(
                    f"Unexpected error during GCP validation: {e}. "
                    f"Troubleshooting script saved to {script_path}"
                )
            else:
                raise

        logger.success("Artifacts validation successful")
        
    except (FileNotFoundError, PermissionError) as e:
        raise


def upload_artifacts_to_gcs(
    artifacts_local_path: str,
    artifacts_gcp_service_account_json_path: str,
    artifacts_gcp_bucket_name: str,
    artifacts_gcp_bucket_prefix: str = ""
):
    """
    Upload all files (recursively) from the local artifacts directory to the configured GCP bucket/prefix.
    Preserves subdirectory structure in GCS.
    """
    client = storage.Client.from_service_account_json(artifacts_gcp_service_account_json_path)
    bucket = client.get_bucket(artifacts_gcp_bucket_name)
    uploaded = []

    # Always walk the directory tree and upload all files
    for root, _, files in os.walk(artifacts_local_path):
        for fname in files:
            abs_path = os.path.join(root, fname)
            rel_path = os.path.relpath(abs_path, artifacts_local_path)
            blob_name = os.path.join(artifacts_gcp_bucket_prefix, rel_path) if artifacts_gcp_bucket_prefix else rel_path
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(abs_path)
            uploaded.append(rel_path)
    return uploaded

def ensure_artifact_gcp_bucket_and_prefix(
    artifacts_gcp_service_account_json_path: str,
    artifacts_gcp_bucket_name: str,
    artifacts_gcp_bucket_prefix: str,
    artifacts_gcp_auto_create_bucket: bool,
    artifacts_gcp_auto_create_bucket_prefix: bool
):
    """
    Ensure the GCP bucket and prefix for artifacts exist, using auto-create flags and robust troubleshooting.
    Raises on unrecoverable errors.
    """
    try:
        client = storage.Client.from_service_account_json(artifacts_gcp_service_account_json_path)
        # === Bucket ===
        try:
            bucket = client.get_bucket(artifacts_gcp_bucket_name)
            logger.success(f"Accessed GCP bucket: {artifacts_gcp_bucket_name}")
        except NotFound:
            if artifacts_gcp_auto_create_bucket:
                logger.warning(f"Bucket '{artifacts_gcp_bucket_name}' not found, attempting to create (auto-create enabled)")
                try:
                    bucket = client.create_bucket(artifacts_gcp_bucket_name)
                    logger.success(f"Created GCP bucket: {artifacts_gcp_bucket_name}")
                except Exception as e:
                    logger.error(f"Failed to auto-create GCP bucket: {e}")
                    _generate_artifact_bucket_troubleshooting_script(artifacts_gcp_service_account_json_path, artifacts_gcp_bucket_name, e)
                    raise FileNotFoundError(f"Failed to create GCP bucket '{artifacts_gcp_bucket_name}'. Troubleshooting script generated.")
            else:
                logger.error(f"GCP bucket '{artifacts_gcp_bucket_name}' not found and auto-create is disabled.")
                raise FileNotFoundError(f"GCP bucket '{artifacts_gcp_bucket_name}' not found.")
        except Forbidden as e:
            logger.error(f"Permission denied accessing GCP bucket '{artifacts_gcp_bucket_name}': {e}")
            _generate_artifact_bucket_troubleshooting_script(artifacts_gcp_service_account_json_path, artifacts_gcp_bucket_name, e)
            raise PermissionError(f"Permission denied accessing GCP bucket '{artifacts_gcp_bucket_name}'. Troubleshooting script generated.")
        # === Prefix ===
        prefix = artifacts_gcp_bucket_prefix
        if prefix:
            blobs = list(bucket.list_blobs(prefix=prefix, max_results=1))
            if not blobs:
                if artifacts_gcp_auto_create_bucket_prefix:
                    logger.warning(f"Prefix '{prefix}' not found in bucket, attempting to create marker file (auto-create enabled)")
                    try:
                        marker_blob = bucket.blob(f"{prefix.rstrip('/')}/.keep")
                        marker_blob.upload_from_string("")
                        logger.success(f"Created prefix marker: gs://{artifacts_gcp_bucket_name}/{prefix.rstrip('/')}/.keep")
                    except Exception as e:
                        logger.error(f"Failed to create prefix marker: {e}")
                        _generate_artifact_prefix_troubleshooting_script(artifacts_gcp_service_account_json_path, artifacts_gcp_bucket_name, prefix, e)
                        raise FileNotFoundError(f"Failed to create prefix marker for '{prefix}'. Troubleshooting script generated.")
                else:
                    logger.error(f"GCP prefix '{prefix}' not found and auto-create is disabled.")
                    raise FileNotFoundError(f"GCP prefix '{prefix}' not found.")
    except Exception as e:
        logger.error(f"Unexpected error during GCP bucket/prefix validation: {e}")
        raise

def _generate_artifact_bucket_troubleshooting_script(service_account_json_path, bucket_name, error):
    dir_path = "canonmap_troubleshooting"
    os.makedirs(dir_path, exist_ok=True)
    script_name = f"create_artifacts_bucket_{bucket_name}.sh"
    script_path = os.path.join(dir_path, script_name)
    try:
        with open(service_account_json_path) as f:
            sa_info = json.load(f)
        project_id = sa_info.get("project_id", "<PROJECT_ID>")
    except Exception:
        project_id = "<PROJECT_ID>"
    script_contents = f"""#!/usr/bin/env bash
# Script to create GCP bucket '{bucket_name}'
set -e
PROJECT_ID={project_id}
BUCKET={bucket_name}

echo "Creating bucket $BUCKET in project $PROJECT_ID..."
gcloud storage buckets create gs://$BUCKET --project=$PROJECT_ID --location=US --uniform-bucket-level-access
"""
    with open(script_path, "w") as file:
        file.write(script_contents)
    os.chmod(script_path, 0o755)
    logger.success(f"Troubleshooting script for bucket creation saved to {script_path}")
    logger.info(f"Run it with: chmod +x {script_path} && {script_path}")

def _generate_artifact_prefix_troubleshooting_script(service_account_json_path, bucket_name, prefix, error):
    dir_path = "canonmap_troubleshooting"
    os.makedirs(dir_path, exist_ok=True)
    script_name = f"create_artifacts_prefix_{bucket_name}_{prefix.rstrip('/')}.sh"
    script_path = os.path.join(dir_path, script_name)
    try:
        with open(service_account_json_path) as f:
            sa_info = json.load(f)
        project_id = sa_info.get("project_id", "<PROJECT_ID>")
    except Exception:
        project_id = "<PROJECT_ID>"
    script_contents = f"""#!/usr/bin/env bash
# Script to create prefix marker for '{prefix}' in bucket '{bucket_name}'
set -e
PROJECT_ID={project_id}
BUCKET={bucket_name}
PREFIX={prefix.rstrip('/')} 

echo "Creating prefix marker .keep in gs://$BUCKET/$PREFIX/..."
touch .keep
gcloud storage cp .keep gs://$BUCKET/$PREFIX/.keep
rm .keep
"""
    with open(script_path, "w") as file:
        file.write(script_contents)
    os.chmod(script_path, 0o755)
    logger.success(f"Troubleshooting script for prefix creation saved to {script_path}")
    logger.info(f"Run it with: chmod +x {script_path} && {script_path}")