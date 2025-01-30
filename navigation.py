import streamlit as st

def make_sidebar():
    with st.sidebar:
        image_path = "static/logo-uinjkt.png" 
        st.image(image_path, use_container_width=True)
        st.write("")

        if st.session_state.get("logged_in", False):
            if st.session_state.role == "admin":
                st.write("Admin Dashboard")
                st.page_link("pages/admin_manage_users_page.py", label="Manage Users", icon=":material/group:")
                st.page_link("pages/admin_manage_questionnaire_page.py", label="Manage Questionnaires", icon=":material/quiz:")
                st.page_link("pages/prediction_loader_page.py", label="Manage Predictions", icon=":material/insights:")
                st.page_link("pages/vdashboard_page.py", label="Manage Responses and Visualization", icon=":material/bar_chart:")
            else:
                st.write("User Form")
                st.page_link("pages/user_dashboard_page.py", label="User form", icon=":material/edit_note:")

            st.write("")
            st.write("")
            if st.button("Log out"):
                logout()

        elif st.session_state.page != "Login":
            st.session_state.page = "Login"
            st.switch_page("app.py")

def logout():
    st.session_state.logged_in = False
    st.session_state.email = None
    st.session_state.role = None
    st.session_state.nim = None
    st.session_state.page = "Login"
    st.info("Logged out successfully!")
    st.switch_page("app.py")