from pydantic import BaseModel

class ChatRequest(BaseModel):
    """
    Model representing the request to the chat service.
    
    Attributes:
        message (str): The message content sent by the user.
        category (str, optional): The category to classify the message. Defaults to None.
    """
    message: str
    category: str = None

class ChatResponse(BaseModel):
    """
    Model representing the response from the chat service.
    
    Attributes:
        response (str): The response message to return to the user.
    """
    response: str
