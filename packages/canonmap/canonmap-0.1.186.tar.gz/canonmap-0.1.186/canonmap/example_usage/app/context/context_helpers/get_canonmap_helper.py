from canonmap import (
    CanonMap,
    CanonMapEmbeddingConfig,
    CanonMapArtifactsConfig
)

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_canonmap():
    artifacts_config = CanonMapArtifactsConfig(
        artifacts_local_path="artifacts",
        artifacts_gcp_service_account_json_path="dev_service_account.json",
        artifacts_gcp_bucket_name="keenai-test-bucket",
        artifacts_gcp_bucket_prefix="artifacts",
        artifacts_gcp_auto_create_bucket=True,
        artifacts_gcp_auto_create_bucket_prefix=True,
        artifacts_gcp_sync_strategy="refresh",  # options: "none", "missing", "overwrite", "refresh"
        troubleshooting=True,
    )

    embedding_config = CanonMapEmbeddingConfig(
        embedding_model_hf_name="sentence-transformers/all-MiniLM-L12-v2",
        embedding_model_local_path="models/sentence-transformers/all-MiniLM-L12-v2",
        embedding_model_gcp_service_account_json_path="dev_service_account.json",
        embedding_model_gcp_bucket_name="keenai-test-bucket",
        embedding_model_gcp_bucket_prefix="models/sentence-transformers/all-MiniLM-L12-v2",
        embedding_model_gcp_auto_create_bucket=True,
        embedding_model_gcp_auto_create_bucket_prefix=True,
        embedding_model_gcp_sync_strategy="refresh",  # options: "none", "missing", "overwrite", "refresh"
        troubleshooting=True,
    )

    canonmap = CanonMap(
        artifacts_config=artifacts_config,
        embedding_config=embedding_config,
        verbose=True,
    )
    logger.info("CanonMap initialized")
    return canonmap
