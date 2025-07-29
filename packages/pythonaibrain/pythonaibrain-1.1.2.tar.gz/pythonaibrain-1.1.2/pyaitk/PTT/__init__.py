import fitz  # PyMuPDF

def PTT(path : str = None) -> str:
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Example usage
#print(PTT("sample.pdf"))
