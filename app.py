import streamlit as st
from firebase_setup import initialize_firebase, db

st.set_page_config(layout="centered")
# mulai Firebase
initialize_firebase()

# Authentication and role retrieval functions
def authenticate_user(email, password):
    try:
        # Fetch the user document using NIM (password is NIM here)
        user_doc = db.collection("users").document(password).get()
        if not user_doc.exists:
            return None

        user_data = user_doc.to_dict()
        
        # Check if the provided email matches the stored email in Firestore
        if user_data['email'] == email:
            return user_data  # Return the full user data instead of True/False
        else:
            return None
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None

# Set up session state for user data
if 'page' not in st.session_state:
    st.session_state.page = "Login"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Define navigation logic
if st.session_state.logged_in:
    if st.session_state.role == "admin":
        st.write("You are logged in as Admin.")
        st.write("Navigating to Admin Dashboard...")
        st.switch_page("pages/admin_manage_questionnaire_page.py")
    else:
        st.write("You are logged in as User.")
        st.write("Navigating to User form...")
        st.switch_page("pages/user_dashboard_page.py")
else:
    # Display login form
    image_path = "static/logo-uinjkt.png" 
    st.image(image_path, use_container_width=True)
    st.write("")

    with st.form(key='login_form'):
        email = st.text_input("Email")
        password = st.text_input("NIM (as password)", type="password")
        submit_button = st.form_submit_button(label="Login")

    if submit_button:
        # Authenticate user and retrieve data
        user_data = authenticate_user(email, password)
        if user_data:
            # Store necessary user information in session state
            st.session_state.email = email
            st.session_state.nim = password  # NIM is stored as password
            st.session_state.role = user_data['role']
            st.session_state.fakultas = user_data.get('fakultas', '')
            st.session_state.prodi = user_data.get('prodi', '')
            st.session_state.ipk2 = user_data.get('IPK_2', 0.0)
            st.session_state.lama_studi = user_data.get('lama_studi', 0)
            st.session_state.tahun_masuk = user_data.get('tahun_masuk', '')
            st.session_state.tahun_lulus = user_data.get('tahun_lulus', '')
            st.session_state.logged_in = True

            # Refresh the page to load the correct dashboard
            st.rerun()
        else:
            st.error("Login failed. Please check your credentials.")
