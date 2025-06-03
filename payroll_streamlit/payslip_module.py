import streamlit as st
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
from connection import engine
from db_setup import Employee, Attendance

Session = sessionmaker(bind=engine)

def payslip_page():
    st.title("Generate Payslip")

    if not st.session_state.get('is_logged_in', False):
        st.warning("Please login first in 'Login / Sign Up' tab.")
        return

    organization = st.session_state.get('organization')
    if not organization:
        st.error("Organization info missing. Please login again.")
        return

    session = Session()

    employees = session.query(Employee).filter(Employee.organization == organization).all()
    if not employees:
        st.info("No employees found for your organization.")
        session.close()
        return

    employee_names = [emp.name for emp in employees]
    selected_name = st.selectbox("Select Employee", employee_names)
    selected_emp = next((emp for emp in employees if emp.name == selected_name), None)

    if selected_emp:
        today = date.today()
        year = st.selectbox("Select Year", options=[today.year, today.year - 1, today.year - 2], index=0)
        month = st.selectbox("Select Month", options=list(range(1, 13)),
                             format_func=lambda x: date(year, x, 1).strftime("%B"),
                             index=today.month - 1)

        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        weekends = [d for d in all_dates if d.weekday() >= 5]
        workdays = [d for d in all_dates if d.weekday() < 5]

        attendance_records = session.query(Attendance).filter(
            Attendance.employee_id == selected_emp.id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()

        attendance_map = {att.date: att.is_present for att in attendance_records}

        days_present = sum(1 for d in workdays if attendance_map.get(d, False))
        total_workdays = len(workdays)
        attendance_percentage = (days_present / total_workdays) * 100 if total_workdays > 0 else 0

        bonus_percentage = 5 if attendance_percentage >= 95 else 0
        bonus_amount = (bonus_percentage / 100) * selected_emp.basic_salary
        total_salary = selected_emp.basic_salary + bonus_amount

        st.markdown("---")
        st.subheader(f"Payslip for {selected_emp.name} - {date(year, month, 1).strftime('%B %Y')}")
        st.write(f"**Basic Salary:** ₹{selected_emp.basic_salary:.2f}")
        st.write(f"**Attendance:** {days_present} / {total_workdays} days ({attendance_percentage:.2f}%)")
        st.write(f"**Bonus:** {bonus_percentage}% (₹{bonus_amount:.2f})")
        st.write(f"**Total Salary:** ₹{total_salary:.2f}")

    session.close()
