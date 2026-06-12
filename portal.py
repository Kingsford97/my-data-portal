import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import sqlite3
import bcrypt
import requests
from PIL import Image
import io
import os


# ==================== DATABASE SETUP ====================

def init_db():
    conn = sqlite3.connect('portal_data.db')
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     username
                     TEXT
                     UNIQUE
                     NOT
                     NULL,
                     password
                     TEXT
                     NOT
                     NULL,
                     role
                     TEXT
                     DEFAULT
                     'user',
                     created_at
                     TIMESTAMP
                     DEFAULT
                     CURRENT_TIMESTAMP
                 )''')

    # Students table (School)
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     name
                     TEXT
                     NOT
                     NULL,
                     class
                     TEXT
                     NOT
                     NULL,
                     parent_contact
                     TEXT,
                     photo
                     BLOB,
                     created_at
                     TIMESTAMP
                     DEFAULT
                     CURRENT_TIMESTAMP
                 )''')

    # Crops table (Farmers)
    c.execute('''CREATE TABLE IF NOT EXISTS crops
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     crop_name
                     TEXT
                     NOT
                     NULL,
                     area_acres
                     REAL,
                     planted_date
                     TEXT,
                     expected_harvest
                     TEXT,
                     status
                     TEXT,
                     image
                     BLOB,
                     created_at
                     TIMESTAMP
                     DEFAULT
                     CURRENT_TIMESTAMP
                 )''')

    # Add default admin if not exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        hashed = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ('admin', hashed, 'admin'))

    conn.commit()
    conn.close()


init_db()


# ==================== HELPER FUNCTIONS ====================

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def check_login(username, password):
    conn = sqlite3.connect('portal_data.db')
    c = conn.cursor()
    c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and verify_password(password, result[0]):
        return result[1]
    return None


