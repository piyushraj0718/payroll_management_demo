import streamlit as st
from connection import get_session
from db_setup import ContactMessage

def contact_page():
    session = get_session()
    
    st.title("Contact Us")
    st.write("Please fill in the form below to get in touch.")

    with st.form("contact_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Your Message")

        submitted = st.form_submit_button("Send")

        if submitted:
            if name and email and message:
                new_message = ContactMessage(name=name, email=email, message=message)
                session.add(new_message)
                session.commit()
                st.success("Your message has been sent. Thank you!")
            else:
                st.error("Please fill in all the fields.")
