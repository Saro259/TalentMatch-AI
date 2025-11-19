from pypdf import PdfReader

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from uploaded PDF file.
    Args:
        pdf_file: Streamlit UploadedFile object
    Returns:
        str: Extracted text from all pages
    TODO: 
    - Create PdfReader object
    - Loop through all pages
    - Extract text from each page
    - Combine all text with spaces
    - Handle errors (what if PDF is corrupted?)
    """
    extracted = []
    try:
        pdf_reader = PdfReader(pdf_file)
        print(len(pdf_reader.pages))
        print(pdf_reader.pages)
        for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted.append(page_text)
        return " ".join(extracted).strip()
    except Exception as e:
        return f"Error reading file. An error occured: {e}"
    



