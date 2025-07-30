"""
CanonMap Configuration Helper

This module provides a configurable way to initialize CanonMap with support for:
- Environment variable configuration
- GCP integration with generic placeholders
- Local-only mode for development
- Flexible configuration options
"""

import os
from pathlib import Path
from typing import Optional
from canonmap import (
    CanonMap,
    CanonMapEmbeddingConfig,
    CanonMapArtifactsConfig
)

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Environment variable keys
ENV_KEYS = {
    # GCP Configuration
    'GCP_PROJECT_ID': 'your-gcp-project-id',
    'GCP_BUCKET_NAME': 'your-gcp-bucket-name',
    'GCP_SERVICE_ACCOUNT_PATH': 'your-service-account.json',
    
    # Artifacts Configuration
    'ARTIFACTS_LOCAL_PATH': 'artifacts',
    'ARTIFACTS_GCP_PREFIX': 'artifacts',
    'ARTIFACTS_SYNC_STRATEGY': 'refresh',
    
    # Embedding Configuration
    'EMBEDDING_MODEL_NAME': 'sentence-transformers/all-MiniLM-L12-v2',
    'EMBEDDING_LOCAL_PATH': 'models/sentence-transformers/all-MiniLM-L12-v2',
    'EMBEDDING_GCP_PREFIX': 'models/sentence-transformers/all-MiniLM-L12-v2',
    'EMBEDDING_SYNC_STRATEGY': 'refresh',
    
    # General Configuration
    'CANONMAP_VERBOSE': 'true',
    'CANONMAP_TROUBLESHOOTING': 'false',
    'USE_GCP': 'false'
}

def get_env_or_default(key: str, default: str) -> str:
    """Get environment variable or return default value."""
    return os.getenv(key, default)

def get_bool_env_or_default(key: str, default: bool) -> bool:
    """Get boolean environment variable or return default value."""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def check_gcp_model_exists(service_account_path: str, bucket_name: str, prefix: str) -> bool:
    """
    Check if model files exist in GCP bucket/prefix.
    
    Args:
        service_account_path: Path to GCP service account JSON
        bucket_name: GCP bucket name
        prefix: GCP bucket prefix
        
    Returns:
        True if model files exist in GCP, False otherwise
    """
    try:
        from google.cloud import storage
        
        # Set up GCP client
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        
        # List blobs with the prefix
        blobs = list(bucket.list_blobs(prefix=prefix))
        
        # Check if we have any model files (not just the prefix directory)
        model_files = [blob for blob in blobs if blob.name != prefix.rstrip('/')]
        
        logger.info(f"Found {len(model_files)} model files in GCP bucket {bucket_name}/{prefix}")
        return len(model_files) > 0
        
    except Exception as e:
        logger.warning(f"Could not check GCP model existence: {e}")
        return False

def check_local_model_exists(local_path: str) -> bool:
    """
    Check if model files exist locally.
    
    Args:
        local_path: Local model path
        
    Returns:
        True if model files exist locally, False otherwise
    """
    try:
        local_model_path = Path(local_path)
        if not local_model_path.exists():
            return False
            
        # Check for common model files
        required_files = ['config.json', 'model.safetensors', 'tokenizer.json']
        existing_files = [f.name for f in local_model_path.iterdir() if f.is_file()]
        
        # Check if we have at least some model files
        has_model_files = any(file in existing_files for file in required_files)
        
        logger.info(f"Local model path {local_path}: {len(existing_files)} files found, has model files: {has_model_files}")
        return has_model_files
        
    except Exception as e:
        logger.warning(f"Could not check local model existence: {e}")
        return False

