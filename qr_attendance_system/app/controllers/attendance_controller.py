from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.models.models import db, Session, Attendance, Student, Course, Enrollment
from app.utils.helpers import role_required, roles_required, generate_time_bound_qr
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/faculty/session/create', methods=['POST'])
@role_required('faculty')
def create_session():
    """Create a new attendance session with QR code"""
    try:
        faculty_id = get_jwt().get('user_id')
        data = request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({'msg': 'Course ID is required'}), 400
        
        # Generate time-bound QR code
        qr_data = generate_time_bound_qr(course_id, faculty_id)
        
        # Create session
        session = Session(
            course_id=course_id,
            faculty_id=faculty_id,
            qr_code_token=qr_data['token'],
            qr_expiration=qr_data['expiration']
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'msg': 'Session created successfully',
            'session_id': session.id,
            'qr_code': qr_data['qr_code'],
            'expiration': qr_data['expiration']
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Failed to create session', 'error': str(e)}), 500

@attendance_bp.route('/student/attendance/mark', methods=['POST'])
@role_required('student')
def mark_attendance():
    """Mark attendance using QR code token"""
    try:
        student_user_id = get_jwt_identity()
        data = request.get_json()
        qr_token = data.get('qr_token')
        
        if not qr_token:
            return jsonify({'msg': 'QR token is required'}), 400
        
        # Find the session with the QR token
        session = Session.query.filter_by(qr_code_token=qr_token).first()
        
        if not session:
            return jsonify({'msg': 'Invalid QR code'}), 400
        
        # Check if session is still active
        if not session.is_active or session.qr_expiration < datetime.utcnow():
            return jsonify({'msg': 'QR code has expired'}), 400
        
        # Get student profile
        student = Student.query.filter_by(user_id=student_user_id).first()
        
        if not student:
            return jsonify({'msg': 'Student profile not found'}), 404
        
        # Check if student is enrolled in the course
        enrollment = Enrollment.query.filter_by(
            student_id=student.id,
            course_id=session.course_id
        ).first()
        
        if not enrollment:
            return jsonify({'msg': 'You are not enrolled in this course'}), 403
        
        # Check if attendance already marked
        existing_attendance = Attendance.query.filter_by(
            session_id=session.id,
            student_id=student.id
        ).first()
        
        if existing_attendance:
            return jsonify({'msg': 'Attendance already marked for this session'}), 400
        
        # Mark attendance
        attendance = Attendance(
            session_id=session.id,
            student_id=student.id
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        # Get course information
        course = Course.query.get(session.course_id)
        
        return jsonify({
            'msg': 'Attendance marked successfully',
            'course': course.course_name if course else 'Unknown',
            'session_date': session.session_date
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Failed to mark attendance', 'error': str(e)}), 500

@attendance_bp.route('/faculty/session/<int:session_id>/attendances', methods=['GET'])
@role_required('faculty')
def get_session_attendances(session_id):
    """Get all attendances for a specific session"""
    try:
        faculty_id = get_jwt().get('user_id')
        
        # Verify the session belongs to this faculty
        session = Session.query.filter_by(id=session_id, faculty_id=faculty_id).first()
        
        if not session:
            return jsonify({'msg': 'Session not found or unauthorized'}), 404
        
        # Get all attendances for this session
        attendances = Attendance.query.filter_by(session_id=session_id).all()
        
        # Prepare attendance data
        attendance_data = []
        for att in attendances:
            student = Student.query.get(att.student_id)
            if student:
                attendance_data.append({
                    'student_id': student.student_id,
                    'student_name': student.full_name,
                    'marked_at': att.marked_at
                })
        
        # Get course information
        course = Course.query.get(session.course_id)
        
        return jsonify({
            'session_id': session_id,
            'course': course.course_name if course else 'Unknown',
            'total_attendances': len(attendance_data),
            'attendances': attendance_data
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve attendances', 'error': str(e)}), 500

@attendance_bp.route('/student/attendance/history', methods=['GET'])
@role_required('student')
def get_student_attendance_history():
    """Get attendance history for the logged-in student"""
    try:
        student_user_id = get_jwt_identity()
        
        # Get student profile
        student = Student.query.filter_by(user_id=student_user_id).first()
        
        if not student:
            return jsonify({'msg': 'Student profile not found'}), 404
        
        # Get all attendances for this student
        attendances = Attendance.query.filter_by(student_id=student.id).all()
        
        # Prepare attendance data
        attendance_data = []
        for att in attendances:
            session = Session.query.get(att.session_id)
            course = Course.query.get(session.course_id) if session else None
            
            attendance_data.append({
                'course': course.course_name if course else 'Unknown',
                'course_code': course.course_code if course else 'Unknown',
                'session_date': session.session_date if session else None,
                'marked_at': att.marked_at
            })
        
        return jsonify({
            'student_name': student.full_name,
            'total_attendances': len(attendance_data),
            'attendance_history': attendance_data
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve attendance history', 'error': str(e)}), 500