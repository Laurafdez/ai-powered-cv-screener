from dotenv import load_dotenv
import os

load_dotenv() 

# AWS
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_PREFIX = os.getenv("S3_PREFIX", "uploads/dev/")

# Bedrock
BEDROCK_MODEL = os.getenv("BEDROCK_MODEL", "anthropic.claude-v2")
BEDROCK_MAX_TOKENS = int(os.getenv("BEDROCK_MAX_TOKENS", 1024))
BEDROCK_TEMPERATURE = float(os.getenv("BEDROCK_TEMPERATURE", 0.7))
BEDROCK_TOP_K = int(os.getenv("BEDROCK_TOP_K", 5))

# Knowledge Bases
KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID")
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K", 3))
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
KNOWLEDGE_BASE_ROLE_ARN = os.getenv("KNOWLEDGE_BASE_ROLE_ARN")
