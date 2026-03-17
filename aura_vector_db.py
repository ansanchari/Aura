import json
import logging
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def build_safe_vector_db(input_file: str, db_path: str = "./qdrant_aura_db"):
    logger.info("Initializing ultra-lightweight embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    logger.info(f"Setting up local Qdrant database at: {db_path}")
    client = QdrantClient(path=db_path)
    collection_name = "womens_health_knowledge"
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        logger.info(f"Created new collection: {collection_name}")
    logger.info(f"Loading chunks from {input_file}...")
    with open(input_file, 'r') as f:
        raw_chunks = json.load(f)
    documents = []
    for item in raw_chunks:
        doc = Document(
            page_content=item["text"],
            metadata=item["metadata"]
        )
        documents.append(doc)
    logger.info(f"Total chunks to process: {len(documents)}")
    batch_size = 100
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    logger.info("Starting safe batch ingestion...")
    for i in range(0, len(documents), batch_size):
        batch = documents[i : i + batch_size]
        vector_store.add_documents(batch)
        logger.info(f"Safely ingested batch {i // batch_size + 1} (Chunks {i} to {i + len(batch)})...")
    logger.info("Database build complete! Your system resources are fully released.")

if __name__ == "__main__":
    build_safe_vector_db("aura_economical_chunks.json")