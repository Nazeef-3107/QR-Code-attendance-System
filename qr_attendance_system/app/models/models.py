from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import qrcode
from io import BytesIO
import base64

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # student, faculty, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Student, Faculty, Admin (one-to-one)
    student_profile = db.relationship('Student', backref='user', uselist=False)
    faculty_profile = db.relationship('Faculty', backref='user', uselist=False)
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    semester = db.Column(db.Integer)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with enrollments
    enrollments = db.relationship('Enrollment', backref='student')
    
    def __repr__(self):
        return f'<Student {self.full_name}>'

class Faculty(db.Model):
    __tablename__ = 'faculties'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    faculty_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    joining_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with courses
    courses = db.relationship('Course', backref='faculty')
    
    def __repr__(self):
        return f'<Faculty {self.full_name}>'

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    semester = db.Column(db.Integer)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with enrollments and sessions
    enrollments = db.relationship('Enrollment', backref='course')
    sessions = db.relationship('Session', backref='course')
    
    def __repr__(self):
        return f'<Course {self.course_name}>'

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a student can only be enrolled in a course once
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id'),)
    
    def __repr__(self):
        return f'<Enrollment Student:{self.student_id} Course:{self.course_id}>'

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    faculty_id = db.Column(db.Integer)
    session_date = db.Column(db.DateTime, default=datetime.utcnow)
    qr_code_token = db.Column(db.String(255), unique=True, nullable=False)
    qr_expiration = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship with attendances
    attendances = db.relationship('Attendance', backref='session')
    
    def generate_qr_code(self):
        """Generate a QR code for this session"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.qr_code_token)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, 'PNG')
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def __repr__(self):
        return f'<Session {self.session_date}>'

class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a student can only have one attendance record per session
    __table_args__ = (db.UniqueConstraint('session_id', 'student_id'),)
    
    # Relationship to get student details
    student = db.relationship('Student')
    
    def __repr__(self):
        return f'<Attendance Session:{self.session_id} Student:{self.student_id}>'