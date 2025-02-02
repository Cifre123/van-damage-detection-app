import streamlit as st
from PIL import Image, ImageDraw
import os
import psycopg2
import json
from email.message import EmailMessage
from datetime import datetime
import smtplib
from database_functions import add_report, get_previous_driver

if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]

st.write("Database URL:", os.getenv("DATABASE_URL"))
# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def get_db_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Save image function
def save_image(van_id, driver_name, image, position):
    """Save an image with marked damages."""
    van_dir = os.path.join("vans", van_id)
    os.makedirs(van_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    save_path = os.path.join(van_dir, f"{position}_{timestamp}.jpg")

    if f"damage_points_{position}" in st.session_state:
        draw = ImageDraw.Draw(image)
        for x, y, damage in st.session_state[f"damage_points_{position}"]:
            draw.ellipse((x-10, y-10, x+10, y+10), outline="red", width=3)
            draw.text((x+12, y), damage, fill="red")
    
    image.save(save_path)
    return save_path

# Email Report Function
def send_email_report(driver_name, previous_driver, van_registration, damage_details, images):
    """Send damage report with marked images via email."""
    msg = EmailMessage()
    msg["Subject"] = f"Van Damage Report - {van_registration}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = "prvldbi7@gmail.com"
    
    body = f"""
    New Damage Report:
    Driver Name: {driver_name}
    Van Registration: {van_registration}
    Previous Driver: {previous_driver}
    Damage Details: {damage_details}
    """
    msg.set_content(body)
    
    for position, image_path in images.items():
        if image_path:
            with open(image_path, "rb") as img:
                msg.add_attachment(img.read(), maintype="image", subtype="jpeg", filename=os.path.basename(image_path))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        st.success("Email report sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Streamlit UI
st.title("Van Damage Reporting System")

# Driver input fields
driver_name = st.text_input("Enter your name:")
van_registration = st.text_input("Enter van registration number:")

# Upload multiple images
uploaded_images = {position: st.file_uploader(f"Upload {position} view:", type=["jpg", "png", "jpeg"], key=position) for position in ["Front", "Back", "Right", "Left", "Inside"]}

damage_details = st.text_area("Describe the damage:")

if st.button("Submit Report", key="submit_report"):
    conn = get_db_connection()
    if not conn:
        st.error("Failed to connect to database.")
    else:
        previous_driver = get_previous_driver(van_registration)
        
        image_paths = {}
        for position, uploaded_image in uploaded_images.items():
            if uploaded_image is not None:
                image = Image.open(uploaded_image)
                image_paths[position] = save_image(van_registration, driver_name, image, position)
            else:
                image_paths[position] = ""
        
        damage_points = {position: st.session_state.get(f"damage_points_{position}", []) for position in uploaded_images.keys()}
        damage_points_json = json.dumps(damage_points)
        
        add_report(driver_name, van_registration, image_paths.get("Front", ""), image_paths.get("Back", ""),
                   image_paths.get("Right", ""), image_paths.get("Left", ""), image_paths.get("Inside", ""),
                   damage_details, previous_driver, damage_points_json)
        
        conn.commit()
        conn.close()
        
        send_email_report(driver_name, previous_driver, van_registration, damage_details, image_paths)
        
        st.success("Report submitted successfully!")
