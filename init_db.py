
import sqlite3
import random
from datetime import datetime

conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# 1. Create missing tables
cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        usn TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        total_classes INTEGER DEFAULT 0,
        present_count INTEGER DEFAULT 0
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usn TEXT NOT NULL,
        datetime TEXT NOT NULL,
        status TEXT NOT NULL
    )
""")

# 2. Populate with sample data
student_names = [
    "Aadhya Nair", "Aarav Kumar", "Aditya Singh", "Anaya Mehta", "Arjun Patel",
    "Atharv Bhat", "Ayaan Ghosh", "Ishita Dutta", "Kabir Menon", "Krishna Verma",
    "Meher Paul", "Myra Joshi", "Navya Kapoor", "Reyansh Reddy", "Saanvi Sharma"
]

for i, name in enumerate(student_names):
    usn = f"1RV21CS{str(i+1).zfill(3)}"
    total = random.randint(10, 20)
    present = random.randint(0, total)

    cursor.execute("""
        INSERT OR IGNORE INTO students (usn, name, total_classes, present_count)
        VALUES (?, ?, ?, ?)
    """, (usn, name, total, present))

    for _ in range(5):
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = random.choice(["present", "absent"])
        cursor.execute("""
            INSERT INTO attendance (usn, datetime, status)
            VALUES (?, ?, ?)
        """, (usn, dt, status))

conn.commit()
conn.close()
print("✅ Database initialized with 'students' and 'attendance' tables.")
