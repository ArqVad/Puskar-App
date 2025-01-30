import streamlit as st
from firebase_setup import db
import pandas as pd
import numpy as np
import joblib
from navigation import make_sidebar
from sklearn.preprocessing import StandardScaler

st.session_state.page = "Prediction Result"
make_sidebar()

# Load the saved model and preprocessing objects
rf_classifier = joblib.load('rf_classifier2.pkl')
scaler = joblib.load('scaler2.pkl')
catboost_encoder = joblib.load('catboost_encoder2.pkl')

# Define functions to load Firestore data

def preprocess_data(df):
    # Apply mappings for categorical values
    scale_mapping = {'Tidak Sama Sekali': 1, 'Kurang': 2, 'Cukup Besar': 3, 'Besar': 4, 'Sangat Besar': 5}
    job_search_mapping = {
        'Saya tidak mencari kerja': 1, 'Lebih dari 6 bulan sesudah lulus': 2, 
        'Kurang dari 6 bulan sesudah lulus': 3, 'Kurang dari 6 bulan sebelum lulus': 4
    }
    # Update IPK mapping to process float values
    def map_ipk(ipk):
        if ipk < 3.0:
            return 1
        elif 3.0 <= ipk <= 3.5:
            return 2
        elif ipk > 3.5:
            return 3
        else:
            return np.nan  # Handle NaN or any unexpected values

    for column in ['Perkuliahan', 'Demonstrasi', 'Partisipasi dalam proyek riset', 'Magang', 'Praktikum', 'Kerja Lapangan', 'Diskusi']:
        df[column] = df[column].map(scale_mapping)
    
    df['Kapan anda mulai mencari pekerjaan? Mohon pekerjaan sambilan tidak dimasukkan'] = df['Kapan anda mulai mencari pekerjaan? Mohon pekerjaan sambilan tidak dimasukkan'].map(job_search_mapping)
    # Apply the new IPK mapping function
    df['IPK 2'] = df['IPK 2'].apply(map_ipk)

    relevant_columns = ['NIM', 'Fakultas', 'Prodi', 'IPK 2', 'Lama Studi', 'Tahun Masuk', 'Tahun Lulus', 'Perkuliahan', 'Demonstrasi', 'Partisipasi dalam proyek riset', 'Magang', 'Praktikum', 'Kerja Lapangan', 'Diskusi', 'Kapan anda mulai mencari pekerjaan? Mohon pekerjaan sambilan tidak dimasukkan']
    
    # Replace '-' with NaN so they can be treated as missing values
    df.replace('-', np.nan, inplace=True)

    # Drop rows with NaN (including those where '-' was replaced) in relevant columns
    df_cleaned = df.dropna(subset=relevant_columns)
    return df_cleaned

def predict_with_model(df, model):
    # Select relevant columns
    X = df[['Fakultas', 'Prodi', 'IPK 2', 'Lama Studi', 'Tahun Masuk', 'Tahun Lulus', 'Perkuliahan', 'Demonstrasi', 'Partisipasi dalam proyek riset', 'Magang', 'Praktikum', 'Kerja Lapangan', 'Diskusi', 'Kapan anda mulai mencari pekerjaan? Mohon pekerjaan sambilan tidak dimasukkan']]
    
    # Encoding categorical features
    X_encoded = catboost_encoder.transform(X[['Fakultas', 'Prodi']])
    X_rest = X.drop(columns=['Fakultas', 'Prodi'])
    X_final = pd.concat([X_encoded.reset_index(drop=True), X_rest.reset_index(drop=True)], axis=1)
    
    # Scaling numerical features
    numerical_features = ['IPK 2', 'Lama Studi', 'Perkuliahan', 'Demonstrasi', 'Partisipasi dalam proyek riset', 'Magang', 'Praktikum', 'Kerja Lapangan', 'Diskusi', 'Kapan anda mulai mencari pekerjaan? Mohon pekerjaan sambilan tidak dimasukkan']
    X_final[numerical_features] = scaler.transform(X_final[numerical_features])
    
    # Making predictions using the passed model
    predictions = model.predict(X_final)
    
    # Add predictions as a new column to the original dataframe
    df['Job_within_6_months'] = predictions
    return df

def save_predictions_to_firestore(df):
    for index, row in df.iterrows():
        doc_id = row['Document ID']
        prediction = row['Job_within_6_months']
        response_ref = db.collection('user_data').document(doc_id)
        
        # Update the `responses` field with the prediction result
        response_ref.update({
            f'responses.Prediction_Result': {
                'question_text': 'Prediction Result',
                'answer': str(prediction)
            }
        })

