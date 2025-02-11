import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
DATABASE = 'database.db'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database and create the images table if it doesn't exist."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            filename TEXT NOT NULL,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def allowed_file(filename):
    """Check if the file has one of the allowed extensions."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Validate that username and file are provided
        if 'username' not in request.form or not request.form['username'].strip():
            return redirect(request.url)
        if 'image' not in request.files:
            return redirect(request.url)
        
        username = request.form['username'].strip()
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            conn = get_db_connection()
            conn.execute('INSERT INTO images (username, filename) VALUES (?, ?)', (username, filename))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    
    # GET: fetch images from the database (latest first)
    conn = get_db_connection()
    images = conn.execute('SELECT * FROM images ORDER BY uploaded_at DESC').fetchall()
    conn.close()
    return render_template('index.html', images=images)

if __name__ == '__main__':
    # Use the PORT environment variable if available (Render sets it), default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
