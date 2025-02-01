import sqlite3

def init_db():
    conn = sqlite3.connect("van_damage_detection.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS van_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        driver_name TEXT,
                        van_registration TEXT,
                        image_path TEXT,
                        damage_details TEXT,
                        previous_driver TEXT,
                        report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
