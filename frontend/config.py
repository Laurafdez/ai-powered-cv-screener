import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# API URLs
UPLOAD_URL = os.getenv("UPLOAD_URL", "http://localhost:8000/api/upload")  # Default to local if not set
CHAT_URL = os.getenv("CHAT_URL", "http://localhost:8000/api/chat")      # Default to local if not set

# Available roles in the system
ROLES = [
    "Data Scientist",    # Data analysis experts
    "Product Manager",   # Oversees product development
    "Security Engineer", # Focused on system security
    "Legal Counsel"      # Provides legal guidance
]

