"""
Simple QR Attendance System API
Demonstrates core functionality without external dependencies
"""

from flask import Flask, request, jsonify, render_template
from app.models.simple_models import User, Student, Faculty, Course, Session, Attendance, storage
import uuid
from datetime import datetime, timedelta
import qrcode
import io
import base64

app = Flask(__name__)

# Simple authentication storage (in production, use proper JWT)
current_user = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api')
def api_info():
    return jsonify({"message": "QR Code Attendance System API", "endpoints": [
        "POST /register/student",
        "POST /register/faculty", 
        "POST /login",
        "POST /faculty/session/create",
        "POST /student/attendance/mark",
        "GET /student/attendance/history"
    ]})

@app.route('/register/student', methods=['POST'])
def register_student():
    """Register a new student"""
    try:
        data = request.get_json()
        
        # Check if username already exists
        if storage.get_user_by_username(data['username']):
            return jsonify({'msg': 'Username already exists'}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],  # In real app, this would be hashed
            role='student'
        )
        
        storage.add_user(user)
        
        # Create student profile
        student = Student(
            user_id=user.id,
            student_id=data['student_id'],
            full_name=data['full_name'],
            department=data.get('department'),
            semester=data.get('semester')
        )
        
        storage.add_student(student)
        
        return jsonify({'msg': 'Student registered successfully', 'user_id': user.id}), 201
    except Exception as e:
        return jsonify({'msg': 'Registration failed', 'error': str(e)}), 500

@app.route('/register/faculty', methods=['POST'])
def register_faculty():
    """Register a new faculty member"""
    try:
        data = request.get_json()
        
        # Check if username already exists
        if storage.get_user_by_username(data['username']):
            return jsonify({'msg': 'Username already exists'}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],  # In real app, this would be hashed
            role='faculty'
        )
        
        storage.add_user(user)
        
        # Create faculty profile
        faculty = Faculty(
            user_id=user.id,
            faculty_id=data['faculty_id'],
            full_name=data['full_name'],
            department=data.get('department')
        )
        
        storage.add_faculty(faculty)
        
        return jsonify({'msg': 'Faculty registered successfully', 'user_id': user.id}), 201
    except Exception as e:
        return jsonify({'msg': 'Registration failed', 'error': str(e)}), 500

@app.route('/register/admin', methods=['POST'])
def register_admin():
    """Register a new admin (requires admin code)"""
    try:
        data = request.get_json()
        print(f"Admin registration attempt - Username: {data.get('username')}, Admin code provided: {data.get('admin_code')}")
        
        # Verify admin code
        provided_code = data.get('admin_code', '').strip()
        expected_code = 'ADMIN2024'
        
        if provided_code != expected_code:
            print(f"Admin code mismatch! Provided: '{provided_code}', Expected: '{expected_code}'")
            return jsonify({'msg': f'Invalid admin code. Expected: {expected_code}'}), 403
        
        # Check if username already exists
        if storage.get_user_by_username(data['username']):
            return jsonify({'msg': 'Username already exists'}), 400
        
        # Create admin user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role='admin'
        )
        
        storage.add_user(user)
        print(f"Admin user created successfully: {user.username}")
        
        return jsonify({'msg': 'Admin registered successfully', 'user_id': user.id}), 201
    except Exception as e:
        print(f"Admin registration error: {str(e)}")
        return jsonify({'msg': 'Registration failed', 'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """Authenticate user"""
    try:
        global current_user
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'msg': 'Missing username or password'}), 400
        
        user = storage.get_user_by_username(username)
        
        if user and user.check_password(password):
            current_user = user
            return jsonify({
                'msg': 'Login successful',
                'user_id': user.id,
                'role': user.role
            }), 200
        else:
            return jsonify({'msg': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'msg': 'Login failed', 'error': str(e)}), 500

@app.route('/faculty/session/create', methods=['POST'])
def create_session():
    """Create a new attendance session with QR code"""
    global current_user
    if not current_user:
        return jsonify({'msg': 'Please login first'}), 401
    
    if current_user.role != 'faculty':
        return jsonify({'msg': 'Access Denied: Faculty access required. You are logged in as ' + current_user.role}), 403
    
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({'msg': 'Course ID is required'}), 400
        
        # Create session
        session = Session(course_id, current_user.id)
        storage.add_session(session)
        
        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4,
        )
        qr.add_data(session.qr_code_token)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'msg': 'Session created successfully',
            'session_id': session.id,
            'qr_code_token': session.qr_code_token,
            'qr_code_image': f'data:image/png;base64,{img_base64}',
            'expiration': session.qr_expiration
        }), 201
    except Exception as e:
        return jsonify({'msg': 'Failed to create session', 'error': str(e)}), 500

