"""
Simple models for the QR Attendance System
This version doesn't depend on external packages for easier testing
"""

import json
import uuid
from datetime import datetime, timedelta

class SimpleModel:
    """Base class for all models"""
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        """Convert model to dictionary"""
        return self.__dict__
    
    def save(self):
        """Save model to file storage"""
        # In a real application, this would save to a database
        pass

class User(SimpleModel):
    """User model for students, faculty, and admins"""
    def __init__(self, username, email, password, role):
        super().__init__()
        self.username = username
        self.email = email
        self.password = password  # In real app, this would be hashed
        self.role = role  # student, faculty, admin
    
    def check_password(self, password):
        """Check if provided password matches stored password"""
        return self.password == password

class Student(SimpleModel):
    """Student profile model"""
    def __init__(self, user_id, student_id, full_name, department=None, semester=None):
        super().__init__()
        self.user_id = user_id
        self.student_id = student_id
        self.full_name = full_name
        self.department = department
        self.semester = semester

class Faculty(SimpleModel):
    """Faculty profile model"""
    def __init__(self, user_id, faculty_id, full_name, department=None):
        super().__init__()
        self.user_id = user_id
        self.faculty_id = faculty_id
        self.full_name = full_name
        self.department = department

class Course(SimpleModel):
    """Course model"""
    def __init__(self, course_code, course_name, department=None, semester=None, faculty_id=None):
        super().__init__()
        self.course_code = course_code
        self.course_name = course_name
        self.department = department
        self.semester = semester
        self.faculty_id = faculty_id

class Session(SimpleModel):
    """Attendance session with QR code"""
    def __init__(self, course_id, faculty_id):
        super().__init__()
        self.course_id = course_id
        self.faculty_id = faculty_id
        self.qr_code_token = str(uuid.uuid4())
        self.qr_expiration = (datetime.now() + timedelta(minutes=3)).isoformat()
        self.is_active = True

class Attendance(SimpleModel):
    """Attendance record"""
    def __init__(self, session_id, student_id):
        super().__init__()
        self.session_id = session_id
        self.student_id = student_id
        self.marked_at = datetime.now().isoformat()

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
    
    def get_faculty_by_user_id(self, user_id):
        for faculty in self.faculties.values():
            if faculty.user_id == user_id:
                return faculty
        return None
    
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