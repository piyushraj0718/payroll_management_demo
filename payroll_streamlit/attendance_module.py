import streamlit as st
from connection import get_session
from sqlalchemy import func
from db_setup import Employee, Attendance
from datetime import datetime
import calendar
import pandas as pd

def attendance_page():
    if not st.session_state.get('is_logged_in', False):
        st.warning("Please login first in 'Login / Sign Up' tab.")
        return

    organization = st.session_state.get('organization')
    if not organization:
        st.error("Organization info missing. Please login again.")
        return

    session = get_session()

    st.title("Attendance Management")

    selected_date = st.date_input("Select Date", datetime.today())

    if selected_date > datetime.today().date():
        st.warning("You cannot mark attendance for a future date.")
        return

    employees = session.query(Employee).filter_by(organization=organization).all()
    if not employees:
        st.info("No employees found for your organization. Please add employees first.")
        return

    employee_names = [emp.name for emp in employees]
    selected_employee = st.selectbox("Select Employee", employee_names)

    is_present = st.checkbox("Present", value=True)

    if st.button("Mark Attendance"):
        mark_attendance(session, selected_employee, selected_date, is_present, organization)

    st.subheader("Delete Employee")
    delete_employee_name = st.selectbox("Select Employee to Delete", employee_names, key="delete_emp")

    if st.button("Delete Selected Employee"):
        delete_employee(session, delete_employee_name, organization)

    st.subheader("Attendance Data")
    refresh_treeview(session, selected_date, organization)

def mark_attendance(session, selected_employee, selected_date, is_present, organization):
    employee = session.query(Employee).filter_by(name=selected_employee, organization=organization).first()

    if not employee:
        st.error("Employee not found in the database.")
        return

    attendance_record = session.query(Attendance).filter_by(employee_id=employee.id, date=selected_date).first()

    if attendance_record:
        attendance_record.is_present = is_present
    else:
        attendance_record = Attendance(employee_id=employee.id, date=selected_date, is_present=is_present)
        session.add(attendance_record)

    try:
        session.commit()
        st.success(f"Attendance marked for {selected_employee} on {selected_date} as {'Present' if is_present else 'Absent'}.")
    except Exception as e:
        session.rollback()
        st.error(f"Failed to mark attendance: {e}")

def delete_employee(session, employee_name, organization):
    employee = session.query(Employee).filter_by(name=employee_name, organization=organization).first()
    if employee:
        session.delete(employee)
        try:
            session.commit()
            st.success(f"Deleted employee '{employee_name}' successfully.")
        except Exception as e:
            session.rollback()
            st.error(f"Failed to delete employee: {e}")
    else:
        st.error("Employee not found.")

def refresh_treeview(session, selected_date, organization):
    employees = session.query(Employee).filter_by(organization=organization).all()

    if not employees:
        st.info("No employees found for your organization.")
        return

    attendance_data = []
    for emp in employees:
        attendance = session.query(Attendance).filter_by(employee_id=emp.id, date=selected_date).first()
        status = "Present" if attendance and attendance.is_present else "Absent"
        attendance_data.append([emp.name, emp.department, status])

    df = pd.DataFrame(attendance_data, columns=["Name", "Department", "Attendance"])
    st.dataframe(df)
