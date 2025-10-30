from typing import Tuple


def extract_text_from_pdf(file_bytes: bytes) -> str:
    import pdfplumber
    import io

    text_content = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text_content += page.extract_text() or ""
    return text_content


def extract_text_from_docx(file_bytes: bytes) -> str:
    from docx import Document
    import io

    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)


def sniff_extension(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "pdf"
    if lower.endswith(".docx"):
        return "docx"
    if lower.endswith(".txt") or lower.endswith(".text"):
        return "txt"
    return "unknown"


def extract_text(filename: str, content_type: str, file_bytes: bytes) -> Tuple[str, str]:
    ext = sniff_extension(filename)
    if ext == "pdf" or content_type in ("application/pdf",):
        text = extract_text_from_pdf(file_bytes)
        used = "pdf"
    elif ext == "docx" or content_type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ):
        text = extract_text_from_docx(file_bytes)
        used = "docx"
    elif ext == "txt" or content_type.startswith("text/"):
        text = file_bytes.decode(errors="ignore")
        used = "txt"
    else:
        # attempt pdf then docx then text
        try:
            text = extract_text_from_pdf(file_bytes)
            used = "pdf"
        except Exception:
            try:
                text = extract_text_from_docx(file_bytes)
                used = "docx"
            except Exception:
                text = file_bytes.decode(errors="ignore")
                used = "txt"
    return text, used 