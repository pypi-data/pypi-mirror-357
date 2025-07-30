import os
import tempfile
from pathlib import Path
from typing import Optional

from canonmap.config import CanonMapEmbeddingConfig
from canonmap.embedder import Embedder
from canonmap.logger import setup_logger
from canonmap.utils.embedding_model_validation import (
    get_model_state,
    download_from_gcp,
    download_from_hf,
    trigger_troubleshooting,
    validate_required_files,
    upload_to_gcp,
    ensure_gcp_bucket_and_prefix,
)

logger = setup_logger(__name__)


def get_embedder_from_config(config: CanonMapEmbeddingConfig) -> Optional[Embedder]:
    """
    Comprehensive embedding model loading with fallback mechanisms.
    
    Args:
        config: CanonMapEmbeddingConfig instance
        
    Returns:
        Embedder instance if successful, None if failed
        
    Raises:
        Exception: If model loading fails after all fallback attempts
    """
    logger.info("Starting comprehensive embedding model loading...")
    
    # Get current model state
    state = get_model_state(config)
    logger.info(f"Model state: local_exists={state['local_exists']}, local_complete={state['local_complete']}, gcp_available={state['gcp_available']}")
    
    # Handle different sync strategies
    if config.embedding_model_gcp_sync_strategy == "none":
        return _handle_none_strategy_loading(state, config)
    else:
        return _handle_gcp_strategy_loading(state, config)


def _handle_none_strategy_loading(state: dict, config: CanonMapEmbeddingConfig) -> Optional[Embedder]:
    """Handle loading for 'none' sync strategy."""
    local_exists = state["local_exists"]
    local_complete = state["local_complete"]
    
    # Scenario 1.1: Local path exists + all required files present
    if local_exists and local_complete:
        logger.info("✅ Local model is complete and ready to use")
        return _load_embedder(config.embedding_model_local_path, config)
    
    # Scenario 1.2: Local path exists + missing required files + troubleshooting=true
    if local_exists and not local_complete and config.troubleshooting:
        logger.warning("⚠️ Local model files are incomplete")
        trigger_troubleshooting("local_missing_files", config)
        # Try to download from HF as fallback
        if _download_from_hf_fallback(config):
            return _load_embedder(config.embedding_model_local_path, config)
        return None
    
    # Scenario 1.3: Local path exists + missing required files + troubleshooting=false
    if local_exists and not local_complete and not config.troubleshooting:
        logger.warning("⚠️ Local model files are incomplete, attempting HF download")
        if _download_from_hf_fallback(config):
            return _load_embedder(config.embedding_model_local_path, config)
        return None
    
    # Scenario 1.4: Local path doesn't exist + troubleshooting=true
    if not local_exists and config.troubleshooting:
        logger.warning("⚠️ Local model path does not exist")
        trigger_troubleshooting("local_path_not_exists", config)
        if _download_from_hf_fallback(config):
            return _load_embedder(config.embedding_model_local_path, config)
        return None
    
    # Scenario 1.5: Local path doesn't exist + troubleshooting=false
    if not local_exists and not config.troubleshooting:
        logger.warning("⚠️ Local model path does not exist, attempting HF download")
        if _download_from_hf_fallback(config):
            return _load_embedder(config.embedding_model_local_path, config)
        return None
    
    return None


