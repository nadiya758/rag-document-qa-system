
import os
import uuid

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

from app.embedding import create_embedding

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    check_compatibility=False,
    timeout=60
)                      

# New collection for Gemini embeddings
collection_name = "training_institute_docs_gemini"

VECTOR_SIZE = 768

def ensure_collection():

    if not client.collection_exists(collection_name):

        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE
            )
        )

        print("Gemini Qdrant Collection Created!")

    else:
        print("Gemini Qdrant Collection Already Exists!")

    client.create_payload_index(
        collection_name=collection_name,
        field_name="document_id",
        field_schema=models.PayloadSchemaType.KEYWORD
    )

def store_chunks(chunks, filename, file_hash):
    ensure_collection()

    document_id = str(uuid.uuid4())
    points = []

    for index, chunk in enumerate(chunks):

        vector = create_embedding(
            chunk["text"],
            task_type="RETRIEVAL_DOCUMENT"
        )

        points.append(
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "chunk_index": index,
                    "filename": filename,
                    "file_hash": file_hash,
                    "page_number": chunk["page_number"],
                    "text": chunk["text"]
                }
            )
        )

    if points:

        client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True
        )

    return {
        "document_id": document_id,
        "total_chunks_saved": len(points)
    }
def list_documents():

    records, next_page = client.scroll(
        collection_name=collection_name,
        limit=100,
        with_payload=True,
        with_vectors=False
    )

    documents = {}

    for record in records:

        payload = record.payload or {}

        document_id = payload.get("document_id")

        if document_id not in documents:

            documents[document_id] = {
                "document_id": document_id,
                "filename": payload.get("filename"),
                
                "total_chunks": 0
            }

        documents[document_id]["total_chunks"] += 1

    return list(documents.values())
def delete_document(document_id):

    query_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="document_id",
                match=models.MatchValue(value=document_id)
            )
        ]
    )

    records, _ = client.scroll(
        collection_name=collection_name,
        scroll_filter=query_filter,
        limit=1,
        with_payload=False,
        with_vectors=False
    )

    if not records:
        return False

    client.delete(
        collection_name=collection_name,
        points_selector=models.FilterSelector(
            filter=query_filter
        ),
        wait=True
    )

    return True
def create_document_index():

    client.create_payload_index(
        collection_name=collection_name,
        field_name="document_id",
        field_schema=models.PayloadSchemaType.KEYWORD,
        wait=True
    )

    print("Document ID index created successfully!")
def is_duplicate_file(file_hash):

    query_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="file_hash",
                match=models.MatchValue(value=file_hash)
            )
        ]
    )

    records, _ = client.scroll(
        collection_name=collection_name,
        scroll_filter= query_filter,
        limit=1,
        with_payload=True,
        with_vectors=False
    )

    return len(records) > 0
def create_file_hash_index():

    client.create_payload_index(
        collection_name=collection_name,
        field_name="file_hash",
        field_schema=models.PayloadSchemaType.KEYWORD,
        wait=True
    )

    print("File Hash index created successfully!")