def add_user(username, password, role='user'):
    conn = sqlite3.connect('portal_data.db')
    c = conn.cursor()
    try:
        hashed = hash_password(password)
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (username, hashed, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def add_student(name, student_class, parent_contact, photo_bytes=None):
    conn = sqlite3.connect('portal_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (name, class, parent_contact, photo) VALUES (?, ?, ?, ?)",
              (name, student_class, parent_contact, photo_bytes))
    conn.commit()
    conn.close()


def get_students():
    conn = sqlite3.connect('portal_data.db')
    df = pd.read_sql_query("SELECT id, name, class, parent_contact, created_at FROM students ORDER BY created_at DESC",
                           conn)
    conn.close()
    return df


def add_crop(crop_name, area, planted_date, expected_harvest, status, image_bytes=None):
    conn = sqlite3.connect('portal_data.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO crops (crop_name, area_acres, planted_date, expected_harvest, status, image) VALUES (?, ?, ?, ?, ?, ?)",
        (crop_name, area, planted_date, expected_harvest, status, image_bytes))
    conn.commit()
    conn.close()


def get_crops():
    conn = sqlite3.connect('portal_data.db')
    df = pd.read_sql_query(
        "SELECT id, crop_name, area_acres, planted_date, expected_harvest, status, created_at FROM crops ORDER BY created_at DESC",
        conn)
    conn.close()
    return df


# ==================== WEATHER API ====================

def get_weather(city, api_key="YOUR_API_KEY"):
    """Get real weather data - sign up for free key at openweathermap.org"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "temp": data['main']['temp'],
                "humidity": data['main']['humidity'],
                "condition": data['weather'][0]['description'],
                "icon": data['weather'][0]['icon']
            }
    except:
        pass
    return None


# ==================== SESSION STATE ====================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "portal" not in st.session_state:
    st.session_state.portal = None

# ==================== LOGIN SYSTEM ====================

if not st.session_state.logged_in:
    st.title("🔐 Login to Multi-Portal System")

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            role = check_login(login_user, login_pass)
            if role:
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.session_state.role = role
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm")
        role_select = st.selectbox("Role", ["user", "teacher", "farmer"])

        if st.button("Register"):
            if new_pass != confirm_pass:
                st.error("Passwords don't match")
            elif len(new_pass) < 4:
                st.error("Password too short")
            elif add_user(new_user, new_pass, role_select):
                st.success("Account created! Please login.")
            else:
                st.error("Username already exists")

    st.stop()

# ==================== MAIN PORTAL SELECTION ====================

st.set_page_config(page_title="Multi-Portal System", layout="wide")

st.sidebar.write(f"👋 Welcome, {st.session_state.username} ({st.session_state.role})")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.portal = None
    st.rerun()

if st.session_state.portal is None:
    st.title("🏠 Welcome to Multi-Portal System")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏫 School Portal")
        st.write("Student Management, Teacher Dashboard, Exam Results, Attendance")
        if st.button("🎓 Enter School Portal", use_container_width=True):
            st.session_state.portal = "school"
            st.rerun()

    with col2:
        st.markdown("### 🌾 Farmers Portal")
        st.write("Crop Management, Weather Forecast, Market Prices, Yield Predictor")
        if st.button("🚜 Enter Farmers Portal", use_container_width=True):
            st.session_state.portal = "farmers"
            st.rerun()

    st.stop()

if st.sidebar.button("🏠 Back to Homepage"):
    st.session_state.portal = None
    st.rerun()

# ==================== SCHOOL PORTAL ====================
if st.session_state.portal == "school":
    st.title("🏫 School Management Portal")
    st.caption(f"Today: {datetime.now().strftime('%A, %B %d, %Y')}")

    st.sidebar.title("🏫 School Menu")
    school_page = st.sidebar.radio("Navigate to:", [
        "📊 Dashboard", "👨‍🎓 Students", "👩‍🏫 Teachers",
        "📝 Exam Results", "📈 Performance", "💬 Notifications"
    ])

    if school_page == "📊 Dashboard":
        st.header("School Dashboard")
        students_df = get_students()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Students", len(students_df), "+56")
        col2.metric("Total Teachers", "78", "+3")
        col3.metric("Pass Rate", "87%", "+5%")
        col4.metric("Attendance", "94%", "-2%")

        st.subheader("Monthly Attendance")
        attendance = pd.DataFrame({"Month": ["Sep", "Oct", "Nov", "Dec"], "Attendance": [92, 94, 91, 88]})
        st.line_chart(attendance.set_index("Month"))

    elif school_page == "👨‍🎓 Students":
        st.header("Student Management")

        tab1, tab2 = st.tabs(["📋 Student List", "➕ Add Student"])

        with tab1:
            students_df = get_students()
            if len(students_df) > 0:
                st.dataframe(students_df, use_container_width=True)
                csv = students_df.to_csv(index=False)
                st.download_button("📎 Download CSV", csv, "students.csv", "text/csv")
            else:
                st.info("No students yet")

        with tab2:
            with st.form("add_student_form"):
                name = st.text_input("Student Name")
                student_class = st.selectbox("Class", ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"])
                parent_contact = st.text_input("Parent Contact")
                uploaded_photo = st.file_uploader("Student Photo", type=["jpg", "png", "jpeg"])

                if st.form_submit_button("Add Student"):
                    if name:
                        photo_bytes = uploaded_photo.read() if uploaded_photo else None
                        add_student(name, student_class, parent_contact, photo_bytes)
                        st.success(f"Added {name}")
                        st.rerun()

    elif school_page == "💬 Notifications":
        st.header("Notifications")
        msg = st.text_area("Send notification to all")
        if st.button("Send"):
            st.success("Notification sent!")

    elif school_page == "👩‍🏫 Teachers":
        teachers = pd.DataFrame({
            "Name": ["Mr. Williams", "Mrs. Davis", "Ms. Garcia"],
            "Subject": ["Math", "Science", "English"],
            "Years Exp": [12, 8, 5]
        })
        st.dataframe(teachers)

    elif school_page == "📝 Exam Results":
        results = pd.DataFrame({
            "Student": ["Alice", "Bob", "Charlie"],
            "Math": [92, 78, 88], "Science": [89, 85, 91], "English": [95, 80, 87]
        })
        st.dataframe(results)
        st.bar_chart(results[["Math", "Science", "English"]].mean())

    else:
        performance = pd.DataFrame({"Subject": ["Math", "Science", "English"], "Average": [85, 82, 88]})
        st.dataframe(performance)
        fig = px.bar(performance, x="Subject", y="Average")
        st.plotly_chart(fig)

# ==================== FARMERS PORTAL ====================
else:
    st.title("🌾 Farmers Portal")
    st.caption(f"Today: {datetime.now().strftime('%A, %B %d, %Y')}")

    st.sidebar.title("🌾 Farmers Menu")
    farmer_page = st.sidebar.radio("Navigate to:", [
        "📊 Dashboard", "🌱 Crop Management", "💰 Market Prices",
        "🌤 Weather", "📈 Yield Predictor", "💬 Alerts"
    ])

    if farmer_page == "📊 Dashboard":
        crops_df = get_crops()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Active Crops", len(crops_df), "+2")
        col2.metric("Total Yield (kg)", "12,450", "+1,200")
        col3.metric("Avg. Price/kg", "$2.50", "+$0.30")
        col4.metric("Revenue", "$31,125", "+15%")

        yield_data = pd.DataFrame({"Day": ["Mon", "Tue", "Wed", "Thu", "Fri"], "Yield": [450, 520, 480, 610, 580]})
        st.line_chart(yield_data.set_index("Day"))

    elif farmer_page == "🌱 Crop Management":
        st.header("Crop Management")

        tab1, tab2 = st.tabs(["📋 Crop List", "➕ Add Crop"])

        with tab1:
            crops_df = get_crops()
            if len(crops_df) > 0:
                st.dataframe(crops_df, use_container_width=True)
                csv = crops_df.to_csv(index=False)
                st.download_button("📎 Download CSV", csv, "crops.csv", "text/csv")
            else:
                st.info("No crops yet")

        with tab2:
            with st.form("add_crop_form"):
                crop_name = st.text_input("Crop Name")
                area = st.number_input("Area (acres)", min_value=0.1, value=1.0)
                planted_date = st.date_input("Planted Date")
                expected_harvest = st.date_input("Expected Harvest")
                status = st.selectbox("Status", ["Growing", "Ready", "Harvested"])
                crop_image = st.file_uploader("Crop Image", type=["jpg", "png", "jpeg"])

                if st.form_submit_button("Add Crop"):
                    if crop_name:
                        img_bytes = crop_image.read() if crop_image else None
                        add_crop(crop_name, area, str(planted_date), str(expected_harvest), status, img_bytes)
                        st.success(f"Added {crop_name}")
                        st.rerun()

    elif farmer_page == "💰 Market Prices":
        prices = pd.DataFrame({
            "Crop": ["Maize", "Wheat", "Rice", "Tomatoes", "Onions"],
            "Price/kg": ["$2.80", "$3.20", "$4.50", "$1.80", "$2.10"],
            "Trend": ["📈 +5%", "📈 +2%", "📉 -3%", "📈 +8%", "📉 -1%"]
        })
        st.dataframe(prices, use_container_width=True)

        price_chart = pd.DataFrame({"Crop": ["Maize", "Wheat", "Rice"], "Price": [2.80, 3.20, 4.50]})
        st.bar_chart(price_chart.set_index("Crop"))

    elif farmer_page == "🌤 Weather":
        st.header("Live Weather Forecast")

        api_key = st.text_input("Enter OpenWeatherMap API Key (or use demo)", type="password",
                                placeholder="Get free key at openweathermap.org")
        city = st.text_input("Enter City", "London")

        if city:
            if api_key:
                weather = get_weather(city, api_key)
                if weather:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Temperature", f"{weather['temp']}°C")
                    col2.metric("Humidity", f"{weather['humidity']}%")
                    col3.metric("Condition", weather['condition'].title())
                else:
                    st.warning("Demo mode: Showing sample data")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Temperature", "24°C")
                    col2.metric("Humidity", "65%")
                    col3.metric("Condition", "Sunny")
            else:
                st.info("💡 Demo weather data (add API key for live data)")
                col1, col2, col3 = st.columns(3)
                col1.metric("Temperature", "24°C", "+2°")
                col2.metric("Rainfall", "15%", "-5%")
                col3.metric("Humidity", "65%", "+3%")

            st.subheader("7-Day Forecast")
            forecast = pd.DataFrame({
                "Day": ["Today", "Tomorrow", "Wed", "Thu", "Fri"],
                "Condition": ["☀️ Sunny", "⛅️ Cloudy", "🌧 Rain", "☀️ Sunny", "☀️ Sunny"],
                "Temp": [28, 26, 22, 27, 29]
            })
            st.dataframe(forecast, use_container_width=True)

    elif farmer_page == "📈 Yield Predictor":
        st.header("AI Yield Predictor")

        col1, col2 = st.columns(2)
        with col1:
            crop = st.selectbox("Crop", ["Maize", "Wheat", "Rice", "Soybeans"])
            area = st.number_input("Area (acres)", 1, 500, 50)
            with col2:
                soil = st.select_slider("Soil Quality", ["Poor", "Average", "Good", "Excellent"])
            irrigation = st.selectbox("Irrigation", ["Rain-fed", "Drip", "Sprinkler"])

        base = {"Maize": 2000, "Wheat": 1500, "Rice": 2500, "Soybeans": 1800}
        soil_factor = {"Poor": 0.6, "Average": 0.8, "Good": 1.0, "Excellent": 1.2}
        irrigation_factor = {"Rain-fed": 0.7, "Drip": 1.1, "Sprinkler": 1.0}

        predicted = base[crop] * area * soil_factor[soil] * irrigation_factor[irrigation]

        st.subheader("Prediction Result")
        col1, col2, col3 = st.columns(3)
        col1.metric("Yield", f"{predicted:,.0f} kg")
        col2.metric("Revenue", f"${predicted * 2.5:,.0f}")
        col3.metric("Profit", f"${predicted * 1.2:,.0f}")

        if predicted > 5000:
            st.balloons()

    else:
        st.header("Pest Alerts")
        st.warning("⚠️ Pest alert: Locusts spotted in nearby region!")
        st.info("✅ No active alerts for your crops")

st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Streamlit")