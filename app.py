from flask import Flask
from flask_cors import CORS
import concurrent.futures

from config import CORS_CONFIG
from routes.upload_routes import upload_blueprint
from routes.chat_routes import chat_blueprint
from routes.health_routes import health_blueprint

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, **CORS_CONFIG)

# Create thread pool executor for background processing
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# Register blueprints
app.register_blueprint(upload_blueprint)
app.register_blueprint(chat_blueprint)
app.register_blueprint(health_blueprint)

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == "__main__":
    app.run(debug=True, threaded=True)

