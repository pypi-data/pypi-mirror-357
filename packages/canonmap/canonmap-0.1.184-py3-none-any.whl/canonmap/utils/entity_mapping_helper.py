import logging
import pickle
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List

from canonmap.logger import setup_logger
from canonmap.config import CanonMapArtifactsConfig
from canonmap.requests.entity_mapping_request import EntityMappingRequest
from canonmap.requests.entity_mapping_response import EntityMappingResponse, SingleMapping, MatchItem
from canonmap.entity_mapping_service import EntityMapper
from canonmap.utils.get_files_from_gcs import get_files_from_gcs

logger = setup_logger()


def map_entities_helper(
    request: EntityMappingRequest,
    artifacts_config: CanonMapArtifactsConfig,
    embedder: Any,
) -> Dict[str, Any]:
    """
    Map entities using the existing artifacts and embedder.
    
    Args:
        request: EntityMappingRequest specifying what to map
        artifacts_config: CanonMapArtifactsConfig for artifact storage settings
        embedder: Embedding model instance
        
    Returns:
        Dict containing mapping results and metadata
        
    Raises:
        FileNotFoundError: If artifacts don't exist
        ValueError: If request validation fails
        Exception: If mapping process fails
    """
    
    # Use artifacts_config for storage settings
    artifacts_path = Path(artifacts_config.artifacts_local_path)
    
    if not artifacts_path.exists():
        raise FileNotFoundError(f"Artifacts path does not exist: {artifacts_path}")
    
    logger.info(f"Loading artifacts from: {artifacts_path}")
    
    # Load canonical entities
    canonical_entities_path = artifacts_path / "canonical_entities.pkl"
    if not canonical_entities_path.exists():
        # Try alternative naming patterns
        potential_paths = [
            artifacts_path / "canonical_entities.pkl",
            artifacts_path / "football-data_canonical_entities.pkl",
            artifacts_path / "data_canonical_entities.pkl",
        ]
        
        canonical_entities_path = None
        for path in potential_paths:
            if path.exists():
                canonical_entities_path = path
                break
        
        if not canonical_entities_path:
            raise FileNotFoundError(f"No canonical entities file found in {artifacts_path}")
    
    with open(canonical_entities_path, "rb") as f:
        canonical_entities = pickle.load(f)
    
    logger.info(f"Loaded {len(canonical_entities)} canonical entities")
    
    # Load embeddings if available and semantic search is requested
    embeddings = None
    nn = None
    
    if request.use_semantic_search and embedder:
        embeddings_path = artifacts_path / "canonical_entity_embeddings.npz"
        if not embeddings_path.exists():
            # Try alternative naming patterns
            potential_emb_paths = [
                artifacts_path / "canonical_entity_embeddings.npz",
                artifacts_path / "football-data_canonical_entity_embeddings.npz",
                artifacts_path / "data_canonical_entity_embeddings.npz",
            ]
            
            embeddings_path = None
            for path in potential_emb_paths:
                if path.exists():
                    embeddings_path = path
                    break
        
        if embeddings_path and embeddings_path.exists():
            embeddings_data = np.load(embeddings_path)
            embeddings = embeddings_data['embeddings']
            logger.info(f"Loaded embeddings with shape: {embeddings.shape}")
            
            # Build nearest neighbors index for semantic search
            from sklearn.neighbors import NearestNeighbors
            nn = NearestNeighbors(n_neighbors=min(50, len(embeddings)), metric='cosine')
            nn.fit(embeddings)
            logger.info("Built nearest neighbors index for semantic search")
        else:
            logger.warning("Semantic search requested but no embeddings found. Falling back to fuzzy matching only.")
            request.use_semantic_search = False
    
    # Initialize the entity mapper
    mapper = EntityMapper(
        embedder=embedder,
        canonical_entities=canonical_entities,
        embeddings=embeddings,
        nn=nn,
    )
    
    # Perform entity mapping
    logger.info(f"Mapping {len(request.entities)} entities...")
    response = mapper.map_entities(request)
    
    logger.info("Entity mapping completed successfully")
    
    # Convert response to dictionary format for consistency with other helpers
    return {
        "status": "success",
        "message": f"Successfully mapped {len(request.entities)} entities",
        "results": [
            {
                "query": result.query,
                "matches": [
                    {
                        "entity": match.entity,
                        "score": match.score,
                        "passes": match.passes,
                        "metadata": match.metadata
                    }
                    for match in result.matches
                ]
            }
            for result in response.results
        ],
        "total_entities_mapped": len(request.entities),
        "total_matches_found": sum(len(result.matches) for result in response.results),
    } 