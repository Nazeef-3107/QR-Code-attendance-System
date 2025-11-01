from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt
from app.models.models import db, User, Student, Faculty
from app.utils.helpers import role_required
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    """Register a new student"""
    try:
        data = request.get_json()
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'msg': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'msg': 'Email already exists'}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            role='student'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Get the user ID without committing
        
        # Create student profile
        student = Student(
            user_id=user.id,
            student_id=data['student_id'],
            full_name=data['full_name'],
            department=data.get('department'),
            semester=data.get('semester')
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({'msg': 'Student registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Registration failed', 'error': str(e)}), 500

@auth_bp.route('/register/faculty', methods=['POST'])
def register_faculty():
    """Register a new faculty member (admin only)"""
    try:
        data = request.get_json()
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'msg': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'msg': 'Email already exists'}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            role='faculty'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Get the user ID without committing
        
        # Create faculty profile
        faculty = Faculty(
            user_id=user.id,
            faculty_id=data['faculty_id'],
            full_name=data['full_name'],
            department=data.get('department')
        )
        
        db.session.add(faculty)
        db.session.commit()
        
        return jsonify({'msg': 'Faculty registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Registration failed', 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'msg': 'Missing username or password'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Create additional claims
            additional_claims = {
                'role': user.role,
                'user_id': user.id
            }
            
            access_token = create_access_token(
                identity=user.id, 
                additional_claims=additional_claims
            )
            
            return jsonify({
                'access_token': access_token,
                'role': user.role,
                'user_id': user.id
            }), 200
        else:
            return jsonify({'msg': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'msg': 'Login failed', 'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@role_required('student')
def student_profile():
    """Get student profile information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
            
        student = Student.query.filter_by(user_id=current_user_id).first()
        
        if not student:
            return jsonify({'msg': 'Student profile not found'}), 404
            
        return jsonify({
            'username': user.username,
            'email': user.email,
            'student_id': student.student_id,
            'full_name': student.full_name,
            'department': student.department,
            'semester': student.semester
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve profile', 'error': str(e)}), 500