import sqlite3

DATABASE = "van_damage_detection.db"

def add_report(driver_name, van_registration, image_path, damage_details):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Retrieve the last driver name for this van
    cursor.execute("SELECT driver_name FROM van_reports WHERE van_registration = ? ORDER BY report_time DESC LIMIT 1", (van_registration,))
    result = cursor.fetchone()
    previous_driver = result[0] if result else "Unknown"

    # Insert new record
    cursor.execute("""INSERT INTO van_reports (driver_name, van_registration, image_path, damage_details, previous_driver)
                      VALUES (?, ?, ?, ?, ?)""",
                   (driver_name, van_registration, image_path, damage_details, previous_driver))

    conn.commit()
    conn.close()
    return previous_driver

def get_previous_driver(van_registration):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT driver_name FROM van_reports WHERE van_registration = ? ORDER BY report_time DESC LIMIT 1", (van_registration,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Unknown"
