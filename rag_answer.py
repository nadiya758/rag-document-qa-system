import re
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
        limit=5
    ).points

    if not results:
        return FALLBACK_MESSAGE

    # Step 3: Similarity filtering
        
    relevant_results = [
        result for result in results
        if result.score >= SIMILARITY_THRESHOLD
    ]

    # Remove duplicate sources
    unique_results = []
    seen_sources = set()

    for result in relevant_results:
        payload = result.payload or {}

        source_key = (
            payload.get("filename"),
            payload.get("page_number"),
            payload.get("text")
        )

        if source_key not in seen_sources:
            seen_sources.add(source_key)
            unique_results.append(result)

    relevant_results = unique_results

    if not relevant_results:
        return FALLBACK_MESSAGE

    # Debug information
    print("\nRetrieved Sources and Scores:")

    for result in relevant_results:
        payload = result.payload or {}

        print(
            "Filename:", payload.get("filename"),
            "| Page:", payload.get("page_number"),
            "| Score:", result.score
        )
    print("\nRetrieved Text:")

    for result in relevant_results:
        payload = result.payload or {}

        print("\nFilename:", payload.get("filename"))
        print("Text:", payload.get("text"))
    
    # Step 4: Prepare context
    context_parts = []

    for result in relevant_results:
        payload = result.payload or {}

        context_parts.append(
            f"Page Content:\n{payload.get('text', '')}"
        )

    context = "\n\n".join(context_parts)
    print("\nFINAL CONTEXT SENT TO GEMINI:")
    print(context)

    # Step 5: Gemini Prompt
    prompt = f"""
You are a helpful Training Institute Assistant.

Rules:
1. Read all provided page contents carefully.
2. Find the text that directly answers the question.
3. The context may contain information from multiple documents.
4. Do not confuse Python Course with Advanced Python Course.
5. If the question asks about the Python course, use the information
   explicitly labeled for the Python course.
6. If the requested information is explicitly available,
   answer it directly.
7. Only return the fallback message if the requested information
   is genuinely missing from all provided context.
8. Never invent information.
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
    print("\nRAW GEMINI RESPONSE:")
    print(repr(response.text))

    answer = (response.text or "").strip()

    if not answer or FALLBACK_MESSAGE.lower() in answer.lower():
        return FALLBACK_MESSAGE

    # Step 7: Get actual source from Qdrant
        # Step 7: Filter sources using answer evidence
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "for",
        "on", "in", "of", "to", "and", "with", "from", "this",
        "that", "course", "classes", "class", "held", "days"
    }

    answer_terms = set(re.findall(r"\b[a-z0-9]+\b", answer.lower()))
    answer_terms = answer_terms - stop_words

    numeric_terms = {
        term for term in answer_terms
        if any(char.isdigit() for char in term)
    }

    sources = []

    for result in relevant_results:
        payload = result.payload or {}
        source_text_lower = payload.get("text", "").lower()
        source_terms = set(re.findall(r"\b[a-z0-9]+\b", source_text_lower))

        matched_terms = answer_terms.intersection(source_terms)

        if not answer_terms:
            continue

        match_ratio = len(matched_terms) / len(answer_terms)
        has_all_numbers = numeric_terms.issubset(source_terms)

        if match_ratio >= 0.60 and has_all_numbers:
            filename = payload.get("filename", "Unknown")
            page = payload.get("page_number", "Unknown")
            source = f"{filename}, Page: {page}"
            if source not in sources:
                sources.append(source)

    if not sources:
        source_text = "- Source could not be confidently identified."
    else:
        source_text = "\n".join(f"- {source}" for source in sources)

    return f"{answer}\n\nSources:\n{source_text}"

if __name__ == "__main__":

    question = "What is the Python course fee?"
    answer = ask_question(question)

    print("\nQuestion:", question)
    print("\nAI Answer:", answer)
