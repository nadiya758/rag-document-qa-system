import os
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient

from app.embedding import create_embedding

load_dotenv()

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

def ask_question(question):

    query_vector = create_embedding(question)

    results = qdrant_client.query_points(
        collection_name="training_institute_docs",
        query=query_vector,
        limit=2
    ).points

    context = "\n\n".join(
    f"Source: {result.payload['filename']}, "
    f"Page: {result.payload['page_number']}\n"
    f"{result.payload['text']}"
    for result in results
)
    
    prompt = f"""
    You are a helpful Training Institute Assistant.

    Answer the question using ONLY the provided context.

    If the answer is not available in the context,
    say: "Sorry, this information is not available in the document.
    At the end of your answer, mention the source filename and page number."

    Context:
    {context}

    Question:
    {question}
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    question = "What is the Python course fee?"
    answer = ask_question(question)

    print("\nQuestion:", question)
    print("\nAI Answer:", answer)