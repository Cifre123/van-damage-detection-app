import sqlite3

def init_db():
    conn = sqlite3.connect("van_damage_detection.db")
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS van_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        driver_name TEXT NOT NULL,
                        van_registration TEXT NOT NULL,
                        front_image TEXT,
                        back_image TEXT,
                        right_image TEXT,
                        left_image TEXT,
                        inside_image TEXT,
                        damage_details TEXT,
                        previous_driver TEXT,
                        report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")