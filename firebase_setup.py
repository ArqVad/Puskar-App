import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

def initialize_firebase():
    if not firebase_admin._apps:
        # Retrieve Firebase credentials from Streamlit secrets
        firebase_credentials = {
            "type": "service_account",
            "project_id": st.secrets["firebase"]["project_id"],
            "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets["firebase"]["client_email"],
            "client_id": st.secrets["firebase"]["client_id"],
            "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        }

        # Initialize Firebase with credentials
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)

# Call this function to ensure Firebase is initialized
initialize_firebase()

# Get Firestore client
db = firestore.client()
