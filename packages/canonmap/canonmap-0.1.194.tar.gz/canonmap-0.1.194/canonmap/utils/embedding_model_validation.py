import os
import json
import re
import traceback
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from canonmap.logger import setup_logger
from google.cloud import storage
from google.api_core.exceptions import Forbidden, NotFound
from canonmap.config import CanonMapEmbeddingConfig

logger = setup_logger(__name__)


def upload_model_to_gcp(
    embedding_model_local_path: str,
    embedding_model_gcp_service_account_json_path: str,
    embedding_model_gcp_bucket_name: str,
    embedding_model_gcp_bucket_prefix: str = "",
):
    """
    Upload all files from the local embedding model directory to the configured GCP bucket and prefix.

    Args:
        embedding_model_local_path: Local directory where the model is stored.
        embedding_model_gcp_service_account_json_path: Path to GCP service account JSON.
        embedding_model_gcp_bucket_name: GCP bucket name for model storage.
        embedding_model_gcp_bucket_prefix: Bucket prefix (subdirectory) for the model.

    Raises:
        FileNotFoundError: If the local model directory does not exist.
        Exception: On upload failures.
    Returns:
        List of uploaded filenames.
    """
    local_path = embedding_model_local_path
    service_account_json = embedding_model_gcp_service_account_json_path
    bucket_name = embedding_model_gcp_bucket_name
    bucket_prefix = embedding_model_gcp_bucket_prefix or ""
    
    if not os.path.isdir(local_path):
        logger.error("Local embedding model path does not exist: %s", local_path)
        raise FileNotFoundError(f"Local embedding model path does not exist: {local_path}")
    
    try:
        client = storage.Client.from_service_account_json(service_account_json)
        bucket = client.get_bucket(bucket_name)
        logger.info("Uploading local model files from %s to gs://%s/%s", local_path, bucket_name, bucket_prefix)
        uploaded = []
        for fname in os.listdir(local_path):
            fpath = os.path.join(local_path, fname)
            if os.path.isfile(fpath):
                blob_name = os.path.join(bucket_prefix, fname) if bucket_prefix else fname
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(fpath)
                logger.success("Uploaded %s to gs://%s/%s", fpath, bucket_name, blob_name)
                uploaded.append(fname)
        return uploaded
    except Exception as e:
        # Special handling for GCP 403 storage.objects.delete errors
        err_str = str(e)
        # Check for storage.objects.delete in error message
        if isinstance(e, Forbidden) and "storage.objects.delete" in err_str:
            dir_path = "canonmap_troubleshooting"
            os.makedirs(dir_path, exist_ok=True)
            sanitized_bucket = re.sub(r'\W+', '_', bucket_name)
            sanitized_prefix = re.sub(r'\W+', '_', bucket_prefix or "root")
            script_name = f"fix_gcp_model_permissions_{sanitized_bucket}_{sanitized_prefix}.sh"
            script_path = os.path.join(dir_path, script_name)
            # Attempt to extract service account email
            try:
                with open(service_account_json) as f:
                    sa_info = json.load(f)
                sa_email = sa_info.get("client_email", "<SERVICE_ACCOUNT_EMAIL>")
            except Exception:
                sa_email = "<SERVICE_ACCOUNT_EMAIL>"
            script_contents = f"""#!/usr/bin/env bash
# Script to fix GCP storage permissions for bucket '{bucket_name}' and prefix '{bucket_prefix}'

set -e  # Exit on any error

echo "=========================================="
echo "GCP Storage Permissions Fix Script"
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
if [ -f "{service_account_json}" ]; then
    EXTRACTED_PROJECT=$(python3 -c "import json; print(json.load(open('{service_account_json}')).get('project_id', ''))" 2>/dev/null || echo "")
    if [ -n "$EXTRACTED_PROJECT" ]; then
        PROJECT_ID="$EXTRACTED_PROJECT"
        echo "✅ Using project from service account: $PROJECT_ID"
    fi
fi

echo ""
echo "🔧 Fixing GCP storage permissions..."
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
    echo "🎉 GCP permissions fixed! You can now retry your upload operation."
    echo ""
else
    echo ""
    echo "❌ Failed to grant permissions. You may need to:"
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
            # Log success and run commands in consistent format
            logger.success("Troubleshooting script saved to %s", script_path)
            logger.info("Run it with:")
            logger.info(f"\n\n\n{'#' * 37}  GCP PERMISSIONS FIX COMMANDS  {'#' * 37}\n\nchmod +x {script_path}\n{script_path}\n\n{'#' * 111}\n\n\n")
            raise PermissionError(
                f"Missing 'storage.objects.delete' permission for uploading to GCP bucket. "
                f"Troubleshooting script saved to {script_path}"
            )
        else:
            logger.error("Failed to upload local model files to GCP: %s", e)
            logger.debug("Full traceback:\n%s", traceback.format_exc())
            raise


def upload_to_gcp(config: CanonMapEmbeddingConfig) -> bool:
    """
    Upload local model files to GCP using config parameters.
    
    Args:
        config: CanonMapEmbeddingConfig instance
        
    Returns:
        True if upload successful, False otherwise
    """
    try:
        uploaded_files = upload_model_to_gcp(
            embedding_model_local_path=config.embedding_model_local_path,
            embedding_model_gcp_service_account_json_path=config.embedding_model_gcp_service_account_json_path,
            embedding_model_gcp_bucket_name=config.embedding_model_gcp_bucket_name,
            embedding_model_gcp_bucket_prefix=config.embedding_model_gcp_bucket_prefix,
        )
        return len(uploaded_files) > 0
    except Exception as e:
        logger.error(f"Failed to upload to GCP: {e}")
        return False


def validate_required_files(model_path: str) -> Dict[str, bool]:
    """
    Check if all required files for a SentenceTransformer model are present.
    
    Args:
        model_path: Path to the model directory
        
    Returns:
        Dict with file paths as keys and existence status as values
    """
    model_dir = Path(model_path)
    required_files = [
        "config.json",
        "sentence_bert_config.json",
        "tokenizer.json",
        "vocab.txt",
        "special_tokens_map.json",
        "tokenizer_config.json",
        "modules.json",
        "README.md",
        "1_Pooling/config.json",
        "2_Normalize/config.json",
    ]
    
    # Check for model.safetensors or pytorch_model.bin
    model_files = ["model.safetensors", "pytorch_model.bin"]
    has_model_file = any((model_dir / f).exists() for f in model_files)
    
    results = {}
    for file_path in required_files:
        full_path = model_dir / file_path
        results[str(full_path)] = full_path.exists()
    
    # Add model file check
    results["model_file"] = has_model_file
    
    return results


def validate_gcp_resources(config: CanonMapEmbeddingConfig) -> Dict[str, bool]:
    """
    Check if GCP resources (bucket and prefix) exist and are accessible.
    
    Args:
        config: CanonMapEmbeddingConfig instance
        
    Returns:
        Dict with validation results
    """
    if not config.embedding_model_gcp_service_account_json_path:
        return {"gcp_configured": False, "bucket_exists": False, "prefix_exists": False}
    
    try:
        from google.cloud import storage
        from google.auth import default
        
        # Initialize GCP client
        if config.embedding_model_gcp_service_account_json_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.embedding_model_gcp_service_account_json_path
        
        client = storage.Client()
        
        # Check if bucket exists
        bucket = client.bucket(config.embedding_model_gcp_bucket_name)
        bucket_exists = bucket.exists()
        
        # Check if prefix exists (list blobs with prefix)
        prefix_exists = False
        if bucket_exists:
            blobs = list(bucket.list_blobs(prefix=config.embedding_model_gcp_bucket_prefix, max_results=1))
            prefix_exists = len(blobs) > 0
        
        return {
            "gcp_configured": True,
            "bucket_exists": bucket_exists,
            "prefix_exists": prefix_exists
        }
        
    except Exception as e:
        logger.warning(f"GCP validation failed: {e}")
        return {
            "gcp_configured": False,
            "bucket_exists": False,
            "prefix_exists": False,
            "error": str(e)
        }


def get_model_state(config: CanonMapEmbeddingConfig) -> Dict[str, Any]:
    """
    Get comprehensive state of the embedding model setup.
    
    Args:
        config: CanonMapEmbeddingConfig instance
        
    Returns:
        Dict with complete model state information
    """
    local_path = Path(config.embedding_model_local_path)
    local_exists = local_path.exists()
    
    # Check local files
    local_files_status = {}
    if local_exists:
        local_files_status = validate_required_files(str(local_path))
    
    # Check GCP resources
    gcp_status = validate_gcp_resources(config)
    
    # Determine overall state
    local_complete = local_exists and all(local_files_status.values())
    gcp_available = gcp_status.get("gcp_configured", False) and gcp_status.get("bucket_exists", False)
    
    return {
        "local_path": str(local_path),
        "local_exists": local_exists,
        "local_files_status": local_files_status,
        "local_complete": local_complete,
        "gcp_status": gcp_status,
        "gcp_available": gcp_available,
        "sync_strategy": config.embedding_model_gcp_sync_strategy,
        "troubleshooting": config.troubleshooting
    }


def download_from_gcp(config: CanonMapEmbeddingConfig) -> bool:
    """
    Download model files from GCP bucket to local path.
    
    Args:
        config: CanonMapEmbeddingConfig instance
        
    Returns:
        True if download successful, False otherwise
    """
    try:
        from google.cloud import storage
        
        # Initialize GCP client
        if config.embedding_model_gcp_service_account_json_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.embedding_model_gcp_service_account_json_path
        
        client = storage.Client()
        bucket = client.bucket(config.embedding_model_gcp_bucket_name)
        
        # Create local directory
        local_path = Path(config.embedding_model_local_path)
        local_path.mkdir(parents=True, exist_ok=True)
        
        # List all blobs with the prefix
        blobs = bucket.list_blobs(prefix=config.embedding_model_gcp_bucket_prefix)
        
        downloaded_count = 0
        for blob in blobs:
            # Get relative path from prefix
            relative_path = blob.name[len(config.embedding_model_gcp_bucket_prefix):].lstrip('/')
            if not relative_path:
                continue
                
            local_file_path = local_path / relative_path
            local_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            blob.download_to_filename(str(local_file_path))
            downloaded_count += 1
            logger.info(f"Downloaded: {relative_path}")
        
        logger.info(f"Downloaded {downloaded_count} files from GCP")
        return downloaded_count > 0
        
    except Exception as e:
        logger.error(f"Failed to download from GCP: {e}")
        return False


def download_from_hf(model_name: str, local_path: str) -> bool:
    """
    Download model from Hugging Face to local path.
    
    Args:
        model_name: Hugging Face model name (e.g., "sentence-transformers/all-MiniLM-L12-v2")
        local_path: Local directory to save the model
        
    Returns:
        True if download successful, False otherwise
    """
    try:
        from sentence_transformers import SentenceTransformer
        
        logger.info(f"Downloading model '{model_name}' to '{local_path}'...")
        
        # Create directory
        Path(local_path).mkdir(parents=True, exist_ok=True)
        
        # Download model
        model = SentenceTransformer(model_name, cache_folder=local_path)
        
        # Save to the specified path
        model.save(local_path)
        
        logger.info(f"Successfully downloaded model to '{local_path}'")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download from Hugging Face: {e}")
        return False


def trigger_troubleshooting(scenario: str, config: CanonMapEmbeddingConfig) -> None:
    """
    Trigger user troubleshooting for specific scenarios.
    
    Args:
        scenario: The troubleshooting scenario
        config: CanonMapEmbeddingConfig instance
    """
    instructions = get_troubleshooting_instructions(scenario, config)
    
    logger.error("=" * 80)
    logger.error("TROUBLESHOOTING REQUIRED")
    logger.error("=" * 80)
    logger.error(instructions)
    logger.error("=" * 80)
    
    if config.troubleshooting:
        # In troubleshooting mode, we can provide more detailed guidance
        logger.error("Please follow the instructions above and try again.")
    else:
        logger.error("Set troubleshooting=True in your config for detailed guidance.")


def get_troubleshooting_instructions(scenario: str, config: CanonMapEmbeddingConfig) -> str:
    """
    Get troubleshooting instructions for specific scenarios.
    
    Args:
        scenario: The troubleshooting scenario
        config: CanonMapEmbeddingConfig instance
        
    Returns:
        Troubleshooting instructions as string
    """
    base_instructions = {
        "local_missing_files": f"""
