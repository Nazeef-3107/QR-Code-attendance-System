# API Documentation
## QR Code Attendance System

---

## Authentication

### Register Student
**POST** `/api/auth/register/student`

Registers a new student user.

#### Request Body
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "student_id": "string",
  "full_name": "string",
  "department": "string (optional)",
  "semester": "integer (optional)"
}
```

#### Response
```json
{
  "msg": "Student registered successfully"
}
```

#### Response Codes
- `201`: Student registered successfully
- `400`: Validation error or username/email already exists
- `500`: Server error

---

### Register Faculty
**POST** `/api/auth/register/faculty`

Registers a new faculty user (admin only).

#### Request Body
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "faculty_id": "string",
  "full_name": "string",
  "department": "string (optional)"
}
```

#### Response
```json
{
  "msg": "Faculty registered successfully"
}
```

#### Response Codes
- `201`: Faculty registered successfully
- `400`: Validation error or username/email already exists
- `403`: Unauthorized (admin only)
- `500`: Server error

---

### Login
**POST** `/api/auth/login`

Authenticates a user and returns a JWT token.

#### Request Body
```json
{
  "username": "string",
  "password": "string"
}
```

#### Response
```json
{
  "access_token": "string",
  "role": "string",
  "user_id": "string"
}
```

#### Response Codes
- `200`: Login successful
- `400`: Missing credentials
- `401`: Invalid credentials
- `500`: Server error

---

## Student Endpoints

### Get Student Profile
**GET** `/api/auth/profile`

Retrieves the logged-in student's profile information.

#### Response
```json
{
  "username": "string",
  "email": "string",
  "student_id": "string",
  "full_name": "string",
  "department": "string",
  "semester": "integer"
}
```

#### Response Codes
- `200`: Profile retrieved successfully
- `401`: Unauthorized
- `403`: Access forbidden (student only)
- `404`: User or profile not found
- `500`: Server error

---

### Mark Attendance
**POST** `/api/attendance/student/attendance/mark`

Marks attendance using a QR code token.

#### Request Body
```json
{
  "qr_token": "string"
}
```

#### Response
```json
{
  "msg": "Attendance marked successfully",
  "course": "string",
  "session_date": "datetime"
}
```

#### Response Codes
- `201`: Attendance marked successfully
- `400`: Invalid QR token or attendance already marked
- `401`: Unauthorized
- `403`: Access forbidden (student only) or not enrolled in course
- `500`: Server error

---

### Get Attendance History
**GET** `/api/attendance/student/attendance/history`

Retrieves the attendance history for the logged-in student.

#### Response
```json
{
  "student_name": "string",
  "total_attendances": "integer",
  "attendance_history": [
    {
      "course": "string",
      "course_code": "string",
      "session_date": "datetime",
      "marked_at": "datetime"
    }
  ]
}
```

#### Response Codes
- `200`: Attendance history retrieved successfully
- `401`: Unauthorized
- `403`: Access forbidden (student only)
- `404`: Student profile not found
- `500`: Server error

---

## Faculty Endpoints

### Create Attendance Session
**POST** `/api/attendance/faculty/session/create`

Creates a new attendance session with a QR code.

#### Request Body
```json
{
  "course_id": "string"
}
```

#### Response
```json
{
  "msg": "Session created successfully",
  "session_id": "string",
  "qr_code": "base64 encoded image",
  "expiration": "datetime"
}
```

#### Response Codes
- `201`: Session created successfully
- `400`: Missing course ID
- `401`: Unauthorized
- `403`: Access forbidden (faculty only)
- `500`: Server error

---

### Get Session Attendances
**GET** `/api/attendance/faculty/session/{session_id}/attendances`

Retrieves all attendances for a specific session.

#### Response
```json
{
  "session_id": "string",
  "course": "string",
  "total_attendances": "integer",
  "attendances": [
    {
      "student_id": "string",
      "student_name": "string",
      "marked_at": "datetime"
    }
  ]
}
```

