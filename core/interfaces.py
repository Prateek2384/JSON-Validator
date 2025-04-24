from abc import ABC, abstractmethod
from fastapi import UploadFile
from typing import List, Optional

#Used for extracting text content from a file
class ITextExtractor(ABC):
    @abstractmethod
    async def extract_text(self, file: UploadFile) -> str:
        pass

    @staticmethod
    @abstractmethod
    #It checks whether extractor supports the file type or not
    def supports(file: UploadFile) -> bool:
        pass
class IFileHandler(ABC):
    @abstractmethod
    async def extract_text(self, file: UploadFile) -> str:
        pass

    @staticmethod
    @abstractmethod
    def supports(file: UploadFile) -> bool:
        pass

class IBlockExtractor(ABC):
    @abstractmethod
    def extract_blocks(self, content: str) -> List[str]:
        pass

class IValidator(ABC):
    @abstractmethod
    def validate(self, content: str) -> bool:
        pass