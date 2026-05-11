import os
import tempfile
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from steganography import encode_image, decode_image

app = Flask(__name__)

# Configure upload and output folders to use the system temp directory
# This is required for Vercel (Serverless) since the main filesystem is read-only
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'stealthguard_uploads')
OUTPUT_FOLDER = os.path.join(tempfile.gettempdir(), 'stealthguard_outputs')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def landing():
    """Renders the landing page."""
    return render_template('landing.html')

@app.route('/app')
def index():
    """Renders the main steganography tool."""
    return render_template('index.html')

@app.route('/api/encode', methods=['POST'])
def handle_encode():
    """Handles the API request to hide a message in an image."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
        
    file = request.files['image']
    message = request.form.get('message')
    password = request.form.get('password')
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    if not message or not password:
        return jsonify({'error': 'Message and password are required'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Output must be PNG to avoid losing LSB data due to compression
        output_filename = f"secret_{filename.rsplit('.', 1)[0]}.png"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        try:
            encode_image(input_path, message, password, output_path)
            # Return the file directly for download
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up input file to save space
            if os.path.exists(input_path):
                os.remove(input_path)
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/decode', methods=['POST'])
def handle_decode():
    """Handles the API request to extract a message from an image."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
        
    file = request.files['image']
    password = request.form.get('password')
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    if not password:
        return jsonify({'error': 'Password is required'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        try:
            secret_message = decode_image(input_path, password)
            return jsonify({'message': secret_message})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        finally:
            # Clean up
            if os.path.exists(input_path):
                os.remove(input_path)
                
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    # Run the Flask app on localhost:5000
    app.run(debug=True, host='0.0.0.0', port=5000)
