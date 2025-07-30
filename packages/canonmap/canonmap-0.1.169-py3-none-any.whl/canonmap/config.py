# canonmap/config.py
import os
from pathlib import Path
from typing import Optional, Union

class CanonMapConfig:
    def __init__(self):
        # Dynamic project root detection
        self.project_root = Path(__file__).parent.parent
        
        # Environment-based overrides
        model_dir_env = os.getenv("CANONMAP_MODEL_DIR", str(self.project_root / "models"))
        spacy_model_dir_env = os.getenv("CANONMAP_SPACY_MODEL_DIR", str(self.project_root / "spacy_models"))
        artifacts_dir_env = os.getenv("CANONMAP_ARTIFACTS_DIR", str(self.project_root / "artifacts"))
        
        # Initialize private attributes
        self._model_dir = Path(model_dir_env)
        self._spacy_model_dir = Path(spacy_model_dir_env)
        self._artifacts_dir = Path(artifacts_dir_env)
        
        self.offline_mode = os.getenv("CANONMAP_OFFLINE_MODE", "false").lower() == "true"
        
        # Model names from environment
        self.sentence_transformer_model = os.getenv("CANONMAP_SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
        self.spacy_model = os.getenv("CANONMAP_SPACY_MODEL", "en_core_web_sm")
        
        # Ensure directories exist
        self._model_dir.mkdir(parents=True, exist_ok=True)
        self._spacy_model_dir.mkdir(parents=True, exist_ok=True)
        self._artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def model_dir(self) -> Path:
        return self._model_dir
    
    @model_dir.setter
    def model_dir(self, value: Union[str, Path]):
        self._model_dir = Path(value) if isinstance(value, str) else value
    
    @property
    def spacy_model_dir(self) -> Path:
        return self._spacy_model_dir
    
    @spacy_model_dir.setter
    def spacy_model_dir(self, value: Union[str, Path]):
        self._spacy_model_dir = Path(value) if isinstance(value, str) else value
    
    @property
    def artifacts_dir(self) -> Path:
        return self._artifacts_dir
    
    @artifacts_dir.setter
    def artifacts_dir(self, value: Union[str, Path]):
        self._artifacts_dir = Path(value) if isinstance(value, str) else value 