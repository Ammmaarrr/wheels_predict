from flask import Flask, render_template, request, jsonify
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Try to import optional modules
try:
    from flows.conversation_manager import handle_user_message
    HAS_CONVERSATION_MANAGER = True
except ImportError:
    HAS_CONVERSATION_MANAGER = False

try:
    from models.monitoring_api import monitoring_bp
    HAS_MONITORING = True
except ImportError:
    HAS_MONITORING = False

from utils.logger import setup_logger, log_error, APIError
from functools import wraps
import traceback

# Set up logger
logger = setup_logger(__name__)

app = Flask(__name__)

# Register monitoring blueprint if available
if HAS_MONITORING:
    app.register_blueprint(monitoring_bp)
    logger.info("Monitoring dashboard enabled")
else:
    logger.warning("Monitoring dashboard not available")

def handle_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            log_error(logger, e)
            return jsonify({'error': str(e)}), e.status_code or 400
        except Exception as e:
            log_error(logger, e)
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function

@app.route('/')
@handle_exceptions
def index():
    logger.info("Rendering main interface")
    return '''
    <html>
    <head><title>Wheels Predict ML Platform</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px;">
        <h1>🚗 Wheels Predict ML Platform</h1>
        <p>Welcome to the Wheels Predict Machine Learning Platform!</p>
        <h2>Available Services:</h2>
        <ul>
            <li><a href="/monitoring/dashboard" style="color: #007bff; text-decoration: none;">
                📊 Model Monitoring Dashboard
            </a> - Real-time model performance monitoring</li>
            <li><a href="/monitoring/api/summary" style="color: #007bff; text-decoration: none;">
                📈 Monitoring API Summary
            </a> - JSON API endpoint</li>
        </ul>
        <h2>Quick Status:</h2>
        <div id="status" style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
            Loading system status...
        </div>
        <script>
            // Only try to load monitoring if available
            ''' + ('true' if HAS_MONITORING else 'false') + ''' && 
            fetch('/monitoring/api/summary')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status').innerHTML = 
                        '<strong>Monitoring System:</strong> Active<br>' +
                        '<strong>Models Evaluated:</strong> ' + (data.models_evaluated?.length || 0) + '<br>' +
                        '<strong>Last Update:</strong> ' + (data.summary_timestamp ? new Date(data.summary_timestamp).toLocaleString() : 'Never');
                })
                .catch(e => {
                    document.getElementById('status').innerHTML = 
                        '<strong>Status:</strong> <span style="color: red;">Error loading status</span>';
                });
            
            if (!''' + ('true' if HAS_MONITORING else 'false') + ''') {
                document.getElementById('status').innerHTML = 
                    '<strong>Monitoring System:</strong> <span style="color: orange;">Not Available</span><br>' +
                    '<em>Install required dependencies to enable monitoring</em>';
            }
        </script>
    </body>
    </html>
    '''

@app.route('/chat', methods=['POST'])
@handle_exceptions
def chat():
    try:
        if not HAS_CONVERSATION_MANAGER:
            raise APIError("Conversation manager not available", 501)
            
        data = request.get_json()
        if not data or 'message' not in data:
            raise APIError("Invalid request: message is required", 400)
        
        logger.info(f"Processing chat request: {data.get('message')[:100]}...")
        response = handle_user_message(data['message'])
        return jsonify(response)
    
    except Exception as e:
        log_error(logger, e, {'request_data': data})
        raise

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 error: {request.url}")
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)}\n{traceback.format_exc()}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True, port=8080)
