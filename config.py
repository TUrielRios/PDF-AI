from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Tu API Key de Gemini
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")  # Modelo por defecto
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS"))  # Tokens máximos para la generación de texto

# Configuración de CORS
CORS_CONFIG = {
    "resources": {
        r"/": {
            "origins": "*", 
            "allow_headers": ["Content-Type", "Authorization"]
        }
    }
}

# Configuración de caché
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", 100))  # Número máximo de elementos en cada caché