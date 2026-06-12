import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px

# ==================== SIMPLE LOGIN (No Database Issues) ====================

# Simple in-memory user storage (works on Streamlit Cloud)
if "users" not in st.session_state:
    st.session_state.users = {"admin": {"password": "admin123", "role": "admin"}}
    st.session_state.users["kingsford"] = {"password": "Kingsford@97", "role": "admin"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "portal" not in st.session_state:
    st.session_state.portal = None


# ==================== LOGIN / REGISTER ====================

def check_login(username, password):
    if username in st.session_state.users:
        if st.session_state.users[username]["password"] == password:
            return st.session_state.users[username]["role"]
    return None


def add_user(username, password, role):
    if username in st.session_state.users:
        return False
    st.session_state.users[username] = {"password": password, "role": role}
    return True


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
        "📝 Exam Results", "📈 Performance"
    ])

    if school_page == "📊 Dashboard":
        st.header("School Dashboard")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Students", "1,245", "+56")
        col2.metric("Total Teachers", "78", "+3")
        col3.metric("Pass Rate", "87%", "+5%")
        col4.metric("Attendance", "94%", "-2%")

        st.subheader("Monthly Attendance")
        attendance = pd.DataFrame({"Month": ["Sep", "Oct", "Nov", "Dec"], "Attendance": [92, 94, 91, 88]})
        st.line_chart(attendance.set_index("Month"))

    elif school_page == "👨‍🎓 Students":
        st.header("Student List")
        students = pd.DataFrame({
            "ID": [1001, 1002, 1003, 1004],
            "Name": ["Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Ross"],
            "Class": ["Grade 5", "Grade 4", "Grade 5", "Grade 3"],
            "Parent Contact": ["+123456789", "+123456788", "+123456787", "+123456786"]
        })
        st.dataframe(students, use_container_width=True)
        csv = students.to_csv(index=False)
        st.download_button("📎 Download CSV", csv, "students.csv", "text/csv")

    elif school_page == "👩‍🏫 Teachers":
        teachers = pd.DataFrame({
            "Name": ["Mr. Williams", "Mrs. Davis", "Ms. Garcia"],
            "Subject": ["Math", "Science", "English"],
            "Years Exp": [12, 8, 5]
        })
        st.dataframe(teachers, use_container_width=True)

    elif school_page == "📝 Exam Results":
        results = pd.DataFrame({
            "Student": ["Alice", "Bob", "Charlie", "Diana"],
            "Math": [92, 78, 88, 95],
            "Science": [89, 85, 91, 88],
            "English": [95, 80, 87, 92]
        })
        st.dataframe(results, use_container_width=True)
        st.subheader("Subject Averages")
        st.bar_chart(results[["Math", "Science", "English"]].mean())

    else:
        performance = pd.DataFrame({"Subject": ["Math", "Science", "English"], "Average": [85, 82, 88]})
        fig = px.bar(performance, x="Subject", y="Average", title="Class Performance")
        st.plotly_chart(fig, use_container_width=True)

# ==================== FARMERS PORTAL ====================
else:
    st.title("🌾 Farmers Portal")
    st.caption(f"Today: {datetime.now().strftime('%A, %B %d, %Y')}")

    st.sidebar.title("🌾 Farmers Menu")
    farmer_page = st.sidebar.radio("Navigate to:", [
        "📊 Dashboard", "🌱 Crop Management", "💰 Market Prices",
        "🌤 Weather", "📈 Yield Predictor"
    ])

    if farmer_page == "📊 Dashboard":
        st.header("Farm Dashboard")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Active Crops", "5", "+2")
        col2.metric("Total Yield (kg)", "12,450", "+1,200")
        col3.metric("Avg. Price/kg", "$2.50", "+$0.30")
        col4.metric("Revenue", "$31,125", "+15%")

        yield_data = pd.DataFrame({"Day": ["Mon", "Tue", "Wed", "Thu", "Fri"], "Yield": [450, 520, 480, 610, 580]})
        st.line_chart(yield_data.set_index("Day"))

    elif farmer_page == "🌱 Crop Management":
        st.header("Crop List")
        crops = pd.DataFrame({
            "Crop Name": ["Maize", "Wheat", "Rice", "Tomatoes"],
            "Area (acres)": [120, 85, 95, 40],
            "Planted Date": ["2025-03-01", "2025-03-15", "2025-04-01", "2025-02-15"],
            "Status": ["🌱 Growing", "🌱 Growing", "🌱 Growing", "🌻 Ready"]
        })
        st.dataframe(crops, use_container_width=True)
        csv = crops.to_csv(index=False)
        st.download_button("📎 Download CSV", csv, "crops.csv", "text/csv")

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
        st.header("Weather Forecast")
        city = st.text_input("Enter City", "New York")
        if city:
            col1, col2, col3 = st.columns(3)
            col1.metric("Temperature", "28°C", "+2°")
            col2.metric("Humidity", "65%", "+3%")
            col3.metric("Condition", "Sunny", "")

            forecast = pd.DataFrame({
                "Day": ["Today", "Tomorrow", "Wed", "Thu", "Fri"],
                "Condition": ["☀️ Sunny", "⛅️ Cloudy", "🌧 Rain", "☀️ Sunny", "☀️ Sunny"],
                "Temp": [28, 26, 22, 27, 29]
            })
            st.dataframe(forecast, use_container_width=True)

    else:
        st.header("Yield Predictor")

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

st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Streamlit")