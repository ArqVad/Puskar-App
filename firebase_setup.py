import streamlit as st
import firebase_admin
from firebase_admin import credentials

# Access the secret from Streamlit
cred_dict = st.secrets["firebase_credentials"]

# Initialize Firebase using the secret credentials
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
