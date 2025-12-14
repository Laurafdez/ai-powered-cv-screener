import re
import boto3
import logging
import json
from typing import Dict
from config.settings import AWS_REGION

logger = logging.getLogger(__name__)

def normalize_filename(filename: str) -> str:
    """
    Normalizes the file name by performing the following transformations:
    - Converts to lowercase.
    - Replaces spaces with underscores.
    - Removes non-alphanumeric characters except for underscores and periods.
    - Keeps the file extension in lowercase.

    Args:
        filename (str): The original file name to normalize.

    Returns:
        str: The normalized file name.
    """
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
        name = name.lower().replace(" ", "_")
        name = re.sub(r"[^a-z0-9_]", "", name)
        ext = ext.lower()
        return f"{name}.{ext}"
    else:
        name = filename.lower().replace(" ", "_")
        name = re.sub(r"[^a-z0-9_]", "", name)
        return name

def extract_filename_from_uri(s3_uri: str) -> str:
    """
    Extracts the filename from the S3 URI.
    
    Args:
        s3_uri (str): The full URI of the file in S3 (e.g., "s3://bucket-name/path/to/file.pdf").
    
    Returns:
        str: The extracted filename (e.g., "file.pdf").
    """
    try:
        return s3_uri.split('/')[-1]
    except Exception as e:
        logger.exception("Error extracting filename from URI.")
        return "document"

def generate_presigned_url(s3_uri: str, expiration: int = 3600) -> str:
    """
    Generates a pre-signed URL for downloading an S3 document.
    
    Args:
        s3_uri: The S3 URI (e.g., s3://bucket-name/path/to/file.pdf).
        expiration: The expiration time in seconds (default: 1 hour).
    
    Returns:
        str: The pre-signed URL for downloading the file.
    """
    try:
        # Parse S3 URI
        if not s3_uri.startswith('s3://'):
            logger.warning(f"Invalid URI: {s3_uri}")
            return None
        
        # Extract bucket and key
        parts = s3_uri.replace('s3://', '').split('/', 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ''
        
        # Generate pre-signed URL
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
        
        logger.info(f"Pre-signed URL generated for: {s3_uri}")
        return url
        
    except Exception as e:
        logger.exception(f"Error generating pre-signed URL for {s3_uri}")
        return None