@app.route('/student/attendance/mark', methods=['POST'])
def mark_attendance():
    """Mark attendance using QR code token"""
    global current_user
    if not current_user or current_user.role != 'student':
        return jsonify({'msg': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        qr_token = data.get('qr_token')
        
        if not qr_token:
            return jsonify({'msg': 'QR token is required'}), 400
        
        # Find the session with the QR token
        session = storage.get_session_by_token(qr_token)
        
        if not session:
            return jsonify({'msg': 'Invalid QR code'}), 400
        
        # Check if session is still active
        expiration = datetime.fromisoformat(session.qr_expiration)
        if not session.is_active or expiration < datetime.now():
            return jsonify({'msg': 'QR code has expired'}), 400
        
        # Get student profile
        student = storage.get_student_by_user_id(current_user.id)
        
        if not student:
            return jsonify({'msg': 'Student profile not found'}), 404
        
        # Mark attendance
        attendance = Attendance(session.id, student.id)
        storage.add_attendance(attendance)
        
        return jsonify({
            'msg': 'Attendance marked successfully',
            'session_id': session.id,
            'marked_at': attendance.marked_at
        }), 201
    except Exception as e:
        return jsonify({'msg': 'Failed to mark attendance', 'error': str(e)}), 500

@app.route('/student/attendance/history', methods=['GET'])
def get_student_attendance_history():
    """Get attendance history for the logged-in student"""
    global current_user
    if not current_user or current_user.role != 'student':
        return jsonify({'msg': 'Unauthorized'}), 401
    
    try:
        # Get student profile
        student = storage.get_student_by_user_id(current_user.id)
        
        if not student:
            return jsonify({'msg': 'Student profile not found'}), 404
        
        # Get all attendances for this student
        attendances = storage.get_attendances_by_student(student.id)
        
        # Prepare attendance data
        attendance_data = []
        for att in attendances:
            session = storage.get_session(att.session_id)
            attendance_data.append({
                'session_id': att.session_id,
                'marked_at': att.marked_at,
                'course_id': session.course_id if session else None
            })
        
        return jsonify({
            'student_name': student.full_name,
            'total_attendances': len(attendance_data),
            'attendance_history': attendance_data
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve attendance history', 'error': str(e)}), 500

@app.route('/student/profile', methods=['GET'])
def get_student_profile():
    """Get student profile information"""
    global current_user
    if not current_user or current_user.role != 'student':
        return jsonify({'msg': 'Unauthorized'}), 401
    
    try:
        student = storage.get_student_by_user_id(current_user.id)
        if not student:
            return jsonify({'msg': 'Student profile not found'}), 404
        
        return jsonify({
            'username': current_user.username,
            'email': current_user.email,
            'student_id': student.student_id,
            'full_name': student.full_name,
            'department': student.department,
            'semester': student.semester
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve profile', 'error': str(e)}), 500

# Faculty Course Management
@app.route('/faculty/courses', methods=['GET'])
def get_faculty_courses():
    """Get courses assigned to the logged-in faculty"""
    global current_user
    if not current_user:
        return jsonify({'msg': 'Please login first'}), 401
    
    if current_user.role != 'faculty':
        return jsonify({'msg': 'Access Denied: Faculty access required'}), 403
    
    try:
        faculty = storage.get_faculty_by_user_id(current_user.id)
        if not faculty:
            return jsonify({'msg': 'Faculty profile not found'}), 404
        
        # Get courses assigned to this faculty
        courses_data = []
        for course in storage.courses.values():
            if course.faculty_id == faculty.id:
                courses_data.append({
                    'id': course.id,
                    'course_code': course.course_code,
                    'course_name': course.course_name,
                    'department': course.department,
                    'semester': course.semester
                })
        
        return jsonify({
            'total_courses': len(courses_data),
            'courses': courses_data
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve courses', 'error': str(e)}), 500

@app.route('/faculty/course/create', methods=['POST'])
def create_course():
    """Create a new course (Faculty)"""
    global current_user
    if not current_user or current_user.role != 'faculty':
        return jsonify({'msg': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        faculty = storage.get_faculty_by_user_id(current_user.id)
        
        if not faculty:
            return jsonify({'msg': 'Faculty profile not found'}), 404
        
        # Check if course code already exists
        for course in storage.courses.values():
            if course.course_code == data['course_code']:
                return jsonify({'msg': 'Course code already exists'}), 400
        
        # Create course
        course = Course(
            course_code=data['course_code'],
            course_name=data['course_name'],
            department=data.get('department'),
            semester=data.get('semester'),
            faculty_id=faculty.id
        )
        
        storage.add_course(course)
        
        return jsonify({
            'msg': 'Course created successfully',
            'course_id': course.id
        }), 201
    except Exception as e:
        return jsonify({'msg': 'Failed to create course', 'error': str(e)}), 500

@app.route('/faculty/course/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete a course (Faculty - only their own courses)"""
    global current_user
    if not current_user or current_user.role != 'faculty':
        return jsonify({'msg': 'Unauthorized'}), 401
    
    try:
        faculty = storage.get_faculty_by_user_id(current_user.id)
        if not faculty:
            return jsonify({'msg': 'Faculty profile not found'}), 404
        
        course = storage.get_course(course_id)
        if not course:
            return jsonify({'msg': 'Course not found'}), 404
        
        # Check if course belongs to this faculty
        if course.faculty_id != faculty.id:
            return jsonify({'msg': 'Unauthorized - not your course'}), 403
        
        # Delete course
        del storage.courses[course_id]
        
        return jsonify({'msg': 'Course deleted successfully'}), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to delete course', 'error': str(e)}), 500

@app.route('/faculty/profile', methods=['GET'])
def get_faculty_profile():
    """Get faculty profile information"""
    global current_user
    if not current_user or current_user.role != 'faculty':
        return jsonify({'msg': 'Unauthorized'}), 401
    
    try:
        faculty = storage.get_faculty_by_user_id(current_user.id)
        if not faculty:
            return jsonify({'msg': 'Faculty profile not found'}), 404
        
        return jsonify({
            'username': current_user.username,
            'email': current_user.email,
            'faculty_id': faculty.faculty_id,
            'full_name': faculty.full_name,
            'department': faculty.department
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve profile', 'error': str(e)}), 500

@app.route('/faculty/attendance/report', methods=['GET'])
def get_attendance_report():
    """Get attendance report for a specific course (Faculty only)"""
    global current_user
    if not current_user:
        return jsonify({'msg': 'Please login first'}), 401
    
    if current_user.role != 'faculty':
        return jsonify({'msg': 'Access Denied: Faculty access required'}), 403
    
    try:
        course_id = request.args.get('course_id')
        if not course_id:
            return jsonify({'msg': 'Course ID is required'}), 400
        
        # Get all students
        all_students = storage.students
        
        # Sample data - In production, this would query actual attendance records
        # For now, generating sample data based on course
        students_data = []
        total_sessions = 20  # Sample: assume 20 sessions per course
        
        for student in all_students:
            # Generate sample attendance (in production, query actual records)
            import random
            classes_attended = random.randint(10, 20)
            attendance_percentage = round((classes_attended / total_sessions) * 100, 1)
            
            students_data.append({
                'student_id': student.student_id,
                'student_name': student.full_name,
                'classes_attended': classes_attended,
                'total_classes': total_sessions,
                'attendance_percentage': attendance_percentage
            })
        
        # Calculate average attendance
        if students_data:
            avg_attendance = round(sum(s['attendance_percentage'] for s in students_data) / len(students_data), 1)
        else:
            avg_attendance = 0
        
        return jsonify({
            'course_id': course_id,
            'total_students': len(students_data),
            'total_sessions': total_sessions,
            'average_attendance': avg_attendance,
            'students': students_data
        }), 200
        
    except Exception as e:
        print(f"Attendance report error: {str(e)}")
        return jsonify({'msg': 'Failed to generate report', 'error': str(e)}), 500

# Admin endpoints
@app.route('/admin/users', methods=['GET'])
def get_all_users():
    """Get all users (Admin only)"""
    global current_user
    if not current_user:
        return jsonify({'msg': 'Please login first'}), 401
    
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access Denied: Administrator access required'}), 403
    
    try:
        users_data = []
        for user in storage.users.values():
            user_info = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
            
            if user.role == 'student':
                student = storage.get_student_by_user_id(user.id)
                if student:
                    user_info['full_name'] = student.full_name
                    user_info['student_id'] = student.student_id
                    user_info['department'] = student.department
            elif user.role == 'faculty':
                faculty = storage.get_faculty_by_user_id(user.id)
                if faculty:
                    user_info['full_name'] = faculty.full_name
                    user_info['faculty_id'] = faculty.faculty_id
                    user_info['department'] = faculty.department
                    
            users_data.append(user_info)
        
        return jsonify({
            'total_users': len(users_data),
            'users': users_data
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve users', 'error': str(e)}), 500

@app.route('/admin/courses', methods=['GET'])
def get_all_courses():
    """Get all courses (Admin only)"""
    global current_user
    if not current_user:
        return jsonify({'msg': 'Please login first'}), 401
    
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access Denied: Administrator access required'}), 403
    
    try:
        courses_data = []
        for course in storage.courses.values():
            faculty = storage.get_faculty(course.faculty_id) if course.faculty_id else None
            courses_data.append({
                'id': course.id,
                'course_code': course.course_code,
                'course_name': course.course_name,
                'department': course.department,
                'semester': course.semester,
                'faculty_name': faculty.full_name if faculty else 'Not assigned'
            })
        
        return jsonify({
            'total_courses': len(courses_data),
            'courses': courses_data
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve courses', 'error': str(e)}), 500

@app.route('/admin/sessions', methods=['GET'])
def get_all_sessions():
    """Get all sessions (Admin only)"""
    global current_user
    if not current_user:
        return jsonify({'msg': 'Please login first'}), 401
    
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access Denied: Administrator access required'}), 403
    
    try:
        sessions_data = []
        for session in storage.sessions.values():
            course = storage.get_course(session.course_id)
            attendances = storage.get_attendances_by_session(session.id)
            sessions_data.append({
                'id': session.id,
                'course': course.course_name if course else 'Unknown',
                'session_date': session.session_date.isoformat() if hasattr(session.session_date, 'isoformat') else str(session.session_date),
                'is_active': session.is_active,
                'total_attendances': len(attendances)
            })
        
        return jsonify({
            'total_sessions': len(sessions_data),
            'sessions': sessions_data
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve sessions', 'error': str(e)}), 500

@app.route('/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get dashboard statistics (Admin only)"""
    global current_user
    if not current_user:
        return jsonify({'msg': 'Please login first'}), 401
    
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access Denied: Administrator access required'}), 403
    
    try:
        total_students = len([s for s in storage.students.values()])
        total_faculty = len([f for f in storage.faculties.values()])
        total_courses = len([c for c in storage.courses.values()])
        total_sessions = len([s for s in storage.sessions.values()])
        total_attendances = len([a for a in storage.attendances.values()])
        
        return jsonify({
            'total_students': total_students,
            'total_faculty': total_faculty,
            'total_courses': total_courses,
            'total_sessions': total_sessions,
            'total_attendances': total_attendances
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve statistics', 'error': str(e)}), 500

@app.route('/admin/profile', methods=['GET'])
def get_admin_profile():
    """Get admin profile information"""
    global current_user
    if not current_user or current_user.role != 'admin':
        return jsonify({'msg': 'Unauthorized'}), 401
    
    try:
        return jsonify({
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to retrieve profile', 'error': str(e)}), 500

if __name__ == '__main__':
    # Add sample data for testing
    # Create admin user
    admin_user = User('admin', 'admin@college.edu', 'admin123', 'admin')
    storage.add_user(admin_user)
    
    # Create a faculty user
    faculty_user = User('prof_smith', 'smith@college.edu', 'password123', 'faculty')
    storage.add_user(faculty_user)
    
    faculty = Faculty(faculty_user.id, 'F001', 'Professor Smith', 'Computer Science')
    storage.add_faculty(faculty)
    
    # Create a course
    course = Course('CS101', 'Introduction to Computer Science', 'Computer Science', 1, faculty.id)
    storage.add_course(course)
    
    # Create a student user
    student_user = User('john_doe', 'john@student.edu', 'password123', 'student')
    storage.add_user(student_user)
    
    student = Student(student_user.id, 'S001', 'John Doe', 'Computer Science', 1)
    storage.add_student(student)
    
    print("Sample data created:")
    print("- Admin: admin / admin123")
    print("- Faculty: prof_smith / password123")
    print("- Student: john_doe / password123")
    print("- Course: CS101")
    
    app.run(debug=True, host='0.0.0.0', port=5000)