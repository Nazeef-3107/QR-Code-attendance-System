"""
QR Code Attendance System - Command Line Demo
This demonstrates the core functionality of the system without web dependencies
"""

import uuid
import json
from datetime import datetime, timedelta

class User:
    """User model for students, faculty, and admins"""
    def __init__(self, user_id, username, email, password, role):
        self.id = user_id
        self.username = username
        self.email = email
        self.password = password  # In real app, this would be hashed
        self.role = role  # student, faculty, admin
        self.created_at = datetime.now()
    
    def check_password(self, password):
        """Check if provided password matches stored password"""
        return self.password == password

class Student:
    """Student profile model"""
    def __init__(self, student_id, user_id, full_name, department=None, semester=None):
        self.id = student_id
        self.user_id = user_id
        self.full_name = full_name
        self.department = department
        self.semester = semester

class Faculty:
    """Faculty profile model"""
    def __init__(self, faculty_id, user_id, full_name, department=None):
        self.id = faculty_id
        self.user_id = user_id
        self.full_name = full_name
        self.department = department

class Course:
    """Course model"""
    def __init__(self, course_id, course_code, course_name, department=None, semester=None, faculty_id=None):
        self.id = course_id
        self.course_code = course_code
        self.course_name = course_name
        self.department = department
        self.semester = semester
        self.faculty_id = faculty_id

class Session:
    """Attendance session with QR code"""
    def __init__(self, session_id, course_id, faculty_id):
        self.id = session_id
        self.course_id = course_id
        self.faculty_id = faculty_id
        self.qr_code_token = str(uuid.uuid4())
        self.qr_expiration = datetime.now() + timedelta(minutes=3)
        self.is_active = True
        self.session_date = datetime.now()

class Attendance:
    """Attendance record"""
    def __init__(self, attendance_id, session_id, student_id):
        self.id = attendance_id
        self.session_id = session_id
        self.student_id = student_id
        self.marked_at = datetime.now()

# Simple in-memory storage for demonstration
class Storage:
    """Simple storage for demonstration purposes"""
    def __init__(self):
        self.users = {}
        self.students = {}
        self.faculties = {}
        self.courses = {}
        self.sessions = {}
        self.attendances = {}
    
    def add_user(self, user):
        self.users[user.id] = user
    
    def get_user(self, user_id):
        return self.users.get(user_id)
    
    def get_user_by_username(self, username):
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def add_student(self, student):
        self.students[student.id] = student
    
    def get_student(self, student_id):
        return self.students.get(student_id)
    
    def get_student_by_user_id(self, user_id):
        for student in self.students.values():
            if student.user_id == user_id:
                return student
        return None
    
    def add_faculty(self, faculty):
        self.faculties[faculty.id] = faculty
    
    def get_faculty(self, faculty_id):
        return self.faculties.get(faculty_id)
    
    def add_course(self, course):
        self.courses[course.id] = course
    
    def get_course(self, course_id):
        return self.courses.get(course_id)
    
    def add_session(self, session):
        self.sessions[session.id] = session
    
    def get_session(self, session_id):
        return self.sessions.get(session_id)
    
    def get_session_by_token(self, token):
        for session in self.sessions.values():
            if session.qr_code_token == token:
                return session
        return None
    
    def add_attendance(self, attendance):
        self.attendances[attendance.id] = attendance
    
    def get_attendance(self, attendance_id):
        return self.attendances.get(attendance_id)
    
    def get_attendances_by_session(self, session_id):
        return [a for a in self.attendances.values() if a.session_id == session_id]
    
    def get_attendances_by_student(self, student_id):
        return [a for a in self.attendances.values() if a.student_id == student_id]

# Global storage instance
storage = Storage()

