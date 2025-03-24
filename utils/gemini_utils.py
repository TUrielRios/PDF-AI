import google.generativeai as genai
import time
import traceback
from config import GEMINI_API_KEY, DEFAULT_MODEL, DEFAULT_MAX_TOKENS
from utils.cache_utils import generate_text_hash, get_from_cache, add_to_cache, prompt_cache
import re

# Configurar la API de Gemini
genai.configure(api_key=GEMINI_API_KEY)

def generate_text_internal(prompt_str, model=DEFAULT_MODEL, max_tokens=DEFAULT_MAX_TOKENS, stream=False):
    """Generar texto usando la API de Gemini con soporte para streaming."""
    try:
        print(f"Enviando solicitud a la API de Gemini usando el modelo {model}...")
        start_time = time.time()

        # Crear una instancia del modelo de Gemini
        model_instance = genai.GenerativeModel(model)

        if stream:
            # Generar la respuesta en streaming
            response = model_instance.generate_content(prompt_str, stream=True)
            return response  # Devuelve el generador de streaming
        else:
            # Generar la respuesta de una sola vez
            response = model_instance.generate_content(prompt_str)
            end_time = time.time()
            print(f"Tiempo de respuesta de Gemini: {end_time - start_time:.2f} segundos")
            return response.text
    except Exception as e:
        print(f"Error en generate_text: {str(e)}")
        traceback.print_exc()
        return f"Error generando la explicación: {str(e)}"
    
def generate_text(prompt_str, model=DEFAULT_MODEL, max_tokens=DEFAULT_MAX_TOKENS):
    """Generar texto con caché"""
    # Crear un hash del prompt para el caché
    prompt_hash = generate_text_hash(prompt_str)

    # Verificar si ya tenemos una respuesta en caché
    cached_response = get_from_cache(prompt_cache, prompt_hash)
    if cached_response:
        print(f"Usando respuesta en caché para el hash: {prompt_hash[:10]}...")
        return cached_response

    # Generar una nueva respuesta
    response = generate_text_internal(prompt_str, model, max_tokens)

    # Almacenar la respuesta en caché
    return add_to_cache(prompt_cache, prompt_hash, response)

def check_gemini_health():
    """Verificar si la API de Gemini está funcionando"""
    try:
        # Verificar la conexión con la API
        models = genai.list_models()
        if models:
            return {
                "status": "ok",
                "model_available": True
            }
        else:
            return {
                "status": "error",
                "model_available": False
            }
    except Exception as e:
        return {
            "status": "not_running",
            "model_available": False
        }