def upload_local_model_to_gcp(embedding_config: CanonMapEmbeddingConfig) -> bool:
    """
    Upload local model files to GCP if they exist and GCP doesn't have them.
    
    Args:
        embedding_config: CanonMapEmbeddingConfig instance
        
    Returns:
        True if upload was successful or not needed, False if failed
    """
    try:
        # Check if we should upload (sync strategy is not "none")
        if embedding_config.embedding_model_gcp_sync_strategy == "none":
            logger.info("GCP sync strategy is 'none', skipping upload check")
            return True
            
        # Check if GCP is configured
        if not embedding_config.embedding_model_gcp_service_account_json_path:
            logger.info("GCP service account not configured, skipping upload check")
            return True
            
        # Check if local model exists
        local_exists = check_local_model_exists(embedding_config.embedding_model_local_path)
        if not local_exists:
            logger.info("Local model files not found, skipping upload")
            return True
            
        # Check if GCP already has the model
        gcp_exists = check_gcp_model_exists(
            embedding_config.embedding_model_gcp_service_account_json_path,
            embedding_config.embedding_model_gcp_bucket_name,
            embedding_config.embedding_model_gcp_bucket_prefix
        )
        
        if gcp_exists:
            logger.info("Model already exists in GCP, skipping upload")
            return True
            
        # Upload local model to GCP
        logger.info("Local model exists but not in GCP, uploading...")
        uploaded_files = embedding_config.upload_local_model_to_gcp()
        
        if uploaded_files:
            logger.info(f"✅ Successfully uploaded {len(uploaded_files)} model files to GCP")
            return True
        else:
            logger.warning("⚠️ Upload to GCP returned no files")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to upload model to GCP: {e}")
        return False

