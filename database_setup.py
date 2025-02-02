import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS van_reports (
                        id SERIAL PRIMARY KEY,
                        driver_name TEXT NOT NULL,
                        van_registration TEXT NOT NULL,
                        front_image TEXT,
                        back_image TEXT,
                        right_image TEXT,
                        left_image TEXT,
                        inside_image TEXT,
                        damage_details TEXT,
                        previous_driver TEXT,
                        damage_points TEXT,
                        report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
