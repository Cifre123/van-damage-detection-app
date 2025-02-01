import streamlit as st
from PIL import Image, ImageDraw
import os
import sqlite3
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Database Setup
def init_db():
    conn = sqlite3.connect("van_damage_detection.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS van_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        driver_name TEXT,
                        van_registration TEXT,
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

init_db()

# Save image function
def save_image(van_id, driver_name, image, position):
    van_dir = os.path.join("vans", van_id)
    os.makedirs(van_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    save_path = os.path.join(van_dir, f"{position}_{timestamp}.jpg")
    image.save(save_path)
    return save_path

# Function to allow users to mark damage points on the image
def draw_damage_interface(image, position):
    st.image(image, caption=f"Click on {position} image to mark damages", use_container_width=True)
    damage_points = st.session_state.get(f"damage_points_{position}", [])
    
    if "damage_select" not in st.session_state:
        st.session_state["damage_select"] = "scratch"
    
    damage_type = st.selectbox("Select damage type:", ["scratch", "dent", "crack"], key=f"damage_type_{position}")
    
    if st.button("Click on Image to Add Damage", key=f"mark_{position}"):
        st.session_state["damage_select"] = damage_type
    
    if st.session_state.get("clicked_x") is not None and st.session_state.get("clicked_y") is not None:
        damage_points.append((st.session_state["clicked_x"], st.session_state["clicked_y"], st.session_state["damage_select"]))
        st.session_state[f"damage_points_{position}"] = damage_points
    
    draw = ImageDraw.Draw(image)
    for x, y, damage in damage_points:
        draw.ellipse((x-5, y-5, x+5, y+5), fill="red", outline="red")
        draw.text((x+10, y), damage, fill="red")
    
    return damage_points

# Email Report Function
def send_email_report(driver_name, previous_driver, van_registration, damage_details, images):
    msg = EmailMessage()
    msg["Subject"] = f"Van Damage Report - {van_registration}"
    msg["From"] = "noreply@yourcompany.com"
    msg["To"] = "admin@yourcompany.com"
    
    body = f"""
    New Damage Report:
    Driver Name: {driver_name}
    Van Registration: {van_registration}
    Previous Driver: {previous_driver}
    Damage Details: {damage_details}
    """
    msg.set_content(body)
    
    for position, image_path in images.items():
        with open(image_path, "rb") as img:
            msg.add_attachment(img.read(), maintype="image", subtype="jpeg", filename=os.path.basename(image_path))
    
    with smtplib.SMTP("smtp.yourcompany.com", 587) as server:
        server.starttls()
        server.login("your_email", "your_password")
        server.send_message(msg)

# Streamlit UI
st.title("Van Damage Reporting System")

# Driver input fields
driver_name = st.text_input("Enter your name:")
van_registration = st.text_input("Enter van registration number:")

# Upload multiple images
uploaded_images = {
    "Front": st.file_uploader("Upload front view:", type=["jpg", "png", "jpeg"], key="front"),
    "Back": st.file_uploader("Upload back view:", type=["jpg", "png", "jpeg"], key="back"),
    "Right": st.file_uploader("Upload right view:", type=["jpg", "png", "jpeg"], key="right"),
    "Left": st.file_uploader("Upload left view:", type=["jpg", "png", "jpeg"], key="left"),
    "Inside": st.file_uploader("Upload inside view:", type=["jpg", "png", "jpeg"], key="inside")
}

damage_details = ""
if uploaded_images:
    for position, uploaded_image in uploaded_images.items():
        if uploaded_image:
            image = Image.open(uploaded_image)
            damage_points = draw_damage_interface(image, position)
            st.image(image, caption=f"{position} view with marked damages", use_container_width=True)

if st.button("Submit Report", key="submit_report"):
    image_paths = {}
    for position, uploaded_image in uploaded_images.items():
        if uploaded_image:
            image = Image.open(uploaded_image)
            image_paths[position] = save_image(van_registration, driver_name, image, position)
    
    # Get previous driver info
    conn = sqlite3.connect("van_damage_detection.db")
    cursor = conn.cursor()
    cursor.execute("SELECT driver_name FROM van_reports WHERE van_registration = ? ORDER BY report_time DESC LIMIT 1", (van_registration,))
    result = cursor.fetchone()
    previous_driver = result[0] if result else "Unknown"
    
    # Insert into database
    cursor.execute("INSERT INTO van_reports (driver_name, van_registration, front_image, back_image, right_image, left_image, inside_image, damage_details, previous_driver) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   (driver_name, van_registration, image_paths.get("Front"), image_paths.get("Back"), image_paths.get("Right"), image_paths.get("Left"), image_paths.get("Inside"), damage_details, previous_driver))
    conn.commit()
    conn.close()
    
    # Send Email Report
    send_email_report(driver_name, previous_driver, van_registration, damage_details, image_paths)
    
    st.success("Report submitted successfully!")