Local model files are missing or incomplete at: {config.embedding_model_local_path}

To fix this:
1. Download the model manually:
   pip install sentence-transformers
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('{config.embedding_model_hf_name}').save('{config.embedding_model_local_path}')"

2. Or use the canonmap download command:
   canonmap-download-model {config.embedding_model_local_path}
""",
        
        "local_path_not_exists": f"""
Local model path does not exist: {config.embedding_model_local_path}

To fix this:
1. Create the directory and download the model:
   mkdir -p {config.embedding_model_local_path}
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('{config.embedding_model_hf_name}').save('{config.embedding_model_local_path}')"

2. Or use the canonmap download command:
   canonmap-download-model {config.embedding_model_local_path}
""",
        
        "gcp_bucket_missing": f"""
GCP bucket '{config.embedding_model_gcp_bucket_name}' does not exist or is not accessible.

To fix this:
1. Create the bucket in GCP Console
2. Ensure your service account has access to the bucket
3. Verify the service account JSON path: {config.embedding_model_gcp_service_account_json_path}
""",
        
        "gcp_prefix_missing": f"""
GCP prefix '{config.embedding_model_gcp_bucket_prefix}' does not exist in bucket '{config.embedding_model_gcp_bucket_name}'.

To fix this:
1. Upload the model files to the GCP bucket with the correct prefix
2. Or change the prefix in your configuration
""",
        
        "gcp_auth_failed": f"""