def get_canonmap() -> CanonMap:
    """
    Initialize CanonMap with configurable settings.
    
    Configuration priority:
    1. Environment variables
    2. Default values with generic placeholders
    
    Environment Variables:
        GCP_PROJECT_ID: Your GCP project ID
        GCP_BUCKET_NAME: Your GCP bucket name
        GCP_SERVICE_ACCOUNT_PATH: Path to service account JSON file
        ARTIFACTS_LOCAL_PATH: Local path for artifacts
        ARTIFACTS_GCP_PREFIX: GCP prefix for artifacts
        EMBEDDING_MODEL_NAME: HuggingFace model name
        EMBEDDING_LOCAL_PATH: Local path for embedding model
        EMBEDDING_GCP_PREFIX: GCP prefix for embedding model
        CANONMAP_VERBOSE: Enable verbose logging
        CANONMAP_TROUBLESHOOTING: Enable troubleshooting mode
        USE_GCP: Enable GCP integration
    
    Returns:
        CanonMap: Configured CanonMap instance
    """
    
    # Get configuration values
    use_gcp = get_bool_env_or_default('USE_GCP', False)
    verbose = get_bool_env_or_default('CANONMAP_VERBOSE', True)
    troubleshooting = get_bool_env_or_default('CANONMAP_TROUBLESHOOTING', False)
    
    # GCP Configuration
    gcp_project_id = get_env_or_default('GCP_PROJECT_ID', ENV_KEYS['GCP_PROJECT_ID'])
    gcp_bucket_name = get_env_or_default('GCP_BUCKET_NAME', ENV_KEYS['GCP_BUCKET_NAME'])
    gcp_service_account_path = get_env_or_default('GCP_SERVICE_ACCOUNT_PATH', ENV_KEYS['GCP_SERVICE_ACCOUNT_PATH'])
    
    # Artifacts Configuration
    artifacts_local_path = get_env_or_default('ARTIFACTS_LOCAL_PATH', ENV_KEYS['ARTIFACTS_LOCAL_PATH'])
    artifacts_gcp_prefix = get_env_or_default('ARTIFACTS_GCP_PREFIX', ENV_KEYS['ARTIFACTS_GCP_PREFIX'])
    artifacts_sync_strategy = get_env_or_default('ARTIFACTS_SYNC_STRATEGY', ENV_KEYS['ARTIFACTS_SYNC_STRATEGY'])
    
    # Embedding Configuration
    embedding_model_name = get_env_or_default('EMBEDDING_MODEL_NAME', ENV_KEYS['EMBEDDING_MODEL_NAME'])
    embedding_local_path = get_env_or_default('EMBEDDING_LOCAL_PATH', ENV_KEYS['EMBEDDING_LOCAL_PATH'])
    embedding_gcp_prefix = get_env_or_default('EMBEDDING_GCP_PREFIX', ENV_KEYS['EMBEDDING_GCP_PREFIX'])
    embedding_sync_strategy = get_env_or_default('EMBEDDING_SYNC_STRATEGY', ENV_KEYS['EMBEDDING_SYNC_STRATEGY'])
    
    # Log configuration
    logger.info("Initializing CanonMap with configuration:")
    logger.info(f"  Use GCP: {use_gcp}")
    logger.info(f"  Verbose: {verbose}")
    logger.info(f"  Troubleshooting: {troubleshooting}")
    logger.info(f"  Artifacts local path: {artifacts_local_path}")
    logger.info(f"  Embedding model: {embedding_model_name}")
    logger.info(f"  Embedding local path: {embedding_local_path}")
    
    if use_gcp:
        logger.info(f"  GCP Project ID: {gcp_project_id}")
        logger.info(f"  GCP Bucket: {gcp_bucket_name}")
        logger.info(f"  GCP Service Account: {gcp_service_account_path}")
    
    # Configure artifacts
    artifacts_config = CanonMapArtifactsConfig(
        artifacts_local_path=Path(artifacts_local_path),
        artifacts_gcp_service_account_json_path=gcp_service_account_path if use_gcp else "",
        artifacts_gcp_bucket_name=gcp_bucket_name if use_gcp else "",
        artifacts_gcp_bucket_prefix=artifacts_gcp_prefix if use_gcp else "",
        artifacts_gcp_auto_create_bucket=use_gcp,
        artifacts_gcp_auto_create_bucket_prefix=use_gcp,
        artifacts_gcp_sync_strategy=artifacts_sync_strategy if use_gcp else "none",
        troubleshooting=troubleshooting,
    )
    
    # Configure embeddings
    embedding_config = CanonMapEmbeddingConfig(
        embedding_model_name=embedding_model_name,
        embedding_model_local_path=embedding_local_path,
        embedding_model_gcp_service_account_json_path=gcp_service_account_path if use_gcp else "",
        embedding_model_gcp_bucket_name=gcp_bucket_name if use_gcp else "",
        embedding_model_gcp_bucket_prefix=embedding_gcp_prefix if use_gcp else "",
        embedding_model_gcp_auto_create_bucket=use_gcp,
        embedding_model_gcp_auto_create_bucket_prefix=use_gcp,
        embedding_model_gcp_sync_strategy=embedding_sync_strategy if use_gcp else "none",
        troubleshooting=troubleshooting,
    )
    
    # Handle GCP model upload if needed
    if use_gcp and embedding_config.embedding_model_gcp_sync_strategy != "none":
        logger.info("🔍 Checking if local model should be uploaded to GCP...")
        upload_success = upload_local_model_to_gcp(embedding_config)
        if not upload_success:
            logger.warning("⚠️ Model upload to GCP failed, but continuing with initialization")
    
    # Initialize CanonMap
    canonmap = CanonMap(
        artifacts_config=artifacts_config,
        embedding_config=embedding_config,
        verbose=verbose,
    )
    
    logger.info("✅ CanonMap initialized successfully")
    return canonmap

def get_canonmap_local_only() -> CanonMap:
    """
    Initialize CanonMap for local-only development (no GCP).
    
    Returns:
        CanonMap: CanonMap instance configured for local development
    """
    # Temporarily set environment variables for local-only mode
    original_use_gcp = os.getenv('USE_GCP')
    os.environ['USE_GCP'] = 'false'
    
    try:
        return get_canonmap()
    finally:
        # Restore original environment variable
        if original_use_gcp is not None:
            os.environ['USE_GCP'] = original_use_gcp
        else:
            os.environ.pop('USE_GCP', None)