# Streamlit UI
st.title('Waiting Time Prediction using Random Forest')
st.divider()
with st.form(key='questionnaire_form'):
    submit_button = st.form_submit_button(label='Change Data Source')

if submit_button:
    st.switch_page("pages/prediction_loader_page.py")

# Check if DataFrame is in session state
if 'df_responses' in st.session_state:
    df_responses = st.session_state['df_responses']

    st.subheader('Original Data')
    st.write(df_responses)
st.divider()
st.subheader("Map Columns for Prediction")
# Create three columns for layout
col1, col2, col3 = st.columns(3)

# Form for selecting columns
with st.form(key='column_mapping_form'):

    # Column 1
    with col1:
        nim_column = st.selectbox('Select NIM column', df_responses.columns, index=df_responses.columns.get_loc('NIM'))
        fakultas_column = st.selectbox('Select Fakultas column', df_responses.columns, index=df_responses.columns.get_loc('Fakultas'))
        prodi_column = st.selectbox('Select Prodi column', df_responses.columns, index=df_responses.columns.get_loc('Prodi'))
        ipk_column = st.selectbox('Select IPK column', df_responses.columns, index=df_responses.columns.get_loc('IPK 2'))
        lama_studi_column = st.selectbox('Select Lama Studi column', df_responses.columns, index=df_responses.columns.get_loc('Lama Studi'))

    # Column 2
    with col2:
        tahun_masuk_column = st.selectbox('Select Tahun Masuk column', df_responses.columns, index=df_responses.columns.get_loc('Tahun Masuk'))
        tahun_lulus_column = st.selectbox('Select Tahun Lulus column', df_responses.columns, index=df_responses.columns.get_loc('Tahun Lulus'))
        perkuliahan_column = st.selectbox('Select Perkuliahan column', df_responses.columns)
        demonstrasi_column = st.selectbox('Select Demonstrasi column', df_responses.columns)
        proyek_riset_column = st.selectbox('Select Proyek Riset column', df_responses.columns)

    # Column 3
    with col3:
        magang_column = st.selectbox('Select Magang column', df_responses.columns)
        praktikum_column = st.selectbox('Select Praktikum column', df_responses.columns)
        kerja_lapangan_column = st.selectbox('Select Kerja Lapangan column', df_responses.columns)
        diskusi_column = st.selectbox('Select Diskusi column', df_responses.columns)
        job_search_column = st.selectbox('Select Job Search column', df_responses.columns)

    # Submit button for the form
    submitted = st.form_submit_button("Map Columns and Proceed")

if submitted:
    # Step 2: Create a new DataFrame using selected columns
    new_df = pd.DataFrame({
        'NIM': df_responses[nim_column],
        'Fakultas': df_responses[fakultas_column],
        'Prodi': df_responses[prodi_column],
        'IPK 2': df_responses[ipk_column],
        'Lama Studi': df_responses[lama_studi_column],
        'Tahun Masuk': df_responses[tahun_masuk_column],
        'Tahun Lulus': df_responses[tahun_lulus_column],
        'Document ID': df_responses['Document ID'],  # Add the Document ID here
        'Perkuliahan': df_responses[perkuliahan_column],
        'Demonstrasi': df_responses[demonstrasi_column],
        'Partisipasi dalam proyek riset': df_responses[proyek_riset_column],
        'Magang': df_responses[magang_column],
        'Praktikum': df_responses[praktikum_column],
        'Kerja Lapangan': df_responses[kerja_lapangan_column],
        'Diskusi': df_responses[diskusi_column],
        'Kapan anda mulai mencari pekerjaan? Mohon pekerjaan sambilan tidak dimasukkan': df_responses[job_search_column]
    })

    # Step 3: Show the new DataFrame
    st.divider()
    st.subheader('New DataFrame for Prediction')
    st.write(new_df)
    st.divider()
    # Step 4: Preprocess the new DataFrame and perform prediction
    df_cleaned = preprocess_data(new_df)

    if not df_cleaned.empty:
        df_result = predict_with_model(df_cleaned, rf_classifier)

        # Save the result to session state
        st.session_state.df_result = df_result

        st.subheader('Predictions')
        st.write(df_result)

        # Save predictions to Firestore
        save_predictions_to_firestore(df_result)
        st.success("Predictions saved to Firestore.")

    else:
        st.error("No data available after cleaning.")

if 'df_result' in st.session_state:
    # Show download button only after predictions are available
    st.divider()
    st.download_button('Download Prediction Result CSV', st.session_state.df_result.to_csv(index=False), 'predictions.csv')
st.divider()