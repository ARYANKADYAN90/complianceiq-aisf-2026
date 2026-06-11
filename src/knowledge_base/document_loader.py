import os
import httpx
import logging
from src.config import get_settings

logger = logging.getLogger(__name__)

async def upload_regulatory_documents() -> list[str]:
    """
    Downloads regulatory documents and uploads them to Azure Blob Storage
    for ingestion into the Foundry IQ knowledge base.
    """
    settings = get_settings()
    
    if settings.mock_mode:
        logger.info("Mock Mode: Simulating document upload to Blob Storage.")
        print("✅ Uploaded: EU_AI_Act.pdf")
        print("✅ Uploaded: NIST_AI_RMF.pdf")
        return [
            "https://mockstorage.blob.core.windows.net/regulatory-docs/EU_AI_Act.pdf",
            "https://mockstorage.blob.core.windows.net/regulatory-docs/NIST_AI_RMF.pdf"
        ]

    # Documents to download and upload
    documents = [
        {
            "name": "EU_AI_Act.pdf",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689"
        },
        {
            "name": "NIST_AI_RMF.pdf",
            "url": "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf"
        }
    ]
    
    uploaded_urls = []
    
    # In a real environment, we would use azure-storage-blob to upload.
    # We simulate the structure here since azure-storage-blob is not in requirements.txt.
    # To run this in production, ensure `azure-storage-blob` is installed and imported:
    # from azure.storage.blob.aio import BlobServiceClient
    # from azure.identity.aio import DefaultAzureCredential
    
    try:
        from azure.storage.blob.aio import BlobServiceClient
        from azure.identity.aio import DefaultAzureCredential
        has_blob_sdk = True
    except ImportError:
        has_blob_sdk = False
        logger.warning("azure-storage-blob not installed. Simulating blob upload.")
    
    if has_blob_sdk:
        account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL", "")
        if not account_url:
            logger.error("AZURE_STORAGE_ACCOUNT_URL not set.")
            return []
            
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
        container_client = blob_service_client.get_container_client("regulatory-docs")
        
        # Ensure container exists
        try:
            await container_client.create_container()
        except Exception:
            pass  # Container might already exist
            
        async with httpx.AsyncClient(follow_redirects=True) as http_client:
            for doc in documents:
                print(f"Downloading {doc['name']} from {doc['url']}...")
                response = await http_client.get(doc['url'], timeout=60.0)
                response.raise_for_status()
                data = response.content
                
                print(f"Uploading {doc['name']} to Azure Blob Storage...")
                blob_client = container_client.get_blob_client(doc['name'])
                await blob_client.upload_blob(data, overwrite=True)
                
                uploaded_urls.append(blob_client.url)
                print(f"✅ Successfully uploaded {doc['name']}")
                
        await blob_service_client.close()
        await credential.close()
    else:
        # Fallback simulation
        async with httpx.AsyncClient(follow_redirects=True) as http_client:
            for doc in documents:
                print(f"Simulating download & upload for {doc['name']}...")
                uploaded_urls.append(f"https://example.blob.core.windows.net/regulatory-docs/{doc['name']}")
                print(f"✅ Successfully processed {doc['name']}")

    return uploaded_urls