def _handle_gcp_strategy_loading(state: dict, config: CanonMapEmbeddingConfig) -> Optional[Embedder]:
    """Handle loading for GCP sync strategies."""
    # Ensure bucket and prefix exist (auto-create if enabled)
    ensure_gcp_bucket_and_prefix(config)
    local_exists = state["local_exists"]
    local_complete = state["local_complete"]
    gcp_available = state["gcp_available"]
    gcp_status = state["gcp_status"]
    
    # Check GCP configuration
    if not gcp_status.get("gcp_configured", False):
        if config.troubleshooting:
            trigger_troubleshooting("gcp_auth_failed", config)
        else:
            logger.error("❌ GCP not properly configured")
        return None
    
    # Check GCP bucket
    if not gcp_status.get("bucket_exists", False):
        if config.troubleshooting:
            trigger_troubleshooting("gcp_bucket_missing", config)
        else:
            logger.error(f"❌ GCP bucket '{config.embedding_model_gcp_bucket_name}' does not exist")
        return None
    
    # Check GCP prefix - if missing but local files exist, upload them
    if not gcp_status.get("prefix_exists", False):
        if local_exists and local_complete:
            logger.info(f"📤 GCP prefix '{config.embedding_model_gcp_bucket_prefix}' missing, uploading local files to GCP")
            try:
                if upload_to_gcp(config):
                    logger.info("✅ Successfully uploaded local model files to GCP")
                    # Update state after upload
                    state = get_model_state(config)
                    gcp_status = state["gcp_status"]
                else:
                    logger.warning("⚠️ Failed to upload local files to GCP, continuing with local model")
            except Exception as e:
                logger.warning(f"⚠️ Error uploading to GCP: {e}, continuing with local model")
        else:
            if config.troubleshooting:
                trigger_troubleshooting("gcp_prefix_missing", config)
            else:
                logger.error(f"❌ GCP prefix '{config.embedding_model_gcp_bucket_prefix}' does not exist")
            return None
    
    # If we get here, GCP is available
    if local_exists and local_complete:
        logger.info("✅ Local model is complete and GCP is available")
        
        # Handle different sync strategies
        if config.embedding_model_gcp_sync_strategy in ["refresh", "overwrite"]:
            logger.info(f"🔄 Sync strategy '{config.embedding_model_gcp_sync_strategy}': downloading from GCP")
            if download_from_gcp(config):
                return _load_embedder(config.embedding_model_local_path, config)
            else:
                logger.warning("⚠️ GCP download failed, using existing local model")
                return _load_embedder(config.embedding_model_local_path, config)
        else:  # "missing" strategy
            logger.info("✅ Using existing local model (sync strategy: missing)")
            return _load_embedder(config.embedding_model_local_path, config)
    
    # Local model missing or incomplete, try GCP download
    if gcp_available:
        logger.info("📥 Downloading model from GCP...")
        if download_from_gcp(config):
            logger.info("✅ Successfully downloaded model from GCP")
            return _load_embedder(config.embedding_model_local_path, config)
        else:
            logger.error("❌ Failed to download model from GCP")
            if config.troubleshooting:
                trigger_troubleshooting("network_error", config)
            return None
    
    return None


def _download_from_hf_fallback(config: CanonMapEmbeddingConfig) -> bool:
    """Download model from Hugging Face as fallback."""
    try:
        logger.info(f"📥 Downloading model from Hugging Face: {config.embedding_model_hf_name}")
        return download_from_hf(config.embedding_model_hf_name, config.embedding_model_local_path)
    except Exception as e:
        logger.error(f"❌ Failed to download from Hugging Face: {e}")
        return False


def _load_embedder(model_path: str, config: CanonMapEmbeddingConfig) -> Optional[Embedder]:
    """Load the embedder with error handling."""
    try:
        # Validate files before loading
        file_status = validate_required_files(model_path)
        if not all(file_status.values()):
            missing_files = [k for k, v in file_status.items() if not v]
            logger.warning(f"⚠️ Some model files are missing: {missing_files}")
        
        # Try to load the embedder
        embedder = Embedder(
            model_name=model_path,
            batch_size=getattr(config, "embedding_batch_size", 1024),
            num_workers=getattr(config, "embedding_num_workers", None)
        )
        
        logger.info("✅ Embedder loaded successfully")
        return embedder
        
    except Exception as e:
        logger.error(f"❌ Failed to load embedder: {e}")
        
        # Provide specific troubleshooting for common issues
        if "permission" in str(e).lower():
            if config.troubleshooting:
                trigger_troubleshooting("permission_error", config)
        elif "disk" in str(e).lower() or "space" in str(e).lower():
            if config.troubleshooting:
                trigger_troubleshooting("disk_space_error", config)
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            if config.troubleshooting:
                trigger_troubleshooting("network_error", config)
        
        return None


def get_embedder_with_fallback(config: CanonMapEmbeddingConfig) -> Optional[Embedder]:
    """
    Get embedder with comprehensive fallback mechanisms.
    
    This function tries multiple strategies to load the embedding model:
    1. Use local model if available and complete
    2. Download from GCP if configured and available
    3. Download from Hugging Face as final fallback
    
    Args:
        config: CanonMapEmbeddingConfig instance
        
    Returns:
        Embedder instance if successful, None if all attempts fail
    """
    logger.info("🔄 Starting embedder loading with fallback mechanisms...")
    
    # Try primary loading method
    embedder = get_embedder_from_config(config)
    if embedder:
        return embedder
    
    # If primary method failed, try HF fallback regardless of strategy
    logger.info("🔄 Primary loading failed, trying Hugging Face fallback...")
    if _download_from_hf_fallback(config):
        return _load_embedder(config.embedding_model_local_path, config)
    
    logger.error("❌ All embedder loading attempts failed")
    return None 