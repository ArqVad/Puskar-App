import streamlit as st
from firebase_setup import db
from navigation import make_sidebar
import pandas as pd
from datetime import datetime

st.session_state.page = "Manage Users"
make_sidebar()

def manage_users():
    st.title("Manage Users")

    faculties_list = sorted([
        "Adab Dan Humaniora", "Dirasat Islamiyah", "Ekonomi Dan Bisnis", 
        "Ilmu Dakwah Dan Ilmu Komunikasi", "Ilmu Kesehatan", "Ilmu Sosial Dan Ilmu Politik",
        "Ilmu Tarbiyah Dan Keguruan", "Psikologi", "Sains Dan Teknologi",
        "Sekolah Pascasarjana", "Syariah Dan Hukum", "Ushuluddin"
    ])

    study_programs_list = sorted([
        "Agribisnis", "Akuntansi", "Bahasa dan Sastra Arab",
        "Bimbingan Penyuluhan Islam", "Biologi", "Dirasat Islamiyah",
        "Doktor Pengkajian Islam", "Ekonomi Pembangunan", "Ekonomi Syariah",
        "Farmasi", "Fisika", "Hukum Ekonomi Syari'ah (Muamalat)",
        "Hukum Keluarga (Ahwal Syakhshiyyah)", "Hukum Pidana Islam (Jinayah)",
        "Hukum Tata Negara (Siyasah)", "Ilmu Alqur'an Dan Tafsir",
        "Ilmu Hubungan Internasional", "Ilmu Hukum", "Ilmu Keperawatan",
        "Ilmu Perpustakaan", "Ilmu Politik", "Ilmu Tasawuf",
        "Komunikasi dan Penyiaran Islam", "Kesejahteraan Sosial", "Kimia",
        "Manajemen", "Manajemen Dakwah", "Manajemen Pendidikan Islam",
        "Matematika", "Pendidikan Agama Islam", "Pendidikan Bahasa Arab",
        "Pendidikan Bahasa dan Sastra Indonesia", "Pendidikan Bahasa Inggris",
        "Pendidikan Biologi", "Pendidikan Fisika", "Pendidikan Guru Madrasah Ibtidaiyah",
        "Pendidikan Ilmu Pengetahuan Sosial", "Pendidikan Kimia",
        "Pendidikan Matematika", "Perbankan Syariah", "Perbandingan Mazhab",
        "Psikologi", "Sastra Inggris", "Sejarah dan Kebudayaan Islam",
        "Sistem Informasi", "Studi Agama Agama", "Tarjamah",
        "Teknik Informatika", "Teknik Pertambangan"
    ])

    def add_user(email, nim, role, fakultas, prodi, ipk2, lama_studi, tahun_masuk, tahun_lulus):
        try:
            user_data = {
                "email": str(email),
                "NIM": str(nim),  # Ensure NIM is a string
                "role": str(role),
                "fakultas": str(fakultas),
                "prodi": str(prodi),
                "IPK_2": float(ipk2),  # If IPK_2 is a number, ensure it's a float
                "lama_studi": str(lama_studi),  # Assuming lama_studi is an integer
                "tahun_masuk": str(tahun_masuk),  # Ensure tahun_masuk is a string
                "tahun_lulus": str(tahun_lulus),  # Ensure tahun_lulus is a string
                "timecreated": datetime.utcnow(),
                "lastedited": datetime.utcnow()
            }
            db.collection("users").document(nim).set(user_data)
            st.success(f"User {email} with role {role} added successfully!")
        except Exception as e:
            st.error(f"Error adding user: {e}")

    def view_users(sort_by="timecreated", limit=None):
        try:
            # Fetch users from Firestore
            users_ref = db.collection("users").order_by(sort_by, direction="DESCENDING")
            if limit:
                users_ref = users_ref.limit(limit)
            users_stream = users_ref.stream()
            
            # Convert Firestore documents to a list of dictionaries
            user_list = [user.to_dict() for user in users_stream]

            if user_list:
                st.subheader("User List")

                # Define the desired column order
                column_order = [
                    "NIM", "email", "fakultas", "prodi", "IPK_2", 
                    "tahun_masuk", "tahun_lulus", "lama_studi", "role", 
                    "timecreated", "lastedited"
                ]

                # Convert to DataFrame and reorder columns
                df = pd.DataFrame(user_list)
                df = df[column_order]  # Ensure correct order

                # Display as an interactive table
                st.dataframe(df, use_container_width=True)
            else:
                st.write("No users found.")

        except Exception as e:
            st.error(f"Error fetching users: {e}")

    def delete_user(nim):
        try:
            db.collection("users").document(nim).delete()
            st.success(f"User with NIM {nim} deleted successfully!")
        except Exception as e:
            st.error(f"Error deleting user: {e}")

    def edit_user(nim, new_email, new_role, fakultas, prodi, ipk2, lama_studi, tahun_masuk, tahun_lulus):
        try:
            user_ref = db.collection("users").document(nim)
            user_ref.update({
                "email": str(new_email),  # Ensure email is a string
                "role": str(new_role),  # Ensure role is a string
                "fakultas": str(fakultas),  # Ensure fakultas is a string
                "prodi": str(prodi),  # Ensure prodi is a string
                "IPK_2": float(ipk2),  # Ensure IPK_2 is a float
                "lama_studi": str(lama_studi),  # Ensure lama_studi is an integer
                "tahun_masuk": str(tahun_masuk),  # Ensure tahun_masuk is a string
                "tahun_lulus": str(tahun_lulus),  # Ensure tahun_lulus is a string
                "lastedited": datetime.utcnow()  # Keep datetime unchanged
            })
            st.success(f"User with NIM {nim} updated successfully!")
        except Exception as e:
            st.error(f"Error updating user: {e}")

    st.divider()
    # View Users - Option to filter by timecreated or lastedited
    st.subheader("View Users")

    # Create three columns for layout consistency
    col1, col2, col3 = st.columns(3)

    # Place widgets in separate columns
    with col1:
        sort_by = st.selectbox("Sort by", ["timecreated", "lastedited"], key="user_sort_by")

    with col2:
        view_option = st.selectbox("View Option", ["View All", "View Last 10", "View Last 25", "Custom Number"], key="user_view_option")

    with col3:
        limit = None
        if view_option == "Custom Number":
            limit = st.number_input("Custom Number", min_value=1, step=1, key="user_custom_limit")
        elif view_option == "View Last 10":
            limit = 10
        elif view_option == "View Last 25":
            limit = 25

    # Button to trigger display of users
    if st.button("Show Users"):
        view_users(sort_by=sort_by, limit=limit)

    st.divider()

    # Add New User
    st.subheader("Add New User")
    with st.expander("Add Users", expanded=False):
        with st.form(key="add_user_form"):
            nim = st.text_input("NIM (Student Number)")
            email = st.text_input("User Email")
            fakultas = st.selectbox(
                "Faculties",
                faculties_list
            )
            prodi = st.selectbox(
                "Study Programs",
                study_programs_list
            )
            ipk2 = st.number_input("GPA 2", min_value=0.0, max_value=4.0, step=0.01)
            lama_studi = st.selectbox(
                "Study Duration (years)",
                [str(year) for year in range(1, 10)]
            )
            tahun_masuk = st.selectbox(
                "Entry Year",
                [str(year) for year in range(2010, 2050)]
            )
            tahun_lulus = st.selectbox(
                "Grad Year",
                [str(year) for year in range(2010, 2050)]
            )
            role = st.selectbox("Role", ["user", "admin"])
            add_user_button = st.form_submit_button(label="Add User")

            if add_user_button:
                if not email or not nim:
                    st.error("Please fill in all required fields.")
                else:
                    add_user(email, nim, role, fakultas, prodi, ipk2, lama_studi, tahun_masuk, tahun_lulus)
                    st.rerun()

    st.divider()

    st.subheader("Edit and Delete Existing User")

    # Edit or Delete Existing Users
    with st.expander("Edit or Delete Existing Users", expanded=True):
        search_nim = st.text_input("Enter NIM to search:")
        
        if search_nim:
            user_ref = db.collection("users").document(search_nim).get()
            
            if user_ref.exists:
                selected_user_data = user_ref.to_dict()
                
                # Convert dictionary to DataFrame for better display
                df = pd.DataFrame([selected_user_data])  # Convert to DataFrame

                # Define the desired column order
                column_order = [
                    "NIM", "email", "fakultas", "prodi", "IPK_2", 
                    "tahun_masuk", "tahun_lulus", "lama_studi", "role", 
                    "timecreated", "lastedited"
                ]

                # Reorder DataFrame columns
                df = df[column_order]

                # Display user details in a table
                st.dataframe(df, use_container_width=True)

                # Edit User Form
                with st.form(key="edit_user_form"):
                    new_email = st.text_input("New Email", value=selected_user_data['email'])
                    fakultas = st.selectbox(
                        "Faculties",
                        faculties_list,
                        index=faculties_list.index(selected_user_data['fakultas'])
                    )
                    prodi = st.selectbox(
                        "Study Programs",
                        study_programs_list,
                        index=study_programs_list.index(selected_user_data['prodi'])                        
                    )
                    ipk2 = st.number_input("GPA 2", min_value=0.0, max_value=4.0, step=0.01, value=selected_user_data['IPK_2'])
                    lama_studi = st.selectbox(
                        "Study Duration (years)",
                        [str(year) for year in range(1, 10)],
                        index=[str(year) for year in range(1, 10)].index(str(selected_user_data['lama_studi']))
                    )
                    tahun_masuk = st.selectbox(
                        "Entry Year",
                        [str(year) for year in range(2010, 2050)],
                        index=[str(year) for year in range(2010, 2050)].index(str(selected_user_data['tahun_masuk']))
                    )
                    tahun_lulus = st.selectbox(
                        "Grad Year",
                        [str(year) for year in range(2010, 2050)],
                        index=[str(year) for year in range(2010, 2050)].index(str(selected_user_data['tahun_lulus']))
                    )
                    new_role = st.selectbox("New Role", ["user", "admin"], index=["user", "admin"].index(selected_user_data['role']))
                    
                    edit_user_button = st.form_submit_button(label="Edit User")
                    delete_user_button = st.form_submit_button(label="Delete User")

                    # Handle Edit User
                    if edit_user_button:
                        edit_user(search_nim, new_email, new_role, fakultas, prodi, ipk2, lama_studi, tahun_masuk, tahun_lulus)
                        st.rerun()

                    # Handle Delete User
                    if delete_user_button:
                        delete_user(search_nim)
                        st.rerun()
            else:
                st.error(f"User with NIM {search_nim} not found.")
        else:
            st.info("Please enter a NIM to search.")

    st.divider()

    # Batch Add Users
    st.subheader("Batch Add Users (for user role only)")
    with st.expander("Batch Add Users from File", expanded=False):
        uploaded_file = st.file_uploader("Upload CSV, XLS, or XLSX file", type=["csv", "xls", "xlsx"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)

                nim_column = st.selectbox("Select NIM column:", df_upload.columns)
                email_column = st.selectbox("Select Email column:", df_upload.columns)
                fakultas_column = st.selectbox("Select Fakultas (Faculty) column:", df_upload.columns)
                prodi_column = st.selectbox("Select Prodi (Program) column:", df_upload.columns)
                ipk2_column = st.selectbox("Select IPK 2 (GPA 2) column:", df_upload.columns)
                lama_studi_column = st.selectbox("Select Lama Studi (Study Duration) column:", df_upload.columns)
                tahun_masuk_column = st.selectbox("Select Tahun Masuk (Year of Admission) column:", df_upload.columns)
                tahun_lulus_column = st.selectbox("Select Tahun Lulus (Year of Graduation) column:", df_upload.columns)

                if st.button("Add Users"):
                    for _, row in df_upload.iterrows():
                        nim = str(row[nim_column])  # Convert NIM to string
                        email = row[email_column]
                        fakultas = row[fakultas_column]
                        prodi = row[prodi_column]
                        ipk2 = row[ipk2_column]
                        lama_studi = row[lama_studi_column]
                        tahun_masuk = row[tahun_masuk_column]
                        tahun_lulus = row[tahun_lulus_column]
                        add_user(email, nim, "user", fakultas, prodi, ipk2, lama_studi, tahun_masuk, tahun_lulus)

                    st.success("Batch users added successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error processing file: {e}")

    st.divider()

manage_users()
