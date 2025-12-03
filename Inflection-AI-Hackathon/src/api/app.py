"""
Flask API for Agri-Adapt AI Maize Resilience Model
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.models.maize_resilience_model import MaizeResilienceModel
from config.settings import API_HOST, API_PORT, API_DEBUG, KENYA_COUNTIES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize model
model = MaizeResilienceModel()

@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Agri-Adapt AI API',
        'version': '1.0.0'
    })

@app.route('/api/counties')
def get_counties():
    """Get list of Kenya counties"""
    return jsonify({
        'counties': KENYA_COUNTIES,
        'count': len(KENYA_COUNTIES)
    })

@app.route('/api/predict', methods=['POST'])
def predict_resilience():
    """
    Predict maize resilience score for given parameters
    
    Expected JSON payload:
    {
        "rainfall": 800.0,
        "soil_ph": 6.5,
        "organic_carbon": 2.1,
        "county": "Nakuru"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['rainfall', 'soil_ph', 'organic_carbon']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {missing_fields}'
            }), 400
        
        # Extract parameters
        rainfall = float(data['rainfall'])
        soil_ph = float(data['soil_ph'])
        organic_carbon = float(data['organic_carbon'])
        county = data.get('county', 'Unknown')
        
        # Validate parameter ranges
        if rainfall < 0 or rainfall > 3000:
            return jsonify({
                'error': 'Rainfall must be between 0 and 3000 mm'
            }), 400
        
        if soil_ph < 4.0 or soil_ph > 10.0:
            return jsonify({
                'error': 'Soil pH must be between 4.0 and 10.0'
            }), 400
        
        if organic_carbon < 0.1 or organic_carbon > 10.0:
            return jsonify({
                'error': 'Organic carbon must be between 0.1 and 10.0%'
            }), 400
        
        # Check if model is trained
        if not model.is_trained:
            return jsonify({
                'error': 'Model not trained. Please train the model first.'
            }), 503
        
        # Make prediction
        prediction = model.predict_resilience_score(rainfall, soil_ph, organic_carbon)
        
        # Add metadata
        response = {
            'prediction': prediction,
            'input_parameters': {
                'rainfall_mm': rainfall,
                'soil_ph': soil_ph,
                'organic_carbon_percent': organic_carbon,
                'county': county
            },
            'timestamp': request.headers.get('X-Request-Timestamp', ''),
            'model_info': {
                'algorithm': 'Random Forest',
                'features': model.feature_names,
                'feature_importance': model.get_feature_importance()
            }
        }
        
        logger.info(f"Prediction made for {county}: {prediction['resilience_score']}%")
        return jsonify(response)
        
    except ValueError as e:
        return jsonify({
            'error': f'Invalid parameter value: {str(e)}'
        }), 400
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            'error': 'Internal server error during prediction'
        }), 500

@app.route('/api/model/status')
def model_status():
    """Get model training status and information"""
    return jsonify({
        'is_trained': model.is_trained,
        'algorithm': 'Random Forest',
        'feature_names': model.feature_names,
        'model_params': model.model_params
    })

@app.route('/api/model/feature-importance')
def feature_importance():
    """Get feature importance scores"""
    if not model.is_trained:
        return jsonify({
            'error': 'Model not trained'
        }), 503
    
    return jsonify({
        'feature_importance': model.get_feature_importance()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info(f"Starting Agri-Adapt AI API on {API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)
