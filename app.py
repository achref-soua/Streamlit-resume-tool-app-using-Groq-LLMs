# Main entry point for Streamlit app
import streamlit as st
from auth import login_page, logout, get_current_user
from resume_builder import resume_builder_page
from resume_adapter import resume_adapter_page
from resume_enhancer import resume_enhancer_page
from resume_export_pdf import resume_export_pdf_page

# Sidebar navigation
PAGES = {
    "Login/Logout": login_page,
    "Resume Builder": resume_builder_page,
    "Job Adaptation": resume_adapter_page,
    "Resume Enhancer": resume_enhancer_page,
    "Export PDF": resume_export_pdf_page,
}


def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    user = get_current_user()
    if selection == "Login/Logout":
        login_page()
        if user:
            if st.sidebar.button("Logout"):
                logout()
    else:
        if not user:
            st.warning("Please log in to access this feature.")
            login_page()
        else:
            PAGES[selection]()


if __name__ == "__main__":
    main()
