import psycopg2
import os

# Get database connection URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Connect to PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")  # Ensure SSL for security
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_db_connection()
    if not conn:
        print("❌ Database connection could not be established.")
        return

    try:
        cursor = conn.cursor()

        # Create table for storing van damage reports
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS van_reports (
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
                damage_points JSONB,  -- Using JSONB to store multiple damage points
                report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        print("✅ Database initialized successfully.")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_db()
