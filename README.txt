================================================================================
                    STUDENT MANAGEMENT SYSTEM
                      Project Documentation
================================================================================

PROJECT OVERVIEW
================================================================================
A comprehensive web-based Student Management System built with role-based access 
control. The system allows administrators to manage students, track attendance, 
and maintain academic records. Features include three distinct user roles with 
different permissions, automated parent notifications, and role-specific 
dashboards.

FEATURES
================================================================================
✓ Role-Based Access Control (Admin, Attendance Staff, Student)
✓ Student Management (Add, Edit, Delete)
✓ Attendance Tracking & Management
✓ Grades Management
✓ Student Personal Records & Dashboards
✓ Email Notifications to Parents
✓ Session-Based Authentication
✓ Responsive Web Interface
✓ Professional UI with Animations

TECHNOLOGIES USED
================================================================================
Backend:
  • Python 3.7+
  • Flask - Web framework for routing and request handling
  • SQLite3 - Database for persistent storage
  • SMTP - For email notifications

Frontend:
  • HTML5 - Markup structure
  • CSS3 - Styling with gradients, animations, and responsive design
  • JavaScript - Client-side interactions and form handling
  • Jinja2 - Flask templating engine

Database:
  • SQLite3 with tables for:
    - users (authentication and role management)
    - students (student information)
    - attendance (attendance records)
    - grades (academic grades)

SYSTEM ARCHITECTURE
================================================================================
├── Backend (app.py)
│   ├── Flask application with routing
│   ├── SQLite database operations
│   ├── Session management
│   ├── Email notification system
│   └── Role-based access decorators
│
├── Frontend
│   ├── Templates (HTML)
│   │   ├── role_select.html - Role selection landing page
│   │   ├── login.html - Unified login page
│   │   ├── dashboard.html - Admin/Attendance staff dashboard
│   │   ├── student_dashboard.html - Student personal dashboard
│   │   ├── students.html - Student management page
│   │   ├── attendance.html - Attendance management
│   │   └── grades.html - Grades management
│   │
│   └── Static (CSS & JS)
│       └── style.css - Complete styling and animations
│
└── Database (database.db)
    └── SQLite database with all system data

USER ROLES & PERMISSIONS
================================================================================

1. ADMIN (👨‍💼)
   ─────────────────────────────────────
   Login: UKVM / 501
   
   Permissions:
   ✓ Full system access
   ✓ Manage all students (Add, Edit, Delete)
   ✓ View all students
   ✓ Mark and manage attendance
   ✓ Add and manage grades
   ✓ View system dashboard with statistics
   
   Dashboard Features:
   • Total Students count
   • Present Today count
   • Absent Today count
   • Average Grade
   
   Navigation:
   → Students (Full CRUD)
   → Attendance (Mark & Manage)
   → Grades (Add & Manage)
   → Dashboard (Statistics)
   → Logout

───────────────────────────────────────────────────────────────────────────────

2. ATTENDANCE STAFF (📋)
   ─────────────────────────────────────
   Login: attendance_staff / 123456
   
   Permissions:
   ✓ Mark attendance for students
   ✓ View attendance records
   ✓ Manage attendance data
   ✗ Cannot manage students
   ✗ Cannot manage grades
   
   Dashboard Features:
   • Total Students count
   • Present Today count
   • Absent Today count
   (No Average Grade displayed)
   
   Navigation:
   → Attendance (Primary function)
   → Dashboard (Attendance statistics)
   → Logout

───────────────────────────────────────────────────────────────────────────────

3. STUDENT (👨‍🎓)
   ─────────────────────────────────────
   Login: <Student Name> / test@123
   Example: ujwal / test@123
   
   (Auto-generated when admin adds a new student)
   Username: Student's name (lowercase, spaces replaced with underscores)
   Password: test@123
   
   Permissions:
   ✓ View personal information
   ✓ View own attendance records
   ✓ View own grades
   ✗ Cannot modify any data
   ✗ Cannot access other students' information
   
   Dashboard Features:
   • Personal Information (Name, DOB, Class, Gender, Enrollment Date, etc.)
   • Attendance Overview (Attendance percentage with color coding)
   • Academic Performance (Average grade)
   • Detailed Attendance Records Table
   • Grades by Subject Table
   
   Navigation:
   → Dashboard (Personal records)
   → Logout

