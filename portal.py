import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ==================== LIGHTWEIGHT MOBILE SETUP ====================

st.set_page_config(
    page_title="Multi-Portal",
    page_icon="🎓",
    layout="centered"
)

# Simple CSS for mobile
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        padding: 12px;
        font-size: 18px;
        margin: 5px 0;
    }
    .stTextInput input {
        font-size: 16px;
        padding: 10px;
    }
    h1 {
        font-size: 24px !important;
    }
    h2 {
        font-size: 20px !important;
    }
    .stMetric label {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIMPLE LOGIN ====================

if "users" not in st.session_state:
    st.session_state.users = {
        "kingsford": {"password": "Kingsford@97", "role": "admin"},
        "admin": {"password": "admin123", "role": "admin"}
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "portal" not in st.session_state:
    st.session_state.portal = None


def check_login(username, password):
    if username in st.session_state.users:
        if st.session_state.users[username]["password"] == password:
            return True
    return False


def add_user(username, password):
    if username in st.session_state.users:
        return False
    st.session_state.users[username] = {"password": password, "role": "user"}
    return True


# ==================== LOGIN SCREEN ====================

if not st.session_state.logged_in:
    st.title("🔐 Multi-Portal")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        login_user = st.text_input("Username", key="login_user_unique")
        login_pass = st.text_input("Password", type="password", key="login_pass_unique")

        if st.button("Login", key="login_btn_unique", use_container_width=True):
            if check_login(login_user, login_pass):
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.rerun()
            else:
                st.error("Invalid credentials")

    with register_tab:
        new_user = st.text_input("Username", key="reg_user_unique")
        new_pass = st.text_input("Password", type="password", key="reg_pass_unique")
        confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm_unique")

        if st.button("Register", key="reg_btn_unique", use_container_width=True):
            if not new_user or not new_pass:
                st.error("Please fill all fields")
            elif new_pass != confirm_pass:
                st.error("Passwords don't match")
            elif len(new_pass) < 4:
                st.error("Password too short (min 4 characters)")
            elif add_user(new_user, new_pass):
                st.success("Account created! Please login.")
            else:
                st.error("Username already exists")

    st.stop()

# ==================== MAIN MENU ====================

st.sidebar.write(f"👋 {st.session_state.username}")
if st.sidebar.button("Logout", key="logout_btn"):
    st.session_state.logged_in = False
    st.session_state.portal = None
    st.rerun()

if st.session_state.portal is None:
    st.title("🏠 Welcome")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏫 School", key="school_btn", use_container_width=True):
            st.session_state.portal = "school"
            st.rerun()
    with col2:
        if st.button("🌾 Farmers", key="farmers_btn", use_container_width=True):
            st.session_state.portal = "farmers"
            st.rerun()

    st.stop()

if st.sidebar.button("← Back to Home", key="back_home_btn"):
    st.session_state.portal = None
    st.rerun()

# ==================== SCHOOL PORTAL (Lightweight) ====================

if st.session_state.portal == "school":
    st.title("🏫 School Portal")
    st.caption(datetime.now().strftime("%B %d, %Y"))

    option = st.radio("Menu", ["Dashboard", "Students", "Exams"], key="school_menu")

    if option == "Dashboard":
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Students", "1,245", "+56")
        with col2:
            st.metric("Teachers", "78", "+3")

        st.subheader("Attendance")
        att_data = pd.DataFrame({
            "Month": ["Sep", "Oct", "Nov", "Dec"],
            "%": [92, 94, 91, 88]
        })
        st.line_chart(att_data.set_index("Month"))

    elif option == "Students":
        students = pd.DataFrame({
            "Name": ["Alice", "Bob", "Charlie", "Diana"],
            "Class": ["Gr5", "Gr4", "Gr5", "Gr3"]
        })
        st.dataframe(students, use_container_width=True)
        st.download_button("Download CSV", students.to_csv(index=False), "students.csv", key="students_csv")

    else:
        results = pd.DataFrame({
            "Student": ["Alice", "Bob", "Charlie"],
            "Math": [92, 78, 88],
            "Science": [89, 85, 91]
        })
        st.dataframe(results, use_container_width=True)
        st.bar_chart(results[["Math", "Science"]].mean())

# ==================== FARMERS PORTAL (Lightweight) ====================

else:
    st.title("🌾 Farmers Portal")
    st.caption(datetime.now().strftime("%B %d, %Y"))

    option = st.radio("Menu", ["Dashboard", "Crops", "Prices"], key="farmers_menu")

    if option == "Dashboard":
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Crops", "5", "+2")
        with col2:
            st.metric("Yield", "12,450kg", "+1,200")

        st.subheader("Weekly Yield")
        yield_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "kg": [450, 520, 480, 610, 580]
        })
        st.line_chart(yield_data.set_index("Day"))

    elif option == "Crops":
        crops = pd.DataFrame({
            "Crop": ["Maize", "Wheat", "Rice", "Tomatoes"],
            "Area": [120, 85, 95, 40],
            "Status": ["Growing", "Growing", "Growing", "Ready"]
        })
        st.dataframe(crops, use_container_width=True)
        st.download_button("Download CSV", crops.to_csv(index=False), "crops.csv", key="crops_csv")

    else:
        prices = pd.DataFrame({
            "Crop": ["Maize", "Wheat", "Rice", "Tomatoes"],
            "Price": ["$2.80", "$3.20", "$4.50", "$1.80"],
            "Trend": ["📈", "📈", "📉", "📈"]
        })
        st.dataframe(prices, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("v1.0 Mobile")