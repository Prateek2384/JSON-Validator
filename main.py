from fastapi import FastAPI, Request, UploadFile, HTTPException, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from core.services import MCPService
from infrastructure.file_handlers.init import TextExtractorFactory
from core.entities import ValidationResult
# used for initialising config and logging
from infrastructure.config.config_manager import ConfigManager
from infrastructure.logging.logger import Logger
import json
import re
from typing import List

# Used for creating FastApi
app = FastAPI(
    title="MCP Validator API",
    description="",
    version="1.0.0"
)
# It is used for setting up templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")



config = ConfigManager()
logger = Logger(
    name="mcp_validator",
    log_path=config.get_log_path(),
    enabled=config.logger_config.get("enabled", True)
).logger
#It checks whether it contains the BEGIN_KNOWLEDGE AND END_KNOWLEDGE blocks or not.
class JSONBlockExtractor:
    
    def extract_blocks(self, content: str) -> List[str]:
        pattern = re.compile(
            r"BEGIN_KNOWLEDGE\s*(\{(?:[^{}]|(?:\{.*?\}))*\})\s*END_KNOWLEDGE",
            re.DOTALL
        )
        blocks = []
        for match in pattern.finditer(content):
            try:
                json.loads(match.group(1))  # Validate JSON first
                blocks.append(match.group(1).strip())
                logger.debug(f"Found valid JSON block: {match.group(1)[:50]}...")
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON block skipped: {str(e)}")
        return blocks

class JSONValidator:
    
    
    def validate(self, content: str) -> bool:
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError as e:
            logger.warning(f"JSON validation failed: {str(e)}")
            return False


service = MCPService(
    file_handler=TextExtractorFactory,
    block_extractor=JSONBlockExtractor(),
    validator=JSONValidator()
)

@app.post(
    "/validate-mcp/",
    response_model=ValidationResult,
    summary="",
    responses={
        400: {"description": config.get_error_message(400)},
        413: {"description": config.get_error_message(413)},
        415: {"description": config.get_error_message(415)},
        422: {"description": config.get_error_message(422)},
        500: {"description": config.get_error_message(500)}
    }
)
async def validate_mcp(file: UploadFile = File(...)) -> ValidationResult:
    
    try:
        logger.info(f"Processing file: {file.filename}")
        result = await service.validate_mcp(file)
        
        if result.blocks_found == 0:
            logger.warning("No valid JSON blocks found")
            raise HTTPException(
                status_code=400,
                detail=config.get_error_message(400)
            )

        return result

    except ValueError as e:
        logger.error(f"Unsupported file type: {str(e)}")
        raise HTTPException(
            status_code=415,
            detail=config.get_error_message(415)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"Validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=config.get_error_message(500)
        )

@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/upload")

@app.get("/upload", response_class=HTMLResponse)
async def pretty_upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})