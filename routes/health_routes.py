from flask import Blueprint, jsonify

from config import DEFAULT_MODEL

# Create a blueprint for health routes
health_blueprint = Blueprint('health', __name__)

@health_blueprint.route("/health", methods=["GET"])
def health_check():
    try:        
        return jsonify({
            "status": "ok",
            "model": DEFAULT_MODEL,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

