import boto3
import logging
import json
from typing import Dict, List
from config.settings import BEDROCK_MODEL, SYSTEM_PROMPT, AWS_REGION, KNOWLEDGE_BASE_ID
from utils.utils import extract_filename_from_uri, generate_presigned_url

# Initialize clients
bedrock_runtime_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)
bedrock_agent_client = boto3.client('bedrock-agent-runtime', region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def call_bedrock(prompt: str) -> str:
    """
    Calls the Amazon Bedrock model to generate a response for a given prompt.

    Args:
        prompt (str): The text prompt to send to the model.

    Returns:
        str: The model's response text.
    """
    try:
        body = json.dumps({
            "messages": [{"role": "user", "content": [{"text": prompt}]}]
        })

        response = bedrock_runtime_client.invoke_model(
            modelId=BEDROCK_MODEL,
            body=body,
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response["body"].read())
        return result["output"]["message"]["content"][0]["text"]

    except Exception as e:
        logger.exception("Error invoking Bedrock model")
        raise e

def retrieve_documents(query: str, category: str = None) -> Dict:
    """
    Retrieves documents from the knowledge base related to the query and category.

    Args:
        query (str): The search query to retrieve relevant documents.
        category (str, optional): A category filter to narrow down the search.

    Returns:
        dict: A dictionary containing the retrieved context and citations.
    """
    try:
        logger.info(f"Retrieving documents for query: '{query}' - Category: '{category}'")
        
        retrieval_configuration = {}
        if category:
            retrieval_configuration["vectorSearchConfiguration"] = {
                "filter": {"equals": {"key": "category", "value": category}}
            }

        response = bedrock_agent_client.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration=retrieval_configuration
        )

        results = response.get('retrievalResults', [])
        logger.info(f"Documents retrieved: {len(results)}")

        # Combine context
        context = "\n\n".join(result['content']['text'] for result in results)

        # Build citations
        citations = []
        seen_sources = {}
        
        for result in results:
            metadata = result.get('metadata', {})
            s3_uri = metadata.get('x-amz-bedrock-kb-source-uri', '')

            # Avoid duplicate citations
            if s3_uri in seen_sources:
                citation_id = seen_sources[s3_uri]
            else:
                citation_id = len(seen_sources) + 1
                seen_sources[s3_uri] = citation_id

                download_url = generate_presigned_url(s3_uri, expiration=3600)
                filename = extract_filename_from_uri(s3_uri)

                citation = {
                    "id": citation_id,
                    "source": s3_uri,
                    "filename": filename,
                    "download_url": download_url,
                    "page": int(metadata.get('x-amz-bedrock-kb-document-page-number', 0)),
                    "category": metadata.get('category', 'Uncategorized'),
                    "score": round(result.get('score', 0), 4),
                    "snippet": result['content']['text'][:200] + "..."
                }
                citations.append(citation)

        return {"context": context, "citations": citations}

    except Exception as e:
        logger.exception("Error retrieving documents")
        raise e

def retriever_function(query: str, category: str = None) -> Dict:
    """
    Main function to retrieve documents and generate a response with citations.

    Args:
        query (str): The user query.
        category (str, optional): Category filter.

    Returns:
        dict: Dictionary containing answer text, citations, and total sources.
    """
    try:
        logger.info(f"Query received: '{query}' - Category: '{category}'")
        retrieval_result = retrieve_documents(query, category)
        context = retrieval_result["context"]
        citations = retrieval_result["citations"]

        if not context:
            return {"answer": "No relevant documents found.", "citations": [], "total_sources": 0}

        # Generate prompt
        prompt = f"{SYSTEM_PROMPT}\n\nContext: {context}\n\nQuestion: {query}\nAnswer:\n"
        answer = call_bedrock(prompt)

        # Format citations in a nicer Markdown style
        if citations:
            citations_text = "\n".join(
                f"**Citation {c['id']}**: [{c['filename']}]({c['download_url']}) - "
                f"Page {c['page']}"
                for c in citations
            )
            full_answer = f"{answer}\n\n**Citations:**\n{citations_text}"
        else:
            full_answer = answer

        return {"answer": full_answer, "citations": citations, "total_sources": len(citations)}

    except Exception as e:
        logger.exception("Error in retriever_function")
        raise e
