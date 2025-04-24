from fastapi import HTTPException, UploadFile
from core.interfaces import ITextExtractor

class TXTTextExtractor(ITextExtractor):
    async def extract_text(self, file: UploadFile) -> str:
        try:
            return (await file.read()).decode('utf-8')
        except Exception as e:
            raise HTTPException(400, f"Text file processing failed: {str(e)}")

    @staticmethod
    def supports(file: UploadFile) -> bool:
        return (
            file.filename.lower().endswith('.txt') or
            file.content_type == "text/plain"
        )