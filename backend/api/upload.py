from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from services.s3_service import S3Service
from schemas.upload import UploadResponse
import logging

# Create an APIRouter instance for organizing routes
router = APIRouter()
# Set up a logger to track activity and errors
logger = logging.getLogger(__name__)
# Initialize the S3Service instance to handle file uploads
s3_service = S3Service()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),  # The file to be uploaded
    category: str = Form(...)      # The category of the document, provided via form
):
    """
    Endpoint to upload documents to S3 with metadata in a JSON format.
    
    This endpoint allows users to upload documents, and metadata is stored alongside the 
    file in S3. It also returns a success message along with the file URL and file ID 
    after a successful upload.

    **Parameters**:
    - `file` (UploadFile): The file to upload. This parameter is required.
    - `category` (str): A category that classifies the uploaded file. This parameter is required.

    **Returns**:
    - `UploadResponse`: A response containing a success message, file ID, URL, and filename.
    """
    try:
        logger.info(f"Upload request: {file.filename} - Category: {category}")

        # Define allowed file extensions for upload
        allowed_extensions = [".pdf", ".docx", ".txt", ".doc"]
        
        # Check if the uploaded file has a valid extension
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            logger.warning(f"Disallowed file type: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"Allowed file types: {', '.join(allowed_extensions)}"
            )

        # Read the file content asynchronously
        contents = await file.read()

        # Use the S3 service to upload the file and get metadata
        result = s3_service.upload_file(
            file_content=contents,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            category=category
        )

        # Return a response with the result of the file upload
        return UploadResponse(
            message="File uploaded successfully with metadata JSON",
            file_id=result["s3_key"],  # Unique identifier for the uploaded file
            url=result["url"],          # The URL for accessing the file
            filename=result["filename"] # The filename of the uploaded document
        )

    except Exception as e:
        # If any error occurs, log the exception and raise an HTTPException
        logger.exception("Error in /upload endpoint")
        raise HTTPException(status_code=500, detail=str(e))
