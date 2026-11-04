import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

from app.embedding import create_embedding

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

collection_name = "training_institute_docs"

question = "What is the Python course fee?"

query_vector = create_embedding(question)

results = client.query_points(
    collection_name=collection_name,
    query=query_vector,
    limit=2
).points

for result in results:
    print("\nScore:", result.score)
    print("Page:", result.payload["page_number"])
    print("Text:", result.payload["text"])
    