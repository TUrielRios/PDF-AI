from utils.text_utils import extract_summary_text
from utils.gemini_utils import generate_text_internal
import traceback
from pdf2image import convert_from_bytes
import pytesseract
import numpy as np

def generate_summary_background(page_text, page_num, file_hash):
    """Generate a summary in the background SIN CACHÉ"""
    try:
        # Extract a shorter version of the text
        short_text = extract_summary_text(page_text)
        
        # Create a more efficient prompt for summarization
        prompt = f"""
            Eres un experto en síntesis de información. Tu tarea es generar un resumen del siguiente texto siguiendo estas pautas:

            1. Identifica el propósito principal del texto.
            2. Extrae los puntos clave y los organiza de manera lógica.
            3. Incluye ejemplos o datos relevantes si están disponibles.
            4. Limita el resumen a 150-200 palabras.
            5. Usa un lenguaje claro y profesional.
            6. Responde únicamente en español.

            Texto:
            {short_text}
            """
        # Generate new response without cache
        return generate_text_internal(prompt, max_tokens=150)
    except Exception as e:
        print(f"Error generating summary for page {page_num}: {str(e)}")
        traceback.print_exc()
        return f"Error generando el resumen: {str(e)}"

def extract_text_from_pdf_images(pdf_bytes):
    try:
        # 1. Convertir PDF a imágenes
        images = convert_from_bytes(pdf_bytes, dpi=300)
        
        # 2. Procesar cada imagen con OCR
        full_text = ""
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image, lang='spa')
            if text.strip():
                full_text += f"\n--- Página {i+1} ---\n{text}\n"
        
        return full_text if full_text else None
    except Exception as e:
        print(f"Error en OCR: {str(e)}")
        return None
