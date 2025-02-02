import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Connect to PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def add_report(driver_name, van_registration, front_image, back_image, right_image, left_image, inside_image, damage_details, previous_driver, damage_points):
    """Insert a damage report into the database."""
    conn = get_db_connection()
    if not conn:
        print("❌ Failed to connect to database.")
        return

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO van_reports (driver_name, van_registration, front_image, back_image, right_image, left_image, inside_image, damage_details, previous_driver, damage_points) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (driver_name, van_registration, front_image, back_image, right_image, left_image, inside_image, damage_details, previous_driver, damage_points))

        conn.commit()
        print("✅ Report successfully added!")

    except Exception as e:
        print(f"❌ Error inserting report: {e}")

    finally:
        cursor.close()
        conn.close()

def get_previous_driver(van_registration):
    """Retrieve the last driver who used the van based on van registration."""
    conn = get_db_connection()
    if not conn:
        return "Unknown"

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT driver_name FROM van_reports
            WHERE van_registration = %s
            ORDER BY report_time DESC
            LIMIT 1
        """, (van_registration,))

        result = cursor.fetchone()
        return result[0] if result else "Unknown"

    except Exception as e:
        print(f"❌ Error retrieving previous driver: {e}")
        return "Unknown"

    finally:
        cursor.close()
        conn.close()

