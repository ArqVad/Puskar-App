import streamlit as st
import pandas as pd
import plotly.express as px
from firebase_setup import db  # Ensure you have this setup correctly
from navigation import make_sidebar

st.session_state.page = "Visualization"
make_sidebar()

st.title("Visualization Dashboard")
st.divider()
with st.form(key='questionnaire_form'):
    submit_button = st.form_submit_button(label='Change Data Source')

if submit_button:
    st.switch_page("pages/vdashboard_page.py")

# Check if DataFrame is in session state
if 'df_response' in st.session_state:
    df_response = st.session_state['df_response']
    st.divider()
    st.subheader('Data Overview')
    st.write(df_response)

    st.divider()
    # Visualization logic starts here
    viz_df = df_response.copy()

    # Identify columns for questions and demographics
    question_columns = [col for col in viz_df.columns if col not in ['NIM', 'Fakultas', 'Prodi', 'IPK 2', 'Lama Studi', 'Tahun Masuk', 'Tahun Lulus']]
    demographic_columns = ['Fakultas', 'Prodi', 'IPK 2', 'Lama Studi', 'Tahun Masuk', 'Tahun Lulus']
    
    # Default x-axis for all charts
    default_x_axis = 'Fakultas'

    # Loop through each question to create visualizations
    for selected_question in question_columns:
        # Expander for each question visualization
        with st.expander(f"Visualization for {selected_question}", expanded=True):
            # Selectbox for changing X-axis per question
            x_axis = st.selectbox(f"Select Demographic Group for X-Axis for {selected_question}", demographic_columns, index=demographic_columns.index(default_x_axis), key=f'x_axis_{selected_question}')
            
            # Multiselect for filtering unique values within the chosen demographic column
            unique_values = viz_df[x_axis].unique()
            selected_values = st.multiselect(f"Filter by {x_axis} values", unique_values, default=unique_values, key=f'filter_{x_axis}_{selected_question}')
            
            # Filter the DataFrame based on selected values
            filtered_df = viz_df[viz_df[x_axis].isin(selected_values)]

            # Determine if the selected question is numerical or categorical
            is_numerical = filtered_df[selected_question].dtype in ['float64', 'int64']

            # Visualization Type
            if is_numerical:
                # Calculate average for numerical questions
                avg_value = filtered_df.groupby(x_axis)[selected_question].mean().reset_index()
                fig = px.bar(avg_value, x=x_axis, y=selected_question,
                             title=f"{selected_question} Average by {x_axis} (Filtered)",
                             labels={selected_question: "Average"},
                             text=selected_question)
                fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig.update_yaxes(range=[0, 100])  # Set Y-axis range to 0-100
                st.plotly_chart(fig)
            else:
                # Calculate percentage for categorical answers
                percentage_data = filtered_df.groupby([x_axis, selected_question]).size().reset_index(name='count')
                percentage_data['percentage'] = (percentage_data['count'] / percentage_data.groupby(x_axis)['count'].transform('sum')) * 100
                fig = px.bar(percentage_data, x=x_axis, y='percentage', color=selected_question,
                             title=f"{selected_question} Percentage by {x_axis} (Filtered)",
                             barmode='group', labels={'percentage': "Percentage"},
                             text='percentage')
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_yaxes(range=[0, 100])  # Set Y-axis range to 0-100
                st.plotly_chart(fig)
        st.divider()
else:
    st.warning("No data loaded. Please load data on the Data Loader page.")