GCP authentication failed.

To fix this:
1. Verify your service account JSON file exists: {config.embedding_model_gcp_service_account_json_path}
2. Ensure the service account has the necessary permissions
3. Check that the JSON file is valid and not corrupted
""",
        
        "network_error": f"""
Network error occurred while downloading the model.

To fix this:
1. Check your internet connection
2. Try downloading again later
3. Use a local model if available
4. Check firewall/proxy settings
""",
        
        "permission_error": f"""
Permission error accessing local model path: {config.embedding_model_local_path}

To fix this:
1. Check file permissions on the directory
2. Ensure you have read/write access
3. Try running with elevated permissions if necessary
4. Choose a different local path with proper permissions
""",
        
        "disk_space_error": f"""
Insufficient disk space to download the model.

To fix this:
1. Free up disk space (model requires ~100MB)
2. Choose a different location with more space
3. Use an existing local model if available
""",
    }
    
    return base_instructions.get(scenario, f"Unknown troubleshooting scenario: {scenario}")


def validate_model(
    hf_name: str,
    local_path: str,
    gcp_service_account_json_path: str,
    gcp_bucket_name: str,
    gcp_bucket_prefix: str,
    gcp_auto_create_bucket: bool,
    gcp_auto_create_bucket_prefix: bool,
    gcp_sync_strategy: str,
    troubleshooting: bool = False,
) -> bool:
    """
    Comprehensive model validation with GCP sync support.
    
    Args:
        hf_name: Hugging Face model name
        local_path: Local model path
        gcp_service_account_json_path: GCP service account JSON path
        gcp_bucket_name: GCP bucket name
        gcp_bucket_prefix: GCP bucket prefix
        gcp_auto_create_bucket: Whether to auto-create GCP bucket
        gcp_auto_create_bucket_prefix: Whether to auto-create GCP bucket prefix
        gcp_sync_strategy: GCP sync strategy ("none", "missing", "overwrite", "refresh")
        troubleshooting: Whether to enable troubleshooting mode
        
    Returns:
        True if model is valid and accessible, False otherwise
    """
    # Create config object for validation
    config = CanonMapEmbeddingConfig(
        embedding_model_hf_name=hf_name,
        embedding_model_local_path=local_path,
        embedding_model_gcp_service_account_json_path=gcp_service_account_json_path,
        embedding_model_gcp_bucket_name=gcp_bucket_name,
        embedding_model_gcp_bucket_prefix=gcp_bucket_prefix,
        embedding_model_gcp_auto_create_bucket=gcp_auto_create_bucket,
        embedding_model_gcp_auto_create_bucket_prefix=gcp_auto_create_bucket_prefix,
        embedding_model_gcp_sync_strategy=gcp_sync_strategy,
        troubleshooting=troubleshooting,
    )
    
    # Get model state
    state = get_model_state(config)
    
    # Handle different scenarios based on sync strategy
    if gcp_sync_strategy == "none":
        return _handle_none_strategy(state, config)
    else:
        return _handle_gcp_strategy(state, config)


def _handle_none_strategy(state: Dict[str, Any], config: CanonMapEmbeddingConfig) -> bool:
    """Handle validation for 'none' sync strategy."""
    local_exists = state["local_exists"]
    local_complete = state["local_complete"]
    
    if local_exists and local_complete:
        logger.info("Local model is complete and ready to use")
        return True
    
    if local_exists and not local_complete:
        if config.troubleshooting:
            trigger_troubleshooting("local_missing_files", config)
        else:
            logger.warning("Local model files are incomplete")
        return True  # Proceed anyway
    
    if not local_exists:
        if config.troubleshooting:
            trigger_troubleshooting("local_path_not_exists", config)
        else:
            logger.warning("Local model path does not exist")
        return True  # Proceed anyway
    
    return True


def _handle_gcp_strategy(state: Dict[str, Any], config: CanonMapEmbeddingConfig) -> bool:
    """Handle validation for GCP sync strategies."""
    local_exists = state["local_exists"]
    local_complete = state["local_complete"]
    gcp_available = state["gcp_available"]
    gcp_status = state["gcp_status"]
    
    # Check GCP configuration
    if not gcp_status.get("gcp_configured", False):
        if config.troubleshooting:
            trigger_troubleshooting("gcp_auth_failed", config)
        else:
            logger.error("GCP not properly configured")
        return False
    
    # Check GCP bucket
    if not gcp_status.get("bucket_exists", False):
        if config.troubleshooting:
            trigger_troubleshooting("gcp_bucket_missing", config)
        else:
            logger.error(f"GCP bucket '{config.embedding_model_gcp_bucket_name}' does not exist")
        return False
    
    # Check GCP prefix
    if not gcp_status.get("prefix_exists", False):
        if config.troubleshooting:
            trigger_troubleshooting("gcp_prefix_missing", config)
        else:
            logger.error(f"GCP prefix '{config.embedding_model_gcp_bucket_prefix}' does not exist")
        return False
    
    # If we get here, GCP is available
    if local_exists and local_complete:
        logger.info("Local model is complete and GCP is available")
        return True
    
    # Try to download from GCP
    if gcp_available:
        logger.info("Downloading model from GCP...")
        if download_from_gcp(config):
            logger.info("Successfully downloaded model from GCP")
            return True
        else:
            logger.error("Failed to download model from GCP")
            return False
    
    return False


def ensure_gcp_bucket_and_prefix(config: CanonMapEmbeddingConfig) -> None:
    """
    Ensure the GCP bucket and prefix exist, using auto-create flags and robust troubleshooting.
    Raises on unrecoverable errors.
    """
    try:
        client = storage.Client.from_service_account_json(config.embedding_model_gcp_service_account_json_path)
        # === Bucket ===
        try:
            bucket = client.get_bucket(config.embedding_model_gcp_bucket_name)
            logger.success(f"Accessed GCP bucket: {config.embedding_model_gcp_bucket_name}")
        except NotFound:
            if getattr(config, "embedding_model_gcp_auto_create_bucket", False):
                logger.warning(f"Bucket '{config.embedding_model_gcp_bucket_name}' not found, attempting to create (auto-create enabled)")
                try:
                    bucket = client.create_bucket(config.embedding_model_gcp_bucket_name)
                    logger.success(f"Created GCP bucket: {config.embedding_model_gcp_bucket_name}")
                except Exception as e:
                    logger.error(f"Failed to auto-create GCP bucket: {e}")
                    _generate_bucket_troubleshooting_script(config, e)
                    raise FileNotFoundError(f"Failed to create GCP bucket '{config.embedding_model_gcp_bucket_name}'. Troubleshooting script generated.")
            else:
                logger.error(f"GCP bucket '{config.embedding_model_gcp_bucket_name}' not found and auto-create is disabled.")
                raise FileNotFoundError(f"GCP bucket '{config.embedding_model_gcp_bucket_name}' not found.")
        except Forbidden as e:
            logger.error(f"Permission denied accessing GCP bucket '{config.embedding_model_gcp_bucket_name}': {e}")
            _generate_bucket_troubleshooting_script(config, e)
            raise PermissionError(f"Permission denied accessing GCP bucket '{config.embedding_model_gcp_bucket_name}'. Troubleshooting script generated.")
        # === Prefix ===
        prefix = config.embedding_model_gcp_bucket_prefix
        if prefix:
            blobs = list(bucket.list_blobs(prefix=prefix, max_results=1))
            if not blobs:
                if getattr(config, "embedding_model_gcp_auto_create_bucket_prefix", False):
                    logger.warning(f"Prefix '{prefix}' not found in bucket, attempting to create marker file (auto-create enabled)")
                    try:
                        marker_blob = bucket.blob(f"{prefix.rstrip('/')}/.keep")
                        marker_blob.upload_from_string("")
                        logger.success(f"Created prefix marker: gs://{config.embedding_model_gcp_bucket_name}/{prefix.rstrip('/')}/.keep")
                    except Exception as e:
                        logger.error(f"Failed to create prefix marker: {e}")
                        _generate_prefix_troubleshooting_script(config, e)
                        raise FileNotFoundError(f"Failed to create prefix marker for '{prefix}'. Troubleshooting script generated.")
                else:
                    logger.error(f"GCP prefix '{prefix}' not found and auto-create is disabled.")
                    raise FileNotFoundError(f"GCP prefix '{prefix}' not found.")
    except Exception as e:
        logger.error(f"Unexpected error during GCP bucket/prefix validation: {e}")
        raise


def _generate_bucket_troubleshooting_script(config: CanonMapEmbeddingConfig, error: Exception):
    dir_path = "canonmap_troubleshooting"
    os.makedirs(dir_path, exist_ok=True)
    script_name = f"create_model_bucket_{config.embedding_model_gcp_bucket_name}.sh"
    script_path = os.path.join(dir_path, script_name)
    try:
        with open(config.embedding_model_gcp_service_account_json_path) as f:
            sa_info = json.load(f)
        project_id = sa_info.get("project_id", "<PROJECT_ID>")
    except Exception:
        project_id = "<PROJECT_ID>"
    script_contents = f"""#!/usr/bin/env bash
