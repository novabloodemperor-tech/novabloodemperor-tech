# transfer_data.py
import os
import django
import sqlite3
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_pilot.settings')
django.setup()

print("📤 Preparing to transfer database to Render...")

# Copy your local database file
local_db = "db.sqlite3"
if os.path.exists(local_db):
    # Create a backup copy
    shutil.copy2(local_db, "db_backup.sqlite3")
    print(f"✅ Database backed up: db_backup.sqlite3")
    
    # Verify the backup has data
    conn = sqlite3.connect("db_backup.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM courses_programme")
    count = cursor.fetchone()[0]
    conn.close()
    
    print(f"📊 Backup contains {count} programmes")
else:
    print("❌ Local database file not found")