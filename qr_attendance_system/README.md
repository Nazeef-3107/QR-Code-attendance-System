# QR Code Attendance System for Colleges

A web-based application designed to automate and streamline the attendance process for educational institutions using QR codes.

## 📋 Project Overview

The QR Code Attendance System for Colleges is a secure, real-time solution that replaces manual paper-based attendance with an efficient QR code-based system. It includes three primary user roles — Student, Faculty, and Admin — each with dedicated access controls and functionalities.

## 🎯 Key Features

### Authentication & User Roles
- Secure login and signup for students
- Predefined login for faculty and admin
- Role-based access control
- Password encryption

### Student Panel
- Register and log in to the portal
- Scan class-specific QR codes to mark attendance
- View personal attendance records and statistics
- Profile management
- Real-time validation to prevent multiple scans per session

### Faculty Panel
- Login with secure credentials
- Add and manage students for assigned courses
- Create and manage courses
- Generate unique, time-bound QR codes (valid for 2–3 minutes)
- View attendance reports for each course
- Export attendance data in CSV or PDF format

### Admin Panel
- Full control over all system data
- Manage student, faculty, and course records
- Assign faculty to specific courses
- View global dashboards and analytics
- Generate backups and maintain system logs

## 🏗️ System Architecture

### Frontend
- React.js / Next.js
- Tailwind CSS / Material UI for design
- QR scanning using `react-qr-reader`

### Backend
- Python Flask
- JWT authentication & middleware for access control

### Database
- SQLite (for development) / PostgreSQL (for production)

### QR Code Services
- Libraries: `qrcode` (Python)
- Time-sensitive token-based QR codes

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd qr_attendance_system
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python run.py
   ```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/student` - Register a new student
- `POST /api/auth/register/faculty` - Register a new faculty member
- `POST /api/auth/login` - Login endpoint

### Attendance
- `POST /api/attendance/faculty/session/create` - Create attendance session (Faculty only)
- `POST /api/attendance/student/attendance/mark` - Mark attendance (Student only)
- `GET /api/attendance/student/attendance/history` - View attendance history (Student only)

### Admin
- `GET /api/admin/users` - Get all users (Admin only)
- `POST /api/admin/course` - Create a new course (Admin only)
- `DELETE /api/admin/course/<id>` - Delete a course (Admin only)

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLite/PostgreSQL
- **Authentication**: JWT
- **QR Code Generation**: qrcode library
- **Frontend**: React.js (separate frontend application)

## 📈 Future Enhancements

- Real-time Attendance Dashboard
- Email Notifications for low attendance
- Geo-location Verification
- Dark Mode & Responsive UI
- Analytics Dashboard with Chart.js
- PWA Support
- Facial Recognition (Optional)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- [Your Name]

## 🙏 Acknowledgments

- Inspired by the need to digitize attendance processes in educational institutions