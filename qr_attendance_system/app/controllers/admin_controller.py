from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.models import db, User, Student, Faculty, Course, Enrollment, Session
from app.utils.helpers import role_required
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/users', methods=['GET'])
@role_required('admin')
def get_all_users():
    """Get all users in the system"""
    try:
        users = User.query.all()
        user_data = []
        
        for user in users:
            user_info = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at
            }
            
            # Add role-specific information
            if user.role == 'student':
                student = Student.query.filter_by(user_id=user.id).first()
                if student:
                    user_info['student_id'] = student.student_id
                    user_info['full_name'] = student.full_name
                    user_info['department'] = student.department
            elif user.role == 'faculty':
                faculty = Faculty.query.filter_by(user_id=user.id).first()
                if faculty:
                    user_info['faculty_id'] = faculty.faculty_id
                    user_info['full_name'] = faculty.full_name
                    user_info['department'] = faculty.department
                    
            user_data.append(user_info)
        
        return jsonify({
            'total_users': len(user_data),
            'users': user_data
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve users', 'error': str(e)}), 500

@admin_bp.route('/admin/student/<int:student_id>', methods=['DELETE'])
@role_required('admin')
def delete_student(student_id):
    """Delete a student and associated user"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'msg': 'Student not found'}), 404
        
        # Delete associated user
        user = User.query.get(student.user_id)
        
        # Delete student record
        db.session.delete(student)
        
        # Delete user record
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        return jsonify({'msg': 'Student deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Failed to delete student', 'error': str(e)}), 500

@admin_bp.route('/admin/faculty/<int:faculty_id>', methods=['DELETE'])
@role_required('admin')
def delete_faculty(faculty_id):
    """Delete a faculty member and associated user"""
    try:
        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            return jsonify({'msg': 'Faculty not found'}), 404
        
        # Delete associated user
        user = User.query.get(faculty.user_id)
        
        # Delete faculty record
        db.session.delete(faculty)
        
        # Delete user record
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        return jsonify({'msg': 'Faculty deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Failed to delete faculty', 'error': str(e)}), 500

@admin_bp.route('/admin/course', methods=['POST'])
@role_required('admin')
def create_course():
    """Create a new course"""
    try:
        data = request.get_json()
        
        # Check if course code already exists
        if Course.query.filter_by(course_code=data['course_code']).first():
            return jsonify({'msg': 'Course code already exists'}), 400
        
        course = Course(
            course_code=data['course_code'],
            course_name=data['course_name'],
            department=data.get('department'),
            semester=data.get('semester'),
            faculty_id=data.get('faculty_id')
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'msg': 'Course created successfully',
            'course_id': course.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Failed to create course', 'error': str(e)}), 500

@admin_bp.route('/admin/course/<int:course_id>', methods=['DELETE'])
@role_required('admin')
def delete_course(course_id):
    """Delete a course"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'msg': 'Course not found'}), 404
        
        db.session.delete(course)
        db.session.commit()
        
        return jsonify({'msg': 'Course deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Failed to delete course', 'error': str(e)}), 500

@admin_bp.route('/admin/enrollment', methods=['POST'])
@role_required('admin')
def create_enrollment():
    """Enroll a student in a course"""
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        course_id = data.get('course_id')
        
        # Check if enrollment already exists
        existing_enrollment = Enrollment.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        
        if existing_enrollment:
            return jsonify({'msg': 'Student already enrolled in this course'}), 400
        
        # Check if student and course exist
        student = Student.query.get(student_id)
        course = Course.query.get(course_id)
        
        if not student:
            return jsonify({'msg': 'Student not found'}), 404
        
        if not course:
            return jsonify({'msg': 'Course not found'}), 404
        
        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            'msg': 'Student enrolled successfully',
            'enrollment_id': enrollment.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Failed to enroll student', 'error': str(e)}), 500

@admin_bp.route('/admin/dashboard', methods=['GET'])
@role_required('admin')
def admin_dashboard():
    """Get admin dashboard statistics"""
    try:
        # Get counts
        total_students = Student.query.count()
        total_faculties = Faculty.query.count()
        total_courses = Course.query.count()
        total_sessions = db.session.query(db.func.count()).select_from(Session).scalar() or 0
        
        # Get recent enrollments
        recent_enrollments = Enrollment.query.order_by(Enrollment.enrollment_date.desc()).limit(5).all()
        enrollment_data = []
        
        for enrollment in recent_enrollments:
            student = Student.query.get(enrollment.student_id)
            course = Course.query.get(enrollment.course_id)
            
            if student and course:
                enrollment_data.append({
                    'student_name': student.full_name,
                    'course_name': course.course_name,
                    'enrollment_date': enrollment.enrollment_date
                })
        
        return jsonify({
            'statistics': {
                'total_students': total_students,
                'total_faculties': total_faculties,
                'total_courses': total_courses,
                'total_sessions': total_sessions
            },
            'recent_enrollments': enrollment_data
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve dashboard data', 'error': str(e)}), 500