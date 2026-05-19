import pdfplumber
import re
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extrae texto de un PDF intentando preservar la estructura del plan."""
    lines = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            # Intentar extraer tablas primero
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        row_text = '\t'.join(cell or '' for cell in row).strip()
                        if row_text:
                            lines.append(row_text)
            else:
                text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if text:
                    lines.append(text)

    raw = '\n'.join(lines)
    return _clean(raw)


def _clean(text: str) -> str:
    """Normaliza el texto extraído para que el parser lo reconozca."""
    # Unificar variantes de porcentaje: "80 %" → "80%", "80%" se queda
    text = re.sub(r'(\d)\s+%', r'\1%', text)
    # Normalizar multiplicador: "5 x 3" / "5×3" → "5x3"
    text = re.sub(r'(\d)\s*[xX×]\s*(\d)', r'\1x\2', text)
    # Eliminar líneas completamente vacías repetidas
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
