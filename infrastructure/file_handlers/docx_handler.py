from docx import Document
import io
from fastapi import HTTPException, UploadFile
from core.interfaces import ITextExtractor

class DOCXTextExtractor(ITextExtractor):
    async def extract_text(self, file: UploadFile) -> str:
        try:
            doc = Document(io.BytesIO(await file.read()))
            return "\n".join(para.text for para in doc.paragraphs)
        except Exception as e:
            raise HTTPException(400, f"DOCX processing failed: {str(e)}")

    @staticmethod
    def supports(file: UploadFile) -> bool:
        return (
            file.filename.lower().endswith('.docx') or
            file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )