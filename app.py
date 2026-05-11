import os
import tempfile
from flask import Flask, render_template, request, send_file, jsonify, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from steganography import encode_image, decode_image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stealthguard-super-secret-key'

# Configure Database
db_path = os.path.join(tempfile.gettempdir(), 'stealthguard.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

with app.app_context():
    db.create_all()

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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username already exists")
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Email already registered")
            
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
            
        return render_template('login.html', error="Invalid email or password")
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs the user out."""
    session.clear()
    return redirect(url_for('landing'))

@app.route('/about')
def about():
    """Renders the About Us page."""
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    """Renders the Privacy Policy page."""
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    """Renders the Terms & Conditions page."""
    return render_template('terms.html')

@app.route('/api/encode', methods=['POST'])
def handle_encode():
    """Handles the API request to hide a message in an image."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized. Please log in.'}), 401
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
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized. Please log in.'}), 401
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
