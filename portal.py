import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px

# ==================== MOBILE OPTIMIZATION (iPhone 6s compatible) ====================

st.set_page_config(
    page_title="Multi-Portal System",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobile viewport and compatibility fixes
st.markdown("""
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
</head>
<style>
    /* Mobile fixes for older iOS */
    .main > div {
        padding: 0.5rem;
    }
    .stButton button {
        width: 100%;
        padding: 0.75rem;
        font-size: 16px;
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        margin: 5px 0;
    }
    input, textarea, select {
        font-size: 16px !important;
        padding: 10px !important;
    }
    .stTextInput > div > div > input {
        font-size: 16px !important;
    }
    .stSelectbox > div > div {
        font-size: 16px !important;
    }
    h1 {
        font-size: 24px !important;
    }
    h2 {
        font-size: 20px !important;
    }
    h3 {
        font-size: 18px !important;
    }
    .stMetric {
        text-align: center;
    }
    .stMetric label {
        font-size: 14px !important;
    }
    .stMetric .stMetricValue {
        font-size: 24px !important;
    }
    @media only screen and (max-width: 768px) {
        .stSidebar {
            position: fixed;
            z-index: 999;
            width: 250px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIMPLE LOGIN ====================

if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "admin123", "role": "admin"},
        "kingsford": {"password": "Kingsford@97", "role": "admin"}
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "portal" not in st.session_state:
    st.session_state.portal = None


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


# ==================== LOGIN SCREEN ====================

if not st.session_state.logged_in:
    st.title("🔐 Multi-Portal System")
    st.markdown("---")

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", key="login_btn"):
            if login_user and login_pass:
                role = check_login(login_user, login_pass)
                if role:
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.session_state.role = role
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.warning("Please enter username and password")

    with tab2:
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm")
        role_select = st.selectbox("Role", ["user", "teacher", "farmer"])

        if st.button("Register", key="reg_btn"):
            if not new_user or not new_pass:
                st.error("Please fill all fields")
            elif new_pass != confirm_pass:
                st.error("Passwords don't match")
            elif len(new_pass) < 4:
                st.error("Password too short (min 4 characters)")
            elif add_user(new_user, new_pass, role_select):
                st.success("✅ Account created! Please login.")
            else:
                st.error("Username already exists")

    st.stop()

# ==================== MAIN PORTAL ====================

st.sidebar.write(f"👋 Welcome, **{st.session_state.username}**")
st.sidebar.write(f"📌 Role: {st.session_state.role}")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.portal = None
    st.rerun()

st.sidebar.markdown("---")

# Portal Selection
if st.session_state.portal is None:
    st.title("🏠 Welcome!")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏫 School Portal")
        st.write("Students, Teachers, Exams")
        if st.button("🎓 Enter School", use_container_width=True):
            st.session_state.portal = "school"
            st.rerun()

    with col2:
        st.markdown("### 🌾 Farmers Portal")
        st.write("Crops, Weather, Prices")
        if st.button("🚜 Enter Farmers", use_container_width=True):
            st.session_state.portal = "farmers"
            st.rerun()

    st.stop()

if st.sidebar.button("🏠 Back to Home"):
    st.session_state.portal = None
    st.rerun()

# ==================== SCHOOL PORTAL ====================
if st.session_state.portal == "school":
    st.title("🏫 School Portal")
    st.caption(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")

    menu = st.radio("📋 Menu", ["Dashboard", "Students", "Teachers", "Exams", "Performance"])

    if menu == "Dashboard":
        st.header("📊 Dashboard")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Students", "1,245", "+56")
            st.metric("Pass Rate", "87%", "+5%")
        with c2:
            st.metric("Teachers", "78", "+3")
            st.metric("Attendance", "94%", "-2%")

        st.subheader("Attendance Trend")
        att = pd.DataFrame({"Month": ["Sep", "Oct", "Nov", "Dec"], "Att": [92, 94, 91, 88]})
        st.line_chart(att.set_index("Month"))

    elif menu == "Students":
        st.header("👨‍🎓 Students")
        students = pd.DataFrame({
            "Name": ["Alice", "Bob", "Charlie", "Diana"],
            "Class": ["Grade 5", "Grade 4", "Grade 5", "Grade 3"],
            "Contact": ["+123456789", "+123456788", "+123456787", "+123456786"]
        })
        st.dataframe(students, use_container_width=True)
        st.download_button("📎 Download CSV", students.to_csv(index=False), "students.csv")

    elif menu == "Teachers":
        teachers = pd.DataFrame({
            "Name": ["Mr. Williams", "Mrs. Davis", "Ms. Garcia"],
            "Subject": ["Math", "Science", "English"],
            "Experience": [12, 8, 5]
        })
        st.dataframe(teachers, use_container_width=True)

    elif menu == "Exams":
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
        perf = pd.DataFrame({"Subject": ["Math", "Science", "English"], "Avg": [85, 82, 88]})
        fig = px.bar(perf, x="Subject", y="Avg", title="Class Performance")
        st.plotly_chart(fig, use_container_width=True)

# ==================== FARMERS PORTAL ====================
else:
    st.title("🌾 Farmers Portal")
    st.caption(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")

    menu = st.radio("📋 Menu", ["Dashboard", "Crops", "Market", "Weather", "Yield Predictor"])

    if menu == "Dashboard":
        st.header("📊 Farm Dashboard")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Active Crops", "5", "+2")
            st.metric("Yield (kg)", "12,450", "+1,200")
        with c2:
            st.metric("Price/kg", "$2.50", "+$0.30")
            st.metric("Revenue", "$31,125", "+15%")

        st.subheader("Weekly Yield")
        yield_data = pd.DataFrame({"Day": ["Mon", "Tue", "Wed", "Thu", "Fri"], "Yield": [450, 520, 480, 610, 580]})
        st.line_chart(yield_data.set_index("Day"))

    elif menu == "Crops":
        st.header("🌱 Crops")
        crops = pd.DataFrame({
            "Crop": ["Maize", "Wheat", "Rice", "Tomatoes"],
            "Area": [120, 85, 95, 40],
            "Status": ["🌱 Growing", "🌱 Growing", "🌱 Growing", "🌻 Ready"]
        })
        st.dataframe(crops, use_container_width=True)
        st.download_button("📎 Download CSV", crops.to_csv(index=False), "crops.csv")

    elif menu == "Market":
        prices = pd.DataFrame({
            "Crop": ["Maize", "Wheat", "Rice", "Tomatoes", "Onions"],
            "Price/kg": ["$2.80", "$3.20", "$4.50", "$1.80", "$2.10"],
            "Trend": ["📈 +5%", "📈 +2%", "📉 -3%", "📈 +8%", "📉 -1%"]
        })
        st.dataframe(prices, use_container_width=True)
        price_chart = pd.DataFrame({"Crop": ["Maize", "Wheat", "Rice"], "Price": [2.80, 3.20, 4.50]})
        st.bar_chart(price_chart.set_index("Crop"))

    elif menu == "Weather":
        st.header("🌤 Weather")
        city = st.text_input("Location", "Accra")
        if city:
            c1, c2, c3 = st.columns(3)
            c1.metric("Temperature", "28°C")
            c2.metric("Humidity", "65%")
            c3.metric("Condition", "☀️ Sunny")

            forecast = pd.DataFrame({
                "Day": ["Today", "Tomorrow", "Wed", "Thu", "Fri"],
                "Weather": ["☀️", "⛅️", "🌧", "☀️", "☀️"],
                "Temp": [28, 26, 22, 27, 29]
            })
            st.dataframe(forecast, use_container_width=True)

    else:
        st.header("📈 Yield Predictor")

        crop = st.selectbox("Crop", ["Maize", "Wheat", "Rice", "Soybeans"])
        area = st.number_input("Area (acres)", 1, 500, 50)
        soil = st.select_slider("Soil Quality", ["Poor", "Average", "Good", "Excellent"])
        irrigation = st.selectbox("Irrigation", ["Rain-fed", "Drip", "Sprinkler"])

        base = {"Maize": 2000, "Wheat": 1500, "Rice": 2500, "Soybeans": 1800}
        soil_factor = {"Poor": 0.6, "Average": 0.8, "Good": 1.0, "Excellent": 1.2}
        irrigation_factor = {"Rain-fed": 0.7, "Drip": 1.1, "Sprinkler": 1.0}

        predicted = base[crop] * area * soil_factor[soil] * irrigation_factor[irrigation]

        st.success(f"### 🌾 Predicted Yield: {predicted:,.0f} kg")
        st.info(f"💰 Estimated Revenue: ${predicted * 2.5:,.0f}")

st.sidebar.markdown("---")
st.sidebar.caption("📱 Mobile Optimized")
st.sidebar.caption("Built with Streamlit")