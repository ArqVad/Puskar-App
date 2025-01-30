import streamlit as st
import pandas as pd
from firebase_setup import db
from navigation import make_sidebar

st.session_state.page = "Data Loader"
make_sidebar()

st.title("Responses Visualization")
st.divider()

def load_user_responses(questionnaire_id):
    """Fetch user responses and assume questionnaire exists if responses are found."""
    responses_ref = db.collection('user_data').where('questionnaire_id', '==', questionnaire_id)
    responses = responses_ref.stream()

    response_list = []
    for resp in responses:
        data = resp.to_dict()
        response_data = {
            'NIM': data.get('user_nim'),
            'Fakultas': data.get('fakultas'),
            'Prodi': data.get('prodi'),
            'IPK 2': data.get('IPK_2'),
            'Lama Studi': data.get('lama_studi'),
            'Tahun Masuk': data.get('tahun_masuk'),
            'Tahun Lulus': data.get('tahun_lulus')
        }

        # Process the 'responses' field
        answers = data.get('responses', {})
        for question_id, response in answers.items():
            question_text = response.get('question_text', f'Q{question_id}')
            answer = response.get('answer', 'N/A')  # Handle missing answers
            response_data[question_text] = answer

        response_list.append(response_data)

    return pd.DataFrame(response_list) if response_list else None  # Return None if no responses are found

# Form to input the questionnaire ID
with st.form(key='questionnaire_form'):
    questionnaire_id = st.text_input("Enter the questionnaire ID for data loading", "")
    submit_button = st.form_submit_button(label='Load Data')

# Load and save data if form is submitted
if submit_button and questionnaire_id:
    df_response = load_user_responses(questionnaire_id)
    
    if df_response is not None:  # Only store data if valid
        st.session_state['df_response'] = df_response
        st.session_state['questionnaire_id'] = questionnaire_id
        st.success("Data loaded successfully! Please proceed to the Visualization page.")
        st.switch_page("pages/visualization_page.py")
    else:
        st.error("No responses found. The questionnaire ID may not exist.")

if 'df_response' in st.session_state:
    st.divider()
    st.info(f"Data for Questionnaire ID '{st.session_state.questionnaire_id}' is already loaded. Please proceed to the Visualization page.")
    # Button to go to the Visualization page
    if st.button("Go to Visualization Page"):
        st.switch_page("pages/visualization_page.py")

st.divider()
