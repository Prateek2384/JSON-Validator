import fitz  
from fastapi import HTTPException, UploadFile
from core.interfaces import ITextExtractor

class PDFTextExtractor(ITextExtractor):
    async def extract_text(self, file: UploadFile) -> str:
        try:
            doc = fitz.open(stream=await file.read(), filetype="pdf")
            return "".join(page.get_text() for page in doc)
        except Exception as e:
            raise HTTPException(400, f"PDF processing failed: {str(e)}")

    @staticmethod
    def supports(file: UploadFile) -> bool:
        return (
            file.filename.lower().endswith('.pdf') or
            file.content_type == "application/pdf"
        )