from typing import List
from core.interfaces import IBlockExtractor, IValidator
from core.entities import ValidationResult, BlockResult
from fastapi import UploadFile

from infrastructure.file_handlers.init import TextExtractorFactory

class MCPService:
    def __init__(
        self,
        file_handler: type[TextExtractorFactory],  
        block_extractor: IBlockExtractor,
        validator: IValidator
    ):
        self.extractor_factory = file_handler
        self.block_extractor = block_extractor
        self.validator = validator

    async def validate_mcp(self, file: UploadFile) -> ValidationResult:
        extractor = self.extractor_factory.get_extractor(file)
        content = await extractor.extract_text(file) 
        
        blocks = self.block_extractor.extract_blocks(content)
        
        results = []
        for idx, block in enumerate(blocks, 1):
            is_valid = self.validator.validate(block)
            results.append(BlockResult(
                block_number=idx,
                valid=is_valid,
                content=block,
                error=None if is_valid else "Invalid JSON"
            ))

        return ValidationResult(
            file_type=file.content_type,
            blocks_found=len(blocks),
            valid_blocks=sum(1 for r in results if r.valid),
            invalid_blocks=sum(1 for r in results if not r.valid),
            results=results
        )