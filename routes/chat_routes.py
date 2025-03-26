from flask import Blueprint, request, jsonify, Response, stream_with_context
import traceback

from utils.text_utils import extract_relevant_context, extract_summary_text
from utils.gemini_utils import generate_text, generate_text_internal
from services.pdf_service import generate_summary_background
import concurrent.futures

# Create a blueprint for chat routes
chat_blueprint = Blueprint('chat', __name__)

# Thread pool for background processing
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

@chat_blueprint.route("/summarize", methods=["POST", "OPTIONS"])
def summarize_page():
    # Manejar la solicitud preflight OPTIONS
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "Falta el texto para resumir"}), 400

        text = data["text"]
        page = data.get("page", 0)
        file_hash = data.get("file_hash", "unknown")
        
        # Extraer una versión más corta del texto
        short_text = extract_summary_text(text)

        # Crear el prompt para el resumen
        prompt = f"""
        Eres un experto en síntesis de información. Tu tarea es generar un resumen del siguiente texto siguiendo estas pautas:

        1. Identifica el propósito principal del texto.
        2. Extrae los puntos clave y los organiza de manera lógica.
        3. Incluye ejemplos o datos relevantes si están disponibles.
        4. Limita el resumen a 150-200 palabras.
        5. Usa un lenguaje claro y profesional.
        6. Responde únicamente en español.
        7. IMPORTANTE: Formatea tu respuesta usando Markdown para mejorar la legibilidad.
           - No uses titulos ni encabezados, ve directo al contenido
           - Usa **texto** para negritas en conceptos importantes
           - Usa *texto* para cursivas en definiciones o términos clave
           - Usa listas con - o 1. para enumerar puntos importantes
           - Usa > para citas o ejemplos destacados

        Texto:
        {text}
        """

        # Generar la respuesta completa (sin streaming)
        response = generate_text_internal(prompt, stream=False)
        print(f"Respuesta completa generada: {response}")
        
        # Devolver la respuesta completa como JSON
        return jsonify({"summary": response})
    except Exception as e:
        print(f"Error en el endpoint de resumen: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error procesando la solicitud: {str(e)}"}), 500

@chat_blueprint.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    # Manejar la solicitud preflight OPTIONS
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.json
        if not data or "question" not in data:
            return jsonify({"error": "Falta la pregunta"}), 400

        question = data["question"]
        context = data.get("context", "")

        # Si no hay contexto, devolver un error
        if not context:
            return jsonify({"error": "Falta el contexto"}), 400

        # Crear el prompt para el chat
        prompt = f"""
        Eres un asistente inteligente que responde preguntas basadas en un contexto proporcionado. Sigue estas instrucciones:

        1. Lee cuidadosamente la pregunta y el contexto.
        2. Proporciona una respuesta clara, precisa y bien estructurada.
        3. Si la pregunta no puede responderse con el contexto, respondelo con tus conocimientos sobre el tema.
        4. Limita la respuesta a un máximo de 200 palabras.
        5. Responde únicamente en español.

        Pregunta:
        {question}

        Contexto:
        {context}
        """

        # Generar la respuesta completa (sin streaming)
        response = generate_text_internal(prompt, stream=False)
        
        # Devolver la respuesta completa como JSON
        return jsonify({"answer": response})
    except Exception as e:
        print(f"Error en el endpoint de chat: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error procesando la solicitud: {str(e)}"}), 500