# Script to create GCP bucket '{config.embedding_model_gcp_bucket_name}'
set -e
PROJECT_ID={project_id}
BUCKET={config.embedding_model_gcp_bucket_name}

echo "Creating bucket $BUCKET in project $PROJECT_ID..."
gcloud storage buckets create gs://$BUCKET --project=$PROJECT_ID --location=US --uniform-bucket-level-access
"""
    with open(script_path, "w") as file:
        file.write(script_contents)
    os.chmod(script_path, 0o755)
    logger.success(f"Troubleshooting script for bucket creation saved to {script_path}")
    logger.info(f"Run it with: chmod +x {script_path} && {script_path}")


def _generate_prefix_troubleshooting_script(config: CanonMapEmbeddingConfig, error: Exception):
    dir_path = "canonmap_troubleshooting"
    os.makedirs(dir_path, exist_ok=True)
    script_name = f"create_model_prefix_{config.embedding_model_gcp_bucket_name}_{config.embedding_model_gcp_bucket_prefix.rstrip('/')}.sh"
    script_path = os.path.join(dir_path, script_name)
    try:
        with open(config.embedding_model_gcp_service_account_json_path) as f:
            sa_info = json.load(f)
        project_id = sa_info.get("project_id", "<PROJECT_ID>")
    except Exception:
        project_id = "<PROJECT_ID>"
    script_contents = f"""#!/usr/bin/env bash
# Script to create prefix marker for '{config.embedding_model_gcp_bucket_prefix}' in bucket '{config.embedding_model_gcp_bucket_name}'
set -e
PROJECT_ID={project_id}
BUCKET={config.embedding_model_gcp_bucket_name}
PREFIX={config.embedding_model_gcp_bucket_prefix.rstrip('/')}

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