INSTALLATION & SETUP
================================================================================

1. Prerequisites:
   - Python 3.7 or higher
   - pip (Python package installer)

2. Install Dependencies:
   pip install -r requirements.txt

3. Run the Application:
   python app.py

4. Access the System:
   Open web browser and go to: http://127.0.0.1:8000

WORKFLOW
================================================================================

LOGIN FLOW:
  1. User visits http://127.0.0.1:8000
  2. Lands on Role Selection page
  3. Clicks their role card (Admin, Attendance Staff, or Student)
  4. Enters credentials on role-specific login page
  5. System validates and creates session
  6. Redirected to role-specific dashboard

ADDING A NEW STUDENT (Admin):
  1. Login as Admin (UKVM / 501)
  2. Navigate to "Students" page
  3. Click "Add New Student" and fill form
  4. System auto-creates login account:
     - Username: Student's name (lowercase)
     - Password: test@123
     - Role: student
  5. Student can now login immediately

MARKING ATTENDANCE:
  1. Login as Attendance Staff or Admin
  2. Navigate to "Attendance"
  3. Select date and status (Present/Absent)
  4. If marked Absent, system sends email to parent with:
     - Student's name
     - Absence date
     - Notification message

DATABASE SCHEMA
================================================================================

users table:
  id (INTEGER PRIMARY KEY)
  username (TEXT UNIQUE)
  password (TEXT)
  role (TEXT) - 'admin', 'attendance', 'student'
  student_id (INTEGER FOREIGN KEY)

students table:
  id (INTEGER PRIMARY KEY)
  name (TEXT)
  dob (TEXT)
  parent_email (TEXT)
  phone (TEXT)
  address (TEXT)
  grade_class (TEXT)
  enrollment_date (TEXT)
  emergency_contact_name (TEXT)
  emergency_contact_phone (TEXT)
  medical_info (TEXT)
  gender (TEXT)

attendance table:
  id (INTEGER PRIMARY KEY)
  student_id (INTEGER FOREIGN KEY)
  date (TEXT)
  status (TEXT) - 'present' or 'absent'

grades table:
  id (INTEGER PRIMARY KEY)
  student_id (INTEGER FOREIGN KEY)
  subject (TEXT)
  score (REAL)

EMAIL NOTIFICATIONS
================================================================================
When attendance is marked as "Absent", the system automatically sends an email
to the parent's email address with:
  • Student's name
  • Absence date
  • Notification message

Example Email:
"Your child ujwal was absent on 2026-01-21."

DEFAULT TEST ACCOUNTS
================================================================================
Admin:
  Username: UKVM
  Password: 501
  Role: admin

Attendance Staff:
  Username: attendance_staff
  Password: 123456
  Role: attendance

Students: (Auto-generated based on added students)
  Example: ujwal / test@123

SECURITY FEATURES
================================================================================
✓ Session-based authentication
✓ Password storage (plaintext in demo - should be hashed in production)
✓ Role-based route protection
✓ SQL parameterized queries (prevents SQL injection)
✓ User input validation
✓ Database foreign key relationships

PROJECT FILES
================================================================================
app.py                 - Main Flask application
requirements.txt       - Python dependencies
database.db           - SQLite database
templates/
  ├── role_select.html - Role selection page
  ├── login.html - Login page
  ├── dashboard.html - Admin/Attendance dashboard
  ├── student_dashboard.html - Student dashboard
  ├── students.html - Student management
  ├── attendance.html - Attendance management
  └── grades.html - Grades management
static/
  └── style.css - Complete styling

NOTES & RECOMMENDATIONS
================================================================================
1. Security: In production, implement:
   - Password hashing (bcrypt/argon2)
   - HTTPS/SSL encryption
   - CSRF protection
   - Input sanitization

2. Enhancements: Consider adding:
   - User profile management
   - Advanced filtering & search
   - Report generation
   - Backup & restore functionality
   - Audit logging

3. Performance:
   - Current implementation uses SQLite (suitable for small to medium scale)
   - For large scale, migrate to PostgreSQL/MySQL

================================================================================
                        End of Documentation
================================================================================
