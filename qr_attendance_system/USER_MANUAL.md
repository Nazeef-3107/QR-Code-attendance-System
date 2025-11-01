# QR Code Attendance System - User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [User Roles](#user-roles)
4. [Getting Started](#getting-started)
5. [Student Guide](#student-guide)
6. [Faculty Guide](#faculty-guide)
7. [Admin Guide](#admin-guide)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Introduction

The QR Code Attendance System is designed to simplify and secure the attendance process in educational institutions. This system uses QR codes to mark attendance, eliminating proxy attendance and reducing manual effort.

## System Requirements

### For All Users:
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Stable internet connection
- Smartphone with camera (for students)

### For Installation (Technical Staff):
- Python 3.8 or higher
- Flask framework
- SQLite or PostgreSQL database
- Web server (Apache, Nginx)

## User Roles

1. **Student**: Can mark attendance by scanning QR codes
2. **Faculty**: Can create attendance sessions and view reports
3. **Admin**: Can manage users, courses, and system settings

## Getting Started

### Registration
1. Students register through the registration portal
2. Faculty and Admin accounts are created by the system administrator

### Login
1. Navigate to the login page
2. Enter your username and password
3. Select your role if prompted
4. Click "Login"

## Student Guide

### Marking Attendance
1. Login to your student account
2. Wait for your faculty to generate a QR code
3. Click on "Scan QR Code" in your dashboard
4. Point your camera at the displayed QR code
5. The system will automatically validate and mark your attendance

### Viewing Attendance History
1. Login to your student account
2. Navigate to "Attendance History"
3. View your attendance records for all courses

### Profile Management
1. Login to your student account
2. Go to "Profile" section
3. Update your personal information
4. Save changes

## Faculty Guide

### Creating Attendance Session
1. Login to your faculty account
2. Navigate to "Create Session"
3. Select the course for which you want to take attendance
4. Click "Generate QR Code"
5. Display the QR code to students for scanning

### Viewing Attendance Reports
1. Login to your faculty account
2. Go to "Attendance Reports"
3. Select the course and date range
4. View or export attendance data

### Managing Courses
1. Login to your faculty account
2. Navigate to "My Courses"
3. View your assigned courses
4. Add or remove students (if permitted)

## Admin Guide

### User Management
1. Login to admin account
2. Go to "User Management"
3. View all users in the system
4. Add new users or deactivate existing ones

### Course Management
1. Login to admin account
2. Navigate to "Course Management"
3. Create new courses
4. Assign faculty to courses
5. Manage course enrollments

### System Analytics
1. Login to admin account
2. Go to "Dashboard"
3. View system statistics
4. Monitor attendance trends

## Troubleshooting

### Common Issues and Solutions

**Issue: Cannot login to the system**
- Solution: Check your username and password. Reset password if necessary.

**Issue: QR code not scanning**
- Solution: Ensure good lighting, hold camera steady, ensure QR code is fully visible.

**Issue: Attendance not marking**
- Solution: Check if session is still active, refresh the page and try again.

**Issue: Slow system performance**
- Solution: Check internet connection, clear browser cache, try a different browser.

## FAQ

**Q: How long is a QR code valid?**
A: QR codes are valid for 2-3 minutes to prevent misuse.

**Q: Can I mark attendance after the session ends?**
A: No, attendance can only be marked during the active session.

**Q: What happens if I miss marking attendance?**
A: Missing attendance is recorded as absent. Contact your faculty for any exceptions.

**Q: Is my data secure?**
A: Yes, all data is encrypted and stored securely. The system complies with data protection regulations.

**Q: Can I use the system on my mobile device?**
A: Yes, the system is fully responsive and works on smartphones and tablets.

**Q: What if I lose my login credentials?**
A: Contact your system administrator to reset your password.

---

For technical support, contact the IT department at support@college.edu or call +1-234-567-8900.