class QRAttendanceSystem:
    """Main system class"""
    
    def __init__(self):
        self.current_user = None
        self.initialize_sample_data()
    
    def initialize_sample_data(self):
        """Create sample data for demonstration"""
        # Create a faculty user
        faculty_user = User('F001', 'prof_smith', 'smith@college.edu', 'password123', 'faculty')
        storage.add_user(faculty_user)
        
        faculty = Faculty('FAC001', faculty_user.id, 'Professor Smith', 'Computer Science')
        storage.add_faculty(faculty)
        
        # Create a course
        course = Course('C001', 'CS101', 'Introduction to Computer Science', 'Computer Science', 1, faculty.id)
        storage.add_course(course)
        
        # Create a student user
        student_user = User('S001', 'john_doe', 'john@student.edu', 'password123', 'student')
        storage.add_user(student_user)
        
        student = Student('STU001', student_user.id, 'John Doe', 'Computer Science', 1)
        storage.add_student(student)
        
        print("Sample data created:")
        print("- Faculty: prof_smith / password123")
        print("- Student: john_doe / password123")
        print("- Course: CS101")
        print()
    
    def login(self, username, password):
        """Authenticate user"""
        user = storage.get_user_by_username(username)
        
        if user and user.check_password(password):
            self.current_user = user
            return {
                'success': True,
                'message': 'Login successful',
                'user_id': user.id,
                'role': user.role
            }
        else:
            return {
                'success': False,
                'message': 'Invalid credentials'
            }
    
    def create_session(self, course_id):
        """Create a new attendance session with QR code"""
        if not self.current_user or self.current_user.role != 'faculty':
            return {
                'success': False,
                'message': 'Unauthorized - Only faculty can create sessions'
            }
        
        # Create session
        session_id = f"SES{len(storage.sessions) + 1}"
        session = Session(session_id, course_id, self.current_user.id)
        storage.add_session(session)
        
        return {
            'success': True,
            'message': 'Session created successfully',
            'session_id': session.id,
            'qr_code_token': session.qr_code_token,
            'expiration': session.qr_expiration.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def mark_attendance(self, qr_token):
        """Mark attendance using QR code token"""
        if not self.current_user or self.current_user.role != 'student':
            return {
                'success': False,
                'message': 'Unauthorized - Only students can mark attendance'
            }
        
        if not qr_token:
            return {
                'success': False,
                'message': 'QR token is required'
            }
        
        # Find the session with the QR token
        session = storage.get_session_by_token(qr_token)
        
        if not session:
            return {
                'success': False,
                'message': 'Invalid QR code'
            }
        
        # Check if session is still active
        if not session.is_active or session.qr_expiration < datetime.now():
            return {
                'success': False,
                'message': 'QR code has expired'
            }
        
        # Get student profile
        student = storage.get_student_by_user_id(self.current_user.id)
        
        if not student:
            return {
                'success': False,
                'message': 'Student profile not found'
            }
        
        # Check if attendance already marked
        existing_attendance = None
        for att in storage.attendances.values():
            if att.session_id == session.id and att.student_id == student.id:
                existing_attendance = att
                break
        
        if existing_attendance:
            return {
                'success': False,
                'message': 'Attendance already marked for this session'
            }
        
        # Mark attendance
        attendance_id = f"ATT{len(storage.attendances) + 1}"
        attendance = Attendance(attendance_id, session.id, student.id)
        storage.add_attendance(attendance)
        
        return {
            'success': True,
            'message': 'Attendance marked successfully',
            'session_id': session.id,
            'marked_at': attendance.marked_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_student_attendance_history(self):
        """Get attendance history for the logged-in student"""
        if not self.current_user or self.current_user.role != 'student':
            return {
                'success': False,
                'message': 'Unauthorized - Only students can view attendance history'
            }
        
        # Get student profile
        student = storage.get_student_by_user_id(self.current_user.id)
        
        if not student:
            return {
                'success': False,
                'message': 'Student profile not found'
            }
        
        # Get all attendances for this student
        attendances = storage.get_attendances_by_student(student.id)
        
        # Prepare attendance data
        attendance_data = []
        for att in attendances:
            session = storage.get_session(att.session_id)
            course = storage.get_course(session.course_id) if session else None
            
            attendance_data.append({
                'session_id': att.session_id,
                'course': course.course_name if course else 'Unknown',
                'marked_at': att.marked_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return {
            'success': True,
            'student_name': student.full_name,
            'total_attendances': len(attendance_data),
            'attendance_history': attendance_data
        }

def main():
    """Main demo function"""
    print("=== QR Code Attendance System Demo ===")
    print()
    
    # Initialize system
    system = QRAttendanceSystem()
    
    # Demo login as faculty
    print("1. Faculty Login Demo:")
    result = system.login('prof_smith', 'password123')
    print(f"   Result: {result['message']}")
    qr_token = None
    
    if result['success']:
        # Demo create session
        print("\n2. Create Attendance Session:")
        result = system.create_session('C001')
        print(f"   Result: {result['message']}")
        if result['success']:
            print(f"   Session ID: {result['session_id']}")
            print(f"   QR Token: {result['qr_code_token']}")
            qr_token = result['qr_code_token']
    
    # Demo login as student
    print("\n3. Student Login Demo:")
    result = system.login('john_doe', 'password123')
    print(f"   Result: {result['message']}")
    
    if result['success']:
        # Demo mark attendance
        print("\n4. Mark Attendance:")
        result = system.mark_attendance(qr_token)
        print(f"   Result: {result['message']}")
        if result['success']:
            print(f"   Marked at: {result['marked_at']}")
    
    # Demo view attendance history
    print("\n5. View Attendance History:")
    result = system.get_student_attendance_history()
    if result['success']:
        print(f"   Student: {result['student_name']}")
        print(f"   Total Attendances: {result['total_attendances']}")
        for att in result['attendance_history']:
            print(f"   - Course: {att['course']}, Date: {att['marked_at']}")
    else:
        print(f"   Result: {result['message']}")
    
    print("\n=== Demo Complete ===")

if __name__ == '__main__':
    main()