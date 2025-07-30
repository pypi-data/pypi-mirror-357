# canonmap/utils/load_spacy_model.py
# Utility module for loading spaCy NLP models

import spacy
import sys
import subprocess
import logging

from canonmap.utils.logger import get_logger

logger = get_logger("load_spacy_model")

def load_spacy_model(model_name: str = "en_core_web_sm", model_loader=None):
    """
    Load a spaCy model using flexible model loading.
    
    Args:
        model_name: Name of the spaCy model to load
        model_loader: Optional FlexibleModelLoader instance
        
    Returns:
        spacy.language.Language: Loaded spaCy model
    """
    logger.info(f"Attempting to load spaCy model '{model_name}'")
    
    if model_loader:
        # Use flexible model loader if provided
        return model_loader.load_spacy_model(model_name)
    else:
        # Fallback to original behavior (backward compatibility)
        try:
            model = spacy.load(model_name)
            logger.info(f"Successfully loaded spaCy model '{model_name}'")
            return model
        except OSError:
            logger.info(f"spaCy model '{model_name}' not found locally; downloading...")
            cmd = [sys.executable, "-m", "spacy", "download", model_name]
            subprocess.run(cmd, check=True)
            logger.info(f"Download complete. Loading spaCy model '{model_name}'...")
            model = spacy.load(model_name)
            logger.info(f"Successfully loaded downloaded spaCy model '{model_name}'")
            return model