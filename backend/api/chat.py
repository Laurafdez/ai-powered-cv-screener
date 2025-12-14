from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.retriever_service import retriever_function
import logging
from schemas.chat import ChatRequest, ChatResponse

# Initialize the APIRouter instance for the chat endpoint
router = APIRouter()
# Set up the logger to track activity and errors
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to process chat queries and return answers with citations included.

    **Parameters**:
    - `request` (ChatRequest): The request body that contains the user's query and an optional category.

    **Returns**:
    - `ChatResponse`: A response containing the generated answer, which includes citations.
    """
    try:
        # Log the incoming chat request message and category
        logger.info(f"Chat request: {request.message} - Category: {request.category}")
        
        # Call the retriever function to retrieve documents and generate an answer
        result = retriever_function(
            query=request.message,  # The message from the user
            category=request.category  # The optional category to filter the documents
        )
        
        # Extract the 'answer' from the result, which contains both the answer and formatted citations
        answer_text = result.get("answer", "")
        
        # Return the response in the ChatResponse format
        return ChatResponse(response=answer_text)
        
    except Exception as e:
        # If any error occurs, log it and raise an HTTP exception with a 500 status code
        logger.exception("Error in /chat endpoint")
        raise HTTPException(status_code=500, detail=str(e))
