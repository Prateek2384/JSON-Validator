import json
from fastapi import HTTPException, UploadFile
from core.interfaces import ITextExtractor

class JSONTextExtractor(ITextExtractor):
    async def extract_text(self, file: UploadFile) -> str:
        try:
            content = (await file.read()).decode('utf-8')
            json.loads(content)  
            return content
        except json.JSONDecodeError as e:
            raise HTTPException(400, f"Invalid JSON: {str(e)}")
        except Exception as e:
            raise HTTPException(400, f"JSON processing failed: {str(e)}")

    @staticmethod
    def supports(file: UploadFile) -> bool:
        return (
            file.filename.lower().endswith('.json') or
            file.content_type == "application/json"
        )