def get_canonmap_with_gcp(project_id: str, bucket_name: str, service_account_path: str) -> CanonMap:
    """
    Initialize CanonMap with specific GCP configuration.
    
    Args:
        project_id: GCP project ID
        bucket_name: GCP bucket name
        service_account_path: Path to service account JSON file
    
    Returns:
        CanonMap: CanonMap instance configured with GCP
    """
    # Temporarily set environment variables
    original_vars = {
        'USE_GCP': os.getenv('USE_GCP'),
        'GCP_PROJECT_ID': os.getenv('GCP_PROJECT_ID'),
        'GCP_BUCKET_NAME': os.getenv('GCP_BUCKET_NAME'),
        'GCP_SERVICE_ACCOUNT_PATH': os.getenv('GCP_SERVICE_ACCOUNT_PATH')
    }
    
    os.environ['USE_GCP'] = 'true'
    os.environ['GCP_PROJECT_ID'] = project_id
    os.environ['GCP_BUCKET_NAME'] = bucket_name
    os.environ['GCP_SERVICE_ACCOUNT_PATH'] = service_account_path
    
    try:
        return get_canonmap()
    finally:
        # Restore original environment variables
        for key, value in original_vars.items():
            if value is not None:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)

def print_configuration_help():
    """Print help information for configuration options."""
    print("🔧 CanonMap Configuration Options")
    print("=" * 50)
    print()
    print("Environment Variables:")
    print()
    print("GCP Configuration:")
    print(f"  GCP_PROJECT_ID          Default: {ENV_KEYS['GCP_PROJECT_ID']}")
    print(f"  GCP_BUCKET_NAME         Default: {ENV_KEYS['GCP_BUCKET_NAME']}")
    print(f"  GCP_SERVICE_ACCOUNT_PATH Default: {ENV_KEYS['GCP_SERVICE_ACCOUNT_PATH']}")
    print(f"  USE_GCP                 Default: {ENV_KEYS['USE_GCP']}")
    print()
    print("Artifacts Configuration:")
    print(f"  ARTIFACTS_LOCAL_PATH    Default: {ENV_KEYS['ARTIFACTS_LOCAL_PATH']}")
    print(f"  ARTIFACTS_GCP_PREFIX    Default: {ENV_KEYS['ARTIFACTS_GCP_PREFIX']}")
    print(f"  ARTIFACTS_SYNC_STRATEGY Default: {ENV_KEYS['ARTIFACTS_SYNC_STRATEGY']}")
    print()
    print("Embedding Configuration:")
    print(f"  EMBEDDING_MODEL_NAME    Default: {ENV_KEYS['EMBEDDING_MODEL_NAME']}")
    print(f"  EMBEDDING_LOCAL_PATH    Default: {ENV_KEYS['EMBEDDING_LOCAL_PATH']}")
    print(f"  EMBEDDING_GCP_PREFIX    Default: {ENV_KEYS['EMBEDDING_GCP_PREFIX']}")
    print(f"  EMBEDDING_SYNC_STRATEGY Default: {ENV_KEYS['EMBEDDING_SYNC_STRATEGY']}")
    print()
    print("General Configuration:")
    print(f"  CANONMAP_VERBOSE        Default: {ENV_KEYS['CANONMAP_VERBOSE']}")
    print(f"  CANONMAP_TROUBLESHOOTING Default: {ENV_KEYS['CANONMAP_TROUBLESHOOTING']}")
    print()
    print("Usage Examples:")
    print()
    print("1. Local development (no GCP):")
    print("   export USE_GCP=false")
    print("   python -m uvicorn app.main:app --reload")
    print()
    print("2. With GCP integration:")
    print("   export USE_GCP=true")
    print("   export GCP_PROJECT_ID=your-actual-project-id")
    print("   export GCP_BUCKET_NAME=your-actual-bucket-name")
    print("   export GCP_SERVICE_ACCOUNT_PATH=path/to/service-account.json")
    print("   python -m uvicorn app.main:app --reload")
    print()
    print("3. Using helper functions:")
    print("   from get_canonmap_helper import get_canonmap_local_only")
    print("   canonmap = get_canonmap_local_only()")
    print()
    print("   from get_canonmap_helper import get_canonmap_with_gcp")
    print("   canonmap = get_canonmap_with_gcp('project-id', 'bucket-name', 'sa.json')")

if __name__ == "__main__":
    # Print configuration help when run directly
    print_configuration_help()
