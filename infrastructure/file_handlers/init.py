from .docx_handler import DOCXTextExtractor
from .pdf_handler import PDFTextExtractor
from .txt_handler import TXTTextExtractor
from .json_handler import JSONTextExtractor
from core.interfaces import ITextExtractor
from fastapi import UploadFile

class TextExtractorFactory:
    """Factory for creating appropriate file handlers"""
    
    _extractors = [
        DOCXTextExtractor(),
        PDFTextExtractor(),
        TXTTextExtractor(),
        JSONTextExtractor()
    ]

    @classmethod
    def get_extractor(cls, file: UploadFile) -> ITextExtractor:
        """Get the appropriate extractor for the file type"""
        for extractor in cls._extractors:
            if extractor.supports(file):
                return extractor
        raise ValueError(f"Unsupported file type: {file.content_type}")