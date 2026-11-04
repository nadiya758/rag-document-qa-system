import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

from app.extractor import extract_pdf
from app.chunker import chunk_text
from app.embedding import create_embedding

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

collection_name = "training_institute_docs"

pdf_path = "documents/training_institute_handbook.pdf"

with open(pdf_path, "rb") as pdf:
    pages = extract_pdf(pdf.read())

chunks = chunk_text(pages)

points = []

for chunk in chunks:
    vector = create_embedding(chunk["text"])

    points.append(
        models.PointStruct(
            id=chunk["chunk_id"],
            vector=vector,
            payload={
                "text": chunk["text"],
                "page_number": chunk["page_number"],
                "filename": "training_institute_handbook.pdf"
            }
        )
    )

client.upsert(
    collection_name=collection_name,
    points=points
)

print("Total Chunks Saved:", len(points))
print("PDF Successfully Stored in Qdrant!")