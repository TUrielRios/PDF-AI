from flask import Blueprint, jsonify

from utils.cache_utils import pdf_cache, summary_cache
from config import DEFAULT_MODEL

# Create a blueprint for health routes
health_blueprint = Blueprint('health', __name__)

@health_blueprint.route("/health", methods=["GET"])
def health_check():
    try:        
        return jsonify({
            "status": "ok",
            "model": DEFAULT_MODEL,
            "cache_size": len(pdf_cache),
            "summary_cache_size": len(summary_cache)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

