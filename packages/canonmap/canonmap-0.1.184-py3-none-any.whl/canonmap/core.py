import logging
import pickle
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List

from canonmap.logger import setup_logger
from canonmap.config import CanonMapArtifactsConfig, CanonMapEmbeddingConfig
from canonmap.utils.get_files_from_gcs import get_files_from_gcs
from canonmap.requests.artifact_generation_request import ArtifactGenerationRequest
from canonmap.utils.convert_input import convert_data_to_df
from canonmap.utils.process_table import process_table
from canonmap.utils.clean_columns import clean_and_format_columns
from canonmap.utils.infer_schema import generate_db_schema_from_df
from canonmap.utils.canonical_entities_generator import generate_canonical_entities
from canonmap.utils.generate_mariadb_loader_script import generate_mariadb_loader_script
from canonmap.utils.embedding_model_factory import get_embedder_with_fallback
from canonmap.utils.artifact_validation import upload_artifacts_to_gcs
from canonmap.utils.artifact_generation_helper import generate_artifacts_helper
from canonmap.utils.entity_mapping_helper import map_entities_helper
from canonmap.requests.entity_mapping_request import EntityMappingRequest
from canonmap.entity_mapping_service import EntityMapper

logger = setup_logger()

class CanonMap:
    def __init__(
        self,
        artifacts_config: CanonMapArtifactsConfig,
        embedding_config: CanonMapEmbeddingConfig,
        verbose: bool = False,
    ):
        self.verbose = verbose
        level = logging.INFO if self.verbose else logging.WARNING
        logging.getLogger('canonmap').setLevel(level)

        self.artifacts_config = artifacts_config
        self.embedding_config = embedding_config
        
        # Use comprehensive embedder loading with fallback
        self.embedder = get_embedder_with_fallback(self.embedding_config)
        if not self.embedder:
            logger.warning("Embedding model could not be loaded. Semantic search will be disabled.")

        # Validate artifacts configuration
        try:
            self.artifacts_config.validate_artifacts(self.artifacts_config.troubleshooting)
        except (FileNotFoundError, PermissionError) as e:
            logger.warning(f"Artifacts integration disabled due to configuration issues: {e}")

        # Validate embedding configuration
        try:
            self.embedding_config.validate_embedding_model(self.embedding_config.troubleshooting)
        except (FileNotFoundError, PermissionError) as e:
            logger.warning(f"Embedding integration disabled due to configuration issues: {e}")


    def generate_artifacts(self, request: ArtifactGenerationRequest) -> Dict[str, Any]:
        """
        Generate artifacts based on the request and current configuration.
        
        Args:
            request: ArtifactGenerationRequest specifying what to generate
            
        Returns:
            Dict containing generation results and metadata
            
        Raises:
            ValueError: If request validation fails
            FileNotFoundError: If input path doesn't exist
            Exception: If generation process fails
        """
        return generate_artifacts_helper(
            request=request,
            artifacts_config=self.artifacts_config,
            embedder=self.embedder,
        )
    


    def map_entities(self, request: EntityMappingRequest) -> Dict[str, Any]:
        """
        Map entities using the existing artifacts and embedder.
        
        Args:
            request: EntityMappingRequest specifying what to map
            
        Returns:
            Dict containing mapping results and metadata
            
        Raises:
            FileNotFoundError: If artifacts don't exist
            ValueError: If request validation fails
            Exception: If mapping process fails
        """
        return map_entities_helper(
            request=request,
            artifacts_config=self.artifacts_config,
            embedder=self.embedder,
        )