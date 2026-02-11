"""
Funções utilitárias para o Nobile Career Strategy
"""

import pdfplumber


def extract_text(file):
    """
    Extrai texto de um arquivo PDF
    
    Args:
        file: Objeto de arquivo PDF (UploadedFile do Streamlit)
        
    Returns:
        str: Texto extraído do PDF ou None se houver erro
    """
    try:
        with pdfplumber.open(file) as pdf:
            return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    except Exception:
        return None
