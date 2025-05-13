import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from io import BytesIO
import glob
import os
from datetime import datetime, date
import subprocess
import sys
import time
import plotly.graph_objects as go

# Ensure this is the correct path
base_folder = '/home/appuser/'

def run_generation_cleaning():
    with st.spinner("Generating data..."):
        try:
            subprocess.run([sys.executable, 'generate_data.py'], check=True)
        except subprocess.CalledProcessError as e:
            st.error(f"Error during data generation: {e}")
            return

    with st.spinner("Cleaning data..."):
        try:
            subprocess.run([sys.executable, 'clean_data.py'], check=True)
        except subprocess.CalledProcessError as e:
            st.error(f"Error during data cleaning: {e}")
            return

    with st.spinner("Analyzing data..."):
        try:
            subprocess.run([sys.executable, 'analyze_data.py'], check=True)
        except subprocess.CalledProcessError as e:
            st.error(f"Error during data analysis: {e}")
            return

    st.success("Data generation, cleaning, and analysis complete!")
    st.session_state['data_loaded'] = False
    time.sleep(1)
    st.rerun()

@st.cache_data
def load_and_report_data(file_pattern):
    list_of_files = glob.glob(file_pattern)
    
    if not list_of_files:
        st.error("No cleaned data files found. Please ensure the correct file pattern is used.")
        return None, None
    
    # Debugging: Show the matched files
    st.write(f"Files found matching pattern: {list_of_files}")

    latest_cleaned_file = max(list_of_files, key=os.path.getmtime)
    df_cleaned = pd.read_csv(latest_cleaned_file)
    df_cleaned['Timestamp'] = pd.to_datetime(df_cleaned['Timestamp'])
    df_cleaned['Hour'] = df_cleaned['Timestamp'].dt.hour

    # Locate analysis summary file
    cleaned_dir = os.path.dirname(latest_cleaned_file)
    analysis_file_pattern = os.path.join(cleaned_dir, 'analysis_summary_*.txt')
    summary_files = glob.glob(analysis_file_pattern)
    
    # Ensure we return exactly two values
    latest_summary_file = max(summary_files, key=os.path.getmtime) if summary_files else None
    
    return df_cleaned, latest_summary_file  # Ensure only two values are returned

# Streamlit UI
st.sidebar.button("Generate and Clean New Data", on_click=run_generation_cleaning)

if 'cleaned_file_pattern' not in st.session_state:
    st.session_state['cleaned_file_pattern'] = os.path.join(
        base_folder, 'Data_*', 'cleaned_it_service_performance_*.csv')

if 'data_loaded' not in st.session_state or not st.session_state['data_loaded']:
    df_cleaned, latest_summary_file = load_and_report_data(st.session_state['cleaned_file_pattern'])
    st.session_state['data_loaded'] = True
    st.session_state['loaded_data'] = df_cleaned
    st.session_state['latest_summary_file'] = latest_summary_file
else:
    df_cleaned = st.session_state.get('loaded_data')
    latest_summary_file = st.session_state.get('latest_summary_file')

if df_cleaned is not None:
    st.title("IT Service Performance Dashboard")
    st.markdown("Visualizing performance, error analysis, and satisfaction of IT services.")

    # Initialize date range
    min_date = df_cleaned['Timestamp'].min().date()
    max_date = df_cleaned['Timestamp'].max().date()

    if 'selected_dates' not in st.session_state:
        st.session_state['selected_dates'] = (min_date, max_date)

    # Date range filter
    selected_dates = st.sidebar.date_input("Select Date Range", value=st.session_state['selected_dates'])
    if len(selected_dates) == 2:
        st.session_state['selected_dates'] = selected_dates
        start_date, end_date = selected_dates
        if start_date > end_date:
            st.warning("Start date must be earlier than or equal to the end date.")
            st.stop()

        # Filter data based on date range
        df_filtered = df_cleaned[
            (df_cleaned['Timestamp'].dt.date >= start_date) &
            (df_cleaned['Timestamp'].dt.date <= end_date)
        ]

        selected_services = st.sidebar.multiselect("Select Services", df_filtered['Service Name'].unique(), 
                                                  default=list(df_filtered['Service Name'].unique()))
        df_filtered = df_filtered[df_filtered['Service Name'].isin(selected_services)]

        if not df_filtered.empty:
            # --- Hourly Response Time Trend ---
            st.header("Hourly Response Time Trend per Service")
            fig4, ax4 = plt.subplots(figsize=(10, 6))
            hourly_response = df_filtered.groupby(['Hour', 'Service Name'])['Response Time (ms)'].mean().unstack()
            hourly_response.plot(kind='line', marker='o', ax=ax4)
            plt.title('Hourly Average Response Time by Service')
            plt.xlabel('Hour of the Day')
            plt.ylabel('Average Response Time (ms)')
            plt.xticks(range(0, 24))
            plt.grid(True)
            plt.legend(title='Service Name')
            st.pyplot(fig4)

            # Most Frequent Error Codes
            st.header("Most Frequent Error Codes")
            error_counts = df_filtered['Error Code'].value_counts()
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            error_counts.plot(kind='bar', ax=ax2, color='skyblue')
            plt.title('Error Code Frequency')
            plt.xlabel('Error Code')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            st.pyplot(fig2)

            # Response Time vs User Satisfaction
            st.header("Response Time vs User Satisfaction")
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            sns.scatterplot(data=df_filtered, x='Response Time (ms)', y='User Satisfaction', hue='Service Name', ax=ax3)
            plt.title('Response Time vs User Satisfaction')
            st.pyplot(fig3)

            # User Satisfaction Distribution
            st.header("User Satisfaction Distribution")
            satisfaction_counts = df_filtered['User Satisfaction'].value_counts(normalize=True) * 100
            fig4, ax4 = plt.subplots(figsize=(8, 5))
            satisfaction_counts.plot(kind='bar', color='orange', ax=ax4)
            plt.title('User Satisfaction Level Distribution (Percentage)')
            st.pyplot(fig4)

        # Insights Summary
        st.header("Insights Summary")
        if latest_summary_file:
            try:
                with open(latest_summary_file, 'r') as file:
                    summary = file.read()
                st.text_area("Analysis Summary", summary, height=200)
            except FileNotFoundError:
                st.warning("Analysis summary file not found.")
            except Exception as e:
                st.error(f"Error reading summary file: {e}")
        else:
            st.warning("No analysis summary file found.")

        st.success("Dashboard loaded successfully!")
else:
    if 'selected_dates' not in st.session_state or len(st.session_state['selected_dates']) != 2:
        st.warning("Please select a valid date range.")
    else:
        st.warning("No cleaned data loaded. Please click 'Generate and Clean New Data'.")

