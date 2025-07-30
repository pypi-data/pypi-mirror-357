from pypdf import PdfReader


def load_pdf(file_path):
    """Extract text from a PDF file using pypdf."""
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text
