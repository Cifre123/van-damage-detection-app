import psycopg2
import os

database_url = os.getenv("DATABASE_URL", "your_supabase_postgres_url")

def get_db_connection():
    return psycopg2.connect(database_url)

def add_report(driver_name, van_registration, front_image, back_image, right_image, left_image, inside_image, damage_details, previous_driver, damage_points):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO van_reports 
        (driver_name, van_registration, front_image, back_image, right_image, left_image, inside_image, damage_details, previous_driver, damage_points) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (driver_name, van_registration, front_image, back_image, right_image, left_image, inside_image, damage_details, previous_driver, damage_points))
    
    conn.commit()
    conn.close()

def get_previous_driver(van_registration):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT driver_name FROM van_reports 
        WHERE van_registration = %s 
        ORDER BY report_time DESC LIMIT 1
    """, (van_registration,))
    
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Unknown"

if __name__ == "__main__":
    print("Database functions are ready.")
