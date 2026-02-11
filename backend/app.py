"""
VoicePulse AI - Flask Backend Server
Main API endpoints for emotion analysis
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import uuid
from datetime import datetime
import logging
from emotion_pipeline import EmotionPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['REPORTS_FOLDER'] = os.path.join(os.path.dirname(__file__), 'reports')

# Allowed audio extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'webm'}

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

# Initialize emotion pipeline
pipeline = EmotionPipeline()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'VoicePulse AI',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/analyze', methods=['POST'])
def analyze_audio():
    """
    Main endpoint for emotion analysis
    
    Accepts: multipart/form-data with 'audio' file
    Returns: Complete emotion analysis results
    """
    try:
        # Check if file is present
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        file = request.files['audio']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Generate unique ID for this analysis
        analysis_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{analysis_id}_{filename}")
        file.save(file_path)
        
        logger.info(f"Processing file: {filename} (ID: {analysis_id})")
        
        # Run emotion analysis
        results = pipeline.analyze_audio(file_path)
        
        if not results.get('success'):
            return jsonify(results), 500
        
        # Add metadata
        results['analysis_id'] = analysis_id
        results['filename'] = filename
        results['timestamp'] = datetime.now().isoformat()
        
        # Save report
        report_path = os.path.join(app.config['REPORTS_FOLDER'], f"{analysis_id}.json")
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Analysis complete for {analysis_id}")
        
        return jsonify(results)
    
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error in analyze endpoint: {e}\n{error_traceback}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/report/<analysis_id>', methods=['GET'])
def get_report(analysis_id):
    """
    Retrieve a saved analysis report
    
    Args:
        analysis_id: UUID of the analysis
        
    Returns: JSON report
    """
    try:
        report_path = os.path.join(app.config['REPORTS_FOLDER'], f"{analysis_id}.json")
        
        if not os.path.exists(report_path):
            return jsonify({
                'success': False,
                'error': 'Report not found'
            }), 404
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        return jsonify(report)
    
    except Exception as e:
        logger.error(f"Error retrieving report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/download/<analysis_id>', methods=['GET'])
def download_report(analysis_id):
    """
    Download analysis report as JSON file
    
    Args:
        analysis_id: UUID of the analysis
    """
    try:
        report_filename = f"{analysis_id}.json"
        return send_from_directory(
            app.config['REPORTS_FOLDER'],
            report_filename,
            as_attachment=True,
            download_name=f"voicepulse_report_{analysis_id}.json"
        )
    
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/quick-analyze', methods=['POST'])
def quick_analyze():
    """
    Quick emotion analysis (single prediction)
    
    Accepts: multipart/form-data with 'audio' file
    Returns: Simple emotion + confidence
    """
    try:
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        file = request.files['audio']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file'
            }), 400
        
        # Save temporarily
        temp_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{temp_id}_{filename}")
        file.save(file_path)
        
        # Quick analysis
        results = pipeline.quick_analyze(file_path)
        
        # Cleanup
        try:
            os.remove(file_path)
        except:
            pass
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error in quick analyze: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large (max 50MB)'
    }), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    logger.info("Starting VoicePulse AI Backend Server...")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"Reports folder: {app.config['REPORTS_FOLDER']}")
    
    # Run server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
