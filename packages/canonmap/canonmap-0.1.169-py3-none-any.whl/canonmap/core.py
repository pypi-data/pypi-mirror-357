# canonmap/core.py

import logging
from typing import Dict, Any, Optional
from functools import lru_cache
from pathlib import Path

from canonmap.models.requests.artifact_generation_request import ArtifactGenerationRequest
from canonmap.models.requests.artifact_unpacking_request import ArtifactUnpackingRequest
from canonmap.models.requests.entity_mapping_request import EntityMappingRequest
from canonmap.utils.logger import _loggers, get_logger
from canonmap.utils.file_utils import find_artifact_files, find_unpackable_files
from canonmap.utils.load_spacy_model import load_spacy_model
from canonmap.utils.model_loader import FlexibleModelLoader
from canonmap.embedder import Embedder
from canonmap.config import CanonMapConfig
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.neighbors import NearestNeighbors
import pickle

logger = get_logger("core")

def _apply_verbosity(verbose: bool):
    """
    Flip the level on the root logger (for stdlib & 3rd-party) and all
    of our own canonmap.* loggers between WARNING and INFO.
    """
    root_level = logging.INFO if verbose else logging.WARNING
    logging.getLogger().setLevel(root_level)

    our_level = logging.INFO if verbose else logging.WARNING
    for lg in _loggers.values():
        lg.setLevel(our_level)

class CanonMap:
    """
    Public façade for canonmap.
    artifacts_path may be None if you only ever call .generate().
    """
    def __init__(
        self, 
        artifacts_path: Optional[str] = None, 
        verbose: bool = False, 
        lazy_load: bool = False,
        # New parameters for flexible model loading
        model_dir: Optional[str] = None,
        spacy_model_dir: Optional[str] = None,
        offline_mode: Optional[bool] = None,
        config: Optional[CanonMapConfig] = None,
        sentence_transformer_model: str = "all-MiniLM-L6-v2",
        spacy_model: str = "en_core_web_sm"
    ):
        # Initialize configuration
        self.config = config or CanonMapConfig()
        
        # Override config with constructor parameters
        if model_dir:
            self.config.model_dir = Path(model_dir)
        if spacy_model_dir:
            self.config.spacy_model_dir = Path(spacy_model_dir)
        if offline_mode is not None:
            self.config.offline_mode = offline_mode
        if sentence_transformer_model:
            self.config.sentence_transformer_model = sentence_transformer_model
        if spacy_model:
            self.config.spacy_model = spacy_model
        
        # Initialize model loader
        self.model_loader = FlexibleModelLoader(self.config)
        
        # global default verbosity
        self.default_verbose = verbose
        self.base_artifacts_path = artifacts_path
        self.lazy_load = lazy_load
        
        # Pre-load heavy components if not lazy loading
        if not self.lazy_load:
            self._embedder()
            self._nlp()

    def _artifact_files(self, path: Optional[str] = None) -> dict:
        """
        Look up the schema/.pkl/.npz files under the given path.
        If no `path` is passed, falls back to the instance's base_artifacts_path.
        """
        target = path or self.base_artifacts_path
        if target is None:
            raise ValueError("No artifacts path provided for locating artifact files.")
        return find_artifact_files(target)

    @lru_cache()
    def _embedder(self):
        return Embedder(
            model_name=self.config.sentence_transformer_model,
            model_loader=self.model_loader
        )

    @lru_cache()
    def _nlp(self):
        return load_spacy_model(
            model_name=self.config.spacy_model,
            model_loader=self.model_loader
        )

    def _canonical_entities(self, path: Optional[str] = None):
        files = self._artifact_files(path)
        with open(files["canonical_entities"], "rb") as f:
            return pickle.load(f)

    def _embeddings(self, path: Optional[str] = None):
        files = self._artifact_files(path)
        arr = np.load(files["canonical_entity_embeddings"])[
            "embeddings"
        ]
        return normalize(arr.astype("float32"), axis=1)

    def _nn_index(self, path: Optional[str] = None):
        ents = self._canonical_entities(path)
        k = min(50, len(ents))
        nn = NearestNeighbors(n_neighbors=k, metric="cosine")
        nn.fit(self._embeddings(path))
        return nn

    def generate(self, config: ArtifactGenerationRequest) -> Dict[str, Any]:
        v = config.verbose if config.verbose is not None else self.default_verbose
        _apply_verbosity(v)
        logger.info(f"Starting generation (verbose={v})")
        from canonmap.services.artifact_generator import ArtifactGenerator
        generator = ArtifactGenerator(
            embedder=self._embedder(),
            nlp=self._nlp(),
        )
        return generator.generate_artifacts(config)

    def unpack(self, config: ArtifactUnpackingRequest) -> Dict[str, Any]:
        # 1) if user didn't give an input_path, fall back to the instance-level one
        if config.input_path is None:
            if self.base_artifacts_path is None:
                raise ValueError("Cannot unpack: no input_path was provided to CanonMap")
            config.input_path = self.base_artifacts_path

        # 2) now toggle verbosity and dispatch
        v = config.verbose if config.verbose is not None else self.default_verbose
        _apply_verbosity(v)
        logger.info(f"Starting unpack (verbose={v})")
        artifact_paths = find_unpackable_files(str(config.input_path))
        from canonmap.services.artifact_unpacker import ArtifactUnpacker
        unpacker = ArtifactUnpacker(artifact_files=artifact_paths)
        return unpacker.unpack_artifacts(config)

    def map_entities(self, config: EntityMappingRequest) -> Any:
        if config.artifacts_path is None:
            if self.base_artifacts_path is None:
                raise ValueError("Cannot map: no artifacts_path was provided to CanonMap")
            config.artifacts_path = self.base_artifacts_path
        v = config.verbose if config.verbose is not None else self.default_verbose
        _apply_verbosity(v)
        logger.info(f"Starting mapping (verbose={v})")
        from canonmap.services.entity_mapper import EntityMapper
        mapper = EntityMapper(
            embedder=self._embedder(),
            canonical_entities=self._canonical_entities(config.artifacts_path),
            embeddings=self._embeddings(config.artifacts_path),
            nn=self._nn_index(config.artifacts_path),
        )
        return mapper.map_entities(config)