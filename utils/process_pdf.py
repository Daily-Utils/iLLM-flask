from PyPDF2 import PdfReader

def process_pdf(file, model: str):
    reader = PdfReader(file)
    text_data = []

    for page in reader.pages:
        text_data.append(page.extract_text())

    data = [{"Content": text} for text in text_data]

    return {"model": model, "body": {"data": str(data)}}
