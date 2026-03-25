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
    
    @app.route('/')
    def root_health():
        return {'status': 'ok'}

    @app.route('/debug/paths')
    def debug_paths():
        import glob
        project_root = os.environ.get('PROJECT_ROOT', 'NOT SET')
        ml_dir = os.path.join(project_root, 'ml-models')
        ml_files = glob.glob(os.path.join(ml_dir, '**/*'), recursive=True) if os.path.exists(ml_dir) else []
        return {
            'project_root': project_root,
            'cwd': os.getcwd(),
            'ml_dir_exists': os.path.exists(ml_dir),
            'ml_files': ml_files,
            'app_contents': os.listdir('/app') if os.path.exists('/app') else [],
        }

    @app.route('/debug/model')
    def debug_model():
        errors = []
        model_path = os.path.join(os.environ.get('PROJECT_ROOT', '/app'), 'ml-models', 'without_structural_features', 'bitcoin_classifier.keras')
        scaler_path = os.path.join(os.environ.get('PROJECT_ROOT', '/app'), 'ml-models', 'without_structural_features', 'scaler.json')
        model_loaded = False
        scaler_loaded = False
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(model_path, compile=False, safe_mode=False)
            model_loaded = True
        except Exception as e:
            errors.append(f"Model load error: {str(e)}")
        try:
            import json
            with open(scaler_path, 'r') as f:
                json.load(f)
            scaler_loaded = True
        except Exception as e:
            errors.append(f"Scaler load error: {str(e)}")
        return {
            'model_path': model_path,
            'scaler_path': scaler_path,
            'model_loaded': model_loaded,
            'scaler_loaded': scaler_loaded,
            'errors': errors,
        }

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