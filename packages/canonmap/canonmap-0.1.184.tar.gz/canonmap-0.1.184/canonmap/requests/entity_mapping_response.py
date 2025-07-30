from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class MatchItem(BaseModel):
    """A single match result for an entity."""
    entity: str
    score: float
    passes: int
    metadata: Dict[str, Any]

class SingleMapping(BaseModel):
    """Mapping results for a single input entity."""
    query: str
    matches: List[MatchItem]

class EntityMappingResponse(BaseModel):
    """Response containing all entity mapping results."""
    results: List[SingleMapping] 