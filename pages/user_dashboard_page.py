import streamlit as st
from firebase_setup import db
from navigation import make_sidebar

st.set_page_config(layout="wide")
def user_dashboard():
    st.session_state.page = "User Dashboard"
    make_sidebar()

    def is_user_authorized(fakultas, prodi, tahun_masuk, tahun_lulus, access_filters, selected_nims, user_nim):
        
        # Check if the user is authorized based on either selected NIMs or access filters.
        
        # Priority check: selected NIMs from random sampling
        if selected_nims:
            return user_nim in selected_nims

        # Check against access filters
        if access_filters.get("faculties") != "all" and fakultas not in access_filters.get("faculties", []):
            return False
        if access_filters.get("study_programs") != "all" and prodi not in access_filters.get("study_programs", []):
            return False
        if access_filters.get("entry_years") != "all" and tahun_masuk not in access_filters.get("entry_years", []):
            return False
        if access_filters.get("grad_years") != "all" and tahun_lulus not in access_filters.get("grad_years", []):
            return False
        return True

    st.title("User Dashboard")

    # Fetch the active questionnaire document where is_active is true
    active_questionnaire_ref = db.collection("questionnaire").where("is_active", "==", True).limit(1).get()

    if not active_questionnaire_ref:
        st.warning("No active questionnaires available.")
        return

    # Assuming there's only one active questionnaire
    active_questionnaire = active_questionnaire_ref[0].to_dict()
    questionnaire_id = active_questionnaire_ref[0].id  # Get the questionnaire ID
    access_filters = active_questionnaire.get("access_filters", {})  # Get the access filters
    selected_nims = active_questionnaire.get("selected_nims", None)  # Get the selected NIMs list

    # Fetch the user's details from session state
    user_nim = st.session_state.nim
    user_fakultas = st.session_state.fakultas
    user_prodi = st.session_state.prodi
    user_tahun_masuk = st.session_state.tahun_masuk
    user_tahun_lulus = st.session_state.tahun_lulus

    # Check if the user is authorized to access this questionnaire
    if not is_user_authorized(user_fakultas, user_prodi, user_tahun_masuk, user_tahun_lulus, access_filters, selected_nims, user_nim):
        st.warning("You are not authorized to access the current active questionnaire.")
        return

    questions_map = active_questionnaire.get("questions", {})  # Fetch the questions from the 'questions' field

    if not questions_map:
        st.warning("No questions found in the active questionnaire.")
        return

    with st.form(key='user_form'):
        responses = {}
        for question_id, question in questions_map.items():
            label = question.get("question_text")  # Use the question text for user display
            q_type = question.get("field_type")
            options = question.get("options", [])
            slider_values = question.get("slider_values", {})

            # Collect responses based on question type
            if q_type == "text":
                user_answer = st.text_input(label, key=f"text_{question_id}")
            elif q_type == "select":
                user_answer = st.selectbox(label, options, key=f"select_{question_id}")
            elif q_type == "slider":
                min_value = slider_values.get("min", 1)  # Default to 1 if not set
                max_value = slider_values.get("max", 5)  # Default to 5 if not set
                user_answer = st.slider(label, min_value=min_value, max_value=max_value, key=f"slider_{question_id}")
            elif q_type == "number":
                user_answer = st.number_input(label, key=f"number_{question_id}")

            # Store each answer in the responses dictionary
            responses[question_id] = {
                "question_id": question_id,
                "question_text": label,
                "answer": user_answer,
                "question_type": q_type
            }

        submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        if user_nim:
            # Prepare the data to submit, including additional fields
            user_data = {
                "response_id": f"response_{user_nim}_{questionnaire_id}",
                "user_nim": user_nim,
                "email": st.session_state.email,
                "role": st.session_state.role,
                "fakultas": user_fakultas,
                "prodi": user_prodi,
                "IPK_2": st.session_state.ipk2,
                "lama_studi": st.session_state.lama_studi,
                "tahun_masuk": user_tahun_masuk,
                "tahun_lulus": user_tahun_lulus,
                "questionnaire_id": questionnaire_id,
                "responses": responses
            }

            # Set the document ID as "user_nim_questionnaire_id"
            db.collection("user_data").document(f"{user_nim}_{questionnaire_id}").set(user_data)

            st.success("Your responses have been submitted!")
            
user_dashboard()