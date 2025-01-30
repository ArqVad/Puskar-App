import streamlit as st
import firebase_admin
from firebase_admin import firestore
from firebase_setup import db
from navigation import make_sidebar
import pandas as pd
from datetime import datetime
import random

st.set_page_config(layout="wide")
st.session_state.page = "Manage Questionnaire"
make_sidebar()

def manage_questionnaire():
    st.title("Manage Questionnaires")

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

    # Add a new question to a questionnaire
    def add_question(questionnaire_id, question, field_type, options=None, slider_values=None):
        try:
            question_id = f"q{int(datetime.utcnow().timestamp() * 1000)}"  # Unique question_id using timestamp
            question_data = {
                "question_id": question_id,
                "question_text": question,
                "field_type": field_type,
                "options": options if options else [],
                "slider_values": slider_values if slider_values else {},  # Add slider values
                "timecreated": datetime.utcnow()  # Add timecreated
            }

            # Add the question as a key-value pair to the 'questions' dictionary
            questionnaire_ref = db.collection("questionnaire").document(questionnaire_id)
            questionnaire_ref.update({
                f"questions.{question_id}": question_data,
                "lastedited": datetime.utcnow()  # Update lastedited when modifying
            })

            st.success(f"Question '{question}' added to questionnaire '{questionnaire_id}' successfully!")
        except Exception as e:
            st.error(f"Error adding question: {e}")

    # Extend the activate_questionnaire_with_filter function
    def activate_questionnaire_with_filter(questionnaire_id, faculties, study_programs, entry_years, grad_years, random_sampling=False, sample_size=None):
        try:
            # Deactivate all other questionnaires
            all_questionnaires_ref = db.collection("questionnaire").stream()
            for q in all_questionnaires_ref:
                db.collection("questionnaire").document(q.id).update({"is_active": False})

            # Construct the filters
            access_filters = {
                "faculties": faculties if faculties else "all",
                "study_programs": study_programs if study_programs else "all",
                "entry_years": entry_years if entry_years else "all",
                "grad_years": grad_years if grad_years else "all",
            }

            selected_nims = None

            # Only fetch user data if random sampling is enabled
            if random_sampling and sample_size:
                if faculties == "all" and study_programs == "all" and entry_years == "all" and grad_years == "all":
                    # If no filters are set, retrieve all users
                    users_ref = db.collection("users").stream()
                else:
                    # Apply filters as usual
                    query = db.collection("users")
                    if faculties and faculties != "all":
                        query = query.where("fakultas", "in", faculties)
                    if study_programs and study_programs != "all":
                        query = query.where("prodi", "in", study_programs)
                    if entry_years and entry_years != "all":
                        query = query.where("tahun_masuk", "in", entry_years)
                    if grad_years and grad_years != "all":
                        query = query.where("tahun_lulus", "in", grad_years)
                    users_ref = query.stream()

                # Collect matching NIMs
                matched_users = [user_doc.to_dict().get("NIM") for user_doc in users_ref]

                # Randomly sample the specified number of users
                if len(matched_users) >= sample_size:
                    selected_nims = random.sample(matched_users, sample_size)
                else:
                    st.warning("Sample size exceeds the number of matched users. Using all matched users.")
                    selected_nims = matched_users

                # Update the access filters with selected NIMs
                access_filters["selected_nims"] = selected_nims

            # Activate the selected questionnaire with the filters
            db.collection("questionnaire").document(questionnaire_id).update({
                "is_active": True,
                "access_filters": access_filters,
                "selected_nims": None if not random_sampling else selected_nims,  # Reset or set selected_nims
            })

            st.success(f"Questionnaire '{questionnaire_id}' is now active with specified access filters!")
            if selected_nims:
                st.write("Selected Users (NIMs):", selected_nims)

        except Exception as e:
            st.error(f"Error activating questionnaire: {e}")

    # Delete a questionnaire
    def delete_questionnaire(questionnaire_id):
        try:
            db.collection("questionnaire").document(questionnaire_id).delete()
            st.success(f"Questionnaire with ID '{questionnaire_id}' deleted successfully!")
        except Exception as e:
            st.error(f"Error deleting questionnaire: {e}")

    # Edit a questionnaire's title
    def edit_questionnaire_title(questionnaire_id, new_title):
        try:
            db.collection("questionnaire").document(questionnaire_id).update({
                "title": new_title,
                "lastedited": datetime.utcnow()  # Update lastedited when editing title
            })
            st.success(f"Questionnaire title updated successfully!")
        except Exception as e:
            st.error(f"Error editing questionnaire title: {e}")

    # View questionnaires sorted by timecreated or lastedited
    def view_questionnaires(sort_by="timecreated", limit=None):
        try:
            # Fetch questionnaires from Firestore
            questionnaires_ref = db.collection("questionnaire").order_by(sort_by, direction="DESCENDING")
            if limit:
                questionnaires_ref = questionnaires_ref.limit(limit)
            questionnaires_stream = questionnaires_ref.stream()

            # Prepare data for display
            questionnaire_list = []
            for q in questionnaires_stream:
                q_data = q.to_dict()
                # You can use the stored questionnaire_id (or the Firestore document ID)
                q_data['questionnaire_id'] = q.id  # Add the document ID if you need it, or use q_data['questionnaire_id']
                questionnaire_list.append(q_data)

            # Display data interactively
            if questionnaire_list:
                df = pd.DataFrame(questionnaire_list)  # Convert list to DataFrame

                # Define the desired column order
                desired_column_order = [
                    'questionnaire_id', 'title', 'description', 'is_active', 'access_filters',
                    'selected_nims', 'timecreated', 'lastedited', 'questions'
                ]
                
                # Reorder columns to match the desired order
                df = df[desired_column_order]

                # Display the DataFrame with the new column order
                st.dataframe(df, use_container_width=True)  # Use st.dataframe for interactivity
            else:
                st.write("No questionnaires found.")
        except Exception as e:
            st.error(f"Error fetching questionnaires: {e}")

    # Delete a specific question from a questionnaire
    def delete_question(questionnaire_id, question_id):
        try:
            questionnaire_ref = db.collection("questionnaire").document(questionnaire_id)
            questionnaire_ref.update({
                f"questions.{question_id}": firestore.DELETE_FIELD,
                "lastedited": datetime.utcnow()  # Update lastedited when modifying
            })
            st.success(f"Question with ID '{question_id}' deleted successfully!")
        except Exception as e:
            st.error(f"Error deleting question: {e}")

    # Edit a specific question in a questionnaire
    def edit_question(questionnaire_id, question_id, new_question_text, field_type, options=None, slider_values=None):
        try:
            question_data = {
                "question_id": question_id,
                "question_text": new_question_text,
                "field_type": field_type,
                "options": options if options else [],
                "slider_values": slider_values if slider_values else {},
                "timecreated": datetime.utcnow()  # Keep the original creation time
            }

            db.collection("questionnaire").document(questionnaire_id).update({
                f"questions.{question_id}": question_data,
                "lastedited": datetime.utcnow()  # Update lastedited when modifying
            })
            st.success(f"Question with ID '{question_id}' updated successfully!")
        except Exception as e:
            st.error(f"Error editing question: {e}")

    st.divider()
    
    # View Questionnaires - Option to filter by timecreated or lastedited
    st.subheader("View Questionnaires")

    # Create three columns
    col1, col2, col3 = st.columns(3)

    # Place widgets in separate columns
    with col1:
        sort_by = st.selectbox("Sort by", ["timecreated", "lastedited"], key="sort_by")

    with col2:
        view_option = st.selectbox("View Option", ["View All", "View Last 10", "View Last 25", "Custom Number"], key="view_option")

    with col3:
        limit = None
        if view_option == "Custom Number":
            limit = st.number_input("Custom Number", min_value=1, step=1, key="custom_limit")
        elif view_option == "View Last 10":
            limit = 10
        elif view_option == "View Last 25":
            limit = 25

    # Button to trigger display of questionnaires
    if st.button("Show Questionnaires"):
        view_questionnaires(sort_by=sort_by, limit=limit)
    
    st.divider()

    # Add New Questionnaire
    st.subheader("Add Questionnaire")
    with st.expander("Add Questionnaire", expanded=False):
        with st.form(key="add_questionnaire_form"):
            title = st.text_input("Questionnaire Title")
            description = st.text_area("Questionnaire Description")  # Added description field
            add_questionnaire_button = st.form_submit_button(label="Add Questionnaire")

        if add_questionnaire_button:
            try:
                questionnaire_id = f"questionnaire_{int(datetime.utcnow().timestamp() * 1000)}"
                questionnaire_data = {
                    "questionnaire_id": questionnaire_id,  # Store questionnaire_id explicitly in the document
                    "title": title,
                    "description": description,  # Added description field
                    "questions": {},  # Initialize as an empty dictionary
                    "timecreated": datetime.utcnow(),
                    "lastedited": datetime.utcnow(),
                    "is_active": False,  # Newly created questionnaires are inactive by default
                    "access_filters": {},  # Ensure access_filters is initialized
                    "selected_nims": []  # Ensure selected_nims is initialized
                }

                # Create a new questionnaire document
                db.collection("questionnaire").document(questionnaire_id).set(questionnaire_data)
                st.success(f"Questionnaire '{title}' added successfully!")
            except Exception as e:
                st.error(f"Error adding questionnaire: {e}")

    st.divider()

    # Edit and Delete Questionnaire (Title and Description)
    st.subheader("Edit and Delete Questionnaire")
    with st.expander("Edit or Delete Questionnaire", expanded=True):
        questionnaire_id_to_edit = st.text_input("Enter Questionnaire ID to search:", key="edit_questionnaire_id")

        if questionnaire_id_to_edit:
            questionnaire_ref = db.collection("questionnaire").document(questionnaire_id_to_edit).get()
            if questionnaire_ref.exists:
                selected_questionnaire_data = questionnaire_ref.to_dict()

                # Convert the selected questionnaire data to DataFrame for better display
                df_selected_questionnaire = pd.DataFrame([selected_questionnaire_data])

                # Define the desired column order
                desired_column_order = [
                    'questionnaire_id', 'title', 'description', 'is_active', 'access_filters',
                    'selected_nims', 'timecreated', 'lastedited', 'questions'
                ]
                
                # Reorder columns to match the desired order
                df_selected_questionnaire = df_selected_questionnaire[desired_column_order]

                # Display the questionnaire details interactively using st.dataframe
                st.dataframe(df_selected_questionnaire)

                # Edit Questionnaire Form
                with st.form(key="edit_questionnaire_form"):
                    new_title = st.text_input("New Title", value=selected_questionnaire_data.get('title', ''))
                    new_description = st.text_area("New Description", value=selected_questionnaire_data.get('description', ''))

                    # Submit buttons
                    edit_questionnaire_button = st.form_submit_button(label="Edit Questionnaire")
                    delete_questionnaire_button = st.form_submit_button(label="Delete Questionnaire")

                    # Handle Edit Questionnaire
                    if edit_questionnaire_button:
                        try:
                            db.collection("questionnaire").document(questionnaire_id_to_edit).update({
                                "title": new_title,
                                "description": new_description,
                                "lastedited": datetime.utcnow()
                            })
                            st.success(f"Questionnaire '{questionnaire_id_to_edit}' updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating questionnaire: {e}")

                    # Handle Delete Questionnaire
                    if delete_questionnaire_button:
                        try:
                            db.collection("questionnaire").document(questionnaire_id_to_edit).delete()
                            st.success(f"Questionnaire '{questionnaire_id_to_edit}' deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting questionnaire: {e}")
            else:
                st.error(f"Questionnaire with ID '{questionnaire_id_to_edit}' not found.")
        else:
            st.info("Please enter a Questionnaire ID to search.")

    st.divider()

    # Activate Questionnaire
    st.subheader("Activate Questionnaire")

    # Activation Section
    with st.expander("Activate a Questionnaire", expanded=True):
        # Input for Questionnaire ID
        questionnaire_id_to_activate = st.text_input("Enter Questionnaire ID to search:", key="activate_questionnaire_id")

        if questionnaire_id_to_activate:
            questionnaire_ref = db.collection("questionnaire").document(questionnaire_id_to_activate).get()
            
            if questionnaire_ref.exists:
                selected_questionnaire_data = questionnaire_ref.to_dict()
                st.write("Questionnaire found:")

                # Convert the selected questionnaire data to DataFrame for better display
                df_selected_questionnaire = pd.DataFrame([selected_questionnaire_data])

                # Define the desired column order
                desired_column_order = [
                    'questionnaire_id', 'title', 'description', 'is_active', 'access_filters',
                    'selected_nims', 'timecreated', 'lastedited', 'questions'
                ]
                
                # Reorder columns to match the desired order
                df_selected_questionnaire = df_selected_questionnaire[desired_column_order]

                # Display the DataFrame with the new column order using st.dataframe
                st.dataframe(df_selected_questionnaire)

                # Filters Section
                st.write("Set Access Filters (Leave empty for all users):")
                faculties = st.multiselect("Faculties", faculties_list, default=[])
                study_programs = st.multiselect("Study Programs", study_programs_list, default=[])
                entry_years = st.multiselect("Entry Years", [str(year) for year in range(2010, 2050)], default=[])
                grad_years = st.multiselect("Graduation Years", [str(year) for year in range(2010, 2050)], default=[])
                random_sampling = st.checkbox("Use Random Sampling?")

                with st.form(key="activation_form"):
                    sample_size = None
                    if random_sampling:
                        sample_size = st.number_input("Number of Random Users to Select:", min_value=1, step=1)
                    
                    # Submit button for activation
                    activate_questionnaire_button = st.form_submit_button(label="Activate Questionnaire")
                    
                    # Submit button for deactivation (secondary button)
                    deactivate_questionnaire_button = st.form_submit_button(label="Deactivate Questionnaire")

                if activate_questionnaire_button:
                    activate_questionnaire_with_filter(
                        questionnaire_id=questionnaire_id_to_activate,
                        faculties=faculties,
                        study_programs=study_programs,
                        entry_years=entry_years,
                        grad_years=grad_years,
                        random_sampling=random_sampling,
                        sample_size=sample_size
                    )
                    st.rerun()

                # Handle Deactivation
                if deactivate_questionnaire_button:
                    try:
                        # Deactivate the questionnaire by updating the `is_active` field to False
                        db.collection("questionnaire").document(questionnaire_id_to_activate).update({
                            "is_active": False,
                            "lastedited": datetime.utcnow()  # Update the lastedited timestamp
                        })
                        st.success(f"Questionnaire '{questionnaire_id_to_activate}' has been deactivated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deactivating questionnaire: {e}")
    
    st.divider()

    # === Manage Questions Independently Section ===

    st.subheader("Manage Questions Within Questionnaire")
    # Enter Questionnaire ID to manage questions
    questionnaire_id_input = st.text_input("Enter Questionnaire ID to manage:", key="manage_questions")

    # Fetch questionnaire details
    if questionnaire_id_input:
        questionnaire_ref = db.collection("questionnaire").document(questionnaire_id_input).get()
        
        if questionnaire_ref.exists:
            selected_questionnaire_data = questionnaire_ref.to_dict()
            st.write("Questionnaire found:")

            # Ensure questions are in a dict format
            questions = selected_questionnaire_data.get("questions", {})
            if not isinstance(questions, dict):
                questions = {}

            # Rearrange columns to ensure 'questions' comes after 'title' and 'description'
            desired_column_order = [
                'questionnaire_id', 'title', 'description', 'questions', 'is_active', 
                'access_filters', 'selected_nims', 'timecreated', 'lastedited'
            ]
            
            # Convert to DataFrame
            df_selected_questionnaire = pd.DataFrame([selected_questionnaire_data])

            # Reorder columns, ensuring 'questions' appears in the correct position
            df_selected_questionnaire = df_selected_questionnaire[[col for col in desired_column_order if col in df_selected_questionnaire.columns]]

            # Display questionnaire details with questions in the right order
            st.dataframe(df_selected_questionnaire)

            # **Add New Question Section**
            st.subheader("Add Question")
            with st.expander("Add New Question", expanded=False):
                new_question_text = st.text_input("New Question Text")
                field_types = ["text", "number", "select", "slider"]
                field_type = st.selectbox("Field Type", field_types)

                with st.form(key="add_question_form"):
                    options = None
                    slider_values = None
                    
                    if field_type == "select":
                        options_input = st.text_area("Options (comma-separated)").strip()
                        options = [opt.strip() for opt in options_input.split(',') if opt.strip()]
                    
                    elif field_type == "slider":
                        min_value = st.number_input("Slider Min Value", value=0)
                        max_value = st.number_input("Slider Max Value", value=100)
                        default_value = st.number_input("Slider Default Value", value=(min_value + max_value) // 2)
                        slider_values = {"min": min_value, "max": max_value, "default": default_value}

                    add_question_button = st.form_submit_button(label="Add Question")

                if add_question_button:
                    add_question(questionnaire_id_input, new_question_text, field_type, options, slider_values)
                    st.rerun()

            # **Manage Existing Questions (Each in Separate DataFrame)**
            if questions:
                st.subheader("Manage Questions")

                for question_id, question in questions.items():
                    # Convert question data to DataFrame
                    df_question = pd.DataFrame([question])

                    # Define order: Move 'question_text' and 'field_type' to the start
                    question_column_order = ['question_id', 'question_text', 'field_type', 'options', 'slider_values']
                    df_question = df_question[[col for col in question_column_order if col in df_question.columns]]                   
                    # Display question in a DataFrame
                    st.dataframe(df_question, use_container_width=True)
                    with st.expander(f"Manage Question: {question['question_id']}", expanded=False):

                        # **Edit Question**
                        field_types = ["text", "number", "select", "slider"]
                        new_question_text = st.text_input("Edit Question Text", value=question['question_text'], key=f"new_question_text_{question_id}")
                        field_type = st.selectbox("Field Type", field_types, index=field_types.index(question['field_type']), key=f"field_type_{question_id}")

                        with st.form(key=f"edit_question_form_{question_id}"):
                            options = None
                            slider_values = None
                            if field_type == "select":
                                options_input = st.text_area("Options (comma-separated)", value=", ".join(question.get("options", []))).strip()
                                options = [opt.strip() for opt in options_input.split(',') if opt.strip()]
                            elif field_type == "slider":
                                min_value = st.number_input("Slider Min Value", value=question.get("slider_values", {}).get("min", 0))
                                max_value = st.number_input("Slider Max Value", value=question.get("slider_values", {}).get("max", 100))
                                default_value = st.number_input("Slider Default Value", value=question.get("slider_values", {}).get("default", (min_value + max_value) // 2))
                                slider_values = {"min": min_value, "max": max_value, "default": default_value}

                            update_question_button = st.form_submit_button(label="Update Question")

                        if update_question_button:
                            edit_question(questionnaire_id_input, question_id, new_question_text, field_type, options, slider_values)
                            st.rerun()

                        # **Delete Question**
                        if st.button(f"Delete Question ID: {question_id}", key=f"delete_question_{question_id}"):
                            delete_question(questionnaire_id_input, question_id)
                            st.rerun()

    st.divider()

manage_questionnaire()
