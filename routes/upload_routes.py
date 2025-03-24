from flask import Blueprint, request, jsonify, send_file, make_response
import io
import hashlib
import os
from PyPDF2 import PdfReader
import traceback
import concurrent.futures

from utils.cache_utils import pdf_cache, add_to_cache
from utils.text_utils import extract_key_info
from utils.gemini_utils import generate_text
from services.pdf_service import generate_summary_background

# Create a blueprint for upload routes
upload_blueprint = Blueprint('upload', __name__)

# Configuración para almacenar archivos PDF
file_cache = {}


# Thread pool for background processing
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

@upload_blueprint.route("/upload", methods=["POST", "OPTIONS"])
def upload_pdf():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return "", 200

    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Read file content for hashing
        file_content = file.read()
        
        # Create a hash of the file content
        file_hash = hashlib.md5(file_content).hexdigest()
        
        # Check if we've already processed this file
        if file_hash in pdf_cache:
                print(f"Using cached result for file: {file.filename}")
                return jsonify(pdf_cache[file_hash])

        # Guarda el PDF en memoria en lugar de disco
        file_cache[file_hash] = file_content  # <-- Almacena bytes en memoria

        # Genera una URL virtual (no es un archivo real)
        file_url = f"https://pdf-ai-teal.vercel.app/api/temp-pdf/{file_hash}"

        # Create a file-like object from the content
        file_io = io.BytesIO(file_content)
        
        # Extract text from PDF
        try:
            reader = PdfReader(file_io)
            total_pages = len(reader.pages)
            
            # Extract text from each page separately
            pages = {}
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:  # Check if page_text is not None or empty
                    pages[i + 1] = page_text
                else:
                    print(f"Warning: Could not extract text from page {i+1} in {file.filename}")
            
            if not pages:
                return jsonify({"error": "Could not extract any text from the PDF"}), 400
            
            # Get text from first page for explanation
            first_page_text = pages.get(1, "")
            
            # Extract key information to reduce context size
            key_info = extract_key_info(first_page_text)
            
            # Generate a simple explanation using Ollama - use a more efficient prompt
            prompt = f"""
                Eres un experto en análisis de documentos. Tu tarea es proporcionar una explicación clara y concisa del siguiente texto. Sigue estas instrucciones:

                1. Identifica el tema principal del texto.
                2. Extrae los puntos clave o ideas más importantes.
                3. Proporciona un resumen breve (máximo 200 palabras y mayor a 150) que capture la esencia del texto.
                4. Si el texto contiene datos numéricos, fechas o nombres propios, menciónalos de manera relevante.
                5. Responde únicamente en español y utiliza un tono profesional.

                Texto:
                {key_info}
                """
            explanation = generate_text(prompt, max_tokens=100)
            
            # Create result with page-by-page text
            result = {
                "total_pages": total_pages,
                "pages": pages,
                "explanation": explanation,
                "file_url": file_url  # Incluir la URL del archivo en la respuesta
            }
            
            add_to_cache(pdf_cache, file_hash, result)  # Cache the result
            
            # Start generating summary for the second page in the background
            if 2 in pages:
                executor.submit(generate_summary_background, pages[2], 2, file_hash)
            
            return jsonify(result)
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            traceback.print_exc()
            return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500
    except Exception as e:
        print(f"Unexpected error in upload_pdf: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@upload_blueprint.route('/api/temp-pdf/<file_hash>', methods=['GET'])
def serve_temp_pdf(file_hash):
    if file_hash not in file_cache:
        return jsonify({"error": "Archivo no encontrado"}), 404
    
    # Crea una respuesta con los bytes del PDF
    pdf_bytes = file_cache[file_hash]
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename={file_hash}.pdf'
    return response