import streamlit as st
from firebase_setup import db
import pandas as pd
import numpy as np
from navigation import make_sidebar

st.session_state.page = "Prediction Loader"
make_sidebar()

def load_user_responses(questionnaire_id):
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
            'Tahun Lulus': data.get('tahun_lulus'),
            'Document ID': resp.id  # Store document ID for saving predictions
        }
        
        # Process the 'responses' field
        answers = data.get('responses', {})
        for question_id, response in answers.items():
            question_text = response.get('question_text', f'Q{question_id}')
            answer = response.get('answer', '')
            response_data[question_text] = answer
        
        response_list.append(response_data)

    return pd.DataFrame(response_list)

# Streamlit UI
st.title('Waiting Time Prediction using Random Forest')
#try new approach
st.divider()
# Form to input the questionnaire ID
with st.form(key='questionnaire_form'):
    questionnaire_id = st.text_input("Enter the questionnaire ID for data loading", "")
    submit_button = st.form_submit_button(label='Load Data')

# Load and save data if form is submitted
if submit_button and questionnaire_id:
    df_responses = load_user_responses(questionnaire_id)
    
    if df_responses is not None:  # Only store data if valid
        st.session_state['df_responses'] = df_responses
        st.session_state['q_id'] = questionnaire_id
        st.success("Data loaded successfully! Please proceed to the Prediction page.")
        st.switch_page("pages/prediction_result_page.py")
    else:
        st.error("No responses found. The questionnaire ID may not exist.")

if 'df_responses' in st.session_state:
    st.divider()
    st.info(f"Data for Questionnaire ID '{st.session_state.q_id}' is already loaded. Please proceed to the Prediction page.")
    # Button to go to the Prediction page
    if st.button("Go to Prediction Page"):
        st.switch_page("pages/prediction_result_page.py")

st.divider()
