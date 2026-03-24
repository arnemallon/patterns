from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Use PostgreSQL if available, otherwise fallback to SQLite
    database_url = (os.getenv('DATABASE_URL') or '').strip()
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bitcoin_classifier.db'
        print("⚠️  Using SQLite database. For production, set DATABASE_URL to use PostgreSQL.")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    db.init_app(app)
    
    # Register blueprints
    from .routes import api
    app.register_blueprint(api, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 