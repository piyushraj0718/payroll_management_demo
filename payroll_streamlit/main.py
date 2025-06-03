import os
import streamlit as st
from PIL import Image

# Page modules
from employee_module import employee_page
from attendance_module import attendance_page
from payslip_module import payslip_page
from auth_module import auth_page
from contact_module import contact_page

# --- Page Configuration ---
st.set_page_config(page_title="Payroll Management System", layout="centered")

# --- Load Logo ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, 'top2.jpg')

# --- Session State Initialization ---
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'organization' not in st.session_state:
    st.session_state.organization = None

# --- Authentication Page ---
if not st.session_state.is_logged_in:
    auth_page()  # defined in auth_module.py
    st.stop()

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("📂 Navigation")
    menu = st.selectbox(
        "Choose Section",
        ["Home", "Employee", "Attendance", "Payslip", "Contact Us"]
    )

    if st.button("🔒 Logout"):
        st.session_state.is_logged_in = False
        st.session_state.username = None
        st.session_state.organization = None
        st.success("Logged out successfully.")
        st.experimental_rerun()

# --- Main Content Display ---
if menu == "Home":
    st.title("🏠 Payroll Management System")
    
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)

    st.markdown(f"""
    Welcome **{st.session_state.username}** from **{st.session_state.organization}**! 🎉

    Use the sidebar to manage employees, mark attendance, or generate payslips.
    """)

elif menu == "Employee":
    employee_page()

elif menu == "Attendance":
    attendance_page()

elif menu == "Payslip":
    payslip_page()

elif menu == "Contact Us":
    contact_page()

# --- Footer ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<center>
    © 2025 Payroll Management System<br>
    Developed by <b>GROUP - 117</b> | Batch - 01
</center>
""", unsafe_allow_html=True)
