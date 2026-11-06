
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from qdrant_client import QdrantClient, models

from app.embedding import create_embedding

load_dotenv()

# Gemini Client
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Qdrant Client
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION_NAME = "training_institute_docs_gemini"
SIMILARITY_THRESHOLD = 0.50

FALLBACK_MESSAGE = (
    "Sorry, this information is not available in the document."
)


def ask_question(question, document_id=None):

    # Step 1: Create question embedding
    query_vector = create_embedding(
        question,
        task_type="RETRIEVAL_QUERY"
    )

    # Step 2: Search Qdrant
    query_filter = None

    if document_id:
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id)
                )
            ]
        )

    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        limit=3
    ).points

    if not results:
        return FALLBACK_MESSAGE

    # Step 3: Similarity filtering
    relevant_results = [
        result for result in results
        if result.score >= SIMILARITY_THRESHOLD
    ]

    # Debug information
    print("Retrieved Text:")
    for result in relevant_results:
        print(result.payload.get("text"))

    print(
        "Similarity Scores:",
        [result.score for result in relevant_results]
    )

    if not relevant_results:
        return FALLBACK_MESSAGE

    # Step 4: Prepare context
    context_parts = []

    for result in relevant_results:
        payload = result.payload or {}

        context_parts.append(
            f"Page Content:\n{payload.get('text', '')}"
        )

    context = "\n\n".join(context_parts)

    # Step 5: Gemini Prompt
    prompt = f"""
You are a helpful Training Institute Assistant.

Rules:
1. Answer using ONLY the provided context.
2. Never invent information.
3. If the answer is not available,
   reply exactly:
   "{FALLBACK_MESSAGE}"
4. Do NOT mention source filename or page number.
5. Give a simple and clear answer.
5. Match the exact course name asked in the question.
6. Do not treat a more advanced or different course as the same course.
7. If the exact course or requested information is not present in the context, return the fallback message.

Context:
{context}

Question:
{question}
"""

    # Step 6: Generate AI Answer
    response = gemini_client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0
        )
    )

    answer = (response.text or "").strip()

    if not answer or FALLBACK_MESSAGE.lower() in answer.lower():
        return FALLBACK_MESSAGE

    # Step 7: Get actual source from Qdrant
    sources = []

    for result in relevant_results:
        payload = result.payload or {}

        filename = payload.get("filename", "Unknown")
        page = payload.get("page_number", "Unknown")

        source = f"{filename}, Page: {page}"

        if source not in sources:
            sources.append(source)

    source_text = "\n".join(
        f"- {source}" for source in sources
    )

    return f"{answer}\n\nSources:\n{source_text}"


if __name__ == "__main__":

    question = "What is the Python course fee?"
    answer = ask_question(question)

    print("\nQuestion:", question)
    print("\nAI Answer:", answer)
