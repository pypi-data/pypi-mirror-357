from pathlib import Path
import logging
import os
import sys
import subprocess
from typing import Any, Optional, Union
from sentence_transformers import SentenceTransformer
import spacy

from canonmap.utils.logger import get_logger

logger = get_logger("model_loader")

class FlexibleModelLoader:
    def __init__(self, config):
        self.config = config
        self.logger = logger
    
    def load_sentence_transformer(self, model_name: str = None) -> SentenceTransformer:
        """Load SentenceTransformer model with fallback strategy"""
        model_name = model_name or self.config.sentence_transformer_model
        
        # Strategy 1: Try local model directory first
        local_path = self.config.model_dir / "sentence-transformers" / model_name
        if local_path.exists():
            self.logger.info(f"Loading SentenceTransformer from local directory: {local_path}")
            return self._load_sentence_transformer_from_local(local_path)
        
        # Strategy 2: Try HuggingFace cache
        hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
        hf_model_path = hf_cache / f"models--{model_name.replace('/', '--')}"
        if hf_cache.exists() and hf_model_path.exists():
            self.logger.info(f"Loading SentenceTransformer from HuggingFace cache: {hf_model_path}")
            return self._load_sentence_transformer_from_local(hf_model_path)
        
        # Strategy 3: Download from HuggingFace (if not offline)
        if not self.config.offline_mode:
            self.logger.info(f"Downloading SentenceTransformer from HuggingFace: {model_name}")
            return self._download_and_cache_sentence_transformer(model_name)
        
        # Strategy 4: Fail gracefully
        raise FileNotFoundError(
            f"SentenceTransformer model {model_name} not found locally and offline mode is enabled. "
            f"Please ensure model files are in {self.config.model_dir} or set CANONMAP_OFFLINE_MODE=false"
        )
    
    def load_spacy_model(self, model_name: str = None) -> Any:
        """Load spaCy model with fallback strategy"""
        model_name = model_name or self.config.spacy_model
        
        # Strategy 1: Try local spaCy model directory first
        local_path = self.config.spacy_model_dir / model_name
        if local_path.exists():
            self.logger.info(f"Loading spaCy model from local directory: {local_path}")
            return self._load_spacy_from_local(local_path)
        
        # Strategy 2: Try spaCy's default location
        try:
            model = spacy.load(model_name)
            self.logger.info(f"Successfully loaded spaCy model '{model_name}' from default location")
            return model
        except OSError:
            pass
        
        # Strategy 3: Download spaCy model (if not offline)
        if not self.config.offline_mode:
            self.logger.info(f"Downloading spaCy model: {model_name}")
            return self._download_and_cache_spacy_model(model_name)
        
        # Strategy 4: Fail gracefully
        raise FileNotFoundError(
            f"spaCy model {model_name} not found locally and offline mode is enabled. "
            f"Please ensure model files are in {self.config.spacy_model_dir} or set CANONMAP_OFFLINE_MODE=false"
        )
    
    def _load_sentence_transformer_from_local(self, model_path: Path) -> SentenceTransformer:
        """Load SentenceTransformer from local filesystem"""
        try:
            return SentenceTransformer(str(model_path))
        except Exception as e:
            self.logger.warning(f"Failed to load SentenceTransformer from {model_path}: {e}")
            raise
    
    def _load_spacy_from_local(self, model_path: Path) -> Any:
        """Load spaCy model from local filesystem"""
        try:
            return spacy.load(str(model_path))
        except Exception as e:
            self.logger.warning(f"Failed to load spaCy model from {model_path}: {e}")
            raise
    
    def _download_and_cache_sentence_transformer(self, model_name: str) -> SentenceTransformer:
        """Download SentenceTransformer and cache it locally"""
        # Temporarily disable offline mode for download
        original_offline = os.environ.get("HUGGINGFACE_HUB_OFFLINE", "1")
        os.environ["HUGGINGFACE_HUB_OFFLINE"] = "0"
        
        try:
            model = SentenceTransformer(model_name)
            
            # Cache the model to our preferred location
            cache_path = self.config.model_dir / "sentence-transformers" / model_name
            cache_path.mkdir(parents=True, exist_ok=True)
            
            # Save model to our cache
            model.save(str(cache_path))
            self.logger.info(f"SentenceTransformer model cached to: {cache_path}")
            
            return model
        finally:
            # Restore offline mode
            os.environ["HUGGINGFACE_HUB_OFFLINE"] = original_offline
    
    def _download_and_cache_spacy_model(self, model_name: str) -> Any:
        """Download spaCy model and cache it locally"""
        try:
            # Download using spaCy CLI
            cmd = [sys.executable, "-m", "spacy", "download", model_name]
            subprocess.run(cmd, check=True)
            
            # Load the downloaded model
            model = spacy.load(model_name)
            self.logger.info(f"spaCy model '{model_name}' downloaded and loaded successfully")
            
            return model
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to download spaCy model {model_name}: {e}")
            raise 