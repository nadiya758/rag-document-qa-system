
def chunk_text(pages, chunk_size=500, overlap=100):

    chunks = []

    for page in pages:

        words = page["text"].split()

        start = 0

        while start < len(words):

            end = start + chunk_size

            chunk_words = words[start:end]

            chunk_content = " ".join(chunk_words)

            chunks.append({
                "chunk_id": len(chunks) + 1,
                "page_number": page["page_number"],
                "text": chunk_content
            })

            if end >= len(words):
                break

            start = end - overlap

    return chunks
