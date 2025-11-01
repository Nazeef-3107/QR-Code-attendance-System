from flask import Flask
from flask_jwt_extended import JWTManager
from config.config import Config
from app.models.models import db
from app.controllers.auth_controller import auth_bp
from app.controllers.attendance_controller import attendance_bp
from app.controllers.admin_controller import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return {'message': 'QR Code Attendance System API'}
    
    return app