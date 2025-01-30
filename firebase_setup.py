import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

# Load credentials from secrets
firebase_credentials = st.secrets["firebase"]

# Create a dictionary from secrets
cred_dict = {
    "type": firebase_credentials["type"],
    "project_id": firebase_credentials["project_id"],
    "private_key_id": firebase_credentials["private_key_id"],
    "private_key": firebase_credentials["private_key"],
    "client_email": firebase_credentials["client_email"],
    "client_id": firebase_credentials["client_id"],
    "auth_uri": firebase_credentials["auth_uri"],
    "token_uri": firebase_credentials["token_uri"],
    "auth_provider_x509_cert_url": firebase_credentials["auth_provider_x509_cert_url"],
    "client_x509_cert_url": firebase_credentials["client_x509_cert_url"],
    "universe_domain": firebase_credentials["universe_domain"]
}

# Function to initialize Firebase
def initialize_firebase():
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

# Now you can use Firestore
db = firestore.client()
