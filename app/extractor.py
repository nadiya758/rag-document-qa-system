import pymupdf
import re


def clean_text(text):
    # Remove unnecessary spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive empty lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_pdf(pdf_bytes):

    document = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    

    extracted_pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text")

        cleaned_text = clean_text(text)

        if cleaned_text:
            extracted_pages.append({
                "page_number": page_number,
                "text": cleaned_text
            })

    document.close()

    return extracted_pages
