from pydantic import BaseModel

class UploadResponse(BaseModel):
    """
    Model representing the response after a file upload.

    Attributes:
        message (str): A message providing feedback on the upload status.
        file_id (str): A unique identifier for the uploaded file.
        url (str): The URL where the uploaded file can be accessed.
        filename (str): The name of the uploaded file.
    """
    message: str
    file_id: str
    url: str
    filename: str
