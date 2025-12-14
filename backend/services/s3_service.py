import boto3
import json
from datetime import datetime
from config.settings import AWS_REGION, S3_BUCKET_NAME, S3_PREFIX
from utils.utils import normalize_filename
import logging

logger = logging.getLogger(__name__)

class S3Service:
    """
    S3Service handles file uploads and metadata management for files stored in Amazon S3.
    It allows for file uploads, including generating metadata files and creating file URLs.
    """

    def __init__(self, prefix: str = S3_PREFIX):
        """
        Initializes the S3Service instance, setting up the S3 client with AWS credentials and the specified S3 prefix.

        Args:
            prefix (str): The S3 prefix for organizing uploaded files (default is from settings).
        """
        self.s3_client = boto3.client('s3', region_name=AWS_REGION)
        self.bucket_name = S3_BUCKET_NAME
        self.prefix = prefix
        logger.info(f"S3Service initialized with bucket '{self.bucket_name}' and prefix '{self.prefix}'")

    def upload_file(self, file_content: bytes, filename: str, content_type: str = None, category: str = None) -> dict:
        """
        Uploads a file to S3, creates a metadata file (.metadata.json) and returns the S3 URL.

        Args:
            file_content (bytes): The content of the file to upload.
            filename (str): The name of the file to upload.
            content_type (str, optional): The MIME type of the file (default is "application/octet-stream").
            category (str, optional): The category to associate with the file for metadata purposes.

        Returns:
            dict: A dictionary containing the S3 key, file URL, and normalized filename.
        """
        try:
            # Normalize the file name using the utility function
            normalized_filename = normalize_filename(filename)
            s3_key = f"{self.prefix}{normalized_filename}"

            # Upload the main file
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type or "application/octet-stream",
                Metadata={
                    "original_filename": normalized_filename,
                    "uploaded_at": datetime.utcnow().isoformat()
                }
            )
            logger.info(f"File uploaded: {s3_key}")

            # Create metadata JSON file
            metadata = {
                "metadataAttributes": {
                    "category": category
                }
            }
            json_key = f"{self.prefix}{normalized_filename}.metadata.json"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=json_key,
                Body=json.dumps(metadata),
                ContentType="application/json"
            )
            logger.info(f"Metadata JSON uploaded: {json_key}")

            # Generate file URL
            file_url = f"https://{self.bucket_name}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
            return {"s3_key": s3_key, "url": file_url, "filename": normalized_filename}

        except Exception as e:
            logger.exception(f"Error uploading file '{filename}'.")
            raise e
