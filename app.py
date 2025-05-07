from flask import Flask, render_template, request, redirect, url_for, g, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'attendance.db'
PASSWORD = 'Agile'  # Password for editing attendance

# --------------------------------
# Database connection
# --------------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --------------------------------
# Home Page — Show Students
# --------------------------------
@app.route('/')
def index():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()

    record_rows = conn.execute("""
        SELECT usn, status, datetime
        FROM attendance
        WHERE (usn, datetime) IN (
            SELECT usn, MAX(datetime)
            FROM attendance
            GROUP BY usn
        )
    """).fetchall()
    conn.close()

    records = {row['usn']: {'status': row['status'], 'datetime': row['datetime']} for row in record_rows}

    return render_template('index.html', students=students, records=records, error=None)

# --------------------------------
# Mark attendance (Present / Absent)
# --------------------------------
@app.route('/mark/<usn>/<status>')
def mark_attendance(usn, status):
    conn = get_db_connection()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn.execute('INSERT INTO attendance (usn, datetime, status) VALUES (?, ?, ?)', (usn, now, status))

    if status == 'present':
        conn.execute('UPDATE students SET total_classes = total_classes + 1, present_count = present_count + 1 WHERE usn = ?', (usn,))
    else:
        conn.execute('UPDATE students SET total_classes = total_classes + 1 WHERE usn = ?', (usn,))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# --------------------------------
# Password verification for Edit page
# --------------------------------
@app.route('/verify', methods=['POST'])
def verify_password():
    password = request.form.get('password')
    if password == PASSWORD:
        return redirect(url_for('edit'))
    else:
        conn = get_db_connection()
        students = conn.execute("SELECT * FROM students").fetchall()
        conn.close()
        return render_template('index.html', students=students, records={}, error='Incorrect password')

# --------------------------------
# Edit Attendance Page (20 students)
# --------------------------------
@app.route('/edit')
def edit():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students LIMIT 20').fetchall()
    conn.close()
    return render_template('edit.html', students=students)

# --------------------------------
# Save Attendance from Edit Page
# --------------------------------
@app.route('/save', methods=['POST'])
def save_attendance():
    conn = get_db_connection()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for usn in request.form:
        status = request.form[usn]
        conn.execute('INSERT INTO attendance (usn, datetime, status) VALUES (?, ?, ?)', (usn, now, status))
        if status == 'present':
            conn.execute('UPDATE students SET total_classes = total_classes + 1, present_count = present_count + 1 WHERE usn = ?', (usn,))
        else:
            conn.execute('UPDATE students SET total_classes = total_classes + 1 WHERE usn = ?', (usn,))

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# --------------------------------
# JSON API: Update Attendance
# --------------------------------
@app.route('/update_attendance', methods=['POST'])
def update_attendance():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Invalid data format'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for item in data:
        usn = item.get('usn')
        status = item.get('status')

        if not usn or not status:
            continue  # Skip malformed entries

        # Get student name
        cursor.execute("SELECT name FROM students WHERE usn = ?", (usn,))
        result = cursor.fetchone()
        if not result:
            continue  # Skip if USN not found
        name = result['name']

        # Insert into attendance table
        cursor.execute("""
            INSERT INTO attendance (usn, datetime, status) VALUES (?, ?, ?)
        """, (usn, now, status))

        # Update attendance summary
        if status == 'present':
            cursor.execute("""
                UPDATE students SET total_classes = total_classes + 1,
                present_count = present_count + 1 WHERE usn = ?
            """, (usn,))
        else:
            cursor.execute("""
                UPDATE students SET total_classes = total_classes + 1
                WHERE usn = ?
            """, (usn,))

    conn.commit()
    conn.close()
    return jsonify({'message': f'Updated attendance for {len(data)} students'})

# --------------------------------
# Run the Flask app
# --------------------------------
if __name__ == '__main__':
    app.run(debug=True)
