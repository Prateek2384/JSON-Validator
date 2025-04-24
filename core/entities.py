from pydantic import BaseModel
from typing import List, Dict, Optional

class BlockResult(BaseModel):
    block_number: int
    valid: bool
    content: str
    error: Optional[str] = None

class ValidationResult(BaseModel):
    file_type: str
    blocks_found: int
    valid_blocks: int
    invalid_blocks: int
    results: List[BlockResult]