#### Response Codes
- `200`: Attendances retrieved successfully
- `401`: Unauthorized
- `403`: Access forbidden (faculty only)
- `404`: Session not found or unauthorized
- `500`: Server error

---

## Admin Endpoints

### Get All Users
**GET** `/api/admin/users`

Retrieves all users in the system.

#### Response
```json
{
  "total_users": "integer",
  "users": [
    {
      "id": "string",
      "username": "string",
      "email": "string",
      "role": "string",
      "created_at": "datetime",
      "student_id": "string (if student)",
      "full_name": "string",
      "department": "string",
      "faculty_id": "string (if faculty)"
    }
  ]
}
```

#### Response Codes
- `200`: Users retrieved successfully
- `401`: Unauthorized
- `403`: Access forbidden (admin only)
- `500`: Server error

---

### Delete Student
**DELETE** `/api/admin/student/{student_id}`

Deletes a student and associated user.

#### Response
```json
{
  "msg": "Student deleted successfully"
}
```

#### Response Codes
- `200`: Student deleted successfully
- `401`: Unauthorized
- `403`: Access forbidden (admin only)
- `404`: Student not found
- `500`: Server error

---

### Delete Faculty
**DELETE** `/api/admin/faculty/{faculty_id}`

Deletes a faculty member and associated user.

#### Response
```json
{
  "msg": "Faculty deleted successfully"
}
```

#### Response Codes
- `200`: Faculty deleted successfully
- `401`: Unauthorized
- `403`: Access forbidden (admin only)
- `404`: Faculty not found
- `500`: Server error

---

### Create Course
**POST** `/api/admin/course`

Creates a new course.

#### Request Body
```json
{
  "course_code": "string",
  "course_name": "string",
  "department": "string (optional)",
  "semester": "integer (optional)",
  "faculty_id": "string (optional)"
}
```

#### Response
```json
{
  "msg": "Course created successfully",
  "course_id": "string"
}
```

#### Response Codes
- `201`: Course created successfully
- `400`: Validation error or course code already exists
- `401`: Unauthorized
- `403`: Access forbidden (admin only)
- `500`: Server error

---

### Delete Course
**DELETE** `/api/admin/course/{course_id}`

Deletes a course.

#### Response
```json
{
  "msg": "Course deleted successfully"
}
```

#### Response Codes
- `200`: Course deleted successfully
- `401`: Unauthorized
- `403`: Access forbidden (admin only)
- `404`: Course not found
- `500`: Server error

---

### Create Enrollment
**POST** `/api/admin/enrollment`

Enrolls a student in a course.

#### Request Body
```json
{
  "student_id": "string",
  "course_id": "string"
}
```

#### Response
```json
{
  "msg": "Student enrolled successfully",
  "enrollment_id": "string"
}
```

#### Response Codes
- `201`: Student enrolled successfully
- `400`: Validation error or already enrolled
- `401`: Unauthorized
- `403`: Access forbidden (admin only)
- `404`: Student or course not found
- `500`: Server error

---

### Admin Dashboard
**GET** `/api/admin/dashboard`

Retrieves admin dashboard statistics.

#### Response
```json
{
  "statistics": {
    "total_students": "integer",
    "total_faculties": "integer",
    "total_courses": "integer",
    "total_sessions": "integer"
  },
  "recent_enrollments": [
    {
      "student_name": "string",
      "course_name": "string",
      "enrollment_date": "datetime"
    }
  ]
}
```

#### Response Codes
- `200`: Dashboard data retrieved successfully
- `401`: Unauthorized
- `403`: Access forbidden (admin only)
- `500`: Server error

---

## Error Responses

All error responses follow this format:
```json
{
  "msg": "Error message",
  "error": "Detailed error information (optional)"
}
```

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Rate Limiting

The API implements rate limiting to prevent abuse:
- 100 requests per hour per IP address
- 10 requests per minute per user

Exceeding these limits will result in a 429 (Too Many Requests) response.