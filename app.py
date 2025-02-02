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
                        damage_points TEXT,
                        report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_db()

# Save image function
def save_image(van_id, driver_name, image, position):
    """Save an image with marked damages."""
    if image is None:
        return ""

    van_dir = os.path.join("vans", van_id)
    os.makedirs(van_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    save_path = os.path.join(van_dir, f"{position}_{timestamp}.jpg")

    # Convert image mode if needed
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Draw damage markers if available
    if f"damage_points_{position}" in st.session_state:
        draw = ImageDraw.Draw(image)
        for x, y, damage in st.session_state[f"damage_points_{position}"]:
            draw.ellipse((x-10, y-10, x+10, y+10), outline="red", width=3)  # Draw circle
            draw.text((x+12, y), damage, fill="red")  # Add text label

    image.save(save_path)
    return save_path

# Function to allow users to mark damage points on the image
def draw_damage_interface(image, position):
    """Allow users to mark damage points on an image and display them."""
    if image is None:
        st.warning(f"No image uploaded for {position}. Please upload an image first.")
        return None

    if f"damage_points_{position}" not in st.session_state:
        st.session_state[f"damage_points_{position}"] = []
    
    # Display the image
    st.image(image, caption=f"Click on {position} image to mark damages", use_container_width=True)

    damage_type = st.selectbox("Select damage type:", ["Scratch", "Dent", "Crack"], key=f"damage_type_{position}")

    if st.button("Start Marking Damage", key=f"start_mark_{position}"):
        st.session_state["marking_mode"] = position
        st.write("Click on the image to add damage markers.")

    if st.session_state.get("marking_mode") == position:
        x = st.slider("X Coordinate", min_value=0, max_value=image.width, key=f"x_{position}")
        y = st.slider("Y Coordinate", min_value=0, max_value=image.height, key=f"y_{position}")

        if st.button("Add Damage Point", key=f"add_damage_{position}"):
            st.session_state[f"damage_points_{position}"].append((x, y, damage_type))
            st.session_state["marking_mode"] = None  

    # Draw circles on the image
    image_with_marks = image.copy()
    draw = ImageDraw.Draw(image_with_marks)
    for x, y, damage in st.session_state[f"damage_points_{position}"]:
        draw.ellipse((x-10, y-10, x+10, y+10), outline="red", width=3)  # Draw circle
        draw.text((x+12, y), damage, fill="red")  # Add text label
    
    # Display the updated image with markings
    st.image(image_with_marks, caption=f"Marked Damages on {position}", use_container_width=True)

    return image_with_marks

# Email Report Function
def send_email_report(driver_name, previous_driver, van_registration, damage_details, images):
    """Send damage report with marked images via email."""
    msg = EmailMessage()
    msg["Subject"] = f"Van Damage Report - {van_registration}"
    msg["From"] = "precisionlogistical@gmail.com"
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
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("precisionlogistical@gmail.com", "your_app_password")
        server.send_message(msg)

# Streamlit UI
st.title("Van Damage Reporting System")

# Driver input fields
driver_name = st.text_input("Enter your name:")
van_registration = st.text_input("Enter van registration number:")

# Upload multiple images
uploaded_images = {position: st.file_uploader(f"Upload {position} view:", type=["jpg", "png", "jpeg"], key=position) for position in ["Front", "Back", "Right", "Left", "Inside"]}

damage_details = st.text_area("Describe the damage:")

if st.button("Submit Report", key="submit_report"):
    conn = sqlite3.connect("van_damage_detection.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT driver_name FROM van_reports WHERE van_registration = ? ORDER BY report_time DESC LIMIT 1", (van_registration,))
    result = cursor.fetchone()
    previous_driver = result[0] if result else "Unknown"
    
    # Convert uploaded images to PIL images before saving
    image_paths = {}
    for position, uploaded_image in uploaded_images.items():
        if uploaded_image:
            img = Image.open(uploaded_image)
            image_paths[position] = save_image(van_registration, driver_name, img, position)
        else:
            image_paths[position] = ""

    cursor.execute("INSERT INTO van_reports (driver_name, van_registration, front_image, back_image, right_image, left_image, inside_image, damage_details, previous_driver) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (driver_name, van_registration, image_paths["Front"], image_paths["Back"], image_paths["Right"], image_paths["Left"], image_paths["Inside"], damage_details, previous_driver))
    
    conn.commit()
    conn.close()
    
    send_email_report(driver_name, previous_driver, van_registration, damage_details, image_paths)
    st.success("Report submitted successfully!")
