from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    student_id INTEGER,
                    FOREIGN KEY (student_id) REFERENCES students (id)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    dob TEXT NOT NULL,
                    parent_email TEXT NOT NULL,
                    phone TEXT,
                    address TEXT,
                    grade_class TEXT,
                    enrollment_date TEXT DEFAULT CURRENT_DATE,
                    emergency_contact_name TEXT,
                    emergency_contact_phone TEXT,
                    medical_info TEXT,
                    gender TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    date TEXT,
                    status TEXT,
                    FOREIGN KEY (student_id) REFERENCES students (id)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    subject TEXT,
                    score REAL,
                    FOREIGN KEY (student_id) REFERENCES students (id)
                )''')
    conn.commit()
    
    # Check if default users exist, if not create them
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        # Create default admin user
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                 ('UKVM', '501', 'admin'))
        conn.commit()
    
    conn.close()

init_db()

# Helper functions for role-based access control
def check_role(*allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                return redirect(url_for('role_select'))
            if session.get('role') not in allowed_roles:
                flash('You do not have permission to access this page')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# Email configuration
EMAIL_ADDRESS = 'student29system@gmail.com'
EMAIL_PASSWORD = 'pwhf uvls rupz yybm'

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
    server.quit()

@app.route('/')
def role_select():
    return render_template('role_select.html')

@app.route('/login')
def login_page():
    role = request.args.get('role', 'admin')
    role_display = {
        'admin': 'Admin',
        'attendance': 'Attendance Staff',
        'student': 'Student'
    }.get(role, 'Admin')
    return render_template('login.html', role=role, role_display=role_display)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    role = request.args.get('role', 'admin')
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, password, role, student_id FROM users WHERE username=?', (username,))
    user = c.fetchone()
    conn.close()
    
    if user and user[1] == password:
        selected_role = user[2]
        
        # Check if user is trying to login as student
        if role == 'student':
            if selected_role != 'student' and selected_role != 'admin':
                flash('Invalid credentials')
                return render_template('login.html', role=role, role_display='Student')
            if not user[3]:
                flash('Student account not properly configured')
                return render_template('login.html', role=role, role_display='Student')
            selected_role = 'student'
        elif role == 'attendance':
            if selected_role != 'attendance' and selected_role != 'admin':
                flash('You do not have permission to login with this role')
                return render_template('login.html', role=role, role_display='Attendance Staff')
        elif role == 'admin':
            if selected_role != 'admin':
                flash('You do not have permission to login with this role')
                return render_template('login.html', role=role, role_display='Admin')
        
        session['logged_in'] = True
        session['username'] = username
        session['role'] = selected_role
        session['user_id'] = user[0]
        session['student_id'] = user[3]
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials')
        role_display = {
            'admin': 'Admin',
            'attendance': 'Attendance Staff',
            'student': 'Student'
        }.get(role, 'Admin')
        return render_template('login.html', role=role, role_display=role_display)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('role_select'))
    
    role = session.get('role')
    
    # Student dashboard - show only their data
    if role == 'student':
        student_id = session.get('student_id')
        if not student_id:
            flash('Student information not found')
            return redirect(url_for('role_select'))
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Get student info
        c.execute('SELECT * FROM students WHERE id=?', (student_id,))
        student_info = c.fetchone()
        
        # Get student attendance
        c.execute('SELECT date, status FROM attendance WHERE student_id=? ORDER BY date DESC', (student_id,))
        attendance_records = c.fetchall()
        
        # Get student grades
        c.execute('SELECT subject, score FROM grades WHERE student_id=? ORDER BY subject', (student_id,))
        grades_records = c.fetchall()
        
        # Calculate attendance percentage
        total_classes = len(attendance_records)
        present_count = sum(1 for a in attendance_records if a[1] == 'present')
        attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
        
        # Calculate average grade
        grades_list = [g[1] for g in grades_records]
        average_grade = sum(grades_list) / len(grades_list) if grades_list else 0
        
        conn.close()
        
        return render_template('student_dashboard.html',
                             student_info=student_info,
                             attendance_records=attendance_records,
                             grades_records=grades_records,
                             attendance_percentage=attendance_percentage,
                             average_grade=average_grade)
    
    # Admin and Attendance staff dashboard
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Total students
    c.execute('SELECT COUNT(*) FROM students')
    total_students = c.fetchone()[0]

    # Today's date
    today = datetime.now().strftime('%Y-%m-%d')

    # Present today
    c.execute('SELECT COUNT(*) FROM attendance WHERE date=? AND status=?', (today, 'present'))
    present_today = c.fetchone()[0]

    # Absent today
    c.execute('SELECT COUNT(*) FROM attendance WHERE date=? AND status=?', (today, 'absent'))
    absent_today = c.fetchone()[0]

    # Average grade
    c.execute('SELECT AVG(score) FROM grades')
    avg_grade = c.fetchone()[0]

    conn.close()
    return render_template('dashboard.html',
                         total_students=total_students,
                         present_today=present_today,
                         absent_today=absent_today,
                         avg_grade=avg_grade)

@app.route('/students', methods=['GET', 'POST'])
@check_role('admin')
def students():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        if 'add' in request.form:
            name = request.form['name']
            dob = request.form['dob']
            parent_email = request.form['parent_email']
            phone = request.form.get('phone', '')
            address = request.form.get('address', '')
            grade_class = request.form.get('grade_class', '')
            emergency_contact_name = request.form.get('emergency_contact_name', '')
            emergency_contact_phone = request.form.get('emergency_contact_phone', '')
            medical_info = request.form.get('medical_info', '')
            gender = request.form.get('gender', '')
            enrollment_date = request.form.get('enrollment_date', '')
            c.execute('''INSERT INTO students (name, dob, parent_email, phone, address, grade_class,
                                              enrollment_date, emergency_contact_name, emergency_contact_phone, medical_info, gender)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (name, dob, parent_email, phone, address, grade_class, enrollment_date,
                      emergency_contact_name, emergency_contact_phone, medical_info, gender))
            conn.commit()
            
            # Get the student_id of the newly created student
            c.execute('SELECT last_insert_rowid()')
            student_id = c.fetchone()[0]
            
            # Create user account for the student with unique username
            username = name.lower().replace(' ', '_')  # Make it lowercase and replace spaces
            password = 'test@123'
            try:
                c.execute('INSERT INTO users (username, password, role, student_id) VALUES (?, ?, ?, ?)',
                         (username, password, 'student', student_id))
                conn.commit()
                flash(f'✓ Student added! Login: {username} | Password: test@123', 'success')
            except sqlite3.IntegrityError:
                # If username already exists, append student_id to make it unique
                username = f"{username}_{student_id}"
                c.execute('INSERT INTO users (username, password, role, student_id) VALUES (?, ?, ?, ?)',
                         (username, password, 'student', student_id))
                conn.commit()
                flash(f'✓ Student added! Login: {username} | Password: test@123', 'success')
        elif 'update' in request.form:
            id = request.form['id']
            name = request.form['name']
            dob = request.form['dob']
            parent_email = request.form['parent_email']
            phone = request.form.get('phone', '')
            address = request.form.get('address', '')
            grade_class = request.form.get('grade_class', '')
            emergency_contact_name = request.form.get('emergency_contact_name', '')
            emergency_contact_phone = request.form.get('emergency_contact_phone', '')
            medical_info = request.form.get('medical_info', '')
            gender = request.form.get('gender', '')
            enrollment_date = request.form.get('enrollment_date', '')
            c.execute('''UPDATE students SET name=?, dob=?, parent_email=?, phone=?, address=?,
                                              grade_class=?, enrollment_date=?, emergency_contact_name=?, emergency_contact_phone=?,
                                              medical_info=?, gender=? WHERE id=?''',
                     (name, dob, parent_email, phone, address, grade_class, enrollment_date,
                      emergency_contact_name, emergency_contact_phone, medical_info, gender, id))
            conn.commit()
        elif 'delete' in request.form:
            id = request.form['id']
            c.execute('DELETE FROM students WHERE id=?', (id,))
            conn.commit()

            # Renumber remaining students sequentially and update related tables
            c.execute('SELECT id FROM students ORDER BY id')
            remaining_ids = [row[0] for row in c.fetchall()]

            # Create a mapping of old_id -> new_id
            id_mapping = {old_id: new_id for new_id, old_id in enumerate(remaining_ids, 1)}

            # Update attendance table with new student IDs
            for old_id, new_id in id_mapping.items():
                c.execute('UPDATE attendance SET student_id = ? WHERE student_id = ?', (new_id, old_id))

            # Update grades table with new student IDs
            for old_id, new_id in id_mapping.items():
                c.execute('UPDATE grades SET student_id = ? WHERE student_id = ?', (new_id, old_id))

            # Create a temporary table with renumbered students
            c.execute('''CREATE TEMPORARY TABLE temp_students AS
                        SELECT ROW_NUMBER() OVER (ORDER BY id) as new_id,
                               name, dob, parent_email, phone, address, grade_class,
                               enrollment_date, emergency_contact_name, emergency_contact_phone,
                               medical_info, gender
                        FROM students ORDER BY id''')

            # Clear the original table
            c.execute('DELETE FROM students')

            # Insert back with new sequential IDs
            c.execute('''INSERT INTO students (id, name, dob, parent_email, phone, address, grade_class,
                                              enrollment_date, emergency_contact_name, emergency_contact_phone,
                                              medical_info, gender)
                        SELECT new_id, name, dob, parent_email, phone, address, grade_class,
                               enrollment_date, emergency_contact_name, emergency_contact_phone,
                               medical_info, gender FROM temp_students''')

            # Drop temporary table
            c.execute('DROP TABLE temp_students')

            # Reset the auto-increment counter
            c.execute("DELETE FROM sqlite_sequence WHERE name='students'")

            conn.commit()

    # Handle search
    search_query = request.args.get('q', '').strip()
    if search_query:
        # More precise search: prioritize name matches, then exact ID, then other fields
        c.execute('''SELECT * FROM students WHERE
                     LOWER(name) LIKE LOWER(?) OR
                     CAST(id AS TEXT) = ? OR
                     LOWER(grade_class) LIKE LOWER(?) OR
                     LOWER(parent_email) LIKE LOWER(?) OR
                     phone LIKE ?
                     ORDER BY
                     CASE
                         WHEN LOWER(name) LIKE LOWER(?) THEN 1
                         WHEN CAST(id AS TEXT) = ? THEN 2
                         ELSE 3
                     END''',
                  ('%' + search_query + '%', search_query, '%' + search_query + '%',
                   search_query + '%', '%' + search_query + '%',
                   search_query + '%', search_query))
    else:
        c.execute('SELECT * FROM students')

    students_list = c.fetchall()
    conn.close()
    return render_template('students.html', students=students_list)

