import boto3
import logging
from config.settings import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, KNOWLEDGE_BASE_ROLE_ARN

# Set up logger to track events, errors, and general info
logger = logging.getLogger(__name__)

class BedrockService:
    """
    A service to interact with Amazon Bedrock using AWS SDK.
    This class facilitates the assumption of a role to access the Bedrock API
    and synchronize data sources with the Knowledge Base (KB).
    """

    def __init__(self):
        """
        Initialize the BedrockService instance.
        
        This will configure the STS client needed to assume a role 
        to interact with Amazon Bedrock Knowledge Base services.
        """
        # Create an STS (Security Token Service) client to assume a role
        self.sts_client = boto3.client(
            "sts",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        # ARN (Amazon Resource Name) for the Knowledge Base role that we need to assume
        self.kb_role_arn = KNOWLEDGE_BASE_ROLE_ARN

    def get_bedrock_client(self):
        """
        Assumes a role in the Knowledge Base and returns a client for Bedrock API.

        This function assumes the specified IAM role to acquire temporary credentials
        and uses these credentials to create a Bedrock agent client.

        Returns:
            bedrock_agent_client (boto3.client): The Bedrock agent client with temporary credentials.
        """
        try:
            # Assume the KB role to gain temporary security credentials for accessing the Bedrock service
            assumed_role = self.sts_client.assume_role(
                RoleArn=self.kb_role_arn,  # ARN of the KB role
                RoleSessionName="BedrockSyncSession"  # A unique name for the assumed role session
            )

            # Extract the temporary credentials from the assumed role response
            credentials = assumed_role['Credentials']

            # Create the Bedrock agent client with the temporary credentials
            bedrock_agent_client = boto3.client(
                "bedrock-agent",
                region_name=AWS_REGION,
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken']  # Include the session token for authorization
            )

            logger.info("Successfully assumed role and created Bedrock client.")
            return bedrock_agent_client

        except Exception as e:
            # Log any error encountered during the role assumption or client creation
            logger.exception("Error assuming role or creating Bedrock agent client.")
            raise e

    def sync_with_bedrock(self, knowledge_base_id: str, data_source_id: str) -> dict:
        """
        Start the ingestion job to sync a data source with the Amazon Bedrock Knowledge Base.

        This method initiates the data synchronization between a given data source and the 
        Bedrock Knowledge Base using the temporary credentials obtained from assuming the role.

        Args:
            knowledge_base_id (str): The ID of the knowledge base where the data should be synced.
            data_source_id (str): The ID of the data source to be ingested into the knowledge base.

        Returns:
            dict: Response from the Bedrock service containing sync job details.
        """
        try:
            # Retrieve the Bedrock client using assumed credentials
            client = self.get_bedrock_client()

            # Start the ingestion job to sync data from the given source to the knowledge base
            response = client.start_ingestion_job(
                knowledgeBaseId=knowledge_base_id,
                dataSourceId=data_source_id
            )

            # Log the successful initiation of the sync job
            logger.info(f"Sync initiated with Bedrock. Job details: {response}")
            return response

        except Exception as e:
            # Log the error if the sync process fails
            logger.exception(f"Error syncing with Bedrock for data source '{data_source_id}'")
            raise e
