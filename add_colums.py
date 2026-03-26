"""
add_columns.py
Run this ONCE from your project root:
    python add_columns.py

Adds the new settings columns to your existing database.db
WITHOUT needing Flask-Migrate at all.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "database.db")

# If not in instance folder, try root
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

print(f"Using database: {DB_PATH}")

# Each tuple = (column_name, sql_type, default_value)
NEW_COLUMNS = [
    ("email",         "VARCHAR(150)", "NULL"),
    ("first_name",    "VARCHAR(80)",  "NULL"),
    ("last_name",     "VARCHAR(80)",  "NULL"),
    ("role",          "VARCHAR(100)", "NULL"),
    ("organisation",  "VARCHAR(120)", "NULL"),
    ("bio",           "TEXT",         "NULL"),
    ("avatar",        "VARCHAR(255)", "NULL"),
    ("dark_mode",     "BOOLEAN",      "0"),
    ("accent_colour", "VARCHAR(50)",  "NULL"),
    ("font_size",     "VARCHAR(30)",  "NULL"),
    ("notifications", "JSON",         "NULL"),
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get existing columns
cursor.execute("PRAGMA table_info(user)")
existing = {row[1] for row in cursor.fetchall()}
print(f"Existing columns: {existing}")

added = []
skipped = []

for col_name, col_type, default in NEW_COLUMNS:
    if col_name in existing:
        skipped.append(col_name)
        continue
    try:
        if default == "NULL":
            sql = f"ALTER TABLE user ADD COLUMN {col_name} {col_type}"
        else:
            sql = f"ALTER TABLE user ADD COLUMN {col_name} {col_type} DEFAULT {default}"
        cursor.execute(sql)
        added.append(col_name)
        print(f"  ✅ Added column: {col_name}")
    except Exception as e:
        print(f"  ❌ Error adding {col_name}: {e}")

conn.commit()
conn.close()

print(f"\nDone — added {len(added)} columns, skipped {len(skipped)} already existing.")
print("You can now run: python app.py")