@app.route('/attendance', methods=['GET', 'POST'])
@check_role('admin', 'attendance')
def attendance():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        if 'mark' in request.form:
            student_id = request.form['student_id']
            date = request.form['date']
            status = request.form['status']
            c.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)', (student_id, date, status))
            if status == 'absent':
                c.execute('SELECT name, parent_email FROM students WHERE id=?', (student_id,))
                result = c.fetchone()
                student_name = result[0]
                parent_email = result[1]
                send_email(parent_email, 'Student Absence Notification', f'Your child {student_name} was absent on {date}.')
            conn.commit()
        elif 'update' in request.form:
            id = request.form['id']
            status = request.form['status']
            c.execute('UPDATE attendance SET status=? WHERE id=?', (status, id))
            if status == 'absent':
                c.execute('SELECT students.name, students.parent_email FROM attendance JOIN students ON attendance.student_id = students.id WHERE attendance.id=?', (id,))
                result = c.fetchone()
                student_name = result[0]
                parent_email = result[1]
                c.execute('SELECT date FROM attendance WHERE id=?', (id,))
                date = c.fetchone()[0]
                send_email(parent_email, 'Student Absence Notification', f'Your child {student_name} was absent on {date}.')
            conn.commit()
        elif 'delete' in request.form:
            id = request.form['id']
            c.execute('DELETE FROM attendance WHERE id=?', (id,))
            conn.commit()

    # Handle search
    search_query = request.args.get('q', '').strip()
    if search_query:
        c.execute('''SELECT attendance.id, students.name, attendance.date, attendance.status
                     FROM attendance
                     JOIN students ON attendance.student_id = students.id
                     WHERE students.name LIKE ? OR attendance.date LIKE ?''',
                  ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        c.execute('SELECT attendance.id, students.name, attendance.date, attendance.status FROM attendance JOIN students ON attendance.student_id = students.id')

    attendance_list = c.fetchall()
    c.execute('SELECT id, name FROM students')
    students_list = c.fetchall()
    conn.close()
    return render_template('attendance.html', attendance=attendance_list, students=students_list)

@app.route('/grades', methods=['GET', 'POST'])
@check_role('admin')
def grades():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        if 'add' in request.form:
            student_id = request.form['student_id']
            subject = request.form['subject']
            score = request.form['score']
            c.execute('INSERT INTO grades (student_id, subject, score) VALUES (?, ?, ?)', (student_id, subject, score))
            conn.commit()
        elif 'update' in request.form:
            id = request.form['id']
            score = request.form['score']
            c.execute('UPDATE grades SET score=? WHERE id=?', (score, id))
            conn.commit()
        elif 'delete' in request.form:
            id = request.form['id']
            c.execute('DELETE FROM grades WHERE id=?', (id,))
            conn.commit()

    # Handle search
    search_query = request.args.get('q', '').strip()
    if search_query:
        c.execute('''SELECT grades.id, students.name, grades.subject, grades.score
                     FROM grades
                     JOIN students ON grades.student_id = students.id
                     WHERE students.name LIKE ? OR grades.subject LIKE ? OR CAST(grades.score AS TEXT) LIKE ?''',
                  ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
    else:
        c.execute('SELECT grades.id, students.name, grades.subject, grades.score FROM grades JOIN students ON grades.student_id = students.id')

    grades_list = c.fetchall()
    c.execute('SELECT id, name FROM students')
    students_list = c.fetchall()
    conn.close()
    return render_template('grades.html', grades=grades_list, students=students_list)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('role_select'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
