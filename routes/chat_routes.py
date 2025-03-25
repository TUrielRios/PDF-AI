from flask import Blueprint, request, jsonify, Response, stream_with_context
import traceback

from utils.text_utils import  extract_summary_text
from utils.gemini_utils import  generate_text_internal
from utils.cache_utils import summary_cache, get_from_cache, add_to_cache, generate_summary_cache_key
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

        # Verificar si ya tenemos este resumen en caché
        cache_key = generate_summary_cache_key(file_hash, page)
        cached_summary = get_from_cache(summary_cache, cache_key)
        if cached_summary:
            print(f"Usando resumen en caché para la página {page}")
            return jsonify({"summary": cached_summary})

        # Extraer una versión más corta del texto
        short_text = extract_summary_text(text)

        # Crear el prompt para el resumen
        prompt = f"""
        Eres un experto en síntesis de información. Tu tarea es generar un resumen del siguiente texto siguiendo estas pautas:

        1. Extrae los puntos clave y los organiza de manera lógica.
        2. Incluye ejemplos o datos relevantes si están disponibles.
        3. Limita el resumen a 150-200 palabras.
        4. Usa un lenguaje claro y profesional.
        5. Responde únicamente en español.
        Una vez tengas todo esto claro realizar un resumen organizado y estructurado

        Texto:
        {short_text}
        """

        # Generar la respuesta en streaming
        response_stream = generate_text_internal(prompt, stream=True)

        # Devolver la respuesta en streaming
        return Response(stream_with_context(generate_summary_stream(response_stream, cache_key)), mimetype="text/event-stream")
    except Exception as e:
        print(f"Error en el endpoint de resumen: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error procesando la solicitud: {str(e)}"}), 500
def generate_summary_stream(response_stream, cache_key):
    """Generar un resumen en streaming para el cliente."""
    full_summary = ""  # Almacenar el resumen completo para caché
    try:
        for chunk in response_stream:
            yield f"data: {chunk.text}\n\n"  # Enviar cada chunk como un evento SSE
            full_summary += chunk.text  # Acumular el resumen completo
        # Almacenar el resumen completo en caché
        add_to_cache(summary_cache, cache_key, full_summary)
    except Exception as e:
        print(f"Error en generate_summary_stream: {str(e)}")
        traceback.print_exc()
        yield f"data: Error en el streaming: {str(e)}\n\n"

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

        # Extraer solo las partes más relevantes del contexto
        # reduced_context = extract_relevant_context(question, context)

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

        # Generar la respuesta en streaming
        response_stream = generate_text_internal(prompt, stream=True)

        # Devolver la respuesta en streaming
        return Response(stream_with_context(generate_streaming_response(response_stream)), mimetype="text/event-stream")
    except Exception as e:
        print(f"Error en el endpoint de chat: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error procesando la solicitud: {str(e)}"}), 500

def generate_streaming_response(response_stream):
    """Generar una respuesta en streaming para el cliente."""
    try:
        for chunk in response_stream:
            yield f"data: {chunk.text}\n\n"  # Enviar cada chunk como un evento SSE
    except Exception as e:
        print(f"Error en generate_streaming_response: {str(e)}")
        traceback.print_exc()
        yield f"data: Error en el streaming: {str(e)}\n\n"