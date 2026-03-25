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
    
    CORS(app, origins="*", supports_credentials=False)
    db.init_app(app)
    
    # Register blueprints
    from .routes import api
    app.register_blueprint(api, url_prefix='/api')
    
    # Root health check so Railway can verify the app is alive
    @app.route('/')
    def root_health():
        return {'status': 'ok'}

    # Create database tables and seed default user
    with app.app_context():
        db.create_all()
        _seed_default_user(app)
    
    return app


def _seed_default_user(app):
    """Create the default admin user if it doesn't exist yet."""
    try:
        from app.models.user import User
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@blockchainanalysis.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Created default admin user.")
    except Exception as e:
        db.session.rollback()
        print(f"Warning: Could not seed default user: {e}")