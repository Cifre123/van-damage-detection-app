import sqlite3

conn = sqlite3.connect("van_damage_detection.db")
cursor = conn.cursor()

# Get column details
cursor.execute("PRAGMA table_info(van_reports)")
columns = cursor.fetchall()
conn.close()

# Print the column names
for column in columns:
    print(column)